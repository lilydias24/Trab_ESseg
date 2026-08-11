# Etapa 3 - Projeto de uma Arquitetura Segura

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lorenzoficher
> São exigidos **3 requisitos de segurança**, e não um por integrante. O grupo levou adiante os riscos mais críticos e que cobrem categorias distintas de controle: autenticação, integridade de dados e autorização.

| Item | Responsável | Situação |
| --- | --- | --- |
| RS01 - requisito e vulnerabilidade | @lilydias24 | Pendente |
| RS02 - requisito e vulnerabilidade | @ARTHUR9011 | Concluído (aguarda revisão cruzada) |
| RS03 - requisito e vulnerabilidade | @PPrauchner | Pendente |
| Diagrama da arquitetura segura | @lorenzoficher | Especificado (seções 3.1 a 3.3); falta exportar o PNG do Lucid |
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

> RS02 está detalhado abaixo. RS01 e RS03 permanecem com seus respectivos responsáveis.

### RS02 - Integridade e rastreabilidade da prescrição ativa (@ARTHUR9011)

**Risco de origem.** R02 - alteração indevida de `dosagemMedicamento` ou
`intervaloConsumo` de uma `PrescricaoMedicamento` ativa, executada pela enfermagem como
se fosse a versão legítima. O requisito atua antes de a mudança chegar à administração
do medicamento, porque o dano clínico não pode ser desfeito pelo sistema depois desse
momento.

**Enunciado completo.** Toda solicitação de alteração de uma prescrição ativa deve ser
processada no servidor e somente pode produzir uma nova versão vigente quando, no mesmo
fluxo controlado e antes da publicação, o SIGH:

1. obtiver o autor da sessão autenticada, sem aceitar identidade informada pelo cliente;
2. confirmar que o autor é médico e está vinculado ao atendimento do paciente;
3. validar `dosagemMedicamento` e `intervaloConsumo` contra a faixa terapêutica cadastrada
   para o medicamento;
4. exigir reautenticação do autor e confirmação de um segundo profissional autorizado,
   diferente do autor da mudança;
5. confirmar que a versão-base ainda é a vigente, preservar a versão anterior e
   acrescentar atomicamente a nova versão e seu registro à trilha de auditoria; e
6. tornar a nova versão disponível para administração somente depois que todas as
   verificações e o registro de auditoria forem concluídos com sucesso.

**Comportamento esperado.** A trilha deve ser somente de acréscimo e registrar, no
mínimo, o identificador da prescrição, do paciente, da versão-base e da nova versão,
medicamento, dose e intervalo anteriores e novos, justificativa, autor, segundo
confirmador, data/hora fornecida pelo servidor e identificador de correlação da operação.
Nenhum desses dados de autoria pode vir do corpo enviado pelo Desktop Cliente. Se
autorização, vínculo, faixa terapêutica, reautenticação, confirmação independente,
controle de concorrência ou gravação da auditoria falhar, a operação deve falhar de forma
fechada: a versão vigente permanece inalterada, nenhuma atualização parcial é persistida
e a tentativa recusada é registrada para detecção. A confirmação humana pode ocorrer
antes da transação de publicação; nesse caso, ela fica vinculada à versão proposta, e as
regras e a versão-base são verificadas novamente imediatamente antes da publicação
atômica, sem manter uma transação de banco aberta durante a espera.

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
| RS02-CA08 | Duas alterações concorrentes tentam partir da mesma versão-base | No máximo uma delas torna-se vigente; a outra recebe conflito, não sobrescreve dados e precisa passar novamente pelas validações e pela confirmação sobre a nova base |

## 2. Vulnerabilidades catalogadas (CWE/OWASP)

| Requisito | Vulnerabilidade relacionada | Referência | Responsável |
| --- | --- | --- | --- |
| RS01 | Improper Authentication | CWE-287 (a confirmar/complementar) | @lilydias24 |
| RS02 | Ausência de autorização no servidor, confiança em validações do cliente, entrada clínica sem validação e auditoria insuficiente | CWE-862, CWE-602, CWE-20 e CWE-778; OWASP A01, A06 e A09:2025 | @ARTHUR9011 |
| RS03 | Missing Authorization / Broken Access Control | CWE-862, OWASP A01 (a confirmar/complementar) | @PPrauchner |

> O mapeamento de RS02 está detalhado abaixo. RS01 e RS03 permanecem com seus respectivos responsáveis.

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

### Rastreabilidade de RS02

RS02 concretiza os controles R02-C1 a R02-C5 definidos no plano de tratamento da
[Etapa 2](E2_Riscos_e_NIST_CSF.md). A tabela evita que um controle seja considerado
implementado apenas porque aparece no texto do requisito.

