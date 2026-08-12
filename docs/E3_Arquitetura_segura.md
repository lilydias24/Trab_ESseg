# Etapa 3 - Projeto de uma Arquitetura Segura

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lorenzoficher
> São exigidos **3 requisitos de segurança**, e não um por integrante. O grupo levou adiante os riscos mais críticos e que cobrem categorias distintas de controle: autenticação, integridade de dados e autorização.

| Item | Responsável | Situação |
| --- | --- | --- |
| RS01 - requisito e vulnerabilidade | @lilydias24 | Concluído (aguarda revisão cruzada) |
| RS02 - requisito e vulnerabilidade | @ARTHUR9011 | Concluído (aguarda revisão cruzada) |
| RS03 - requisito e vulnerabilidade | @PPrauchner | Pendente |
| Diagrama da arquitetura segura | @lorenzoficher | Especificado (seções 3.1 a 3.3); falta exportar o PNG do Lucid |
| Decisão de arquitetura 1 (ligada ao diagrama) | @lorenzoficher | Concluída (DA01) |
| Decisão de arquitetura 2 (ligada a RS03) | @mariasanchez0’s | Pendente |
| Decisão de arquitetura 3 (reforço de autenticação) | @lilydias24 | Concluída (DA03; ponto de contato com a DA01 sinalizado) |

---

## 1. Requisitos de segurança

| ID | Risco de origem | Requisito de segurança | Critério de verificação | Responsável |
| --- | --- | --- | --- | --- |
| RS01 | R01 - Spoofing | O sistema deve exigir autenticação multifator no login e reautenticação antes de operações sensíveis envolvendo a conta de `Funcionario` | Operação sensível pedida sem segundo fator válido ou fora da janela de reautenticação é recusada, e o valor persistido em `senhaLogin` não é diretamente reutilizável (RS01-CA01 a RS01-CA09) | @lilydias24 |
| RS02 | R02 - Tampering | Toda alteração de prescrição ativa deve ser autorizada e validada no servidor, confirmada por segundo profissional e registrada com autoria e versionamento em trilha de auditoria imutável | Alteração sem autorização no servidor, fora da faixa terapêutica ou sem o segundo confirmador não publica versão vigente, e a tentativa fica registrada na auditoria (RS02-CA01 a RS02-CA08) | @ARTHUR9011 |
| RS03 | R06 - Elevation of Privilege | O sistema deve validar `nivelAcesso` no servidor em toda operação administrativa, e não apenas ocultar opções na interface | Requisição que altera `nivelAcesso` partindo de sessão sem alçada é recusada com HTTP 403 e registrada na trilha, mesmo quando enviada direto ao endpoint, sem passar pela interface (RS03-CA01 a RS03-CA08) | @PPrauchner |

> A coluna *Critério de verificação* foi acrescentada porque o §18.1 do enunciado a exige
> na tabela de requisitos - o requisito precisa ser "específico e verificável", e é essa
> coluna que demonstra o segundo adjetivo. Cada célula resume em uma linha os critérios
> detalhados na subseção do requisito correspondente; nenhum critério novo foi criado aqui.

> RS01 e RS02 estão detalhados abaixo. RS03 permanece com seu responsável.

### RS01 - Autenticação forte e reautenticação em operações sensíveis (@lilydias24)

**Risco de origem.** R01 - uso das credenciais legítimas de um profissional para assumir
sua identidade no SIGH. O requisito atua sobre as duas condições que dão ao risco
probabilidade 4: a senha guardada de forma diretamente reutilizável e o fato de saber a
senha ser suficiente para agir como o titular.

**Enunciado completo.** O SIGH deve:

1. persistir `senhaLogin` apenas como valor derivado por função própria para senhas
   (Argon2id, ou scrypt/bcrypt quando aquele não estiver disponível), com **salt
   aleatório e distinto por credencial**, nunca em texto simples nem por função de
   propósito geral como MD5 ou SHA-256 isolado;
2. verificar a credencial por comparação em tempo constante e, quando os parâmetros de
   custo forem reforçados, regravar o registro de forma transparente na primeira
   autenticação bem-sucedida, sem exigir troca de senha;
3. exigir **segundo fator no login**, vinculado à pessoa e não ao terminal, uma vez que
   os postos de atendimento são compartilhados;
