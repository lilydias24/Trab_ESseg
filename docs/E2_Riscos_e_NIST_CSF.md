# Etapa 2 - Análise, Priorização e Tratamento de Riscos com o NIST CSF 2.0

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @ARTHUR9011
> A numeração das seções segue a do enunciado (13.1 a 15). Cada integrante transforma a própria ameaça STRIDE da [Etapa 1](E1_Casos_de_abuso_e_Stride.md) em risco, mantendo a mesma trilha do início ao fim.

| Seção | Responsável | Situação |
| --- | --- | --- |
| 13.1 Critérios de probabilidade | @ARTHUR9011 + @lorenzoficher | Concluída (exemplos do SIGH adicionados) |
| 13.2 Critérios de impacto | @ARTHUR9011 + @lorenzoficher | Escala base definida |
| 13.3 Cálculo e classificação | @ARTHUR9011 | Concluída |
| 13.4 Registro de riscos | Todos (1 risco por pessoa) | R01, R02, R05 e R06 concluídos; R03 e R04 pendentes |
| 13.5 Justificativas | Todos | R01, R02, R05 e R06 concluídas; R03 e R04 pendentes |
| 13.6 Priorização geral | @mariasanchez0’s (compila) | Pendente |
| 13.7 Conclusão da análise | @ARTHUR9011 | Rascunho concluído (revisão após R03-R06) |
| 14.1 Estratégia de tratamento | Todos | R01 e R02 concluídas; demais pendentes |
| 14.2 Funções do NIST CSF | @lorenzoficher | Tabela base definida |
| 14.3 Mapeamento risco → NIST | Todos | R01 e R02 concluídos; demais pendentes |
| 14.4 Plano de tratamento | Todos | R01 e R02 concluídos; demais pendentes |
| 14.5 Ordem de implementação | @mariasanchez0’s | Pendente |
| 14.6 Risco residual | Todos | R01 e R02 concluídos; demais pendentes |
| 15. Considerações finais | @PPrauchner (rascunho) + revisão de todos | Pendente |

---

## 13.1 Critérios de probabilidade

| Valor | Classificação | Critério | Exemplo no contexto do SIGH |
| --- | --- | --- | --- |
| 1 | Baixa | O evento depende de condições incomuns, acesso muito específico ou grande capacidade técnica | Adulteração direta dos dados no SGBD central: exige acesso de infraestrutura ao banco, fora dos perfis da aplicação |
| 2 | Média-baixa | O evento é possível, mas depende de uma vulnerabilidade ou condição específica | Elevação de privilégio pelo `nivelAcesso` do Administrador: depende de a validação existir apenas na interface e de o atacante conhecer essa lacuna (T06) |
| 3 | Média-alta | O evento é plausível e pode ocorrer em situações comuns de uso ou ataque | Alteração de prescrição a partir de uma sessão autenticada que alcança o Serviço de Paciente - situação comum nos postos com terminais compartilhados (T02) |
| 4 | Alta | O evento pode ocorrer com facilidade, frequência ou durante condições previsíveis do sistema | Tentativas de login com senhas fracas ou reaproveitadas: sem bloqueio por tentativas e com `senhaLogin` em texto simples, o vetor está disponível a qualquer momento (T01) |

## 13.2 Critérios de impacto

| Valor | Classificação | Critério |
| --- | --- | --- |
| 1 | Baixo | Causa pequeno transtorno e pode ser corrigido rapidamente |
| 2 | Moderado | Causa interrupção ou inconsistência limitada, com possibilidade de recuperação |
| 3 | Alto | Causa prejuízo relevante aos usuários, ao negócio, à administração ou à privacidade |
| 4 | Muito alto | Pode afetar muitos usuários, comprometer operações críticas ou causar prejuízo grave |

> **Pendente (@lorenzoficher):** acrescentar a cada faixa um exemplo concreto do contexto do SIGH, no mesmo formato adotado em 13.1.

## 13.3 Cálculo e classificação dos riscos

Pontuação = Probabilidade × Impacto

| Pontuação | Nível do risco |
| --- | --- |
| 1 a 3 | Baixo |
| 4 a 7 | Médio |
| 8 a 11 | Alto |
| 12 a 16 | Crítico |

