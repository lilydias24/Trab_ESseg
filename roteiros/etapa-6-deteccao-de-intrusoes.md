# Roteiro de Detecção de Intrusões - SIGH

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Compilado por:** @lilydias24, a partir das três regras especificadas em [`docs/E6_Monitoramento_e_deteccao.md`](../docs/E6_Monitoramento_e_deteccao.md)
> **Origem:** riscos R01, R02 e R06, registrados na [Etapa 2](../docs/E2_Riscos_e_NIST_CSF.md) e tratados na [Etapa 3](../docs/E3_Arquitetura_segura.md)

Este é o artefato exigido pelo §27 do enunciado: um roteiro autônomo, pronto para operar
contra a telemetria do SIGH quando o sistema existir. Como o SIGH não possui
implementação, toda condição de alerta abaixo é **especificação verificável**, não
detecção em produção - os casos de teste de cada regra (seção "Verificação planejada")
descrevem o que precisa passar quando o sistema for construído, e não um resultado já
observado.

Este documento reúne o que uma equipe de segurança precisa para operar as três regras.
O raciocínio completo por trás de cada limiar, gatilho e exclusão - incluindo os casos de
abuso que motivaram cada decisão de desenho - está em
[`docs/E6_Monitoramento_e_deteccao.md`](../docs/E6_Monitoramento_e_deteccao.md), assinado
por regra. Este roteiro não substitui aquele documento; consolida o que dele é
operacional, para que a equipe de plantão não precise abrir cinco arquivos para saber o
que fazer diante de um alerta.

---

## Quadro-resumo das três regras

| Regra | Risco observado | Fonte de dados | Condição de alerta | Resposta inicial | Responsável |
| --- | --- | --- | --- | --- | --- |
| 1 | R01 - Spoofing | Eventos de segurança do serviço de autenticação (RS01, cláusula 7), correlacionados com os de operação sensível | Crítico: sucesso após rajada de falhas, sessões simultâneas em zonas distintas, ou operação sensível de dispositivo desconhecido. Alto: 5 falhas em 15 min na mesma conta, ou mesma origem falhando contra 10 contas | Confirmar a sessão com o titular fora do sistema antes de revogar; havendo comprometimento, revisar o que foi executado durante a sessão | @lilydias24 |
| 2 | R02 - Tampering | Eventos de segurança e trilha de auditoria das prescrições | Publicação que viola uma invariante de RS02, ou 3 recusas suspeitas pelo mesmo autor/prescrição em 10 minutos | Acionar resposta clínica e de segurança conforme a severidade, preservando as evidências | @ARTHUR9011 |
| 3 | R06 - Elevation of Privilege | Decisões do Serviço de Autorização (DA02) e trilha imutável de alteração de perfil (DA01), conforme as cláusulas 5 e 7 de RS03 | Notificação obrigatória, sem limiar, a cada elevação efetivada (Gatilho A, controle R06-C4). Crítico: elevação com solicitante igual ao titular, aprovador igual ao solicitante, `decisionSource` diferente do Serviço de Autorização ou `ruleId` vazio, campo gravado pela via de salvamento do cadastro, ou leitura acima do limite de volume da cláusula 8 até 60 min depois de uma elevação do próprio autor da leitura. Alto: 3 recusas de privilégio em 10 min, requisição direto ao endpoint, 3 usos em 10 min de alçada nova em sessão anterior à promoção, uso isolado de alçada já retirada por rebaixamento, ou leitura acima do limite de volume sem elevação prévia do próprio autor | Notificar Diretor e Segurança da Informação; havendo anomalia, reverter o `nivelAcesso` pelo fluxo de aprovação, reemitir a sessão e apurar o que a alçada leu | @PPrauchner |

## Convenções comuns às três regras

As três foram desenhadas de forma independente, uma por integrante, mas convergiram para
os mesmos princípios operacionais - o que reforça que não são arbitrários:

- **Autoria e tempo vêm sempre do servidor.** Nenhuma regra aceita `authorId`, `actorId`
  ou carimbo de data/hora informados pelo cliente. É a mesma exigência que RS01, RS02 e
  RS03 fazem aos seus respectivos fluxos.
- **Nenhum evento carrega segredo.** Senha, valor derivado dela, código de segundo fator
  e (na Regra 3) `nomeLogin`/`senhaLogin` de terceiros nunca chegam ao índice de
  segurança. Um evento que os contivesse reproduziria, na camada de monitoramento, o
  risco que a regra existe para observar.
- **Deduplicação por `correlationId`.** Reenvio do cliente e falha de rede geram o mesmo
  identificador de correlação; são duplicatas técnicas, descontadas antes de qualquer
  limiar - nunca falsos positivos de fato.
- **Heartbeat de 1 minuto.** As três fontes de eventos emitem um sinal de vida a cada
  minuto; a perda de dois ciclos consecutivos abre alerta operacional próprio e marca a
  regra correspondente como **sem cobertura** até a recuperação. Um sistema calado não é
  um sistema seguro - é um sistema sem visibilidade.
- **O alerta nunca executa a ação corretiva sozinho.** Nenhuma das três regras reverte
  dado, encerra sessão ou muda `nivelAcesso` automaticamente. A decisão de conter cabe a
  uma pessoa, porque as três correções têm custo - assistencial nas Regras 1 e 2,
  administrativo na Regra 3 - que só um humano pode pesar.
- **Falso positivo é dado de calibração, não descarte.** As três regras preveem
  explicitamente cenários de uso legítimo que se parecem com abuso (troca de turno,
  exceção clínica, reestruturação administrativa) e pedem que o resultado - inclusive
  quando não há incidente - seja registrado para ajustar o limiar.

---

## Regra 1 - Uso indevido de credencial de profissional

**Responsável:** @lilydias24 · **Risco observado:** R01 (Spoofing)

Uso das credenciais legítimas de um profissional para assumir sua identidade no SIGH. A
regra observa o serviço de autenticação (DA03), conforme a cláusula 7 de RS01,
correlacionado com eventos de operação sensível dos serviços de negócio.

### Contrato de eventos

| Campo | Uso na detecção |
| --- | --- |
| `eventTime`, `eventType`, `correlationId` | Ordenação, janela e deduplicação |
| `subjectId`, `subjectRole` | Conta alvo e perfil - identificador interno, nunca o `nomeLogin` digitado |
| `outcome`, `failureReason` | `SUCCESS`, `BAD_CREDENTIAL`, `MFA_FAILED`, `ACCOUNT_LOCKED`, `BREAK_GLASS_USED` |
| `mfaPresented`, `mfaValid`, `reauthAt` | Distinguem falha de senha de falha de segundo fator |
| `deviceId`, `networkZone`, `sourceService` | Contexto técnico; a zona é a ala/setor |
| `knownDeviceForSubject` | Se o profissional já autenticou naquele terminal antes |

### Gatilhos

- **A - Crítico e imediato.** Um `SUCCESS` dispara alerta quando: for precedido de 5+
  falhas na mesma conta em 15 min (adivinhação bem-sucedida); **ou** existir outra sessão
  ativa da mesma conta em zona diferente, com sobreposição que nenhum deslocamento
  explicaria; **ou** for seguido, em até 2 min, de prescrição, alta ou óbito a partir de
  dispositivo nunca visto para aquele profissional.
- **B - Alto por repetição.** `BAD_CREDENTIAL`/`MFA_FAILED`: 5ª ocorrência em 15 min na
  mesma conta abre alerta. Em paralelo, falhas da mesma origem contra 10 contas distintas
  abrem alerta de pulverização de senhas.
- `ACCOUNT_LOCKED` não conta (é consequência, não tentativa nova). `BREAK_GLASS_USED`
  nunca gera alerta de intrusão, mas entra obrigatoriamente na fila de revisão da
  cláusula 8 de RS01.

