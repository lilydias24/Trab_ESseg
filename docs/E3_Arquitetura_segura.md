# Etapa 3 - Projeto de uma Arquitetura Segura

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lorenzoficher
> São exigidos **3 requisitos de segurança**, e não um por integrante. O grupo levou adiante os riscos mais críticos e que cobrem categorias distintas de controle: autenticação, integridade de dados e autorização.

| Item | Responsável | Situação |
| --- | --- | --- |
| RS01 - requisito e vulnerabilidade | @lilydias24 | Pendente |
| RS02 - requisito e vulnerabilidade | @ARTHUR9011 | Pendente |
| RS03 - requisito e vulnerabilidade | @PPrauchner | Pendente |
| Diagrama da arquitetura segura | @lorenzoficher | Pendente |
| Decisão de arquitetura 1 (ligada ao diagrama) | @lorenzoficher | Pendente |
| Decisão de arquitetura 2 (ligada a RS03) | @mariasanchez0’s | Pendente |
| Decisão de arquitetura 3 (reforço de autenticação) | @lilydias24 ou @ARTHUR9011 | Pendente |

---

## 1. Requisitos de segurança

| ID | Risco de origem | Requisito de segurança | Responsável |
| --- | --- | --- | --- |
| RS01 | R01 - Spoofing | O sistema deve exigir autenticação multifator no login e reautenticação antes de operações sensíveis envolvendo a conta de `Funcionario` | @lilydias24 |
| RS02 | R02 - Tampering | Toda alteração de `PrescricaoMedicamento` deve ser assinada digitalmente pelo médico responsável e registrada em trilha de auditoria | @ARTHUR9011 |
| RS03 | R06 - Elevation of Privilege | O sistema deve validar `nivelAcesso` no servidor em toda operação administrativa, e não apenas ocultar opções na interface | @PPrauchner |

*(Detalhar cada requisito: enunciado completo, comportamento esperado e critério de verificação.)*

## 2. Vulnerabilidades catalogadas (CWE/OWASP)

| Requisito | Vulnerabilidade relacionada | Referência | Responsável |
| --- | --- | --- | --- |
| RS01 | Improper Authentication | CWE-287 (a confirmar/complementar) | @lilydias24 |
| RS02 | Insufficient Verification of Data Authenticity | CWE-345 (a confirmar/complementar) | @ARTHUR9011 |
| RS03 | Missing Authorization / Broken Access Control | CWE-862, OWASP A01 (a confirmar/complementar) | @PPrauchner |

*(Cada responsável descreve a vulnerabilidade com as próprias palavras, relacionando-a ao ponto concreto do SIGH.)*

## 3. Diagrama da arquitetura segura

> Responsável: **@lorenzoficher** - parte de `diagrams/estrutura/Diagramas_SIGH - Componentes.png` (já versionado) e acrescenta serviço de autenticação, serviço de autorização e componente de logs/auditoria. Exportar como `diagrams/estrutura/SIGH - Arquitetura segura.png`.

<!-- Descomentar quando o diagrama estiver exportado:
![Arquitetura segura do SIGH](../diagrams/estrutura/SIGH%20-%20Arquitetura%20segura.png)
-->

*(Pendente.)*

## 4. Decisões de arquitetura

### DA01 - *(a definir)* - @lorenzoficher

- **Contexto:**
- **Decisão:**
- **Alternativas consideradas:**
- **Consequências:**

### DA02 - *(a definir, ligada a RS03)* - @mariasanchez0’s

- **Contexto:**
- **Decisão:**
- **Alternativas consideradas:**
- **Consequências:**

### DA03 - *(a definir, reforço de autenticação)* - @lilydias24 ou @ARTHUR9011

- **Contexto:**
- **Decisão:**
- **Alternativas consideradas:**
- **Consequências:**