## 13.4 Registro de riscos

| ID | Origem STRIDE | Responsável | Evento de risco | Vulnerabilidade ou condição | Probabilidade | Impacto | Pontuação | Nível |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | T01 - Spoofing | @lilydias24 | | | | | | |
| R02 | T02 - Tampering | @ARTHUR9011 | Alteração indevida da `dosagemMedicamento` ou do `intervaloConsumo` de uma prescrição ativa, executada pela enfermagem como se fosse a prescrição original | `atualizarTratamentosDoPaciente(tratamento)` não recebe o responsável; a regra "apenas médicos autorizados" (UC03) não é validada no servidor; não há faixa terapêutica para os campos; a alteração sobrescreve o registro sem versionamento nem autor | 3 | 4 | 12 | Crítico |
| R03 | T03 - Repudiation | @lorenzoficher | | | | | | |
| R04 | T04 - Information Disclosure | @mariasanchez0’s | | | | | | |
| R05 | T05 - Denial of Service | @PPrauchner | Indisponibilidade simultânea dos módulos assistenciais - prontuário, prescrição em curso e mapa de leitos ficam inacessíveis a todos os perfis ao mesmo tempo, com pacientes internados, por saturação do SGBD central ou do API Gateway | Todos os DAOs terminam em um **SGBD único**, sem réplica, cota de conexões por microsserviço nem prioridade entre carga administrativa e assistencial; o API Gateway é passagem obrigatória e não aplica *rate limiting*; a emissão de faturas (RF25) roda no Serviço de Atendimento Médico por não existir microsserviço Financeiro; a chamada ao «system» Convênio (RF06) é síncrona, sem *timeout* nem modo degradado; RNF01, RNF02 e RNF03 exigem volume simultâneo, escalabilidade e recuperação automática que o diagrama de implantação não sustenta | 3 | 4 | 12 | Crítico |
| R06 | T06 - Elevation of Privilege | @PPrauchner | Um Administrador de nível Supervisor persiste `nivelAcesso: Diretor` no próprio cadastro e passa a operar com alçada de Diretor sobre o Serviço de Funcionários, alcançando o cadastro completo de profissionais e os campos `nomeLogin` e `senhaLogin` de todos os perfis | `Administrador.nivelAcesso` é o **único** atributo de autorização do modelo e é salvo junto com os demais dados do cadastro, sem operação própria e sem regra que impeça o titular de alterar o próprio valor; a verificação de perfil ocorre na montagem da interface e não é revalidada no servidor a partir da sessão autenticada; o firewall de cada serviço separa serviço de serviço, não perfis dentro de uma sessão já autenticada; o Tópico 9 exclui do escopo o registro de eventos críticos de acesso indevido e não existe perfil de auditoria | 2 | 4 | 8 | Alto |

## 13.5 Justificativas das avaliações

### R01

**Probabilidade.** 
**Impacto** 
**Quem é afetado.** 
**Por que Crítico é adequado.** 

### R02

**Probabilidade (3 - Média-alta).** O evento não exige invasão nem capacidade técnica: exige uma sessão autenticada que alcance o Serviço de Paciente - condição comum de uso do SIGH, com terminais compartilhados nos postos de atendimento e sessões sem expiração por inatividade (condições do CA02). Como a regra "apenas médicos autorizados podem alterar tratamentos" (UC03) é textual e não há validação de papel na operação, o alcance não se restringe ao perfil médico. Não é 4 porque ainda depende de intenção deliberada e de acesso à rede interna do hospital.

**Impacto (4 - Muito alto).** É o impacto mais grave do recorte: superdosagem ou subdosagem com dano físico direto ao paciente, potencialmente fatal, e irreversível no momento em que o medicamento é administrado. Somam-se a responsabilização indevida de quem administrou, a responsabilidade civil do hospital, a apuração pelos conselhos profissionais (CFM/COREN) e o tratamento indevido de dado de saúde perante a LGPD.

**Quem é afetado.** O paciente, em primeiro lugar e fisicamente; o profissional de enfermagem que administrou (sem autor registrado, a apuração recai sobre ele); o médico titular da prescrição; e o hospital como instituição.