### Ação da equipe

**Crítico:** (1) incidente único pelo `correlationId`, notificar Segurança e a chefia da
unidade; (2) contatar o titular **fora do sistema antes de revogar** - revogar a sessão
de um médico em atendimento tem custo assistencial; (3) preservar evidências; (4) se o
titular não reconhecer a sessão, revogar, forçar troca de credencial e **revisar o que
foi executado** durante ela, acionando os donos de R02/R03 conforme o que tiver sido
tocado; (5) registrar o resultado, mesmo se falso positivo.

**Alto:** correlacionar com dispositivo, zona e escala de trabalho; bloquear a origem se
houver indício de ataque, ou registrar e orientar se for erro operacional.

O alerta nunca encerra sozinho a sessão de um profissional em atendimento.

### Falsos positivos a não confundir com ataque

Terminal compartilhado (Gatilho B só conta falhas, não sucessos, na mesma origem); troca
de turno (limiar de 5 falhas calibrado acima do erro típico da passagem de plantão);
deslocamento entre alas (o Gatilho A exige sobreposição de sessões, não só mudança de
zona).

### Verificação planejada

| ID | Entrada simulada | Resultado esperado |
| --- | --- | --- |
| R1-TV01 | Login válido com segundo fator, terminal conhecido | Nenhum alerta |
| R1-TV02 | 5 falhas de senha na mesma conta em 15 min | Um alerta Alto |
| R1-TV03 | 5 falhas seguidas de um sucesso | Alerta Crítico pelo Gatilho A |
| R1-TV04 | Falhas da mesma origem contra 10 contas | Alerta Alto de pulverização |
| R1-TV05 | 12 logins de profissionais diferentes no mesmo terminal em 10 min | **Nenhum alerta** - troca de turno |
| R1-TV06 | Sessões simultâneas da mesma conta em duas zonas | Alerta Crítico |
| R1-TV07 | Sucesso seguido, em 1 min, de óbito de dispositivo desconhecido | Alerta Crítico |
| R1-TV08 | Uso de `BREAK_GLASS_USED` | Nenhum alerta; entra na fila de revisão |
| R1-TV09 | Evento com senha ou segredo | Quarentena; falha de esquema |
| R1-TV10 | Perda de 2 heartbeats consecutivos | Alerta operacional; regra sem cobertura |

### Dependências

