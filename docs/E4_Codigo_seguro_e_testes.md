# Etapa 4 - Código Seguro e Testes de Segurança

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @mariasanchez0’s
> São exigidas **2 práticas de código seguro**, escolhidas para cobrir requisitos já definidos na [Etapa 3](E3_Arquitetura_segura.md). O código fica em `codigo/etapa-4/`.

| Prática | Risco/requisito relacionado | Responsável | Situação |
| --- | --- | --- | --- |
| Armazenamento seguro de senhas (hash + salt em `senhaLogin`) | R01 / RS01 | @lilydias24 | Pendente |
| Controle de autorização no servidor (checagem de `nivelAcesso`) | R06 / RS03 | @PPrauchner | Pendente |

Cada responsável entrega: risco e requisito atendidos, **2 testes escritos antes da implementação** (1 caso válido + 1 caso malicioso/não autorizado), pseudocódigo ou implementação simples, resultado esperado e referência ao OWASP Cheat Sheet Series. O @mariasanchez0’s organiza a pasta e revisa os dois PRs.

---

## Prática 1 - Armazenamento seguro de senhas (@lilydias24)

- **Risco e requisito atendidos:** R01 (Spoofing) / RS01
- **Referência OWASP:** *(Password Storage Cheat Sheet - a confirmar)*

### Testes escritos antes da implementação

| # | Cenário | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| 1 | Caso válido | | |
| 2 | Caso malicioso | | |

### Implementação

*(Pseudocódigo ou implementação simples - versionar em `codigo/etapa-4/`.)*

### Resultado obtido

*(Pendente.)*

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