**Por que Crítico é adequado.** 3 × 4 = 12 já coloca R02 na faixa Crítica, mas há duas agravantes que a fórmula não captura: o dano sai do sistema (é mediado por corpo, não por dado) e o próprio ato apaga a evidência - sem valor anterior nem autor guardados, a prescrição adulterada é indistinguível de uma legítima.

### R05

**Probabilidade (3 - Média-alta).** A escala de 13.1 define 3 como o evento plausível
"em situações comuns de uso ou ataque", e é exatamente aí que R05 se encaixa: ele é o
único risco do recorte que **não exige ator malicioso**. A emissão de faturas (RF25),
que roda dentro do Serviço de Atendimento Médico por não existir microsserviço
Financeiro, disputa as mesmas conexões do SGBD de que o Serviço de Internação precisa
para alocar um leito - basta que o fechamento de faturamento coincida com o horário de
maior movimento assistencial. A isso somam-se dois vetores que também não dependem de
ataque: o `buscarPacientePorIdentificador(idPaciente)` com identificador sequencial, que
gera volume de consultas válidas, e a chamada síncrona ao «system» Convênio (RF06), em
que uma lentidão **do terceiro** trava o atendimento do hospital. Não é 4 porque o evento
ainda depende da coincidência entre a janela de carga administrativa e o pico
assistencial - não está disponível a qualquer momento como o vetor de T01; e não é 2
porque não depende de nenhuma vulnerabilidade específica nem de o ator conhecer alguma
lacuna: o uso legítimo já produz a condição.

**Impacto (4 - Muito alto).** A escala de 13.2 reserva o 4 para o que "pode afetar muitos
usuários e comprometer operações críticas", e a indisponibilidade aqui não é parcial nem
localizada: como todos os DAOs terminam no mesmo SGBD e o API Gateway é passagem
obrigatória, os 7 serviços caem juntos, para todos os perfis, no mesmo instante. O que
fica inacessível é prontuário, alergias, prescrição em curso e mapa de leitos - com
pacientes internados no prédio, e não usuários que possam voltar depois. É o oposto
exato do RNF03, que exige operação 24h/7d com recuperação automática de falhas.

**Quem é afetado.** Os pacientes internados, em primeiro lugar, porque a decisão clínica
passa a ser tomada sem o histórico; médicos, enfermeiros e recepcionistas, que voltam ao
papel enquanto durar a janela; e o hospital, que perde simultaneamente os módulos
assistenciais e os administrativos. Entre os ativos, os atingidos são o prontuário do
`Paciente`, a `PrescricaoMedicamento` em curso, o `LeitoHospitalar` e o faturamento do
RF25.

**Por que Crítico é adequado.** 3 × 4 = 12 já coloca R05 na faixa Crítica, e há duas
agravantes que a fórmula não captura. A primeira é que o dano **sobrevive à restauração
do serviço**: tudo o que foi feito no papel entra no sistema depois, digitado por quem
teve tempo, com data e hora informadas por quem digita - a janela de indisponibilidade
fabrica, de forma legítima e em escala, a mesma condição que sustenta T03 (Repudiation).
Uma queda de algumas horas deixa no prontuário um rastro não auditável por semanas. A
segunda é que um dos gatilhos está **fora do controle do hospital**: a disponibilidade do
«system» Convênio é decidida por um terceiro, e o modelo não prevê *timeout* nem modo
degradado que isole essa dependência.

### R06

**Probabilidade (2 - Média-baixa).** O valor acompanha o exemplo já registrado em 13.1,
que usa esta mesma ameaça para ilustrar a faixa: a elevação *"depende de a validação
existir apenas na interface e de o atacante conhecer essa lacuna (T06)"*. São duas
condições específicas, e há uma terceira: o ator precisa **já ser** `Administrador`, o
único perfil do modelo que possui `nivelAcesso` - o que exclui médicos, enfermeiros e
recepcionistas do vetor. Não é 3 porque o evento não decorre de uso comum do sistema:
exige reenviar a requisição de salvamento com um valor que a interface não oferece, isto
é, operar fora do fluxo que a tela monta. E não é 1 porque não há nada de incomum no
acesso exigido nem de raro na capacidade técnica: o campo já trafega no salvamento
normal do cadastro (CA05, passo 2), de modo que quem tem o perfil já tem o caminho -
falta apenas perceber que ele está aberto.