Exige o serviço de autenticação da DA03 como emissor único - sem ele, os eventos ficam
espalhados pelos sete microsserviços e a correlação por conta deixa de ser confiável.
Segue o [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
e o [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html).

---

## Regra 2 - Tentativa de adulteração de prescrição ativa

**Responsável:** @ARTHUR9011 · **Risco observado:** R02 (Tampering)

Alteração indevida de `dosagemMedicamento` ou `intervaloConsumo` de uma prescrição ativa.
A regra observa o fluxo de alteração e a trilha de auditoria imutável de
`PrescricaoMedicamento`.

### Contrato de eventos

| Campo | Uso na detecção |
| --- | --- |
| `eventTime`, `eventType`, `correlationId` | Ordenação, janela e deduplicação |
| `prescriptionId`, `patientId`, `baseVersion`, `newVersion` | Correlação e detecção de sobrescrita |
| `medicationId`, `therapeuticCatalogVersion`, `withinTherapeuticRange` | Prova de validação contra referência conhecida |
| `authorId`, `authorRole`, `authorLinkedToPatient`, `reauthenticationValid` | Autoria e autorização (R02-C1/C2) |
| `confirmerId`, `confirmerAuthorized`, `confirmedProposalVersion` | Independência e vínculo da segunda confirmação |
| `outcome`, `denyReason`, `sourceService`, `deviceId`, `networkZone` | Resultado e contexto para triagem |

Nome do paciente, justificativa em texto livre e demais dados clínicos desnecessários não
são copiados para o evento; permanecem na trilha restrita.

### Gatilhos

- **A - Crítico e imediato.** Uma publicação dispara alerta se: `withinTherapeuticRange`
  for falso; **ou** o autor não for médico vinculado ao paciente, ou a reautenticação for
  inválida; **ou** o segundo confirmador estiver ausente, não autorizado, igual ao autor,
  ou tiver confirmado outra versão; **ou** a `baseVersion` não era a vigente, faltar
  auditoria correspondente, ou houver evidência de alteração da trilha.
- **B - Alto por repetição.** Recusas por faixa fora do padrão, papel não autorizado,
  médico não vinculado, reautenticação falha ou confirmação ausente/inválida: a 3ª
  ocorrência em 10 min, pelo mesmo autor **ou** pela mesma prescrição, abre alerta.
  `STALE_BASE_VERSION` isolado não conta (pode ser concorrência legítima).

### Ação da equipe

**Crítico:** (1) incidente único, notificar Segurança, médico responsável e Farmácia
Clínica; (2) sinalizar a versão como aguardando verificação clínica antes da próxima
administração, mantendo o último histórico íntegro disponível; (3) preservar evidências;
(4) verificar com a equipe clínica qual versão deve permanecer vigente - **sem reversão
automática** de decisão terapêutica; (5) revogar/restringir a conta apenas se a triagem
indicar credencial comprometida ou ação sem autorização, com fluxo de exceção formal para
atendimento emergencial.

**Alto:** correlacionar com autenticação, dispositivo e vínculo assistencial; bloquear
novas tentativas da sessão se houver indício de abuso, ou corrigir e documentar se for
erro operacional ou catálogo desatualizado.

O alerta nunca apaga versão, altera prescrição ou interrompe tratamento sozinho.

### Falsos positivos a não confundir com ataque

Dose excepcional clinicamente justificada mas ainda fora do catálogo; erro de digitação
ou reenvio por instabilidade de rede; fluxo *break-glass* (continua exigindo revisão, não
sai da detecção); alterações concorrentes legítimas (`STALE_BASE_VERSION` isolado).

### Verificação planejada

| ID | Entrada simulada | Resultado esperado |
| --- | --- | --- |
| R2-TV01 | Publicação válida, dentro da faixa, duas identidades | Nenhum alerta |
| R2-TV02 | 3 recusas suspeitas do mesmo autor em 10 min | Um alerta Alto |
| R2-TV03 | 3 recusas contra a mesma prescrição, autores diferentes | Um alerta Alto |
| R2-TV04 | Reenvio do mesmo evento 3x com igual `correlationId` | 1 ocorrência contada; sem alerta |
| R2-TV05 | Publicação fora da faixa ou sem confirmação | Alerta Crítico imediato |
| R2-TV06 | Conflito concorrente só com `STALE_BASE_VERSION` | Registrado; sem alerta Alto |
| R2-TV07 | Evento com nome do paciente ou token | Quarentena; falha de esquema |
| R2-TV08 | Perda de 2 heartbeats consecutivos | Alerta operacional; regra sem cobertura |

### Dependências

Requer relógio sincronizado e canal autenticado para o armazenamento central. Segue o
[OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
e o [NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final).

---

## Regra 3 - Elevação de `nivelAcesso` no Serviço de Funcionários

**Responsável:** @PPrauchner · **Risco observado:** R06 (Elevation of Privilege)

Um Administrador de nível Supervisor passa a operar com alçada de Diretor, alcançando o
cadastro completo de profissionais - incluindo `nomeLogin` e `senhaLogin` de todos os
perfis (T06/CA05). É a única das três regras que observa **alçada, não credencial**: a
identidade não foi falsificada, foi promovida, e por isso nenhum sinal de autenticação
anômala acompanha o abuso. A regra existe para criar a anomalia observável que o modelo
original do SIGH não produz.

### Contrato de eventos

| Campo | Uso na detecção |
| --- | --- |
| `eventTime`, `eventType`, `correlationId` | Ordenação, janela e deduplicação |
| `actorId`, `actorRole`, `actorLevel` | Solicitante, com perfil obtido da sessão |
| `subjectId`, `previousLevel`, `newLevel` | Titular afetado e a transição aplicada pelo servidor - `newLevel` > `previousLevel` define elevação |
| `claimedLevel` | `nivelAcesso` descartado do corpo pela cláusula 1, guardado como afirmação do cliente (cláusula 5). Evidência e contagem do Gatilho C, nunca decisão |
| `approverId`, `approverDistinctFromRequester`, `approverLevel` | Alçada de Diretor e separação entre quem pede e quem aprova |
| `decisionSource`, `ruleId`, `writePath` | Decisão veio do Serviço de Autorização, sob qual regra, e por qual via |
| `bypassedUi` | Requisição chegou ao endpoint sem passar pela interface |
| `sessionId`, `sessionIssuedAt`, `sessionLevel` | Alçada nova exercida em sessão anterior à promoção, e alçada antiga exercida em sessão já rebaixada (cláusula 6) |
| `outcome`, `denyReason`, `httpStatus` | Resultado e motivo da recusa |
| `recordsReturned`, `queryScope`, `unitScope` | Volume e abrangência de leitura administrativa |
| `deviceId`, `networkZone`, `sourceService` | Contexto técnico, mesma convenção das Regras 1 e 2 |

`senhaLogin`, valor derivado, `nomeLogin` de terceiros e código de segundo fator nunca
entram no evento.

### Gatilhos

- **A - Notificação obrigatória.** Todo `PROFILE_CHANGE_APPLIED` com elevação notifica o
  Diretor e a Segurança **no momento**, mesmo íntegro - não é incidente, é o controle
  R06-C4. Exige confirmação de recebimento.
- **B - Crítico e imediato.** Dispara quando: `actorId` = `subjectId` (autopromoção);
  **ou** aprovador ausente, igual ao solicitante, ou sem alçada de Diretor; **ou**
  `writePath` indica a via de salvamento do cadastro em vez da operação própria de perfil
  (o mecanismo exato do CA05); **ou** a decisão não veio do Serviço de Autorização.
- **C - Alto por repetição.** Recusas por autopromoção, campo não gravável, alçada
  insuficiente, aprovador igual ao solicitante ou regra ausente: 3ª ocorrência em 10 min
  no mesmo autor **ou** titular abre alerta. Recusa isolada com `bypassedUi` verdadeiro
  abre alerta Alto **sozinha**. Evento vindo da via de salvamento só conta quando
  `claimedLevel` difere de `previousLevel`: corpo com o valor vigente é reenvio do registro
  pelo cliente, fica registrado sem somar ao limiar. A comparação é com `claimedLevel`
  porque nessa via nada foi aplicado - `newLevel` sempre igualaria `previousLevel`.
- **D - Alto por sessão desatualizada.** Recusa pela cláusula 6, com `denyReason`
  `STALE_SESSION_LEVEL`, nas duas metades de RS03-CA07. Sessão **anterior a uma promoção**
  (`sessionLevel` inferior): 3ª ocorrência do mesmo `sessionId` em 10 min abre alerta - as
  duas primeiras são esperadas (o promovido ainda não teve a sessão reemitida). Sessão de
  perfil **rebaixado** (`sessionLevel` superior): alerta Alto **na primeira**, sem limiar,
  e com revogação da sessão - exercer alçada já retirada é acesso indevido em curso, não
  tentativa frustrada.
- **E - Leitura em massa do cadastro.** Volume ou abrangência acima do limite da cláusula
  8. **Crítico** quando ocorre nos 60 min seguintes a uma promoção do mesmo autor (a
  sequência do CA05); **Alto** quando não há promoção **do mesmo autor** na janela - o
  cenário puro de RS03-CA08, que a cláusula 8 cobre pelo volume, não pela origem da
  alçada. As duas condições são complementares de propósito: promoção de outra pessoa na
  janela não é a sequência do CA05, e sem isso a leitura cairia fora das duas. É o único
  gatilho que também protege R05, nas duas severidades: o mesmo volume, sobre o SGBD
  único, é caminho de indisponibilidade. Quando o alerta de 80% do pool (R05-C5) disparar
  na mesma janela, correlacionar no mesmo incidente.

### Ação da equipe

**Notificação (Gatilho A):** o Diretor confirma o recebimento contra o pedido formal
correspondente. Não reconhecida, a notificação vira incidente Crítico de imediato - é o
único caminho de detecção que resta para uma promoção legítima porém indevida.

**Crítico:** (1) incidente único, notificar Segurança e o Diretor com `previousLevel` →
`newLevel` e `actorId`; (2) reverter o `nivelAcesso` **pelo mesmo fluxo de aprovação**,
com aprovador distinto; (3) reemitir/revogar a sessão do envolvido; (4) apurar o que a
alçada alcançou - se o cadastro foi percorrido, acionar o dono de R01 (exposição de
`senhaLogin` em massa) e o de R04 se prontuário tiver sido alcançado; (5) se o Gatilho E
também disparou, acionar o dono de R05 para verificar saturação do SGBD; (6) registrar o
resultado.

**Alto:** correlacionar com cargo, lotação e pedido de promoção em curso; restringir a
sessão e escalar se houver indício deliberado, especialmente com `bypassedUi`; registrar
e orientar se for erro operacional.

O alerta nunca altera `nivelAcesso` sozinho, em nenhuma direção - isso seria um segundo
caminho de alteração de privilégio fora do fluxo de aprovação, a mesma fraqueza que RS03
fechou.

### Falsos positivos a não confundir com ataque

Promoção em lote por reestruturação (Gatilho A notifica uma a uma - declarar com
antecedência para agrupar os avisos, nunca suprimi-los); sessão antiga após promoção
legítima (Gatilho D, limiar 3 por esse motivo - a tolerância não vale para a sessão
rebaixada); reenvio do registro inteiro pelo cliente, que carrega o `nivelAcesso` vigente
no corpo (não conta no Gatilho C, porque `claimedLevel` não difere de `previousLevel`);
inventário periódico de acessos (Gatilho
E - precisa de janela, executor e escopo declarados); correção de cadastro errado
(indistinguível de promoção nos dados - só o reconhecimento do Diretor no Gatilho A
separa os dois casos, limite honesto da regra).

### Verificação planejada

| ID | Entrada simulada | Resultado esperado |
| --- | --- | --- |
| R3-TV01 | Diretor promove funcionário, aprovador distinto | Notificação obrigatória, sem incidente |
| R3-TV02 | Supervisor tenta se promover pelos dois caminhos: no corpo do próprio cadastro, depois pela operação de perfil | Via de salvamento, **sem 403**: campo descartado, demais dados gravados. Operação própria: recusa 403. As duas contam no Gatilho C |
| R3-TV03 | Cada uma das duas requisições direto ao endpoint | Alerta Alto imediato por `bypassedUi`, em ambas |
| R3-TV04 | Alteração legítima trazendo `nivelAcesso` alterado; e a mesma trazendo o valor vigente | Dados gravados e campo inalterado nas duas; só a primeira conta no Gatilho C |
| R3-TV05 | Diretor tenta elevar o próprio nível | Recusa `SELF_PRIVILEGE_CHANGE`, contada no Gatilho C; Crítico se efetivada por falha |
| R3-TV06 | Operação nova sem regra de autorização declarada | Recusa por regra ausente; Crítico se efetivada |
| R3-TV07 | Sessão pré-promoção chama operação nova 3x em 10 min; e sessão rebaixada chama 1x a operação antiga | `STALE_SESSION_LEVEL` nas duas. 2 informativas + Alto na 3ª; Alto já na 1ª no rebaixamento, com revogação da sessão |
| R3-TV08 | Cadastro completo lido 20 min após a promoção do próprio autor; o mesmo volume sem promoção na janela; e 30 min após a promoção de outro funcionário | Crítico pelo Gatilho E na primeira; Alto na segunda e na terceira |
| R3-TV09 | Aprovador não reconhece o pedido na confirmação | Notificação escala para incidente Crítico |
| R3-TV10 | Evento com `senhaLogin` ou `nomeLogin` de terceiros | Quarentena; falha de esquema |
| R3-TV11 | Perda de 2 heartbeats consecutivos | Alerta operacional; regra sem cobertura |

### Dependências

Depende de duas decisões da Etapa 3: **DA02** (Serviço de Autorização centralizado) é o
que faz existir um evento de decisão - sem ele, permitir não deixa rastro. **DA01**
(Serviço de Auditoria) sustenta valor anterior, autor e carimbo de tempo, sem os quais os
Gatilhos B e E não têm com o que comparar. Segue o
[OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
e o capítulo V4 (Access Control) do
[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/).

---

## Correlação entre as três regras

As regras não operam isoladas. Três pontos de correlação explícita:

1. **Regra 1 → Regras 2 e 3.** Uma conta comprometida (Crítico da Regra 1) exige revisar
   o que a sessão executou; se tocou prescrição ou registro de óbito, os donos de R02/R03
   entram na apuração.
2. **Regra 3 → Regra 1.** Uma elevação que alcançou o cadastro completo (Gatilho E) expõe
   `nomeLogin`/`senhaLogin` de todos os perfis em texto simples - o dono de R01 precisa
   ser acionado para avaliar troca de credenciais em massa.
3. **Regra 3 → risco de disponibilidade (R05).** O mesmo Gatilho E, quando coincide com o
   alerta de saturação do pool de conexões (R05-C5), deve abrir um incidente único: na
   reconstrução do CA05, degradação e elevação foram tratadas como fatos independentes, e
   foi exatamente isso que impediu de ligá-los a tempo.

## Limites reconhecidos

- **Conduta de quem tem alçada legítima.** As três regras detectam elevação, uso indevido
  e adulteração técnica - nenhuma detecta má-fé de quem já possui a permissão dentro do
  fluxo correto. Na Regra 3, o reconhecimento humano do Diretor no Gatilho A é o único
  mecanismo que se aproxima disso, e depende de conduta, não de controle técnico.
- **Detectar não é reduzir impacto.** O residual de R06 permanece Médio mesmo com a Regra
  3 ativa, porque detectar mais cedo encurta a janela de exploração, mas não reduz o dano
  de uma leitura que já ocorreu - a redução de impacto depende do tratamento de R01
  (credenciais em texto simples).
- **Sem sistema, sem evidência executada.** Todos os casos de verificação acima são
  planejados. Nenhum foi rodado contra um SIGH real, porque o SIGH não está implementado.

## Referências

[OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html) ·
[OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html) ·
[OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) ·
[OWASP ASVS - V4 Access Control](https://owasp.org/www-project-application-security-verification-standard/) ·
[NIST SP 800-61r3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)

## Rastreabilidade

| Regra | Ameaça (E1) | Risco (E2) | Requisito (E3) | Decisões de apoio (E3) | Especificação completa |
| --- | --- | --- | --- | --- | --- |
| 1 | T01 - Spoofing | R01 | RS01 | DA03 | [Regra 1, docs/E6](../docs/E6_Monitoramento_e_deteccao.md#regra-1---uso-indevido-de-credencial-de-profissional-lilydias24) |
| 2 | T02 - Tampering | R02 | RS02 | - | [Regra 2, docs/E6](../docs/E6_Monitoramento_e_deteccao.md#regra-2---tentativa-de-adulteração-de-prescrição-ativa-arthur9011) |
| 3 | T06 - Elevation of Privilege | R06 | RS03 | DA01, DA02 | [Regra 3, docs/E6](../docs/E6_Monitoramento_e_deteccao.md#regra-3---elevação-de-nivelacesso-no-serviço-de-funcionários-pprauchner) |
