# Etapa 6 - Monitoramento e Detecção de Intrusões

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lilydias24
> É exigido um **roteiro com 3 regras de detecção**, reaproveitando os riscos já registrados na [Etapa 2](E2_Riscos_e_NIST_CSF.md).

- A compilação final do roteiro fica em `roteiros/etapa-6-deteccao-de-intrusoes.md`.

| Regra | Risco observado | Responsável | Situação |
| --- | --- | --- | --- |
| 1 | R01 - Spoofing | @lilydias24 | Concluída (especificação; aguarda implementação do SIGH) |
| 2 | R02 - Tampering | @ARTHUR9011 | Concluída (especificação; aguarda implementação do SIGH) |
| 3 | R06 - Elevation of Privilege | @PPrauchner | Concluída (especificação; aguarda implementação do SIGH) |
| Compilação | Roteiro final | @lilydias24 | Pendente |

---

## Quadro de regras

| Regra | Risco observado | Fonte de dados | Condição de alerta | Ação esperada | Responsável |
| --- | --- | --- | --- | --- | --- |
| 1 | R01 - Spoofing | Eventos de segurança do serviço de autenticação (RS01, cláusula 7), correlacionados com os de operação sensível | Crítico: sucesso após rajada de falhas, sessões simultâneas em zonas distintas, ou operação sensível de dispositivo desconhecido. Alto: 5 falhas em 15 min na mesma conta, ou mesma origem falhando contra 10 contas | Confirmar a sessão com o titular fora do sistema antes de revogar; havendo comprometimento, revisar o que foi executado durante a sessão | @lilydias24 |
| 2 | R02 - Tampering | Eventos de segurança e trilha de auditoria das prescrições | Publicação que viola uma invariante de RS02 ou 3 recusas suspeitas pelo mesmo autor/prescrição em 10 minutos | Acionar resposta clínica e de segurança conforme a severidade, preservando as evidências | @ARTHUR9011 |
| 3 | R06 - Elevation of Privilege | Decisões do Serviço de Autorização (DA02) e trilha imutável de alteração de perfil (DA01), conforme as cláusulas 5 e 7 de RS03 | Crítico: elevação efetivada com solicitante igual ao titular, aprovador igual ao solicitante, decisão fora do servidor ou campo gravado pela via do cadastro; e leitura administrativa em massa até 60 min após uma elevação. Alto: 3 recusas de privilégio do mesmo autor ou sobre o mesmo titular em 10 min, requisição enviada direto ao endpoint, ou 3 usos de alçada nova em sessão anterior à promoção | Notificar Diretor e Segurança da Informação no momento da elevação; havendo anomalia, reverter o `nivelAcesso` pelo fluxo de aprovação, reemitir a identidade de sessão e apurar o que a alçada leu, acionando o dono de R01 se o cadastro tiver sido percorrido | @PPrauchner |

## Regra 1 - Uso indevido de credencial de profissional (@lilydias24)

- **Risco observado:** R01 - uso das credenciais legítimas de um profissional para
  assumir sua identidade no SIGH.
- **Fonte de dados:** eventos de segurança emitidos pelo serviço de autenticação (DA03),
  conforme a cláusula 7 de [RS01](E3_Arquitetura_segura.md), correlacionados com os
  eventos de operação sensível dos serviços de negócio.
- **Condição de alerta (limiar e janela):** alerta **Crítico** diante de um único sinal de
  comprometimento consumado - autenticação bem-sucedida logo após uma rajada de falhas, ou
  sessões simultâneas da mesma conta em zonas de rede distintas. Alerta **Alto** a partir
  de 5 falhas em 15 minutos contra a mesma conta, ou de falhas da mesma origem contra 10
  contas distintas na mesma janela.
- **O que o alerta indica:** no caso Alto, tentativa de adivinhação ou de reuso de senhas
  vazadas; no caso Crítico, que a tentativa provavelmente teve êxito e a conta pode estar
  sendo operada por outra pessoa.

### Contrato mínimo dos eventos

O serviço de autenticação, e não o Desktop Cliente, preenche os campos usados pela regra.
**Nenhum evento pode conter a senha, o valor derivado dela ou o código do segundo fator** -
a cláusula 9 dos critérios de RS01 existe exatamente para isso, e uma regra de detecção que
vazasse credencial reproduziria o risco que pretende observar.

| Campo | Uso na detecção |
| --- | --- |
| `eventTime`, `eventType`, `correlationId` | Ordenação, janela e deduplicação da tentativa |
| `subjectId`, `subjectRole` | Conta alvo e perfil; identificador interno, nunca o `nomeLogin` digitado |
| `outcome`, `failureReason` | `SUCCESS`, `BAD_CREDENTIAL`, `MFA_FAILED`, `ACCOUNT_LOCKED`, `BREAK_GLASS_USED` |
| `mfaPresented`, `mfaValid`, `reauthAt` | Distinguem falha de senha de falha de segundo fator e alimentam a checagem de operação sensível |
| `deviceId`, `networkZone`, `sourceService` | Contexto técnico; a zona é a ala/setor, não o endereço do paciente |
| `knownDeviceForSubject` | Indicador derivado: se aquele profissional já autenticou naquele terminal antes |

