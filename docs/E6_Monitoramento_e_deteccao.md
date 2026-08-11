# Etapa 6 - Monitoramento e Detecção de Intrusões

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lilydias24
> É exigido um **roteiro com 3 regras de detecção**, reaproveitando os riscos já registrados na [Etapa 2](E2_Riscos_e_NIST_CSF.md).

- A compilação final do roteiro fica em `roteiros/E6-deteccao-de-intrusoes.md`.

| Regra | Risco observado | Responsável | Situação |
| --- | --- | --- | --- |
| 1 | R01 - Spoofing | @lilydias24 | Pendente |
| 2 | R02 - Tampering | @ARTHUR9011 | Concluída (especificação; aguarda implementação do SIGH) |
| 3 | R06 - Elevation of Privilege | @PPrauchner | Pendente |
| Compilação | Roteiro final | @lilydias24 | Pendente |

---

## Quadro de regras

| Regra | Risco observado | Fonte de dados | Condição de alerta | Ação esperada | Responsável |
| --- | --- | --- | --- | --- | --- |
| 1 | R01 - Spoofing | Logs de autenticação | Muitas tentativas malsucedidas seguidas para a mesma conta | | @lilydias24 |
| 2 | R02 - Tampering | Eventos de segurança e trilha de auditoria das prescrições | Publicação que viola uma invariante de RS02 ou 3 recusas suspeitas pelo mesmo autor/prescrição em 10 minutos | Acionar resposta clínica e de segurança conforme a severidade, preservando as evidências | @ARTHUR9011 |
| 3 | R06 - Elevation of Privilege | Logs de autorização | Tentativa de acesso a função administrativa por usuário sem `nivelAcesso` compatível | | @PPrauchner |

## Regra 1 - Tentativas de autenticação suspeitas (@lilydias24)

- **Risco observado:** R01
- **Fonte de dados:**
- **Condição de alerta (limiar e janela):**
- **O que o alerta indica:**
- **Ação esperada da equipe:**
- **Falsos positivos previstos:**

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
