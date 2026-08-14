"""Testes da Prática 2 - controle de autorização no servidor (@PPrauchner).

Estes dois testes foram escritos **antes** da implementação, como pede a Etapa 4.
Eles são exatamente os dois primeiros critérios de verificação de RS03, definidos
na Etapa 3:

- Teste 1 (caso válido)  = RS03-CA01: sessão de Diretor promove outro funcionário.
- Teste 2 (não autorizado) = RS03-CA02 e RS03-CA03: sessão de Supervisor tenta
  elevar o próprio `nivelAcesso`, inclusive chamando o endpoint diretamente.

As verificações auxiliares cobrem RS03-CA04, RS03-CA05, RS03-CA06 e RS03-CA08, e
a validação de entrada da operação de alteração de perfil (HTTP 400).

Execução:  python teste_autorizacao_servidor.py
"""

from autorizacao_servidor import (
    ErroAutorizacao,
    ErroDeEntrada,
    ServicoDeAutorizacao,
    ServicoDeFuncionarios,
    Sessao,
    TrilhaDeAuditoria,
    cadastro_de_exemplo,
)

SESSAO_DIRETOR = Sessao(
    id_funcionario="F001",
    perfil="Administrador",
    nivel_acesso="Diretor",
    terminal="TERM-ADM-01",
)
SESSAO_SUPERVISOR = Sessao(
    id_funcionario="F003",
    perfil="Administrador",
    nivel_acesso="Supervisor",
    terminal="TERM-SET-07",
)


def montar_servico() -> tuple[ServicoDeFuncionarios, TrilhaDeAuditoria]:
    trilha = TrilhaDeAuditoria()
    servico = ServicoDeFuncionarios(
        cadastro=cadastro_de_exemplo(),
        autorizacao=ServicoDeAutorizacao(),
        trilha=trilha,
    )
    return servico, trilha


def teste_1_caso_valido() -> None:
    """RS03-CA01 - Diretor promove outro funcionário a GerenteSetor.

    Verifica a alteração aceita e o conteúdo da trilha: autor, valor anterior,
    valor novo e data/hora carimbada pelo servidor (cláusula 5 de RS03).
    """
    servico, trilha = montar_servico()

    resposta = servico.executar(
        SESSAO_DIRETOR,
        "alterarPerfil",
        id_alvo="F003",
        corpo={"novoNivelAcesso": "GerenteSetor"},
    )

    assert resposta["nivelAcesso"] == "GerenteSetor", (
        "a promocao feita por sessao de Diretor sobre outro funcionario deve ser aceita"
    )

    entrada = trilha.entradas()[-1]
    assert entrada["resultado"] == "EFETIVADA"
    assert entrada["autor"] == SESSAO_DIRETOR.id_funcionario
    assert entrada["valor_anterior"] == "Supervisor"
    assert entrada["valor_novo"] == "GerenteSetor"
    assert entrada["momento_servidor"], "a data/hora tem de ser carimbada pelo servidor"
    assert entrada["terminal"] == SESSAO_DIRETOR.terminal
    assert trilha.alertas_de_elevacao(), (
        "toda elevacao efetivada alimenta a Regra 3 da Etapa 6"
    )

    print("[OK] Teste 1 - caso valido (RS03-CA01)")
    print("     promocao de outro funcionario por sessao Diretor.. aceita")
    print(f"     nivelAcesso do alvo apos a operacao.............. {resposta['nivelAcesso']}")
    print(f"     trilha - autor................................... {entrada['autor']}")
    print(f"     trilha - valor anterior / valor novo............. {entrada['valor_anterior']} -> {entrada['valor_novo']}")
    print(f"     trilha - data/hora carimbada pelo servidor....... {entrada['momento_servidor']}")
    print("     alerta da clausula 7 (elevacao efetivada)........ emitido")