| Controle de R02 | Realização em RS02 | Critérios que o verificam | Evidência esperada quando houver implementação |
| --- | --- | --- | --- |
| R02-C1 - autor obtido da sessão | Cláusulas 1 e 5; autoria nunca é aceita do cliente | RS02-CA01, RS02-CA02 e RS02-CA06 | Teste que adultera o autor no corpo e comprova que a auditoria registra o usuário da sessão |
| R02-C2 - papel e vínculo validados no servidor | Cláusula 2 e falha fechada | RS02-CA02 e RS02-CA03 | Testes de autorização com perfil não médico e médico não vinculado, ambos sem mudança persistida |
| R02-C3 - faixa terapêutica | Cláusula 3 | RS02-CA04 | Testes de limite inferior, limite superior e valores imediatamente fora dos limites para dose e intervalo |
| R02-C4 - versionamento imutável | Cláusulas 5 e 6; comportamento esperado da auditoria | RS02-CA01, RS02-CA06, RS02-CA07 e RS02-CA08 | Consulta exibindo valor anterior e novo; tentativa de alteração/exclusão recusada; falha de auditoria causando rollback; teste concorrente sem atualização perdida |
| R02-C5 - reautenticação e segunda confirmação | Cláusula 4 | RS02-CA01 e RS02-CA05 | Testes sem reautenticação, sem confirmador e com autor igual ao confirmador, além do fluxo válido com duas identidades |

**Contratos necessários para a arquitetura segura.** O diagrama da seção 3 deve permitir
identificar, ainda que em nível lógico:

- a sessão autenticada como fonte de identidade, papel e instante da reautenticação;
- a política de autorização que verifica papel médico e vínculo com o paciente;
- o catálogo clínico versionado que fornece as faixas terapêuticas;
- o fluxo de confirmação independente vinculado à versão proposta;
- o armazenamento transacional das versões da prescrição, com controle de concorrência
  pela versão-base; e
- a trilha de auditoria somente de acréscimo, separada da permissão de alterar a
  prescrição.

Esses são contratos, e não uma prescrição de quantidade de microsserviços. Eles podem ser
implementados em componentes separados ou no mesmo serviço, desde que as fronteiras de
autorização, transação e auditoria permaneçam explícitas e verificáveis.

**Dependências para as próximas etapas.** Os testes listados nesta seção são critérios
de arquitetura enquanto o SIGH não possui implementação; portanto, não devem ser
apresentados como evidência executada. Quando existir código, o resultado automatizado e
a consulta à auditoria comprovarão os controles. A Regra 2 da Etapa 6 deve consumir tanto
alterações concluídas quanto tentativas recusadas, usando o identificador de correlação,
para detectar valor fora da faixa, autorização inválida ou ausência de confirmação sem
depender de uma alteração insegura ter sido persistida.

## 3. Diagrama da arquitetura segura

> Responsável: **@lorenzoficher** - parte de `diagrams/estrutura/Diagramas_SIGH - Componentes.png` (já versionado) e acrescenta serviço de autenticação, serviço de autorização e componente de logs/auditoria. Exportar como `diagrams/estrutura/SIGH - Arquitetura segura.png`.

<!-- Descomentar quando o diagrama estiver exportado:
![Arquitetura segura do SIGH](../diagrams/estrutura/SIGH%20-%20Arquitetura%20segura.png)
-->

O diagrama parte da arquitetura já modelada - Desktop Cliente, API Gateway e 7
microsserviços em 5 camadas sobre um SGBD central - e acrescenta os três componentes que
os requisitos desta etapa exigem, sem redesenhar o que já existe. A leitura abaixo é a
legenda do diagrama e serve para conferir se ele mostra o que precisa mostrar.

### 3.1 Componentes acrescentados

| Componente | O que faz | Requisito que o exige |
| --- | --- | --- |
| **Serviço de Autenticação** | Verifica credenciais, aplica o segundo fator, emite a sessão e responde pela reautenticação em operações sensíveis. Passa a ser a **única** origem de identidade do sistema | RS01; controles R01-C1 a R01-C4 |
| **Serviço de Autorização** | Decide, no servidor, se a sessão pode executar a operação, combinando papel, `nivelAcesso` e vínculo com o paciente. Consultado por todos os serviços de negócio antes de qualquer operação sensível | RS02 e RS03; controles R02-C2, R06-C1 e R03-C1 |
| **Serviço de Auditoria** | Recebe e retém, somente por acréscimo, os eventos de segurança e as versões de dado clínico. Único componente com permissão de escrita no armazenamento de auditoria | RS02; controles R02-C4, R03-C3 e R06-C3 - e é o objeto da decisão DA01 |
| **Catálogo Clínico versionado** | Fornece as faixas terapêuticas por medicamento que a RS02 exige validar | RS02; controle R02-C3 |