### Lógica de correlação

**Gatilho A - Crítico e imediato.** Um único evento `SUCCESS` dispara alerta quando:

- for precedido, para a mesma conta, por 5 ou mais falhas nos 15 minutos anteriores
  (adivinhação bem-sucedida); **ou**
- existir outra sessão ativa da mesma conta em `networkZone` diferente, com sobreposição
  temporal que nenhum deslocamento dentro do hospital explicaria; **ou**
- for seguido, em menos de 2 minutos, por prescrição, autorização de alta ou registro de
  óbito **a partir de um `deviceId` nunca visto para aquele profissional**
  (`knownDeviceForSubject` falso).

**Gatilho B - Alto por repetição.** Contam para o limiar os eventos `BAD_CREDENTIAL` e
`MFA_FAILED`. A quinta ocorrência em 15 minutos para o mesmo `subjectId` abre um único
alerta, ao qual as seguintes da janela são anexadas. Em paralelo, falhas da mesma origem
(`deviceId` + `networkZone`) contra **10 contas distintas** na mesma janela abrem um alerta
de pulverização de senhas, que é o padrão que precede o Gatilho A.

`ACCOUNT_LOCKED` não conta para o limiar - é a consequência do bloqueio de RS01, não uma
tentativa nova, e contá-lo duplicaria o mesmo evento. `BREAK_GLASS_USED` **nunca** gera
alerta de intrusão, mas entra obrigatoriamente na fila de revisão prevista na cláusula 8
de RS01: é acesso legítimo por definição e precisa ser conferido depois, não interrompido
durante um atendimento.

### Ação esperada da equipe

**Alerta Crítico:**

1. abrir incidente único pelo `correlationId` e notificar Segurança da Informação e a
   chefia da unidade do profissional;
2. contatar o profissional titular por canal fora do sistema para confirmar se a sessão é
   dele - **antes** de revogar, porque revogar a sessão de um médico em atendimento é uma
   ação com custo assistencial;
3. preservar eventos, identidade das sessões e contexto técnico em repositório restrito;
4. se o titular não reconhecer a sessão, revogá-la, forçar troca de credencial e **revisar
   o que foi executado durante ela** - prescrições, altas e registros -, acionando os donos
   de R02 e R03 conforme o que tiver sido tocado; e
5. registrar o resultado, inclusive quando for falso positivo, para recalibrar o limiar.

**Alerta Alto:** Segurança correlaciona as tentativas com dispositivo, zona e escala de
trabalho do profissional. Se houver indício de ataque, aplica bloqueio da origem e
comunica o titular; se for erro operacional - senha esquecida após troca, teclado com
layout trocado, terminal com sessão anterior aberta -, registra, orienta e mantém o
histórico para ajuste do limiar.

O alerta nunca deve, sozinho, encerrar a sessão de um profissional em atendimento. A
contenção técnica e a continuidade assistencial precisam ficar separadas e auditadas -
mesmo princípio que a Regra 2 aplica à decisão clínica.

### Falsos positivos previstos

Três deles são específicos deste sistema e mereceram ajuste no desenho da regra:

- **Terminal compartilhado.** Nos postos de atendimento, muitos profissionais autenticam
  do mesmo `deviceId` ao longo do dia. Isso é operação normal, **não** pulverização de
  senhas - por isso o Gatilho B só considera a origem quando as tentativas são de
  **falha**, e não de sucesso.
- **Troca de turno.** A passagem de plantão concentra logins em poucos minutos, com
  senhas digitadas às pressas. É a janela de maior taxa de erro legítimo do dia, e o
  limiar de 5 falhas foi escolhido acima do erro típico por esse motivo.
- **Deslocamento entre alas.** Um profissional que atende em duas unidades pode aparecer
  em zonas diferentes em intervalo curto. Por isso o Gatilho A exige **sobreposição** de
  sessões ativas, e não apenas mudança de zona.

Somam-se os casos gerais: senha recém-trocada digitada por hábito, sincronização de
relógio do gerador de segundo fator e reenvio do cliente por instabilidade de rede -
eventos repetidos com o mesmo `correlationId` são duplicatas técnicas e devem ser
eliminados antes da contagem.

### Verificação da regra

Como o SIGH não possui implementação, estes são casos de teste planejados, e não
evidências já executadas:

| ID | Entrada simulada | Resultado esperado |
| --- | --- | --- |
| R1-TV01 | Login válido com segundo fator, em terminal já conhecido do profissional | Nenhum alerta; evento permanece pesquisável |
| R1-TV02 | 5 falhas de senha na mesma conta em 15 minutos | Exatamente um alerta Alto contendo as cinco correlações |
| R1-TV03 | 5 falhas seguidas de um sucesso na mesma conta | Alerta Crítico pelo Gatilho A, além do Alto já aberto |
| R1-TV04 | Falhas da mesma origem contra 10 contas distintas em 15 minutos | Um alerta Alto de pulverização de senhas |
| R1-TV05 | 12 logins bem-sucedidos de profissionais diferentes no mesmo terminal em 10 minutos | **Nenhum alerta** - é a troca de turno em posto compartilhado |
| R1-TV06 | Sessões ativas simultâneas da mesma conta em duas zonas de rede | Alerta Crítico por sessão concorrente |
| R1-TV07 | Login bem-sucedido seguido, em 1 minuto, de registro de óbito a partir de dispositivo desconhecido | Alerta Crítico pelo terceiro caso do Gatilho A |
| R1-TV08 | Uso do fluxo `BREAK_GLASS_USED` durante emergência | Nenhum alerta de intrusão; entrada obrigatória na fila de revisão |
| R1-TV09 | Evento contendo senha, valor derivado ou código de segundo fator | Evento em quarentena e falha de esquema; credencial não chega ao índice de segurança |
| R1-TV10 | Ausência de dois *heartbeats* consecutivos, emitidos a cada minuto | Alerta operacional após 2 minutos; Regra 1 marcada como sem cobertura |

### Dependências operacionais e referências

A regra depende de o serviço de autenticação da DA03 existir e emitir os eventos da
cláusula 7 de RS01 - sem emissor único, os eventos ficariam espalhados pelos sete
microsserviços e a correlação por conta deixaria de ser confiável. Os produtores devem
usar relógio sincronizado e canal autenticado para armazenamento central protegido contra
alteração. Um *heartbeat* por minuto distingue ausência de tentativas de falha de coleta.

A especificação segue o
[OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html),
quanto a eventos correlacionáveis, proteção dos logs e tratamento de dado sensível, e o
[OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html),
quanto a mensagens de erro que não diferenciam conta existente de inexistente - o que vale
também para o que a regra publica. O procedimento de triagem e resposta é alinhado ao
[NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final), na mesma linha adotada
pela Regra 2.

## Regra 2 - Tentativa de adulteração de prescrição ativa (@ARTHUR9011)

- **Risco observado:** R02 - alteração indevida de `dosagemMedicamento` ou
  `intervaloConsumo` de uma prescrição ativa.
- **Fonte de dados:** eventos de segurança produzidos pelo fluxo de alteração e trilha
  de auditoria imutável de `PrescricaoMedicamento`, centralizados para correlação.
- **Condição de alerta (limiar e janela):** alerta **Crítico** diante de uma única
  publicação que viole uma invariante de RS02; alerta **Alto** a partir de 3 tentativas
  recusadas suspeitas, agrupadas pelo mesmo autor **ou** pela mesma prescrição em uma
  janela deslizante de 10 minutos.
- **O que o alerta indica:** possível tentativa repetida de contornar autorização,
  faixa terapêutica, reautenticação ou confirmação independente; no caso Crítico, indica
  que um controle preventivo pode ter sido contornado e uma versão insegura pode ter
  ficado disponível para administração.

### Contrato mínimo dos eventos

O serviço confiável, e não o Desktop Cliente, deve preencher os campos usados pela regra.
Cada solicitação gera um evento terminal `PRESCRIPTION_CHANGE_PUBLISHED` ou
`PRESCRIPTION_CHANGE_DENIED`. A central de logs valida o esquema antes de aceitar o
evento e conta uma única vez cada par `correlationId` + `eventType`.

| Campo | Uso na detecção |
| --- | --- |
| `eventTime`, `eventType`, `correlationId` | Ordenação, janela e deduplicação da tentativa |
| `prescriptionId`, `patientId`, `baseVersion`, `newVersion` | Correlação da prescrição e detecção de sobrescrita/versionamento inconsistente |
| `medicationId`, `therapeuticCatalogVersion`, `withinTherapeuticRange` | Comprovação de que dose e intervalo foram validados contra uma referência conhecida |
| `authorId`, `authorRole`, `authorLinkedToPatient`, `reauthenticationValid` | Autoria obtida da sessão e verificações de autorização de R02-C1/R02-C2 |
| `confirmerId`, `confirmerAuthorized`, `confirmedProposalVersion` | Independência e vínculo da confirmação com a versão proposta |
| `outcome`, `denyReason`, `sourceService`, `deviceId`, `networkZone` | Resultado, motivo e contexto técnico para triagem |

O evento enviado à plataforma de monitoramento usa identificadores internos e indicadores
derivados. Nome do paciente, texto livre da justificativa, credenciais, tokens e outros
dados clínicos desnecessários não devem ser copiados. Os valores clínicos completos
permanecem na trilha restrita e só são consultados por pessoal autorizado durante a
investigação.

### Lógica de correlação

**Gatilho A - Crítico e imediato.** Um único evento
`PRESCRIPTION_CHANGE_PUBLISHED` dispara o alerta quando qualquer condição abaixo for
verdadeira:

- `withinTherapeuticRange` é falso;
- o autor não é médico vinculado ao paciente ou a reautenticação é inválida;
- o segundo confirmador está ausente, não é autorizado, é igual ao autor ou confirmou
  outra versão proposta; ou
- `baseVersion` não era a versão vigente no instante da publicação, a nova versão não
  possui auditoria correspondente ou há evidência de alteração/exclusão da trilha.

**Gatilho B - Alto por repetição.** Eventos `PRESCRIPTION_CHANGE_DENIED` são contados
quando `denyReason` for `OUT_OF_THERAPEUTIC_RANGE`, `UNAUTHORIZED_ROLE`,
`DOCTOR_NOT_LINKED_TO_PATIENT`, `REAUTHENTICATION_FAILED`,
`MISSING_OR_INVALID_CONFIRMATION` ou `AUDIT_TAMPER_ATTEMPT`. A terceira ocorrência em 10
minutos para o mesmo `authorId` ou `prescriptionId` abre um único alerta, ao qual as
ocorrências seguintes da janela são anexadas.

`STALE_BASE_VERSION` isolado não entra no Gatilho B, pois pode resultar de concorrência
legítima; ele permanece disponível para investigação e passa a ser suspeito somente se
vier acompanhado de um dos motivos acima. Uma recusa isolada também fica registrada, mas
não gera alerta Alto. Os limiares são valores iniciais e devem ser recalibrados com dados
operacionais sem enfraquecer o Gatilho A.

### Ação esperada da equipe

**Alerta Crítico:**

1. abrir um incidente único pelo `correlationId` e notificar imediatamente Segurança da
   Informação, médico responsável e Farmácia Clínica;
2. sinalizar a versão afetada como aguardando verificação clínica antes da próxima
   administração, mantendo disponível o último histórico íntegro;
3. preservar eventos, versões, identidade das sessões e contexto técnico em repositório
   de acesso restrito;
4. verificar com a equipe clínica qual versão deve permanecer vigente, sem executar
   reversão automática de uma decisão terapêutica; e
5. revogar a sessão ou restringir a conta somente quando a triagem indicar credencial
   comprometida ou ação sem autorização. Um atendimento emergencial deve seguir fluxo de
   exceção formal, com nova identidade confirmadora e auditoria própria.

**Alerta Alto:** a equipe de Segurança correlaciona as tentativas com autenticação,
dispositivo e vínculo assistencial, contata o responsável clínico e classifica o caso. Se
houver indício de abuso, bloqueia novas tentativas daquela sessão e escala o incidente;
se for erro operacional ou catálogo desatualizado, mantém o registro, corrige a causa por
processo autorizado e documenta a decisão para ajuste posterior do limiar.

O alerta nunca deve, sozinho, apagar uma versão, alterar uma prescrição ou interromper
silenciosamente um tratamento. A contenção técnica e a decisão clínica precisam ficar
separadas e auditadas.

### Falsos positivos previstos

- dose excepcional ou uso fora da faixa cadastral, clinicamente justificado, mas ainda
  sem atualização do catálogo terapêutico;
- repetição causada por erro de digitação, reenvio do cliente ou instabilidade de rede;
- fluxo emergencial autorizado (*break-glass*), que continua exigindo revisão e não deve
  ser simplesmente excluído da detecção; e
- alterações concorrentes legítimas. Por isso `STALE_BASE_VERSION`, sem outro sinal, não
  contribui para o limiar.

Eventos repetidos com o mesmo `correlationId` são duplicatas técnicas, não falsos
positivos, e devem ser eliminados antes da contagem. Exceções permanentes por usuário ou
medicamento não são permitidas; uma exceção clínica deve ser específica, temporária,
aprovada e auditada.

### Verificação da regra

Como o SIGH ainda não possui implementação, estes são casos de teste planejados, e não
evidências já executadas:

| ID | Entrada simulada | Resultado esperado |
| --- | --- | --- |
| R2-TV01 | Publicação válida, dentro da faixa e com duas identidades diferentes | Nenhum alerta; evento permanece pesquisável |
| R2-TV02 | Três recusas suspeitas do mesmo autor em até 10 minutos | Exatamente um alerta Alto contendo as três correlações |
| R2-TV03 | Três recusas contra a mesma prescrição, originadas por autores diferentes | Um alerta Alto para possível ação coordenada ou alvo comum |
| R2-TV04 | Reenvio do mesmo evento três vezes com igual `correlationId` | Uma ocorrência contabilizada e nenhum alerta de repetição |
| R2-TV05 | Uma publicação fora da faixa ou sem confirmação independente | Alerta Crítico imediato, independentemente do histórico anterior |
| R2-TV06 | Conflito concorrente com apenas `STALE_BASE_VERSION` | Registro disponível, sem alerta Alto da Regra 2 |
| R2-TV07 | Evento contendo nome do paciente, token ou justificativa clínica livre | Evento fica em quarentena e gera falha de esquema; dado sensível não chega ao índice geral de segurança |
| R2-TV08 | Ausência de dois *heartbeats* consecutivos, emitidos a cada minuto | Alerta operacional após 2 minutos; Regra 2 marcada como sem cobertura até a recuperação |