**Impacto (4 - Muito alto).** O `nivelAcesso` é o **único mecanismo de autorização que
existe no modelo inteiro do SIGH** (observação 1 da seção 8.3): elevá-lo não contorna uma
barreira entre várias, contorna *a* barreira. Com alçada de Diretor sobre o Serviço de
Funcionários, o ator alcança o cadastro completo de profissionais, incluindo `nomeLogin`
e `senhaLogin` de todos os perfis - que a seção 8.3.2 registra em texto simples. Isso
**habilita T01 em massa** sem que nenhuma senha precise ser roubada e, a partir das
contas assumidas, viabiliza prescrever (T02) e registrar óbito (T03) em nome de médicos
reais. Some-se a criação de novas contas com perfil de Médico, que o sistema tratará
como legítimas desde o primeiro login, porque no SIGH o perfil *é* a permissão.

**Quem é afetado.** Todos os funcionários cadastrados, cujas credenciais ficam expostas
de uma só vez; os pacientes, por consequência, quando essas credenciais forem usadas
sobre prontuário e prescrição; e o hospital, que perde a integridade do próprio modelo de
autorização e fica sem meio de demonstrar a extensão do acesso perante a LGPD (art. 11).

**Por que Alto é adequado.** 2 × 4 = 8 coloca R06 na faixa Alta, e o número está correto:
a probabilidade é de fato condicionada, e inflá-la para chegar a Crítico contradiria a
escala publicada em 13.1. O que a fórmula não captura são duas agravantes que devem pesar
na priorização de 13.6, e não na pontuação. A primeira é que R06 é um risco
**habilitador**: a pontuação mede o dano que ele causa por si, não o fato de que ele
desbloqueia T01, T02 e T03 de uma vez - a única ameaça do recorte que multiplica as
outras. A segunda é que **não há anomalia a observar**: a identidade não foi falsificada,
foi promovida, e um log - se existisse - registraria um Diretor legítimo fazendo o que
Diretores fazem; com o Tópico 9 excluindo o registro de eventos críticos e sem perfil de
auditoria, a elevação é silenciosa e permanente. O próprio enunciado (13.3) prevê esse
caso ao advertir que "dois riscos com a mesma pontuação podem receber prioridades
diferentes": R06 pede urgência acima do que um 8 sugere.

> **Pendente:** justificativas de R03 e R04, cada uma pelo respectivo responsável.

## 13.6 Priorização geral

> Seção compilada por **@mariasanchez0’s**, com validação coletiva - ordem de tratamento considerando pontuação, gravidade das consequências, usuários afetados, importância do ativo, possibilidade de recuperação, dependências e urgência.

*(Pendente - depende do preenchimento de R02 a R06.)*

### 13.7 Conclusão da análise de riscos

> Seção do **@ARTHUR9011** (líder da etapa), com validação coletiva. Não consta com número próprio no enunciado, mas o exemplo entregue pelo professor traz uma conclusão fechando a análise antes de entrar no tratamento - encerramento do raciocínio de probabilidade × impacto, dizendo quais riscos exigem atenção inicial e em que condições a classificação deve ser revisada.

A análise partiu das ameaças da Etapa 1 e as converteu em riscos comparáveis por uma mesma régua: probabilidade × impacto, nas escalas de 1 a 4 definidas em 13.1 e 13.2. Dois padrões já aparecem nos riscos registrados. Primeiro, os riscos do topo da tabela não são os de ataque mais sofisticado, e sim os que dependem apenas de condições comuns de uso do SIGH - uma senha em texto simples, uma sessão aberta em terminal compartilhado, uma operação que não verifica quem a chama. Segundo, probabilidade e impacto têm origens distintas: a probabilidade vem quase sempre de controles ausentes (autenticação de fator único, validação apenas na interface, ausência de trilha), enquanto o impacto vem da natureza do ativo (dado clínico, prescrição, registro de óbito). Isso orienta o tratamento: reduzir probabilidade é tarefa de engenharia, mas o impacto, na maior parte dos casos, não se reduz - o que dá prioridade aos riscos Críticos, em que as duas dimensões se encontram.