def teste_2_caso_nao_autorizado() -> None:
    """RS03-CA02 e RS03-CA03 - Supervisor tenta elevar o próprio nivelAcesso.

    O ataque tem duas faces, e as duas são exercidas aqui. Pela via de salvamento
    do cadastro (o passo 3 de CA05), o campo é descartado antes de qualquer
    validação e o valor persistido não muda. Pela operação que de fato altera o
    perfil, a resposta é HTTP 403. As chamadas partem direto do serviço, sem
    interface: é o que RS03-CA03 exige - a recusa não depende da tela.
    """
    servico, trilha = montar_servico()

    servico.executar(
        SESSAO_SUPERVISOR,
        "salvarCadastro",
        id_alvo="F003",
        corpo={"setor": "Ambulatorio", "nivelAcesso": "Diretor", "perfil": "Diretor"},
    )
    assert servico.nivel_acesso_de("F003") == "Supervisor", (
        "o nivelAcesso nao pode ser gravado pela via de salvamento do cadastro"
    )

    try:
        servico.executar(
            SESSAO_SUPERVISOR,
            "alterarPerfil",
            id_alvo="F003",
            corpo={"novoNivelAcesso": "Diretor"},
        )
        raise AssertionError("a alteracao de perfil sem alcada deveria ser recusada")
    except ErroAutorizacao as erro:
        assert erro.codigo_http == 403, "a recusa tem de ser HTTP 403"

    assert servico.nivel_acesso_de("F003") == "Supervisor", (
        "a recusa nao pode deixar efeito parcial"
    )

    recusa = trilha.entradas()[-1]
    assert recusa["resultado"] == "RECUSADA"
    assert recusa["autor"] == SESSAO_SUPERVISOR.id_funcionario

    # As duas faces alimentam a Regra 3, como manda RS03-CA02: a do salvamento
    # pelo campo descartado, a da operacao propria pela recusa. Uma asserção só
    # sobre a segunda passaria mesmo se a primeira ficasse invisível.
    eventos = trilha.eventos_para_regra_3()
    assert any(e["operacao"] == "salvarCadastro" for e in eventos), (
        "a tentativa pela via de salvamento tem de alimentar a Regra 3"
    )
    assert any(e["operacao"] == "alterarPerfil" for e in eventos), (
        "a tentativa pela operacao propria tem de alimentar a Regra 3"
    )
    # Cláusula 7: o alerta é das elevações efetivadas. Nenhuma houve aqui.
    assert not trilha.alertas_de_elevacao(), (
        "recusa nao e elevacao efetivada: nao dispara o alerta da clausula 7"
    )

    print("[OK] Teste 2 - caso nao autorizado (RS03-CA02 e RS03-CA03)")
    print("     nivelAcesso enviado no salvamento do cadastro.... descartado")
    print(f"     nivelAcesso persistido apos a tentativa.......... {servico.nivel_acesso_de('F003')}")
    print("     alteracao de perfil sem alcada de Diretor........ recusada com HTTP 403")
    print("     requisicao enviada direto ao endpoint............ mesmo resultado")
    print("     efeito parcial no cadastro....................... nenhum")
    print("     trilha - tentativa recusada registrada........... sim")
    print(f"     eventos que alimentam a Regra 3.................. {len(eventos)} (as duas faces)")
    print("     alerta da clausula 7 (elevacao efetivada)........ nenhum, como esperado")