### Dependências operacionais e referências

Os produtores devem usar relógio sincronizado e transmitir os eventos por canal
autenticado para armazenamento central protegido contra alteração e exclusão. Um
*heartbeat* a cada minuto permite distinguir ausência de tentativas de uma falha de
coleta; a perda de dois ciclos consecutivos deve gerar alerta operacional separado e
indicar que a Regra 2 está sem cobertura. Retenção, acesso e consulta aos dados seguem a
política institucional e devem registrar quem acessou a trilha.

A especificação segue o
[OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html),
que recomenda eventos de aplicação correlacionáveis, proteção dos logs, tratamento de
dados sensíveis e integração com monitoramento e resposta. O procedimento de triagem,
contenção, preservação e aprendizado é alinhado ao
[NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final), que integra resposta a
incidentes ao gerenciamento de riscos do NIST CSF 2.0.

## Regra 3 - Elevação de `nivelAcesso` no Serviço de Funcionários (@PPrauchner)

- **Risco observado:** R06 - um `Administrador` de nível Supervisor passa a operar com
  alçada de Diretor sobre o Serviço de Funcionários, alcançando o cadastro completo de
  profissionais e os campos `nomeLogin` e `senhaLogin` de todos os perfis (T06/CA05).
- **Fonte de dados:** decisões emitidas pelo Serviço de Autorização (DA02) para toda
  operação administrativa e trilha de auditoria imutável de alteração de perfil (DA01),
  conforme as cláusulas 5 e 7 de [RS03](E3_Arquitetura_segura.md), correlacionadas com os
  eventos de leitura em massa do cadastro previstos na cláusula 8.
- **Condição de alerta (limiar e janela):** **notificação obrigatória** a cada elevação
  efetivada, sem limiar e no momento em que ocorre - é o controle R06-C4 da
  [Etapa 2](E2_Riscos_e_NIST_CSF.md). Alerta **Crítico** diante de uma única elevação que
  traga marca de anomalia (solicitante igual ao titular, aprovador igual ao solicitante,
  decisão tomada fora do Serviço de Autorização ou campo gravado pela via de salvamento do
  cadastro), e diante de leitura administrativa em massa nos 60 minutos seguintes a
  qualquer elevação. Alerta **Alto** a partir de 3 recusas de privilégio do mesmo autor
  **ou** sobre o mesmo titular em uma janela deslizante de 10 minutos, na recusa isolada
  cuja requisição não passou pela interface, e a partir de 3 requisições de alçada nova em
  sessão emitida antes da promoção, na mesma janela.
- **O que o alerta indica:** que o `nivelAcesso` - único mecanismo de autorização do modelo
  inteiro do SIGH - mudou, ou que alguém está tentando mudá-lo. No caso Alto, tentativa
  repetida de gravar o campo por uma via que RS03 fechou; no caso Crítico, que a alçada foi
  efetivamente concedida sem passar pelo fluxo de aprovação, e que o alcance obtido pode
  já estar sendo usado para varrer o cadastro - que é o passo 5 do CA05.

Esta regra observa **alçada**, não credencial, e é essa a diferença que a separa da Regra
1. Em R06 a identidade não foi falsificada, foi promovida: o ator autentica com a própria
senha e a sessão é legítima do início ao fim, de modo que nenhum sinal de autenticação
anômala aparece. A [Etapa 1](E1_Casos_de_abuso_e_Stride.md) registra em T06 que, sem
instrumentação, "não há anomalia a observar" - a Regra 3 existe justamente para criar a
anomalia observável que o modelo original não produz, exigindo que a decisão de
autorização emita evento mesmo quando **permite** a operação.

### Contrato mínimo dos eventos

O Serviço de Autorização (DA02), e não o Desktop Cliente nem o Serviço de Funcionários,
preenche os campos usados pela regra: a cláusula 1 de RS03 manda descartar identidade,
papel e `nivelAcesso` recebidos na requisição, e um evento que os copiasse reintroduziria
no monitoramento o valor que o requisito acabou de descartar. Cada operação administrativa
gera um evento terminal `PROFILE_CHANGE_APPLIED` ou `PROFILE_CHANGE_DENIED`; as leituras
da cláusula 8 geram `ADMIN_BULK_READ`. **Nenhum evento pode conter `senhaLogin`, valor
derivado dela, `nomeLogin` de terceiros ou código de segundo fator** - o dano de R06 se
realiza exatamente sobre esses campos, e vazá-los para o índice de segurança seria entregar
pela detecção o que a autorização passou a negar.