A atenção inicial deve ir para essa faixa Crítica: R02, em que a alteração de uma prescrição alcança o paciente fisicamente antes de qualquer detecção, e R01, que além do dano próprio funciona como porta de entrada dos demais riscos - toda ameaça do recorte fica mais provável a partir de uma conta assumida. A classificação deve ser revisada em três momentos: quando R03-R06 forem registrados e a priorização geral (13.6) puder ser compilada; quando os controles de 14.4 forem implementados e verificados, passando a valer os residuais de 14.6; e se o contexto operacional mudar - novos módulos no recorte, nova integração externa ou um incidente real que contradiga alguma estimativa.

> *Rascunho do líder da etapa; revisão prevista quando R03-R06 estiverem registrados.*

## 14.1 Estratégias de tratamento

| Estratégia | Descrição |
| --- | --- |
| Evitar | Eliminar a atividade ou condição que dá origem ao risco |
| Reduzir | Implementar medidas para diminuir a probabilidade ou o impacto |
| Compartilhar | Atribuir parte da operação ou das consequências a um terceiro |
| Aceitar | Reconhecer e manter conscientemente o risco, com justificativa e acompanhamento |

| Risco | Estratégia escolhida | Justificativa |
| --- | --- | --- |
| R01 | | |
| R02 | Reduzir | Alterar prescrição é função essencial do sistema, então o risco não pode ser Evitado; a responsabilidade clínica não pode ser transferida a terceiro, então não há o que Compartilhar; e um risco Crítico com dano potencialmente fatal não pode ser Aceito. Resta Reduzir: controles que diminuam a probabilidade da alteração indevida e aumentem a chance de detecção antes da administração do medicamento |
| R03 | | |
| R04 | | |
| R05 | | |
| R06 | | |

## 14.2 Funções do NIST CSF 2.0

> Seção de responsabilidade do **@lorenzoficher**.

| Função | Finalidade |
| --- | --- |
| Govern | Definir políticas, responsabilidades, prioridades e critérios de decisão |
| Identify | Conhecer ativos, dependências, vulnerabilidades e riscos |
| Protect | Implementar salvaguardas para reduzir a probabilidade ou o impacto |
| Detect | Identificar eventos suspeitos, falhas e possíveis incidentes |
| Respond | Conter, analisar, comunicar e tratar incidentes |
| Recover | Restaurar serviços e dados e reduzir os prejuízos causados |

## 14.3 Mapeamento dos riscos para as funções do NIST CSF

| Risco | Govern | Identify | Protect | Detect | Respond | Recover |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| R01 | | | | | | |
| R02 | X | | X | X | X | |
| R03 | | | | | | |
| R04 | | | | | | |
| R05 | | | | | | |
| R06 | | | | | | |

### Justificativa do mapeamento

- **Govern**
- **Identify**
- **Protect**
- **Detect**
- **Respond** 
- **Recover**

#### R02 (@ARTHUR9011)

- **Govern:** as regras do UC03 - apenas médicos autorizados alteram tratamentos e todo tratamento guarda o responsável - precisam deixar de ser texto de caso de uso e virar política com dono: quem pode alterar prescrição ativa, quando a segunda assinatura é exigida e quem responde pela trilha de auditoria.
- **Protect:** é onde os controles do plano (14.4) atuam - responsável obrigatório na operação, validação de papel no servidor, faixa terapêutica, versionamento e reautenticação reduzem diretamente a probabilidade.
- **Detect:** alteração de dosagem fora de faixa ou sem segunda assinatura deve gerar alerta - é exatamente a regra 2 do roteiro de detecção previsto para a Etapa 6, que observa este risco.
- **Respond:** detectada uma alteração suspeita, a prescrição deve ser bloqueada para administração e farmácia/chefia notificadas antes do próximo horário de medicação - a janela de resposta útil é o intervalo entre a alteração e a administração.
- **Por que não Identify e Recover:** a identificação do ativo e da vulnerabilidade já está feita na Etapa 1 (T02/CA02); e não existe recuperação de sistema para dano clínico já administrado - o versionamento restaura o dado, não o paciente. É por isso que o tratamento de R02 concentra tudo **antes** da administração.

