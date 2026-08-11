"""Testes da Prática 1 - armazenamento seguro de senhas (@lilydias24).

Estes dois testes foram escritos **antes** da implementação, como pede a Etapa 4:
um caso válido e um caso malicioso. O caso malicioso reproduz exatamente o
vetor descrito no caso de abuso CA01 da Etapa 1 - o atacante que obtém o
conteúdo da tabela `Funcionario` e tenta usar o que encontrou para entrar.

Execução:  python teste_armazenamento_seguro_senha.py
"""

from armazenamento_seguro_senha import (
    gerar_registro_senha,
    precisa_atualizar_parametros,
    verificar_senha,
)

SENHA_DA_MEDICA = "Plantao#Noturno-2026"


def teste_1_caso_valido() -> None:
    """Caso válido: a profissional cadastra a senha e autentica com ela.

    Verifica também as duas propriedades que dão sentido ao cadastro:
    a senha não aparece no que foi persistido, e duas pessoas que escolheram
    a mesma senha não produzem o mesmo registro.
    """
    registro = gerar_registro_senha(SENHA_DA_MEDICA)

    assert verificar_senha(SENHA_DA_MEDICA, registro), (
        "a profissional deveria conseguir autenticar com a propria senha"
    )
    assert not verificar_senha("Plantao#Noturno-2025", registro), (
        "uma senha incorreta nao pode ser aceita"
    )
    assert SENHA_DA_MEDICA not in registro, (
        "a senha em claro nao pode aparecer no valor persistido em senhaLogin"
    )

    registro_de_outra_pessoa = gerar_registro_senha(SENHA_DA_MEDICA)
    assert registro != registro_de_outra_pessoa, (
        "duas contas com a mesma senha precisam gerar registros distintos (salt)"
    )

    print("[OK] Teste 1 - caso valido")
    print("     autenticacao com a senha correta.................. aceita")
    print("     autenticacao com senha incorreta.................. recusada")
    print("     senha em claro presente no registro............... nao")
    print("     registros iguais para senhas iguais............... nao (salt por credencial)")
    print(f"     exemplo de valor gravado.......................... {registro[:48]}...")


def teste_2_caso_malicioso() -> None:
    """Caso malicioso: vazamento da tabela Funcionario, como em CA01.

    O atacante lê o conteúdo de `senhaLogin` e tenta duas coisas: usar o valor
    lido diretamente como se fosse a senha, e usar apenas a parte do hash.
    Nenhuma das duas pode funcionar - é isso que diferencia um vazamento
    contornável de um vazamento que ainda exige quebrar cada senha.
    """
    registro_vazado = gerar_registro_senha(SENHA_DA_MEDICA)
    apenas_o_hash = registro_vazado.split("$")[-1]
    apenas_o_salt = registro_vazado.split("$")[-2]

    assert not verificar_senha(registro_vazado, registro_vazado), (
        "reenviar o registro inteiro como senha nao pode autenticar"
    )
    assert not verificar_senha(apenas_o_hash, registro_vazado), (
        "reenviar o hash como senha nao pode autenticar"
    )
    assert not verificar_senha(apenas_o_salt, registro_vazado), (
        "reenviar o salt como senha nao pode autenticar"
    )
    assert not verificar_senha("", registro_vazado), (
        "senha vazia nao pode autenticar"
    )
    assert not verificar_senha(SENHA_DA_MEDICA, "registro-corrompido"), (
        "registro malformado deve recusar, e nao lancar excecao"
    )

    print("[OK] Teste 2 - caso malicioso (posse do conteudo da tabela Funcionario)")
    print("     registro vazado reenviado como senha.............. recusado")
    print("     hash isolado reenviado como senha................. recusado")
    print("     salt isolado reenviado como senha................. recusado")
    print("     senha vazia....................................... recusada")
    print("     registro corrompido no banco...................... recusado sem excecao")


def teste_3_migracao_de_parametros() -> None:
    """Verificação auxiliar da cláusula 2 de RS01 (migração transparente)."""
    registro_atual = gerar_registro_senha(SENHA_DA_MEDICA)
    registro_fraco = registro_atual.replace("$32768$", "$16384$", 1)

    assert not precisa_atualizar_parametros(registro_atual)
    assert precisa_atualizar_parametros(registro_fraco)
    assert precisa_atualizar_parametros("md5$abc")

    print("[OK] Verificacao auxiliar - migracao de parametros")
    print("     registro com parametros vigentes.................. nao remigra")
    print("     registro com fator de trabalho menor.............. marcado para remigrar")
    print("     registro de algoritmo legado...................... marcado para remigrar")


if __name__ == "__main__":
    teste_1_caso_valido()
    print()
    teste_2_caso_malicioso()
    print()
    teste_3_migracao_de_parametros()
    print()
    print("Todos os testes passaram.")