### 3.2 Fronteiras de confiança que o diagrama precisa deixar visíveis

1. **Cliente → API Gateway.** Tudo o que vem do Desktop Cliente é entrada não confiável,
   inclusive identidade, papel, autor e data/hora. O diagrama deve deixar claro que esses
   campos são **descartados** no Gateway e reconstruídos a partir da sessão.
2. **Serviços de negócio → Serviço de Autorização.** A decisão de autorização fica fora
   do serviço que executa a operação. É o que impede que "ocultar o botão na interface"
   volte a ser o controle, como em CWE-602.
3. **Serviços de negócio → Serviço de Auditoria.** Seta de **mão única**, rotulada
   `append`. Nenhum serviço de negócio alcança o armazenamento de auditoria diretamente.
4. **Armazenamento de auditoria ≠ SGBD central.** Precisa aparecer como armazenamento
   próprio, e não como mais uma tabela do banco único - é o ponto da DA01.
5. **SIGH → «system» Sistema Governamental.** A transmissão do óbito atravessa a fronteira
   da instituição e deve aparecer com o registro probatório do R03-C4 ao lado.

### 3.3 Fluxo de referência - registro de óbito (UC10)

O caminho abaixo é o que o diagrama deve permitir percorrer com o dedo, e é o mesmo do
DS10 já versionado, agora com os controles no lugar:

```
Desktop Cliente
  │  registrarObito(causaCID, dataHoraObito)          ← sem autor, sem carimbo
  ▼
API Gateway ──────────────► Serviço de Autenticação   ← valida sessão + reautenticação
  │                                                      (descarta autor vindo do cliente)
  ▼
Serviço de Internação Médica
  │  ├──────────────────► Serviço de Autorização      ← papel médico + vínculo? (R03-C1)
  │  ├──────────────────► Serviço de Auditoria        ← append: autor, sessão, terminal,
  │  │                                                   dataHoraRegistro do servidor
  │  │                                                   (R03-C2, R03-C3)
  │  ▼
  │  SGBD central: grava Obito e encerra o prontuário ← só após o append ter sucesso
  ▼
«system» Sistema Governamental                        ← envio + registro probatório (R03-C4)
```

O ponto que o diagrama precisa comunicar em uma olhada: **a gravação do `Obito` acontece
depois do registro de auditoria, e não antes**. Se o append falhar, nada é persistido - é
o que impede que exista um óbito sem rastro, e é a diferença entre auditar e ter auditoria.

## 4. Decisões de arquitetura

### DA01 - Trilha de auditoria como serviço próprio, somente de acréscimo e com armazenamento separado do SGBD central - @lorenzoficher

- **Contexto.** A arquitetura atual não tem onde registrar quem fez o quê: os 7
  microsserviços gravam no mesmo SGBD central e o Tópico 9 do documento original coloca o
  registro de eventos críticos fora do escopo. Isso não é uma lacuna de uma trilha só. As
  evidências que **quatro** riscos da Etapa 2 exigem em 14.4 dependem da mesma capacidade
  inexistente: R01 pede log de tentativas e de bloqueios, R02 pede log consultável com
  autor e valor anterior, R03 pede autoria e carimbo de tempo do servidor, R06 pede trilha
  imutável de alteração de perfil. As três regras da Etapa 6 consomem exatamente esses
  eventos. Decidir onde a trilha vive é, portanto, uma decisão de arquitetura do grupo
  inteiro, e não um detalhe da trilha Repudiation.

- **Decisão.** Criar um **Serviço de Auditoria** com armazenamento próprio, distinto do
  SGBD central, exposto aos demais serviços por uma interface de **acréscimo apenas**. As
  contas usadas pelos serviços de negócio têm permissão de `append` e não têm `update` nem
  `delete`; nenhum perfil da aplicação - incluindo Diretor - alcança a alteração ou a
  exclusão de uma entrada. Os campos de autoria e de tempo são preenchidos pelo próprio
  serviço a partir da sessão autenticada e do relógio do servidor, nunca copiados do corpo
  da requisição. Para as operações irreversíveis do recorte - registrar óbito (UC10) e
  autorizar alta (UC06) -, o acréscimo é **condição da operação**: se ele falhar, a
  transação de negócio é revertida.

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