> **Pendente:** mapeamento e justificativa de R03 a R06, cada um pelo respectivo responsável (evitar marcar todas as funções sem justificar).

## 14.4 Plano de tratamento

| Risco | Estratégia | Controles propostos | Funções relacionadas | Responsáveis | Evidências e verificação |
| --- | --- | --- | --- | --- | --- |
| R01 | | | | | |
| R02 | Reduzir | **R02-C1** - a operação de alteração passa a registrar o responsável obtido da sessão autenticada no servidor (nunca informado pelo cliente), cumprindo a regra do UC03; **R02-C2** - validação de papel no servidor: apenas médico, e médico vinculado ao paciente; **R02-C3** - validação de faixa terapêutica por medicamento, com bloqueio de valores fora da faixa; **R02-C4** - versionamento da prescrição em trilha imutável (valor anterior, novo valor, autor, data/hora); **R02-C5** - segunda assinatura de outro profissional + reautenticação para alterar prescrição ativa | Govern, Protect, Detect, Respond | @ARTHUR9011 | Testes com caso válido e caso malicioso (Etapa 4); log de auditoria consultável com autor e valor anterior; alerta da regra 2 do roteiro de detecção (Etapa 6) disparando em alteração fora de faixa ou sem segunda assinatura |
| R03 | | | | | |
| R04 | | | | | |
| R05 | | | | | |
| R06 | | | | | |

## 14.5 Ordem inicial de implementação

> Seção compilada pelo **@mariasanchez0’s**, com justificativa - depende dos controles de todos os riscos.

*(Pendente. Observação de @lilydias24 para a compilação: o controle C1 - hash e salt - é pré-requisito dos demais controles de R01 e não depende de nenhum outro item do plano, o que o torna candidato natural às primeiras posições.)*

## 14.6 Estimativa do risco residual

| Risco | Nível inicial | Nível residual esperado | Condição para aceitar o residual |
| --- | --- | --- | --- |
| R01 | | | |
| R02 | Crítico (12) | Médio (4) | Controles R02-C1 a R02-C5 comprovadamente operantes (evidências de 14.4); alerta da Etapa 6 ativo; revisão da classificação se a segunda assinatura for flexibilizada na rotina |
| R03 | | | |
| R04 | | | |
| R05 | | | |
| R06 | | | |

### Justificativa do residual de R01 (@lilydias24)

**Probabilidade**
**Impacto**
**Condição para aceitar o residual Alto:** 

### Justificativa do residual de R02 (@ARTHUR9011)

**Probabilidade (3 → 1).** Com os controles R02-C1 a R02-C5, uma alteração indevida que chegue à administração passa a exigir condições incomuns: uma conta de médico vinculada ao paciente, reautenticada, um valor dentro da faixa terapêutica e a confirmação de um segundo profissional - na prática, o conluio de dois profissionais ou o comprometimento simultâneo de duas contas (cenário que remete ao residual de R01).

**Impacto (4, inalterado).** Se ainda assim o evento ocorrer, o dano continua físico e potencialmente fatal - nenhum controle reduz a gravidade clínica de uma dose errada administrada. O que muda é a visibilidade: com autor e valor anterior versionados, a adulteração deixa de ser indistinguível de uma prescrição legítima, mas não deixa de ser dano.

**Condição para aceitar o residual Médio:** os controles precisam estar comprovadamente operantes (coluna de evidências de 14.4), e a classificação deve ser refeita se a segunda assinatura ganhar exceções de rotina (ex.: emergências) ou se o alerta de detecção da Etapa 6 ficar inativo.

## 15. Considerações finais (Etapa 2)

> Rascunho de responsabilidade do **@PPrauchner**, com revisão de todos.

- **Riscos mais importantes:**
- **Razões da priorização:**
- **Estratégias de tratamento predominantes:**
- **Funções do NIST mais relevantes:**
- **Controles considerados essenciais:**
- **Principais dificuldades e limitações da avaliação:**
- **Pontos a detalhar nas próximas etapas:**