| Campo | Uso na detecção |
| --- | --- |
| `eventTime`, `eventType`, `correlationId` | Ordenação, janela e deduplicação da operação |
| `actorId`, `actorRole`, `actorLevel` | Quem solicitou, com o perfil vigente **obtido da sessão** (cláusula 1) |
| `subjectId`, `previousLevel`, `newLevel` | Titular afetado e a transição de perfil; `newLevel` acima de `previousLevel` é o que define elevação |
| `approverId`, `approverDistinctFromRequester`, `approverLevel` | Verificam a alçada de Diretor e a separação entre quem pede e quem aprova (cláusula 3) |
| `decisionSource`, `ruleId`, `writePath` | Comprovam que a decisão veio do Serviço de Autorização, sob qual regra, e se o campo chegou pela operação própria de perfil ou pela via de salvamento do cadastro |
| `bypassedUi` | Indicador derivado: a requisição chegou ao endpoint sem passar pela interface (RS03-CA03) |
| `sessionId`, `sessionIssuedAt`, `sessionLevel` | Detectam alçada nova exercida em sessão anterior à promoção (cláusula 6) |
| `outcome`, `denyReason`, `httpStatus` | Resultado da decisão e motivo da recusa, para a contagem do Gatilho C |
| `recordsReturned`, `queryScope`, `unitScope` | Volume e abrangência da leitura administrativa, limitados pela cláusula 8 |
| `deviceId`, `networkZone`, `sourceService` | Contexto técnico para triagem, na mesma convenção das Regras 1 e 2 |

### Lógica de correlação

**Gatilho A - Notificação obrigatória.** Todo `PROFILE_CHANGE_APPLIED` com `newLevel`
superior a `previousLevel` notifica o Diretor e a Segurança da Informação **no momento**
da efetivação, ainda que a promoção seja íntegra. Não é incidente e não abre chamado: é o
que a cláusula 7 de RS03 e o controle R06-C4 exigem, e é o que torna a elevação um evento
datado, com autor e valor anterior, em vez de silenciosa e permanente. A notificação exige
confirmação de recebimento - o residual Médio de R06 pressupõe alerta "ativo e com
destinatário definido", e alerta sem destinatário não é controle. Rebaixamento
(`newLevel` inferior) é registrado, mas não notifica por este gatilho.

**Gatilho B - Crítico e imediato.** O mesmo evento `PROFILE_CHANGE_APPLIED` dispara alerta
Crítico quando qualquer condição abaixo for verdadeira:

- `actorId` é igual a `subjectId` - promoção sobre o próprio registro, que a cláusula 3
  proíbe sem exceção; **ou**
- `approverDistinctFromRequester` é falso, `approverId` está ausente ou `approverLevel` não
  é Diretor - quem solicita a promoção aprovou a própria promoção; **ou**
- `writePath` indica a via de salvamento do cadastro, e não a operação própria de alteração
  de perfil - é o mecanismo exato do passo 3 do CA05 (CWE-915); **ou**
- `decisionSource` não é o Serviço de Autorização, ou `ruleId` está vazio - a decisão foi
  tomada dentro do serviço que a executa, ou por omissão de regra, contrariando a cláusula
  2 e a DA02.

**Gatilho C - Alto por repetição.** Contam para o limiar os eventos
`PROFILE_CHANGE_DENIED` cujo `denyReason` seja `SELF_PRIVILEGE_CHANGE`,
`LEVEL_FIELD_NOT_WRITABLE`, `INSUFFICIENT_AUTHORITY`, `APPROVER_EQUALS_REQUESTER` ou
`MISSING_AUTHORIZATION_RULE`. A terceira ocorrência em 10 minutos para o mesmo `actorId`
ou o mesmo `subjectId` abre um único alerta, ao qual as seguintes da janela são anexadas.
Uma recusa isolada com `bypassedUi` verdadeiro abre alerta Alto **sozinha**: uma tela que
não oferece a opção não produz esse tráfego por acidente, e RS03-CA03 registra que a
recusa não depende da interface. O limiar de 3 é mais baixo que o da Regra 1 porque aqui
não existe equivalente da senha digitada errada - não há erro de digitação que produza uma
tentativa de gravar `nivelAcesso`.

**Gatilho D - Alto por sessão desatualizada.** Requisição de operação exclusiva de um
perfil cujo `sessionLevel` diverge do perfil vigente do titular, com `sessionIssuedAt`
anterior à última alteração registrada na trilha, é recusada pela cláusula 6 e contabilizada.
A terceira ocorrência do mesmo `sessionId` em 10 minutos abre alerta Alto. A primeira e a
segunda são informativas: um profissional promovido no meio do plantão esbarra
legitimamente nisso até a identidade de sessão ser reemitida (RS03-CA07). A insistência é
que interessa - ela indica que alguém já conhece a alçada que deveria ter e está tentando
exercê-la fora do fluxo.

