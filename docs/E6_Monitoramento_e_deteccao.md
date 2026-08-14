# Etapa 6 - Monitoramento e Detecção de Intrusões

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lilydias24
> É exigido um **roteiro com 3 regras de detecção**, reaproveitando os riscos já registrados na [Etapa 2](E2_Riscos_e_NIST_CSF.md).

- A compilação final do roteiro fica em `roteiros/etapa-6-deteccao-de-intrusoes.md`.

| Regra | Risco observado | Responsável | Situação |
| --- | --- | --- | --- |
| 1 | R01 - Spoofing | @lilydias24 | Concluída (especificação; aguarda implementação do SIGH) |
| 2 | R02 - Tampering | @ARTHUR9011 | Concluída (especificação; aguarda implementação do SIGH) |
| 3 | R06 - Elevation of Privilege | @PPrauchner | Pendente |
| Compilação | Roteiro final | @lilydias24 | Pendente |

---

## Quadro de regras

| Regra | Risco observado | Fonte de dados | Condição de alerta | Ação esperada | Responsável |
| --- | --- | --- | --- | --- | --- |
| 1 | R01 - Spoofing | Eventos de segurança do serviço de autenticação (RS01, cláusula 7), correlacionados com os de operação sensível | Crítico: sucesso após rajada de falhas, sessões simultâneas em zonas distintas, ou operação sensível de dispositivo desconhecido. Alto: 5 falhas em 15 min na mesma conta, ou mesma origem falhando contra 10 contas | Confirmar a sessão com o titular fora do sistema antes de revogar; havendo comprometimento, revisar o que foi executado durante a sessão | @lilydias24 |
| 2 | R02 - Tampering | Eventos de segurança e trilha de auditoria das prescrições | Publicação que viola uma invariante de RS02 ou 3 recusas suspeitas pelo mesmo autor/prescrição em 10 minutos | Acionar resposta clínica e de segurança conforme a severidade, preservando as evidências | @ARTHUR9011 |
| 3 | R06 - Elevation of Privilege | Logs de autorização | Tentativa de acesso a função administrativa por usuário sem `nivelAcesso` compatível | | @PPrauchner |

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

## Regra 3 - *(a definir)* (@PPrauchner)

- **Risco observado:** R06
- **Fonte de dados:**
- **Condição de alerta:**
- **O que o alerta indica:**
- **Ação esperada da equipe:**
- **Falsos positivos previstos:**
