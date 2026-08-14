"""Testes da Prática 2 - controle de autorização no servidor (@PPrauchner).

Estes dois testes foram escritos **antes** da implementação, como pede a Etapa 4.
Eles são exatamente os dois primeiros critérios de verificação de RS03, definidos
na Etapa 3:

- Teste 1 (caso válido)  = RS03-CA01: sessão de Diretor promove outro funcionário.
- Teste 2 (não autorizado) = RS03-CA02 e RS03-CA03: sessão de Supervisor tenta
  elevar o próprio `nivelAcesso`, inclusive chamando o endpoint diretamente.

As verificações auxiliares cobrem RS03-CA04, RS03-CA05, RS03-CA06 e RS03-CA08.

Execução:  python teste_autorizacao_servidor.py
"""

from autorizacao_servidor import (
    ErroAutorizacao,
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
    print("     alerta de elevacao (Regra 3, Etapa 6)............ emitido")


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
    assert trilha.alertas_de_elevacao(), (
        "tentativa recusada de elevacao tambem dispara o alerta da Regra 3"
    )

    print("[OK] Teste 2 - caso nao autorizado (RS03-CA02 e RS03-CA03)")
    print("     nivelAcesso enviado no salvamento do cadastro.... descartado")
    print(f"     nivelAcesso persistido apos a tentativa.......... {servico.nivel_acesso_de('F003')}")
    print("     alteracao de perfil sem alcada de Diretor........ recusada com HTTP 403")
    print("     requisicao enviada direto ao endpoint............ mesmo resultado")
    print("     efeito parcial no cadastro....................... nenhum")
    print("     trilha - tentativa recusada registrada........... sim")
    print("     alerta de elevacao (Regra 3, Etapa 6)............ emitido")


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
    print(f"     listagem em massa limitada a {servico.limite_de_listagem} registros........ CA08")
    print("     campos de autenticacao na listagem............... nenhum")


if __name__ == "__main__":
    teste_1_caso_valido()
    print()
    teste_2_caso_nao_autorizado()
    print()
    teste_3_verificacoes_auxiliares()
    print()
    print("Todos os testes passaram.")
