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
| RS02 | R02 - Tampering | Toda alteração de prescrição ativa deve ser autorizada e validada no servidor, confirmada por segundo profissional e registrada com autoria e versionamento em trilha de auditoria imutável | @ARTHUR9011 |
| RS03 | R06 - Elevation of Privilege | O sistema deve validar `nivelAcesso` no servidor em toda operação administrativa, e não apenas ocultar opções na interface | @PPrauchner |

*(Detalhar cada requisito: enunciado completo, comportamento esperado e critério de verificação.)*

### RS02 - Integridade e rastreabilidade da prescrição ativa (@ARTHUR9011)

**Risco de origem.** R02 - alteração indevida de `dosagemMedicamento` ou
`intervaloConsumo` de uma `PrescricaoMedicamento` ativa, executada pela enfermagem como
se fosse a versão legítima. O requisito atua antes de a mudança chegar à administração
do medicamento, porque o dano clínico não pode ser desfeito pelo sistema depois desse
momento.

**Enunciado completo.** Toda solicitação de alteração de uma prescrição ativa deve ser
processada no servidor e somente pode produzir uma nova versão vigente quando, na mesma
transação, o SIGH:

1. obtiver o autor da sessão autenticada, sem aceitar identidade informada pelo cliente;
2. confirmar que o autor é médico e está vinculado ao atendimento do paciente;
3. validar `dosagemMedicamento` e `intervaloConsumo` contra a faixa terapêutica cadastrada
   para o medicamento;
4. exigir reautenticação do autor e confirmação de um segundo profissional autorizado,
   diferente do autor da mudança;
5. preservar a versão anterior e acrescentar uma nova versão à trilha de auditoria; e
6. tornar a nova versão disponível para administração somente depois que todas as
   verificações e o registro de auditoria forem concluídos com sucesso.

**Comportamento esperado.** A trilha deve ser somente de acréscimo e registrar, no
mínimo, o identificador da prescrição e do paciente, medicamento, dose e intervalo
anteriores e novos, justificativa, autor, segundo confirmador, data/hora fornecida pelo
servidor e identificador de correlação da operação. Nenhum desses dados de autoria pode
vir do corpo enviado pelo Desktop Cliente. Se autorização, vínculo, faixa terapêutica,
reautenticação, confirmação independente ou gravação da auditoria falhar, a operação deve
falhar de forma fechada: a versão vigente permanece inalterada, nenhuma atualização
parcial é persistida e a tentativa recusada é registrada para detecção.

Neste requisito, **confirmação** ou **coassinatura** significa uma aprovação eletrônica
atribuída a outra sessão autenticada e vinculada à versão exata da prescrição. Ela não é
tratada como assinatura digital criptográfica baseada em certificado. Se o grupo optar
por uma assinatura digital nesse sentido estrito, será necessária uma decisão de
arquitetura própria para identidade do signatário, gestão e revogação de chaves,
formato assinado e verificação de longo prazo.

**Critérios de verificação.** O requisito é considerado atendido quando os seguintes
cenários forem demonstrados por testes automatizados e pela consulta à auditoria:

| ID | Cenário | Resultado verificável |
| --- | --- | --- |
| RS02-CA01 | Médico vinculado informa valores dentro da faixa, reautentica e recebe confirmação válida de outro profissional | Uma nova versão torna-se vigente e a anterior permanece consultável; a auditoria contém todos os campos obrigatórios |
| RS02-CA02 | Perfil não médico tenta alterar a prescrição | A solicitação é recusada, a versão vigente não muda e a tentativa fica registrada |
| RS02-CA03 | Médico não vinculado ao paciente tenta alterar a prescrição | A solicitação é recusada, a versão vigente não muda e a tentativa fica registrada |
| RS02-CA04 | Dose ou intervalo está fora da faixa terapêutica | A solicitação é recusada antes de ficar disponível para administração e a divergência fica registrada |
| RS02-CA05 | Reautenticação está ausente/inválida, não há segundo confirmador ou autor e confirmador são a mesma pessoa | A solicitação é recusada e nenhuma nova versão é criada |
| RS02-CA06 | O registro da auditoria falha durante a alteração | Toda a transação é revertida; a prescrição anterior continua vigente e não há versão parcial |
| RS02-CA07 | Um usuário da aplicação tenta alterar ou excluir uma versão já registrada | A operação é recusada e a trilha preserva integralmente o histórico |

## 2. Vulnerabilidades catalogadas (CWE/OWASP)

| Requisito | Vulnerabilidade relacionada | Referência | Responsável |
| --- | --- | --- | --- |
| RS01 | Improper Authentication | CWE-287 (a confirmar/complementar) | @lilydias24 |
| RS02 | Ausência de autorização no servidor, confiança em validações do cliente, entrada clínica sem validação e auditoria insuficiente | CWE-862, CWE-602, CWE-20 e CWE-778; OWASP A01, A06 e A09:2025 | @ARTHUR9011 |
| RS03 | Missing Authorization / Broken Access Control | CWE-862, OWASP A01 (a confirmar/complementar) | @PPrauchner |

*(Cada responsável descreve a vulnerabilidade com as próprias palavras, relacionando-a ao ponto concreto do SIGH.)*

### Vulnerabilidades relacionadas a RS02 (@ARTHUR9011)

Como o SIGH não está implementado, os itens abaixo são **fraquezas potenciais indicadas
pelo modelo**, e não vulnerabilidades confirmadas em código. Elas devem ser verificadas
pelos critérios de RS02 e pelos testes de segurança das etapas seguintes.

| Referência | Relação concreta com o SIGH |
| --- | --- |
| [CWE-862 - Missing Authorization](https://cwe.mitre.org/data/definitions/862.html) | A regra do UC03 exige médico autorizado, mas `atualizarTratamentosDoPaciente(tratamento)` não demonstra uma checagem de papel e de vínculo com o paciente no servidor. É a fraqueza principal de RS02. |
| [CWE-602 - Client-Side Enforcement of Server-Side Security](https://cwe.mitre.org/data/definitions/602.html) | Se o Desktop Cliente apenas ocultar a opção para outros perfis, a proteção pode ser contornada por uma chamada modificada. A decisão precisa ser repetida no servidor com dados da sessão. |
| [CWE-20 - Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html) | O modelo não especifica validação de `dosagemMedicamento` e `intervaloConsumo` contra limites terapêuticos antes de persistir a mudança. |
| [CWE-778 - Insufficient Logging](https://cwe.mitre.org/data/definitions/778.html) | A alteração destrutiva sem autor, versão anterior e horário do servidor impede detectar e reconstruir a adulteração. |

No OWASP Top 10:2025, a relação principal é com
[A01 - Broken Access Control](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/),
pois um usuário pode executar uma função fora de sua autorização; o desenho também se
relaciona a
[A06 - Insecure Design](https://owasp.org/Top10/2025/A06_2025-Insecure_Design/),
pela ausência das regras clínicas no fluxo confiável, e a
[A09 - Security Logging and Alerting Failures](https://owasp.org/Top10/2025/A09_2025-Security_Logging_and_Alerting_Failures/),
pela falta de evidência e alerta sobre alterações suspeitas.

A referência anterior a **CWE-345 - Insufficient Verification of Data Authenticity**
permanece útil como conceito geral de autenticidade, mas não como mapeamento principal:
ela é abstrata demais para distinguir as quatro falhas concretas acima e sua própria
ficha recomenda preferir uma fraqueza mais específica quando disponível.

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
