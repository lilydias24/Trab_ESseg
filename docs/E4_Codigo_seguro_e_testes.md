# Etapa 4 - Código Seguro e Testes de Segurança

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @mariasanchez0’s
> São exigidas **2 práticas de código seguro**, escolhidas para cobrir requisitos já definidos na [Etapa 3](E3_Arquitetura_segura.md). O código fica em `codigo/etapa-4/`.

| Prática | Risco/requisito relacionado | Responsável | Situação |
| --- | --- | --- | --- |
| Armazenamento seguro de senhas (hash + salt em `senhaLogin`) | R01 / RS01 | @lilydias24 | Concluída (testes executados) |
| Controle de autorização no servidor (checagem de `nivelAcesso`) | R06 / RS03 | @PPrauchner | Pendente |

Cada responsável entrega: risco e requisito atendidos, **2 testes escritos antes da implementação** (1 caso válido + 1 caso malicioso/não autorizado), pseudocódigo ou implementação simples, resultado esperado e referência ao OWASP Cheat Sheet Series. O @mariasanchez0’s organiza a pasta e revisa os dois PRs.

---

## Prática 1 - Armazenamento seguro de senhas (@lilydias24)

- **Risco e requisito atendidos:** R01 (Spoofing) / RS01, cláusulas 1 e 2
- **Referência OWASP:** [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- **Arquivos:** [`armazenamento_seguro_senha.py`](../codigo/etapa-4/armazenamento_seguro_senha.py) e [`teste_armazenamento_seguro_senha.py`](../codigo/etapa-4/teste_armazenamento_seguro_senha.py)

**O que esta prática ataca.** No modelo de domínio do SIGH, `Funcionario.senhaLogin` é um
atributo de texto simples. O caso de abuso CA01 usa exatamente isso: entre os caminhos
para obter a credencial de um médico está ler diretamente a tabela `Funcionario` após
acesso ao banco. A prática elimina esse caminho específico - não o acesso ao banco, mas o
fato de esse acesso entregar senhas prontas para uso.

### Testes escritos antes da implementação

| # | Cenário | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| 1 | **Caso válido** - a médica cadastra a senha e autentica com ela | `Plantao#Noturno-2026`, informada no cadastro e depois no login | Autenticação aceita; senha incorreta recusada; a senha em claro **não** aparece no valor persistido; duas contas com a mesma senha produzem registros diferentes |
| 2 | **Caso malicioso** - atacante de posse do conteúdo da tabela `Funcionario`, como em CA01 | O próprio valor gravado em `senhaLogin`, reenviado no campo de senha - inteiro, só o hash e só o salt | Todas as tentativas recusadas; senha vazia recusada; registro corrompido recusado sem lançar exceção |

Uma verificação auxiliar cobre a cláusula 2 de RS01: registros gerados com fator de
trabalho menor, ou com algoritmo legado, precisam ser marcados para regravação
transparente na próxima autenticação bem-sucedida.

### Implementação

Implementação executável em Python, sem dependências externas, para que qualquer
integrante consiga conferir o resultado. O registro gravado tem o formato
`scrypt$N$r$p$salt$hash`, guardando o algoritmo e os parâmetros junto do valor - é isso
que permite reforçar o custo depois sem invalidar as senhas já cadastradas.

Três decisões merecem registro:

- **Algoritmo.** O Cheat Sheet recomenda Argon2id em primeiro lugar e aceita scrypt como
  alternativa. Aqui foi usado `hashlib.scrypt`, da biblioteca padrão, porque torna a
  prática verificável sem instalar nada. **Em produção o SIGH deveria usar Argon2id**, e o
  formato do registro já prevê essa troca.
- **Salt por credencial.** Gerado com `secrets.token_bytes(16)`. É o que impede que duas
  pessoas com a mesma senha tenham o mesmo registro e o que inviabiliza tabelas
  pré-computadas.
- **Comparação em tempo constante.** `hmac.compare_digest`, para que o tempo de resposta
  não revele quantos bytes do valor derivado foram acertados.

Durante a execução apareceu uma limitação prática que vale documentar: com `N = 2^15` e
`r = 8`, o scrypt precisa de exatamente 32 MiB, e o OpenSSL recusa a operação nesse limite
se ele não for declarado. Foi preciso informar `maxmem` explicitamente. O custo de memória
não é um efeito colateral a contornar - é ele que torna caro o ataque em GPU.

### Resultado obtido

Execução real, em Python 3.13.7:

```
$ python teste_armazenamento_seguro_senha.py

[OK] Teste 1 - caso valido
     autenticacao com a senha correta.................. aceita
     autenticacao com senha incorreta.................. recusada
     senha em claro presente no registro............... nao
     registros iguais para senhas iguais............... nao (salt por credencial)
     exemplo de valor gravado.......................... scrypt$32768$8$1$3202ChjmCDMZrEd0sxK0qA==$UeN9jZ...

[OK] Teste 2 - caso malicioso (posse do conteudo da tabela Funcionario)
     registro vazado reenviado como senha.............. recusado
     hash isolado reenviado como senha................. recusado
     salt isolado reenviado como senha................. recusado
     senha vazia....................................... recusada
     registro corrompido no banco...................... recusado sem excecao

[OK] Verificacao auxiliar - migracao de parametros
     registro com parametros vigentes.................. nao remigra
     registro com fator de trabalho menor.............. marcado para remigrar
     registro de algoritmo legado...................... marcado para remigrar

Todos os testes passaram.
```

**O que isto comprova e o que não comprova.** Comprova o controle **R01-C1** do plano de
tratamento da [Etapa 2](E2_Riscos_e_NIST_CSF.md) e as cláusulas 1 e 2 de
[RS01](E3_Arquitetura_segura.md): o vazamento da tabela deixa de ser diretamente
reutilizável. **Não** comprova os demais controles de R01 - MFA, bloqueio por tentativas e
expiração de sessão seguem sendo especificação, não código. É por isso que o risco
residual de R01 permanece Alto: esta prática fecha um dos cinco caminhos, e o phishing em
tempo real, que é o caminho remanescente, não passa pelo banco de dados.

---

## Prática 2 - Controle de autorização no servidor (@PPrauchner)

- **Risco e requisito atendidos:** R06 (Elevation of Privilege) / RS03
- **Referência OWASP:** *(Authorization Cheat Sheet - a confirmar)*

### Testes escritos antes da implementação

| # | Cenário | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| 1 | Caso válido | | |
| 2 | Caso não autorizado | | |

### Implementação

*(Pseudocódigo ou implementação simples - versionar em `codigo/etapa-4/`.)*

### Resultado obtido

*(Pendente.)*