**Gatilho E - Crítico por sequência de CA05.** Eventos `ADMIN_BULK_READ` do mesmo `actorId`
nos **60 minutos** seguintes a um `PROFILE_CHANGE_APPLIED` que o tenha promovido abrem
alerta Crítico quando `recordsReturned` acumulado ultrapassar o limite de volume da
cláusula 8, ou quando `unitScope` abranger unidades além da lotação do solicitante. É a
sequência do CA05 - promover, e em seguida percorrer o cadastro de todas as unidades - e
o único gatilho desta regra que também protege R05: o mesmo volume, sobre o SGBD único,
é o caminho de indisponibilidade descrito em T05. Quando o alerta de 80% do pool de
conexões (controle R05-C5) disparar dentro dessa janela, os dois eventos devem ser
correlacionados no mesmo incidente, porque na apuração de CA05 a degradação e a elevação
sempre foram tratadas como fatos independentes - foi isso que impediu de ligá-las.

### Ação esperada da equipe

**Notificação do Gatilho A:** o Diretor confirma o recebimento e valida a promoção contra
o pedido formal correspondente. Uma elevação notificada e não reconhecida por quem consta
como aprovador vira, imediatamente, incidente Crítico - é o único caminho de detecção que
resta para a promoção legítima indevida, limite que a própria RS03 reconhece: conta de
Diretor comprometida ou conluio de quem aprova continua produzindo uma elevação válida.

**Alerta Crítico:**

1. abrir incidente único pelo `correlationId` e notificar Segurança da Informação e o
   Diretor, com o par `previousLevel` → `newLevel` e o `actorId` explícitos;
2. reverter o `nivelAcesso` ao valor anterior registrado na trilha, **pelo mesmo fluxo de
   aprovação** da cláusula 3 e com aprovador distinto - diferente da Regra 1 e da Regra 2,
   a reversão aqui não tem custo assistencial nem decide conduta clínica, mas continua
   sendo uma operação administrativa e não pode ser feita por atalho;
3. reemitir ou revogar a identidade de sessão do envolvido, porque a cláusula 6 exige que a
   alçada acompanhe o perfil vigente e uma sessão elevada sobrevive à correção do campo;
4. apurar, pela trilha da DA01 e pelos eventos `ADMIN_BULK_READ`, **o que a alçada alcançou
   enquanto durou** - cadastro de profissionais, escalas, medicamentos. Se o cadastro tiver
   sido percorrido, acionar o dono de R01: enquanto `senhaLogin` estiver em texto simples,
   a leitura equivale à exposição das credenciais de todos os perfis e exige troca em massa,
   e o dono de R04 quando a varredura tiver alcançado prontuário;
5. quando o Gatilho E também tiver disparado, acionar o dono de R05 para verificar a
   saturação do SGBD e aplicar a regra de degradação, preservando prontuário, prescrição e
   mapa de leitos; e
6. registrar o resultado, inclusive quando for falso positivo, para recalibrar limiar e
   janela.

**Alerta Alto:** Segurança correlaciona as tentativas com o cargo, a lotação e o pedido de
promoção eventualmente em curso, e contata a chefia administrativa do envolvido. Havendo
indício de tentativa deliberada - especialmente com `bypassedUi` verdadeiro -, restringe a
sessão às operações do perfil vigente, escala o incidente e mantém a conta sob observação
até a apuração terminar. Sendo erro operacional ou pedido legítimo mal encaminhado,
registra, orienta o fluxo correto e mantém o histórico para ajuste do limiar.

O alerta nunca deve, sozinho, alterar `nivelAcesso` de ninguém - nem para cima nem para
baixo. Uma regra de detecção que reescrevesse o campo automaticamente se tornaria um
segundo caminho de alteração de privilégio fora do fluxo de aprovação, isto é, exatamente
a fraqueza que RS03 fechou.

### Falsos positivos previstos

- **Promoção em lote por reestruturação.** Posse de nova diretoria, fusão de setores ou
  abertura de unidade produzem várias elevações legítimas em sequência. O Gatilho A as
  notifica uma a uma, o que é o comportamento correto, mas a operação deve ser declarada
  com antecedência à Segurança para que as notificações sejam agrupadas em um único aviso -
  e nunca suprimidas.
- **Sessão antiga após promoção legítima.** É o caso mais frequente previsto para o Gatilho
  D e o motivo de o limiar ser 3, e não 1: o promovido tenta usar a alçada nova antes de a
  identidade de sessão ser reemitida, e o próprio RS03-CA07 descreve isso como recusa
  esperada, não como ataque.
- **Inventário periódico de acessos.** A revisão de perfis exigida pela política
  institucional percorre o cadastro e cairia no Gatilho E. Ela deve ter janela declarada,
  executor identificado e escopo registrado; fora dessas condições, permanece suspeita.
- **Correção de cadastro errado.** Um funcionário cadastrado com o nível errado é corrigido
  por quem tem alçada - operação legítima, indistinguível de uma promoção nos dados. Só o
  reconhecimento pelo Diretor no Gatilho A a separa de uma elevação indevida, o que é o
  limite honesto desta regra.

Eventos repetidos com o mesmo `correlationId` são duplicatas técnicas, não falsos
positivos, e devem ser eliminados antes da contagem. Não são admitidas exceções permanentes
por usuário: uma conta que gerasse alertas rotineiros do Gatilho B ou C indicaria fluxo de
aprovação mal desenhado, e a resposta é corrigir o fluxo, não silenciar a regra.