def teste_3_verificacoes_auxiliares() -> None:
    """RS03-CA04, RS03-CA05, RS03-CA06 e RS03-CA08."""
    servico, trilha = montar_servico()

    # RS03-CA04 - alteração legítima de dados funcionais com nivelAcesso junto.
    resposta = servico.executar(
        SESSAO_DIRETOR,
        "salvarCadastro",
        id_alvo="F002",
        corpo={"setor": "Emergencia", "nivelAcesso": "Diretor"},
    )
    assert resposta["setor"] == "Emergencia", "os dados funcionais devem ser gravados"
    assert servico.nivel_acesso_de("F002") == "GerenteGeral", (
        "o campo de privilegio permanece inalterado"
    )
    assert trilha.entradas()[-1]["campos_descartados"] == ("nivelAcesso",), (
        "a tentativa de gravar o campo precisa ficar registrada, sem erro silencioso"
    )
    # A trilha guarda o par que a Regra 3 da Etapa 6 compara: o nível vigente,
    # do servidor, e o que o corpo afirmava. Valores diferentes são tentativa de
    # gravação e contam no Gatilho C; iguais seriam reenvio de rotina.
    assert trilha.entradas()[-1]["nivel_afirmado"] == "Diretor", (
        "o valor afirmado pelo cliente e evidencia (clausula 5), nao so o nome do campo"
    )
    assert trilha.entradas()[-1]["valor_anterior"] == "GerenteGeral", (
        "sem o nivel vigente na entrada, a Regra 3 nao separa reenvio de tentativa"
    )

    # RS03-CA05 - o Diretor não tem alçada sobre o próprio registro.
    try:
        servico.executar(
            SESSAO_DIRETOR,
            "alterarPerfil",
            id_alvo=SESSAO_DIRETOR.id_funcionario,
            corpo={"novoNivelAcesso": "Diretor"},
        )
        raise AssertionError("o titular nunca e autorizado sobre o proprio registro")
    except ErroAutorizacao as erro:
        assert erro.codigo_http == 403

    # RS03-CA06 - endpoint novo, sem regra declarada: negação por padrão.
    try:
        servico.executar(
            SESSAO_DIRETOR, "exportarFolhaDePagamento", id_alvo="F002", corpo={}
        )
        raise AssertionError("operacao sem regra declarada tem de ser recusada")
    except ErroAutorizacao as erro:
        assert erro.codigo_http == 403

    # Cláusula 3 - a via de salvamento não alcança o registro de terceiro sem
    # alçada, nem grava campo fora dos dados funcionais. Sem os dois limites, o
    # Supervisor reescreveria a `senhaLogin` do Diretor e entraria como ele:
    # R06 pela porta ao lado, sobre exatamente o que RS01 protege.
    try:
        servico.executar(
            SESSAO_SUPERVISOR,
            "salvarCadastro",
            id_alvo="F001",
            corpo={"senhaLogin": "senha-do-atacante"},
        )
        raise AssertionError("salvar cadastro de terceiro sem alcada tem de ser recusado")
    except ErroAutorizacao as erro:
        assert erro.codigo_http == 403

    servico.executar(
        SESSAO_DIRETOR,
        "salvarCadastro",
        id_alvo="F003",
        corpo={"setor": "Almoxarifado", "senhaLogin": "senha-do-atacante"},
    )
    assert servico.credencial_de("F003") != "senha-do-atacante", (
        "a via de salvamento nunca grava campo de autenticacao, nem com alcada"
    )
    assert "senhaLogin" in trilha.entradas()[-1]["campos_descartados"], (
        "o campo fora da allowlist tem de ficar registrado, sem erro silencioso"
    )

    # RS03-CA08 - leitura em massa: limite de volume e nenhum campo de autenticação.
    pagina = servico.executar(SESSAO_DIRETOR, "listarCadastro", id_alvo=None, corpo={})
    assert len(pagina) <= servico.limite_de_listagem
    assert all("senhaLogin" not in registro for registro in pagina)
    assert all("nomeLogin" not in registro for registro in pagina)
    assert trilha.entradas()[-1]["operacao"] == "listarCadastro", (
        "cada consulta em massa fica registrada"
    )

    print("[OK] Verificacoes auxiliares - RS03-CA04 a RS03-CA08")
    print("     dados funcionais gravados, nivelAcesso ignorado.. CA04")
    print("     Diretor elevando a si mesmo...................... CA05, recusado (403)")
    print("     endpoint sem regra declarada..................... CA06, negado por padrao")
    print("     salvar cadastro de terceiro sem alcada........... recusado (403)")
    print("     senhaLogin pela via de salvamento................ fora da allowlist")
    print(f"     listagem em massa limitada a {servico.limite_de_listagem} registros........ CA08")
    print("     campos de autenticacao na listagem............... nenhum")


