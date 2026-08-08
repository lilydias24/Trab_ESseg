# Etapa 6 - Monitoramento e Detecção de Intrusões

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lilydias24
> É exigido um **roteiro com 3 regras de detecção**, reaproveitando os riscos já registrados na [Etapa 2](E2_Riscos_e_NIST_CSF.md).

 - A compilação final do roteiro fica em `roteiros/E6-deteccao-de-intrusoes.md`.

| Regra | Risco observado | Responsável | Situação |
| --- | --- | --- | --- |
| 1 | R01 - Spoofing | @lilydias24 | Pendente |
| 2 | R02 - Tampering | @ARTHUR9011 | Pendente |
| 3 | R06 - Elevation of Privilege | @PPrauchner | Pendente |
| Compilação do roteiro final | @lilydias24 | Pendente |

---

## Quadro de regras

| Regra | Risco observado | Fonte de dados | Condição de alerta | Ação esperada | Responsável |
| --- | --- | --- | --- | --- | --- |
| 1 | R01 - Spoofing | Logs de autenticação | Muitas tentativas malsucedidas seguidas para a mesma conta | | @lilydias24 |
| 2 | R02 - Tampering | Logs de alteração de prescrição | Alteração de dosagem fora do padrão registrado, sem segunda assinatura | | @ARTHUR9011 |
| 3 | R06 - Elevation of Privilege | Logs de autorização | Tentativa de acesso a função administrativa por usuário sem `nivelAcesso` compatível | | @PPrauchner |

## Regra 1 - Tentativas de autenticação suspeitas (@lilydias24)

- **Risco observado:** R01
- **Fonte de dados:**
- **Condição de alerta (limiar e janela):**
- **O que o alerta indica:**
- **Ação esperada da equipe:**
- **Falsos positivos previstos:**

## Regra 2 - *(a definir)* (@ARTHUR9011)

- **Risco observado:** R02
- **Fonte de dados:**
- **Condição de alerta:**
- **O que o alerta indica:**
- **Ação esperada da equipe:**
- **Falsos positivos previstos:**

## Regra 3 - *(a definir)* (@PPrauchner)

- **Risco observado:** R06
- **Fonte de dados:**
- **Condição de alerta:**
- **O que o alerta indica:**
- **Ação esperada da equipe:**
- **Falsos positivos previstos:**