### Verificação da regra

Como o SIGH não possui implementação, estes são casos de teste planejados, e não evidências
já executadas. Os oito primeiros correspondem, na mesma ordem, aos critérios RS03-CA01 a
RS03-CA08 da [Etapa 3](E3_Arquitetura_segura.md).

| ID | Entrada simulada | Resultado esperado |
| --- | --- | --- |
| R3-TV01 | Sessão Diretor promove outro funcionário a GerenteSetor, com aprovador distinto | Nenhum alerta de incidente; notificação obrigatória do Gatilho A ao Diretor e à Segurança, com confirmação de recebimento |
| R3-TV02 | Sessão Supervisor envia o próprio cadastro com `nivelAcesso: "Diretor"` no corpo | Recusa HTTP 403 registrada e contabilizada no Gatilho C; o campo permanece `Supervisor` |
| R3-TV03 | A requisição de R3-TV02 enviada direto ao endpoint, sem passar pela interface | Alerta Alto imediato pelo `bypassedUi`, sem esperar a terceira ocorrência |
| R3-TV04 | Alteração legítima de dados funcionais trazendo `nivelAcesso` alterado junto no corpo | Dados funcionais gravados, campo inalterado e tentativa registrada com `writePath` de cadastro; sem alerta se isolada, contando para o Gatilho C |
| R3-TV05 | Diretor tenta elevar o próprio `nivelAcesso` | Recusa registrada; se a elevação tiver sido efetivada por falha do controle, alerta Crítico pelo primeiro caso do Gatilho B |
| R3-TV06 | Operação administrativa nova sem regra de autorização declarada | Recusa por omissão de regra com `MISSING_AUTHORIZATION_RULE`, contabilizada no Gatilho C; efetivação com `ruleId` vazio gera Crítico |
| R3-TV07 | Sessão aberta antes de uma promoção legítima chama, três vezes em 10 minutos, operação exclusiva do perfil novo | Duas recusas informativas e um alerta Alto na terceira, pelo Gatilho D |
| R3-TV08 | Sessão administrativa percorre o cadastro completo de todas as unidades 20 minutos após ter sido promovida | Alerta Crítico pelo Gatilho E, com o limite de volume aplicado e nenhum campo de autenticação retornado |
| R3-TV09 | Promoção íntegra, mas o aprovador declarado não reconhece o pedido na confirmação | Escalada da notificação do Gatilho A para incidente Crítico |
| R3-TV10 | Evento contendo `senhaLogin`, valor derivado ou `nomeLogin` de terceiros | Evento em quarentena e falha de esquema; credencial não chega ao índice de segurança |
| R3-TV11 | Ausência de dois *heartbeats* consecutivos, emitidos a cada minuto | Alerta operacional após 2 minutos; Regra 3 marcada como sem cobertura até a recuperação |

### Dependências operacionais e referências

A regra depende de duas decisões de arquitetura da [Etapa 3](E3_Arquitetura_segura.md), e
sem elas não há o que observar. A **DA02** - Serviço de Autorização centralizado - é o que
faz existir um evento de decisão: com a autorização resolvida na montagem da tela, permitir
não produz registro algum, e a elevação continuaria sendo o evento invisível que T06
descreve. A **DA01** - Serviço de Auditoria com trilha imutável - é o que sustenta o valor
anterior, o autor vindo da sessão e a data/hora carimbada pelo servidor, sem os quais os
Gatilhos B e E não têm com o que comparar. A **DA03** entra indiretamente, por ser a origem
da identidade de sessão de que a cláusula 1 depende.

Vale registrar o que a regra **não** cobre: ela detecta a elevação e a tentativa, não a
promoção legítima decidida por má-fé de quem tem alçada. O reconhecimento pelo aprovador no
Gatilho A é o único mecanismo que se aproxima disso, e ele depende de conduta humana, não
de controle técnico. Vale também repetir o limite que a [Etapa 2](E2_Riscos_e_NIST_CSF.md)
fixou no residual de R06: detectar mais cedo encurta a janela de exploração, mas **não
reduz o impacto** enquanto `senhaLogin` permanecer em texto simples - a redução do impacto
de R06 depende do tratamento de R01.

Os produtores devem usar relógio sincronizado e canal autenticado para armazenamento
central protegido contra alteração e exclusão. Um *heartbeat* por minuto distingue ausência
de operações administrativas de falha de coleta; a perda de dois ciclos consecutivos gera
alerta operacional separado.

A especificação segue o
[OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html),
de onde vêm a negação por padrão e a reavaliação de autorização a cada requisição que os
Gatilhos B e D verificam, e o capítulo **V4 - Access Control** do
[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/),
que sustenta a exigência de decisão no servidor. O contrato de eventos segue o
[OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html),
quanto a eventos correlacionáveis e tratamento de dado sensível, na mesma convenção das
Regras 1 e 2, e o procedimento de triagem e resposta é alinhado ao
[NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final).