def teste_4_entrada_invalida() -> None:
    """Validação de entrada da alteração de perfil - HTTP 400, e nada gravado.

    Não é critério de RS03: a cláusula 3 fala de *quem* pode alterar, não de
    *para qual valor*. É o complemento necessário para que a decisão do servidor
    nunca opere sobre um nível fora do conjunto de domínio, e para que entrada
    malformada de cliente não vire erro de servidor.
    """
    servico, trilha = montar_servico()

    # Nível inexistente, com sessão plenamente autorizada: a alçada não autoriza
    # inventar perfil.
    try:
        servico.executar(
            SESSAO_DIRETOR,
            "alterarPerfil",
            id_alvo="F003",
            corpo={"novoNivelAcesso": "SuperDiretor"},
        )
        raise AssertionError("nivel fora do conjunto conhecido tem de ser recusado")
    except ErroDeEntrada as erro:
        assert erro.codigo_http == 400, "entrada invalida e 400, nao 403"

    assert servico.nivel_acesso_de("F003") == "Supervisor", (
        "recusa por nivel invalido nao pode deixar gravacao"
    )

    # Parâmetro ausente: 400, e não KeyError virando 500.
    try:
        servico.executar(
            SESSAO_DIRETOR, "alterarPerfil", id_alvo="F003", corpo={}
        )
        raise AssertionError("parametro ausente tem de ser recusado")
    except KeyError:
        raise AssertionError("parametro ausente nao pode virar KeyError (HTTP 500)")
    except ErroDeEntrada as erro:
        assert erro.codigo_http == 400

    assert servico.nivel_acesso_de("F003") == "Supervisor", (
        "recusa por parametro ausente nao pode deixar gravacao"
    )
    # Alvo inexistente: mesma classe de pedido malformado. Sem o guarda, a busca
    # no cadastro levantaria KeyError - erro de servidor para entrada de cliente.
    try:
        servico.executar(
            SESSAO_DIRETOR,
            "alterarPerfil",
            id_alvo="F999",
            corpo={"novoNivelAcesso": "Diretor"},
        )
        raise AssertionError("alvo inexistente tem de ser recusado")
    except KeyError:
        raise AssertionError("alvo inexistente nao pode virar KeyError (HTTP 500)")
    except ErroDeEntrada as erro:
        assert erro.codigo_http == 400, "alvo inexistente e 400, nao 403"

    assert not trilha.alertas_de_elevacao(), (
        "nenhuma elevacao foi efetivada: nada a alertar"
    )

    print("[OK] Validacao de entrada da alteracao de perfil")
    print("     promocao para nivel inexistente.................. recusada (400)")
    print("     parametro novoNivelAcesso ausente................ recusado (400), sem KeyError")
    print("     alvo inexistente no cadastro..................... recusado (400), sem KeyError")
    print(f"     nivelAcesso persistido apos as tres tentativas... {servico.nivel_acesso_de('F003')}")


def teste_5_rebaixamento_nao_alerta() -> None:
    """O alerta da cláusula 7 é de **elevação**, não de toda alteração de perfil.

    Um rebaixamento fica registrado na trilha, mas não notifica Diretor e
    Segurança da Informação: é o Gatilho A da Regra 3 da Etapa 6, que trata
    rebaixamento como registro e não como notificação. Sem esta verificação, a
    Prática 2 reivindicaria ser a fonte de evento da cláusula 7 emitindo evento
    onde a cláusula não pede.
    """
    servico, trilha = montar_servico()

    servico.executar(
        SESSAO_DIRETOR,
        "alterarPerfil",
        id_alvo="F002",
        corpo={"novoNivelAcesso": "Supervisor"},
    )

    entradas = [e for e in trilha.entradas() if e["operacao"] == "alterarPerfil"]
    assert len(entradas) == 1, "o rebaixamento tem de ficar na trilha"
    assert entradas[0]["resultado"] == "EFETIVADA"
    assert not trilha.alertas_de_elevacao(), (
        "rebaixamento nao e elevacao: nao alerta pela clausula 7"
    )

    # A elevação seguinte, sobre o mesmo alvo, volta a alertar - o filtro
    # distingue a direção da mudança, não a operação.
    servico.executar(
        SESSAO_DIRETOR,
        "alterarPerfil",
        id_alvo="F002",
        corpo={"novoNivelAcesso": "GerenteGeral"},
    )
    assert len(trilha.alertas_de_elevacao()) == 1, (
        "a elevacao seguinte tem de alertar"
    )

    print("[OK] Direcao da alteracao de perfil (clausula 7)")
    print("     rebaixamento GerenteGeral -> Supervisor.......... registrado, sem alerta")
    print("     elevacao Supervisor -> GerenteGeral.............. alerta emitido")
    print(f"     alertas da clausula 7 apos as duas operacoes..... {len(trilha.alertas_de_elevacao())}")


if __name__ == "__main__":
    teste_1_caso_valido()
    print()
    teste_2_caso_nao_autorizado()
    print()
    teste_3_verificacoes_auxiliares()
    print()
    teste_4_entrada_invalida()
    print()
    teste_5_rebaixamento_nao_alerta()
    print()
    print("Todos os testes passaram.")