4. exigir **reautenticação com segundo fator**, dentro de uma janela curta e explícita,
   imediatamente antes de prescrever medicamento, autorizar alta e registrar óbito - as
   três operações que a Etapa 1 identificou como de efeito clínico ou irreversível;
5. aplicar bloqueio temporário progressivo por conta **e** por origem após tentativas
   malsucedidas, sem que a mensagem de erro permita distinguir conta existente de
   inexistente;
6. encerrar a sessão por inatividade e vinculá-la ao dispositivo e à zona de rede em que
   foi aberta, exigindo nova autenticação quando esse vínculo mudar;
7. emitir evento de segurança para toda tentativa de autenticação, reautenticação,
   bloqueio, desbloqueio e alteração de credencial, com autoria e data/hora fornecidas
   pelo servidor; e
8. oferecer um caminho de exceção assistencial (*break-glass*) para quando o segundo
   fator estiver indisponível durante o atendimento, com acesso em escopo reduzido, por
   tempo limitado, mediante identificação de um segundo profissional e com registro
   destacado para revisão obrigatória.

**Comportamento esperado.** A falha é fechada: sem credencial válida, sem segundo fator
válido ou sem reautenticação dentro da janela, a operação sensível não é executada e
nenhum efeito parcial é persistido. A identidade nunca é aceita do corpo enviado pelo
Desktop Cliente - vem sempre da sessão autenticada no servidor. Nem a senha em claro, nem
o valor derivado, nem os códigos do segundo fator podem aparecer em log, em mensagem de
erro ou em resposta de API.

A cláusula 8 existe por uma razão específica deste sistema, e precisa ser lida junto com
as demais: **um hospital não pode tratar o bloqueio de acesso como resultado seguro por
padrão.** Impedir um médico de prescrever durante uma emergência transfere o dano para o
paciente - exatamente o bem que as outras cláusulas protegem. Por isso a exceção é
prevista, delimitada e auditada, em vez de acontecer informalmente pelo empréstimo de
credencial entre colegas, que é justamente o comportamento descrito em CA01.

**Limite reconhecido do requisito.** O segundo fator reduz a probabilidade do risco, mas
não substitui uma segunda pessoa: continua sendo algo que o próprio titular carrega e
pode ser obtido pela mesma manobra que obtém a senha (*phishing* em tempo real). É por
isso que o residual de R01 permanece Alto na [Etapa 2](E2_Riscos_e_NIST_CSF.md) mesmo com
RS01 implementado, e por isso a cláusula 4 se limita a reautenticar, sem exigir
coassinatura - exigir segunda identidade em operação irreversível é uma decisão que o
grupo pode tomar depois, e que teria de ser pesada contra o custo assistencial de travar
uma alta ou um registro de óbito.

**Critérios de verificação.** O requisito é considerado atendido quando os cenários
abaixo forem demonstrados por testes automatizados e pela consulta aos eventos de
segurança:

| ID | Cenário | Resultado verificável |
| --- | --- | --- |
| RS01-CA01 | Profissional cadastra a senha e autentica com ela, apresentando o segundo fator | Autenticação aceita; o valor persistido em `senhaLogin` não contém a senha e difere do de outra conta com a mesma senha |
| RS01-CA02 | Atacante de posse do conteúdo da tabela `Funcionario` reenvia o valor armazenado como se fosse a senha | Autenticação recusada; o vazamento não é diretamente reutilizável |
| RS01-CA03 | Senha correta apresentada sem o segundo fator | Autenticação recusada e nenhuma sessão é aberta |
| RS01-CA04 | Sessão válida tenta prescrever, autorizar alta ou registrar óbito fora da janela de reautenticação | Operação recusada; nenhum efeito parcial persistido |
| RS01-CA05 | Sequência de tentativas malsucedidas contra a mesma conta e contra várias contas da mesma origem | Bloqueio progressivo aplicado nos dois eixos; as mensagens não distinguem conta existente de inexistente |
| RS01-CA06 | Sessão permanece inativa além do limite, ou é reapresentada de outro dispositivo ou zona de rede | Sessão encerrada e nova autenticação exigida |
| RS01-CA07 | Parâmetros de custo são reforçados e o profissional autentica em seguida | Registro regravado com os novos parâmetros, de forma transparente, sem troca de senha |
| RS01-CA08 | Fluxo de exceção assistencial é acionado sem o segundo fator | Acesso concedido em escopo e prazo reduzidos, com segundo profissional identificado e registro destacado para revisão |
| RS01-CA09 | Log e resposta de erro são inspecionados após uma falha de autenticação | Nenhuma senha, valor derivado ou código de segundo fator aparece |

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
| RS01 | Senha persistida em texto simples, autenticação de fator único, ausência de limite de tentativas e sessão sem expiração | CWE-256, CWE-308, CWE-307, CWE-613 e CWE-287 | @lilydias24 |
| RS02 | Ausência de autorização no servidor, confiança em validações do cliente, entrada clínica sem validação e auditoria insuficiente | CWE-862, CWE-602, CWE-20 e CWE-778; OWASP A01, A06 e A09:2025 | @ARTHUR9011 |
| RS03 | Missing Authorization / Broken Access Control | CWE-862, OWASP A01 (a confirmar/complementar) | @PPrauchner |

> Os mapeamentos de RS01 e RS02 estão detalhados abaixo. RS03 permanece com seu responsável.

### Vulnerabilidades relacionadas a RS01 (@lilydias24)

Como o SIGH não está implementado, os itens abaixo são **fraquezas potenciais indicadas
pelo modelo**, e não vulnerabilidades confirmadas em código. A primeira delas, porém, é
menos hipotética que as demais: `senhaLogin` aparece como atributo de texto simples no
modelo de domínio, e o RNF05 exige criptografia para as informações médicas - a
contradição está documentada no próprio projeto.

| Referência | Relação concreta com o SIGH |
| --- | --- |
| [CWE-256 - Plaintext Storage of a Password](https://cwe.mitre.org/data/definitions/256.html) | `Funcionario.senhaLogin` é um atributo de texto sem indicação de derivação. É a fraqueza principal de RS01: torna um vazamento do SGBD central imediatamente utilizável contra todas as contas. |
| [CWE-916 - Use of Password Hash With Insufficient Computational Effort](https://cwe.mitre.org/data/definitions/916.html) | Aplicar um hash de propósito geral, sem salt e sem fator de trabalho, resolveria a aparência do problema sem resolver o problema. É a armadilha que a cláusula 1 fecha ao exigir função própria para senhas. |
| [CWE-308 - Use of Single-factor Authentication](https://cwe.mitre.org/data/definitions/308.html) | A autenticação se resume à comparação de `nomeLogin` e `senhaLogin`: quem sabe a senha é o titular, para todos os efeitos do sistema. |
| [CWE-307 - Improper Restriction of Excessive Authentication Attempts](https://cwe.mitre.org/data/definitions/307.html) | O modelo não prevê bloqueio nem atraso após tentativas malsucedidas, o que viabiliza força bruta a partir da própria rede interna. |
| [CWE-613 - Insufficient Session Expiration](https://cwe.mitre.org/data/definitions/613.html) | Sem expiração por inatividade, o terminal compartilhado deixado aberto entre plantões é uma sessão válida à disposição de quem passar. |
| [CWE-287 - Improper Authentication](https://cwe.mitre.org/data/definitions/287.html) | Permanece como categoria-mãe do requisito, útil para a rastreabilidade geral, mas abstrata demais para orientar controle: as cinco fraquezas acima é que dizem o que precisa mudar. |

No **OWASP Top 10**, a relação principal é com a categoria de **falhas de identificação e
autenticação** e, pelo armazenamento da senha, com a de **falhas criptográficas**. O
grupo está citando a edição 2025 (ver o mapeamento de RS02); a numeração exata dessas duas
categorias nessa edição deve ser conferida na lista vigente antes da entrega final, para
não citar identificador de edição diferente. As referências de controle usadas aqui, e
que não dependem dessa numeração, são o
[OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
e o
[OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html),
este último aplicado na prática da [Etapa 4](E4_Codigo_seguro_e_testes.md).

### Rastreabilidade de RS01

RS01 concretiza os controles R01-C1 a R01-C5 definidos no plano de tratamento da
[Etapa 2](E2_Riscos_e_NIST_CSF.md).

| Controle de R01 | Realização em RS01 | Critérios que o verificam | Evidência esperada |
| --- | --- | --- | --- |
| R01-C1 - hash e salt | Cláusulas 1 e 2 | RS01-CA01, RS01-CA02 e RS01-CA07 | Já demonstrada na [Etapa 4](E4_Codigo_seguro_e_testes.md): testes executados de caso válido e de posse do conteúdo da tabela |
| R01-C2 - MFA e reautenticação | Cláusulas 3, 4 e 8 | RS01-CA03, RS01-CA04 e RS01-CA08 | Testes sem segundo fator, fora da janela de reautenticação e pelo fluxo de exceção assistencial |
| R01-C3 - bloqueio por tentativas | Cláusula 5 | RS01-CA05 | Teste de bloqueio por conta e por origem, com mensagens indistinguíveis |
| R01-C4 - expiração de sessão | Cláusula 6 | RS01-CA06 | Teste de inatividade e de reapresentação da sessão em outro dispositivo ou zona |
| R01-C5 - política de senha | Cláusulas 1 e 2, mais a política institucional prevista na função Govern do mapeamento NIST | RS01-CA01 e RS01-CA07 | Política publicada e verificação contra listas públicas de senhas vazadas |

**Contratos necessários para a arquitetura segura.** O diagrama da seção 3 deve permitir
identificar, ainda que em nível lógico:

- um **serviço de autenticação** como emissor único da identidade de sessão, separado
  dos serviços de negócio (ver DA03);
- o armazenamento das credenciais derivadas, isolado do restante do cadastro de
  `Funcionario`, de modo que ler o cadastro não implique ler as credenciais;
- o verificador do segundo fator e o registro da janela de reautenticação, consultáveis
  pelos serviços que executam operações sensíveis;
- o contador de tentativas e o estado de bloqueio, compartilhados entre instâncias para
  que o limite não seja contornado alternando de servidor; e
- o canal de eventos de segurança que alimenta a Regra 1 da
  [Etapa 6](E6_Monitoramento_e_deteccao.md).

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

- **Alternativas consideradas.**
  - *Tabela de auditoria no próprio SGBD central, escrita por cada serviço.* Rejeitada por
    dois motivos independentes. Quem tem permissão de escrita no banco para gravar o
    registro tem, pela mesma credencial, permissão para alterá-lo - a trilha ficaria sob o
    controle de quem ela audita, que é precisamente a condição que R06 explora. E o banco
    único já é o ponto de concentração que sustenta R05: um comprometimento ou uma queda
    alcançaria o dado e a sua prova no mesmo movimento.
  - *Auditoria implementada dentro de cada microsserviço.* Rejeitada por repetir sete vezes
    a mesma implementação, com sete oportunidades de divergência de formato - inviabilizando
    a correlação por `correlationId` de que a Regra 2 da Etapa 6 depende - e por manter a
    trilha dentro da fronteira do componente auditado.
  - *Encaminhar tudo a um SIEM externo como solução única.* Rejeitada como substituto,
    aceita como complemento. Um SIEM é ferramenta de detecção e correlação e costuma
    aplicar amostragem e retenção curta; a trilha exigida por R03 precisa de custódia
    íntegra e de longo prazo, porque serve de prova em apuração de conselho profissional ou
    em juízo. O SIEM consome o que o Serviço de Auditoria retém, não o contrário.

- **Consequências.**
  - *Positivas.* Uma única implementação satisfaz as evidências dos quatro riscos e habilita
    as três regras da Etapa 6. A separação de armazenamento faz com que comprometer o dado
    e apagar o seu rastro passem a exigir **dois** comprometimentos. E a autoria deixa de
    depender do que o cliente envia, o que é o núcleo de RS02 e de R03-C1.
  - *Negativas, e a principal precisa ser dita.* Tornar o acréscimo condição da operação
    cria um **acoplamento de disponibilidade**: se o Serviço de Auditoria cair, as operações
    irreversíveis param. Isso é, em si, um caminho de negação de serviço, e portanto uma
    interação direta com o R05 do @PPrauchner - a decisão que melhora a rastreabilidade
    piora a disponibilidade. A mitigação adotada é um **buffer local durável** em cada
    serviço de negócio: o evento é gravado localmente de forma persistente antes da resposta
    ao usuário e entregue ao Serviço de Auditoria com garantia de entrega, de modo que uma
    indisponibilidade curta não interrompe o atendimento e nenhum evento se perde. A regra
    permanece: nenhuma operação irreversível se conclui sem que o evento esteja **durável em
    algum lugar**.
  - *Custo.* Um componente novo para operar, monitorar e dimensionar, e uma decisão de
    retenção e de acesso que a função Govern do mapeamento de R03 exige tomar - uma trilha
    que qualquer perfil possa consultar recria, na privacidade, o problema que resolve na
    responsabilização.

### DA02 - *(a definir, ligada a RS03)* - @mariasanchez0’s

- **Contexto:**
- **Decisão:**
- **Alternativas consideradas:**
- **Consequências:**

### DA03 - Serviço de autenticação dedicado como emissor único da identidade de sessão - @lilydias24

- **Contexto.** O diagrama de componentes do SIGH mostra 7 microsserviços, cada um com
  seu firewall antes do DAO, todos atrás de um API Gateway. **Nenhum deles é um serviço
  de autenticação**: as credenciais são atributos de `Funcionario`, dentro do Serviço de
  Funcionários, que é também o serviço de cadastro administrativo. Isso produz três
  efeitos que a análise já registrou: quem alcança o cadastro alcança as credenciais
  (T06/CA05), não existe um lugar único onde impor MFA, bloqueio e expiração de sessão
  (R01), e cada serviço fica livre para decidir sozinho o que aceita como identidade -
  inclusive aceitá-la do corpo da requisição, que é a raiz de T02 e T06.
- **Decisão.** Introduzir um **serviço de autenticação dedicado**, atrás do API Gateway e
  separado do Serviço de Funcionários, como **único emissor** da identidade de sessão. As
  credenciais derivadas, o verificador do segundo fator, o contador de tentativas e o
  estado de bloqueio passam a residir nele. O Gateway valida a sessão a cada requisição e
  propaga aos serviços de negócio uma identidade verificada (quem é, qual papel, quando
  reautenticou). **Os serviços de negócio nunca aceitam identidade vinda do cliente** -
  apenas a que chega por esse canal verificado.
- **Alternativas consideradas.**
  - *Manter a autenticação dentro do Serviço de Funcionários.* Rejeitada: mantém as
    credenciais no mesmo perímetro do cadastro administrativo, que é exatamente o
    caminho que CA05 percorre para ler `senhaLogin` de todos os perfis.
  - *Cada serviço valida credenciais por conta própria.* Rejeitada: multiplica a
    implementação de MFA e bloqueio por sete, e faz o limite de tentativas ser
    contornável alternando o serviço atacado.
  - *Validar a sessão apenas no API Gateway, sem repassar identidade verificada.*
    Rejeitada por não sobreviver a defesa em profundidade: qualquer chamada que alcance
    um serviço por outro caminho ficaria sem verificação, e a decisão de autorização
    dentro do serviço voltaria a depender do que o cliente afirma ser.
  - *Delegar a um provedor de identidade institucional (SSO externo).* Não rejeitada,
    apenas adiada. Resolve bem MFA e política de senha, mas acrescenta dependência
    externa a um sistema com requisito de operação 24h/7d (RNF03) e não transfere a
    responsabilidade do hospital sobre os dados. Fica registrada como evolução possível
    depois que o serviço próprio existir e a fronteira estiver clara.
- **Consequências.**
  - *Positivas.* Cria o lugar único onde RS01 pode ser implementado de fato, e onde as
    cláusulas 3 a 7 passam a ter dono. Separa ler o cadastro de ler as credenciais,
    cortando o encadeamento T06 → T01 descrito em CA05. Fornece a identidade verificada
    de que **RS02 e RS03 também dependem** - os dois exigem que o servidor saiba quem
    está chamando, e nenhum dos dois pode garantir isso sozinho.
  - *Negativas, e esta precisa ficar explícita.* O serviço de autenticação passa a ser
    **passagem obrigatória de toda operação**, somando-se ao API Gateway e ao SGBD único
    como mais um ponto de concentração - a mesma característica que sustenta T05/R05. Se
    ele cair, ninguém entra no sistema, com pacientes internados no prédio. A decisão só
    é aceitável acompanhada de redundância desse serviço e de uma política explícita para
    o que acontece durante sua indisponibilidade, que é o papel da cláusula 8 de RS01
    (*break-glass*). **Este ponto precisa ser conciliado com a DA01**, de responsabilidade
    do @lorenzoficher, que trata do isolamento e do desenho geral da arquitetura segura.
  - *Custo.* Exige migrar as credenciais existentes para fora do Serviço de Funcionários
    e reescrever o fluxo de login do Desktop Cliente - trabalho concentrado, mas feito
    uma vez só, contra sete implementações na alternativa descartada.

