# Etapa 2 - Análise, Priorização e Tratamento de Riscos com o NIST CSF 2.0

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @ARTHUR9011
> A numeração das seções segue a do enunciado (13.1 a 15). Cada integrante transforma a própria ameaça STRIDE da [Etapa 1](E1_Casos_de_abuso_e_Stride.md) em risco, mantendo a mesma trilha do início ao fim.

| Seção | Responsável | Situação |
| --- | --- | --- |
| 13.1 Critérios de probabilidade | @ARTHUR9011 + @lorenzoficher | Concluída (exemplos do SIGH adicionados) |
| 13.2 Critérios de impacto | @ARTHUR9011 + @lorenzoficher | Concluída (exemplos do SIGH adicionados) |
| 13.3 Cálculo e classificação | @ARTHUR9011 | Concluída |
| 13.4 Registro de riscos | Todos (1 risco por pessoa) | R01, R02, R03, R05 e R06 concluídos; R04 pendente |
| 13.5 Justificativas | Todos | R01, R02, R03, R05 e R06 concluídas; R04 pendente |
| 13.6 Priorização geral | @mariasanchez0’s (compila) | Pendente |
| 13.7 Conclusão da análise | @ARTHUR9011 | Rascunho concluído (revisão após R03-R06) |
| 14.1 Estratégia de tratamento | Todos | R01, R02, R03, R05 e R06 concluídas; R04 pendente |
| 14.2 Funções do NIST CSF | @lorenzoficher | Concluída |
| 14.3 Mapeamento risco → NIST | Todos | R01, R02, R03, R05 e R06 concluídos; R04 pendente |
| 14.4 Plano de tratamento | Todos | R01, R02, R03, R05 e R06 concluídos; R04 pendente |
| 14.5 Ordem de implementação | @mariasanchez0’s | Pendente |
| 14.6 Risco residual | Todos | R01, R02, R03, R05 e R06 concluídos; R04 pendente |
| 15. Considerações finais | @PPrauchner (rascunho) + revisão de todos | Rascunho concluído sobre R01, R02, R05 e R06 (revisão após R03, R04, 13.6 e 14.5) |

---

## 13.1 Critérios de probabilidade

| Valor | Classificação | Critério | Exemplo no contexto do SIGH |
| --- | --- | --- | --- |
| 1 | Baixa | O evento depende de condições incomuns, acesso muito específico ou grande capacidade técnica | Adulteração direta dos dados no SGBD central: exige acesso de infraestrutura ao banco, fora dos perfis da aplicação |
| 2 | Média-baixa | O evento é possível, mas depende de uma vulnerabilidade ou condição específica | Elevação de privilégio pelo `nivelAcesso` do Administrador: depende de a validação existir apenas na interface e de o atacante conhecer essa lacuna (T06) |
| 3 | Média-alta | O evento é plausível e pode ocorrer em situações comuns de uso ou ataque | Alteração de prescrição a partir de uma sessão autenticada que alcança o Serviço de Paciente - situação comum nos postos com terminais compartilhados (T02) |
| 4 | Alta | O evento pode ocorrer com facilidade, frequência ou durante condições previsíveis do sistema | Tentativas de login com senhas fracas ou reaproveitadas: sem bloqueio por tentativas e com `senhaLogin` em texto simples, o vetor está disponível a qualquer momento (T01) |

## 13.2 Critérios de impacto

| Valor | Classificação | Critério | Exemplo no contexto do SIGH |
| --- | --- | --- | --- |
| 1 | Baixo | Causa pequeno transtorno e pode ser corrigido rapidamente | Indisponibilidade momentânea do agendamento de consultas (RF04): o horário é remarcado no mesmo dia, sem perda de dado clínico e sem efeito sobre paciente internado |
| 2 | Moderado | Causa interrupção ou inconsistência limitada, com possibilidade de recuperação | Alocação concorrente do mesmo `LeitoHospitalar` a dois pacientes: gera remanejamento e retrabalho no setor de internação, mas a `Ocupacao` é corrigida pela própria equipe, sem dano ao paciente |
| 3 | Alto | Causa prejuízo relevante aos usuários, ao negócio, à administração ou à privacidade | Registro de óbito sem autoria comprovável: a apuração de responsabilidade não se conclui e expõe o médico titular e a instituição, mas o efeito é legal e administrativo, sem dano físico e restrito ao caso apurado (T03) |
| 4 | Muito alto | Pode afetar muitos usuários, comprometer operações críticas ou causar prejuízo grave | Alteração da `dosagemMedicamento` de uma prescrição ativa: o dano é físico, potencialmente fatal e irreversível assim que o medicamento é administrado (T02); ou a queda simultânea dos módulos assistenciais, que atinge todos os perfis com pacientes internados no prédio (T05) |

As duas escalas separam **o que torna o evento provável** do **quanto ele custa quando
ocorre**, e a diferença aparece na origem de cada uma: a probabilidade é decidida por
controles que existem ou não existem no projeto, enquanto o impacto é decidido pela
natureza do ativo atingido. Por isso um mesmo controle costuma mover apenas uma das
colunas - o que é retomado nas estimativas de risco residual em 14.6.

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
| R01 | T01 - Spoofing | @lilydias24 | Uso das credenciais legítimas de um profissional para assumir sua identidade no SIGH e executar consultas ao prontuário e operações clínicas em nome dele | `senhaLogin` armazenada como texto simples na classe `Funcionario`, contrariando o RNF05; autenticação de fator único, sem MFA nem reautenticação em operações sensíveis; sem bloqueio após tentativas malsucedidas; sessões sem expiração por inatividade em terminais compartilhados; o Tópico 9 exclui do escopo o registro de eventos críticos de acesso indevido | 4 | 4 | 16 | Crítico |
| R02 | T02 - Tampering | @ARTHUR9011 | Alteração indevida da `dosagemMedicamento` ou do `intervaloConsumo` de uma prescrição ativa, executada pela enfermagem como se fosse a prescrição original | `atualizarTratamentosDoPaciente(tratamento)` não recebe o responsável; a regra "apenas médicos autorizados" (UC03) não é validada no servidor; não há faixa terapêutica para os campos; a alteração sobrescreve o registro sem versionamento nem autor | 3 | 4 | 12 | Crítico |
| R03 | T03 - Repudiation | @lorenzoficher | Um registro de óbito é criado - por engano, por pressa, para encerrar um caso ou para liberar um leito - sem que o SIGH consiga atribuí-lo a um autor nem situá-lo no tempo real, de modo que quem registrou pode negar tê-lo feito e quem não registrou não tem como se defender | `Obito.registrarObito(data, hora)` não recebe o responsável, e a regra "somente médicos podem registrar óbito" (UC10) existe apenas como texto do caso de uso; data e hora chegam por parâmetro em vez de serem carimbadas pelo servidor, permitindo registro retroativo; o Tópico 9 exclui do escopo o registro de eventos críticos, de modo que não há trilha de auditoria, log de sessão nem de terminal; o registro encerra e bloqueia o prontuário, dificultando correção posterior; e o dado é transmitido ao «system» Sistema Governamental por integração sem requisito funcional documentado | 4 | 3 | 12 | Crítico |
| R04 | T04 - Information Disclosure | @mariasanchez0’s | | | | | | |
| R05 | T05 - Denial of Service | @PPrauchner | Indisponibilidade simultânea dos módulos assistenciais - prontuário, prescrição em curso e mapa de leitos ficam inacessíveis a todos os perfis ao mesmo tempo, com pacientes internados, por saturação do SGBD central ou do API Gateway | Todos os DAOs terminam em um **SGBD único**, sem réplica, cota de conexões por microsserviço nem prioridade entre carga administrativa e assistencial; o API Gateway é passagem obrigatória e não aplica *rate limiting*; a emissão de faturas (RF25) roda no Serviço de Atendimento Médico por não existir microsserviço Financeiro; a chamada ao «system» Convênio (RF06) é síncrona, sem *timeout* nem modo degradado; RNF01, RNF02 e RNF03 exigem volume simultâneo, escalabilidade e recuperação automática que o diagrama de implantação não sustenta | 3 | 4 | 12 | Crítico |
| R06 | T06 - Elevation of Privilege | @PPrauchner | Um Administrador de nível Supervisor persiste `nivelAcesso: Diretor` no próprio cadastro e passa a operar com alçada de Diretor sobre o Serviço de Funcionários, alcançando o cadastro completo de profissionais e os campos `nomeLogin` e `senhaLogin` de todos os perfis | `Administrador.nivelAcesso` é o **único** atributo de autorização do modelo e é salvo junto com os demais dados do cadastro, sem operação própria e sem regra que impeça o titular de alterar o próprio valor; a verificação de perfil ocorre na montagem da interface e não é revalidada no servidor a partir da sessão autenticada; o firewall de cada serviço separa serviço de serviço, não perfis dentro de uma sessão já autenticada; o Tópico 9 exclui do escopo o registro de eventos críticos de acesso indevido e não existe perfil de auditoria | 2 | 4 | 8 | Alto |

## 13.5 Justificativas das avaliações

### R01

**Probabilidade (4 - Alta).** O único obstáculo entre o atacante e a conta é saber a senha, e os caminhos para obtê-la são todos de baixo custo: observação da digitação em terminal compartilhado, reuso de senha já vazada em outro serviço, phishing dirigido ao corpo clínico, ou leitura direta da tabela `Funcionario` - que, sem hash, entrega as credenciais prontas para uso. Sem bloqueio por tentativas malsucedidas, a força bruta a partir da rede interna também está disponível.

Duas condições sustentam o valor 4 sem depender de suposição, porque vêm da documentação do próprio SIGH: o **RNF05** exige criptografia para as informações médicas, mas o modelo guarda `senhaLogin` em texto simples - a proteção está no requisito e não chegou ao projeto; e o **Tópico 9** coloca o registro de eventos críticos de acesso indevido fora do escopo, de modo que uma sequência de tentativas não encontra barreira nem gera alarme. É o critério de "condições previsíveis do sistema" da escala 13.1.

**Impacto (4 - Muito alto).** Uma sessão assumida alcança o prontuário de qualquer paciente - dado pessoal sensível pela LGPD (art. 5º, II) e protegido por sigilo médico - e habilita operações de consequência assistencial imediata: prescrever medicamento, autorizar alta e registrar óbito. As duas últimas são irreversíveis fora do sistema: uma alta indevida coloca um paciente para fora do hospital, e um registro de óbito produz efeitos legais e administrativos que nenhum `rollback` desfaz. Como o SIGH atribui a autoria pela sessão autenticada, as ações constam como sendo do profissional legítimo.

**Quem é afetado.** O paciente, na segurança clínica e na privacidade; o profissional cuja conta foi assumida, responsabilizado por atos que não praticou e sem meios de demonstrar o contrário; e a instituição, exposta perante a LGPD, os conselhos profissionais e eventuais ações judiciais.

**Por que Crítico é adequado.** 4 × 4 = 16 é a pontuação máxima da escala, e o que a justifica não é apenas a soma das duas dimensões: **R01 é o habilitador dos demais riscos do registro**. Uma conta assumida é o ponto de partida natural para a alteração de prescrição (R02), o registro de óbito irrastreável (R03) e a leitura indevida de prontuários (R04) - os casos de abuso CA02, CA03 e CA04 citam explicitamente a conta assumida como caminho de entrada alternativo. Tratar R01 reduz a probabilidade efetiva de todos eles, o que reforça sua posição no topo da priorização.

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

### R03

**Probabilidade (4 - Alta).** R03 é o único risco deste registro em que **o uso correto do
sistema já produz a condição do evento**. Nos demais, a probabilidade mede o quanto falta
para alguém explorar uma lacuna: em R01 é preciso obter uma senha, em R02 é preciso a
intenção de alterar a prescrição, em R06 é preciso perceber que a validação só existe na
interface. Aqui não é preciso nada disso. Toda chamada legítima a
`registrarObito(data, hora)` já nasce sem autor, com data e hora escolhidas por quem
chama e sem trilha que registre a sessão ou o terminal - o registro não atribuível é o
**resultado padrão** da operação, não o desvio dela.

Isso corresponde exatamente ao que a escala 13.1 reserva ao valor 4: o evento ocorre "com
facilidade, frequência ou durante condições previsíveis do sistema", e a condição
previsível aqui é a rotina. Não é 3 porque 3 exige que o evento seja apenas "plausível em
situações comuns", e a plausibilidade já foi ultrapassada: não existe execução da operação
que produza um registro atribuível. Há ainda um segundo vetor, independente da conduta de
qualquer pessoa e já identificado pelo @PPrauchner na justificativa de R05: a janela de
indisponibilidade obriga o registro em papel e a digitação posterior, com data e hora
informadas por quem digita - o que **fabrica a mesma condição em escala e de forma
inteiramente legítima**.

**Impacto (3 - Alto).** O dano de R03 é legal, administrativo e reputacional, e recai
sobre o caso apurado: uma responsabilização que não se conclui, um médico titular sem meio
de demonstrar que não foi o autor e uma instituição sem meio de inocentá-lo. É o critério
de "prejuízo relevante aos usuários, ao negócio, à administração" da escala 13.2, e é o
exemplo com que aquela faixa foi ilustrada.

Não é 4, e a diferença precisa ser dita porque o argumento contrário é tentador. R03 **não
afeta muitos usuários** de uma vez, como R05 e R06, nem produz dano físico irreversível,
como R02: cada evento diz respeito a um registro, um paciente e um profissional. O que R03
tem e os outros não é alcance sobre *as demais ameaças* - sem autoria registrada, nenhuma
delas pode ser comprovada depois, como observa a seção 8.5.1 da Etapa 1. Esse efeito é
real, mas é **habilitador**, e o documento já decidiu como tratá-lo: na justificativa de
R06, o @PPrauchner registrou que a natureza habilitadora "deve pesar na priorização de
13.6, e não na pontuação". Elevar o impacto a 4 por esse motivo pontuaria duas vezes a
mesma propriedade e contradiria a régua publicada em 13.2. O peso vai para 13.6.

**Quem é afetado.** O médico titular da conta, em primeiro lugar, que responde perante o
hospital e o conselho profissional por um ato que não tem como provar não ter praticado; a
família do paciente, que contesta data, hora ou causa e encontra um registro íntegro e
inexplicável; e a instituição, que perde a capacidade de apurar internamente e de se
defender externamente. Entre os ativos, o atingido é aquele que a seção 8.3.2 registra
como **não modelado**: a rastreabilidade das operações. É o único ativo do recorte cuja
ausência é, ela própria, a vulnerabilidade.

**Por que Crítico é adequado.** 4 × 3 = 12 coloca R03 na faixa Crítica, e a pontuação vem
inteiramente da probabilidade - o oposto de R06, que chega ao seu nível pelo impacto. Duas
agravantes que a fórmula não captura, e que pertencem à priorização: a primeira é que o
efeito **já saiu do domínio do hospital** quando a dúvida aparece, porque o registro foi
transmitido ao Sistema Governamental por uma integração que a seção 8.2 aponta como sem
requisito funcional documentado - não se sabe sequer se o que trafegou levava identificação
de responsável. A segunda é que a ausência de prova **não é recuperável retroativamente**:
uma senha se troca, um leito se realoca, uma prescrição se versiona a partir de agora, mas
nenhum controle implantado amanhã produz evidência sobre um registro feito ontem. Todo o
tratamento de R03 precisa ser anterior ao ato.

> **Pendente:** justificativa de R04, pelo respectivo responsável.

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
| R01 | Reduzir | Autenticar profissionais é função indispensável do SIGH, então não há como Evitar. Compartilhar atenderia só em parte: delegar a autenticação a um provedor de identidade institucional transfere a implementação, mas não a responsabilidade do hospital sobre os dados nem a consequência clínica de um acesso indevido. Aceitar é insustentável em um risco de pontuação máxima que habilita todos os demais. Resta Reduzir, e o espaço é amplo porque nenhuma barreira usual existe hoje: a redução ataca as condições que tornam a probabilidade alta - armazenamento inadequado da senha, fator único e ausência de bloqueio e de detecção |
| R02 | Reduzir | Alterar prescrição é função essencial do sistema, então o risco não pode ser Evitado; a responsabilidade clínica não pode ser transferida a terceiro, então não há o que Compartilhar; e um risco Crítico com dano potencialmente fatal não pode ser Aceito. Resta Reduzir: controles que diminuam a probabilidade da alteração indevida e aumentem a chance de detecção antes da administração do medicamento |
| R03 | Reduzir | Evitar significaria deixar de registrar óbitos - mas o registro é obrigação legal e assistencial (UC10) e alimenta o «system» Sistema Governamental; eliminar a operação eliminaria um dever, não um risco. Compartilhar não alcança o essencial: um serviço externo de carimbo de tempo pode ancorar **quando** o registro foi feito, e isso vira um controle, mas a autoria de um ato clínico praticado dentro do hospital e a responsabilidade por ele não são delegáveis a terceiro. Aceitar é insustentável na operação de maior efeito legal do recorte, porque significaria manter a instituição sem meio de prova diante de uma apuração judicial ou de conselho profissional. Resta Reduzir, e com uma diferença em relação aos demais riscos: aqui os controles não disputam com um atacante, eles **produzem a evidência que hoje não existe** - o espaço é atipicamente grande justamente porque nenhuma barreira foi construída ainda |
| R04 | | |
| R05 | Reduzir | Não há o que Evitar: o acesso concorrente de todos os módulos ao banco é a operação normal do SIGH, e eliminá-lo seria eliminar o sistema. Compartilhar cobre no máximo uma parte (hospedagem com acordo de nível de serviço) e não transfere a consequência assistencial - e a parcela que já está compartilhada, a validação de cobertura pelo «system» Convênio (RF06), hoje **amplia** o risco em vez de reduzi-lo, por ser síncrona e sem modo degradado. Aceitar contrariaria frontalmente o RNF03. Resta Reduzir, e nas duas pontas: controles que diminuam a probabilidade da saturação (cota de conexões, *rate limiting*, réplica de leitura) e controles que reduzam alcance e duração da janela (modo degradado e prioridade dos serviços assistenciais) |
| R06 | Reduzir | Evitar exigiria eliminar a graduação de acesso do `Administrador` - mas o `nivelAcesso` é o único mecanismo de autorização do modelo, e retirá-lo pioraria a situação em vez de resolvê-la. Compartilhar não se aplica: decidir quem tem alçada sobre o cadastro de profissionais é decisão interna e indelegável, não existe terceiro a quem atribuí-la. Aceitar é insustentável para um risco que expõe as credenciais de todos os perfis e habilita T01, T02 e T03 em cascata. Resta Reduzir, com um deslocamento preciso: mover a decisão de autorização da montagem da interface para o servidor, e tornar observável a alteração do campo que hoje muda em silêncio |

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

Duas observações orientam o uso da tabela no mapeamento de 14.3. A primeira é que
**Govern é a função introduzida pela versão 2.0** do framework e não fica ao lado das
outras cinco: ela as atravessa, definindo quem decide, sob qual política e com qual
prioridade. É por isso que ela aparece marcada nos riscos deste registro em que a regra
existe apenas como texto de caso de uso, sem dono - situação de R02 (UC03), de R03 (UC10)
e de R06 (`nivelAcesso`) -, e não aparece em R05, em que a política existe nos requisitos
não funcionais e o que falta é contrapartida de projeto.

A segunda é que as seis funções **não são etapas de um processo em sequência**, e marcar
todas seria transformar o mapeamento em formalidade. Cada risco deve marcar apenas as
funções em que exista um resultado esperado distinto, e as justificativas abaixo explicam
tanto as marcações quanto as ausências - critério que os riscos já mapeados seguiram ao
registrar, por exemplo, por que R02 não tem Recover e por que R05 não tem Govern.

## 14.3 Mapeamento dos riscos para as funções do NIST CSF

| Risco | Govern | Identify | Protect | Detect | Respond | Recover |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| R01 | X | | X | X | X | X |
| R02 | X | | X | X | X | |
| R03 | X | | X | X | X | X |
| R04 | | | | | | |
| R05 | | X | X | X | X | X |
| R06 | X | | X | X | X | |

### Justificativa do mapeamento

#### R01 (@lilydias24)

- **Govern:** o risco nasce da ausência de uma política institucional de credenciais - não há regra definida de complexidade, expiração, não reuso, nem responsável designado pela gestão das contas de profissionais. Sem essa decisão no nível de governança, os controles técnicos não têm parâmetro para serem configurados: "bloquear após N tentativas" só existe depois que alguém define o N e quem responde pelo desbloqueio.
- **Protect:** é o núcleo do tratamento. Hash com salt, autenticação multifator, bloqueio por tentativas e expiração de sessão atuam diretamente sobre as condições que tornam a probabilidade alta.
- **Detect:** hoje uma sequência de tentativas malsucedidas ou um login fora do padrão do profissional passa despercebido - o Tópico 9 coloca esse registro fora do escopo. A detecção é o que permite perceber o abuso **antes** de a sessão ser usada, e é exatamente a regra 1 do roteiro previsto para a Etapa 6.
- **Respond:** havendo suspeita de conta comprometida, é preciso procedimento definido - bloquear a conta, encerrar as sessões ativas e comunicar o profissional titular e a chefia -, e não apenas abrir um chamado.
- **Recover:** marcado aqui, diferente de R02, e a diferença é o que justifica a marcação. Em R02 não existe recuperação para uma dose já administrada; em R01 existe recuperação real e necessária: rotacionar as credenciais, revogar sessões e, sobretudo, **auditar e reverter o que a sessão comprometida produziu** - prescrições, altas e registros gerados em nome do titular. Sem esse passo, o incidente termina com a senha trocada e os atos indevidos ainda válidos no prontuário.
- **Por que não Identify:** o ativo (`Funcionario.senhaLogin`), os perfis e a vulnerabilidade já foram levantados na Etapa 1 (T01/CA01). O tratamento de R01 não depende de nenhum trabalho adicional de identificação, e marcar a função aqui seria apenas preencher a tabela.

#### R02 (@ARTHUR9011)

- **Govern:** as regras do UC03 - apenas médicos autorizados alteram tratamentos e todo tratamento guarda o responsável - precisam deixar de ser texto de caso de uso e virar política com dono: quem pode alterar prescrição ativa, quando a segunda assinatura é exigida e quem responde pela trilha de auditoria.
- **Protect:** é onde os controles do plano (14.4) atuam - responsável obrigatório na operação, validação de papel no servidor, faixa terapêutica, versionamento e reautenticação reduzem diretamente a probabilidade.
- **Detect:** alteração de dosagem fora de faixa ou sem segunda assinatura deve gerar alerta - é exatamente a regra 2 do roteiro de detecção previsto para a Etapa 6, que observa este risco.
- **Respond:** detectada uma alteração suspeita, a prescrição deve ser bloqueada para administração e farmácia/chefia notificadas antes do próximo horário de medicação - a janela de resposta útil é o intervalo entre a alteração e a administração.
- **Por que não Identify e Recover:** a identificação do ativo e da vulnerabilidade já está feita na Etapa 1 (T02/CA02); e não existe recuperação de sistema para dano clínico já administrado - o versionamento restaura o dado, não o paciente. É por isso que o tratamento de R02 concentra tudo **antes** da administração.

#### R05 (@PPrauchner)

- **Identify:** é a função de entrada deste risco, e o único da trilha em que ela é
  marcada. Antes de proteger, é preciso saber **quanto** o SGBD central suporta e **quem**
  consome o quê: não existe hoje um levantamento de capacidade, de conexões por
  microsserviço nem do inventário de dependências externas - e uma delas, o «system»
  Convênio (RF06), é caminho crítico do atendimento sem estar reconhecida como tal.
  Cota e *rate limiting* só podem ser calibrados depois desse levantamento.
- **Protect:** onde atuam os controles que reduzem a probabilidade da saturação - cota de
  conexões por microsserviço, *rate limiting* no API Gateway, réplica de leitura para
  relatórios e *timeout* com modo degradado na chamada ao Convênio. É também o que separa
  a carga administrativa (RF25) da carga assistencial, hoje indistinguíveis para o banco.
- **Detect:** a saturação tem indicador antecedente, ao contrário das demais ameaças da
  trilha: o uso do pool de conexões cresce antes de o serviço cair. Alertar acima de um
  limiar transforma um incidente em uma janela de intervenção.
- **Respond:** detectada a saturação, a resposta é a degradação controlada - suspender
  relatórios e exportações e preservar prontuário, prescrição e mapa de leitos. A decisão
  de **o que derrubar primeiro** precisa estar tomada antes, não durante a queda.
- **Recover:** é o núcleo do tratamento aqui, e **R05 é o único risco desta trilha em que
  Recover é legítimo** - nos demais, o dano já consumado não se restaura. Aqui restaurar
  o serviço *é* tratar o risco, e o RNF03 exige exatamente isso ao pedir recuperação
  automática de falhas. A recuperação inclui a reintegração dos registros feitos no papel
  durante a janela, que é o que impede o encadeamento com T03 (Repudiation).
- **Por que não Govern:** a política já existe e é explícita - RNF01, RNF02 e RNF03
  determinam volume simultâneo, escalabilidade e operação 24h/7d. O que falta não é
  decisão nem dono: é contrapartida de projeto. Marcar Govern aqui sugeriria uma lacuna de
  governança que a documentação do SIGH não tem; a lacuna é arquitetural, e é como decisão
  de arquitetura que ela será tratada na Etapa 3.

#### R06 (@PPrauchner)

- **Govern:** é a função de entrada deste risco. Hoje não existe política dizendo quem
  pode alterar `nivelAcesso`, sob qual aprovação e com qual registro - o campo é apenas
  mais um atributo do cadastro. As regras de autorização do SIGH vivem como texto de caso
  de uso (UC03, UC10) e não têm dono; enquanto isso não mudar, qualquer controle técnico
  fica sem critério para decidir o que recusar.
- **Protect:** onde atua o controle central do plano (14.4) - revalidação de autorização
  no servidor, com o perfil vindo da sessão autenticada e nunca do corpo da requisição.
  É o que fecha exatamente a lacuna que o passo 3 do CA05 explora, e é o que retira do
  Desktop Cliente, controlado pelo usuário, a decisão de autorização.
- **Detect:** hoje a elevação é invisível porque **não há anomalia a observar** - a
  identidade é legítima. A detecção precisa, portanto, ser do **evento**, não do
  comportamento: toda alteração de `nivelAcesso` registrada em trilha imutável e alertada
  no momento em que ocorre. É a regra 3 prevista para o roteiro da Etapa 6.
- **Respond:** detectada uma elevação não aprovada, a resposta é reverter o campo,
  encerrar as sessões do titular e - por causa do encadeamento com T01 - tratar como
  comprometidas as credenciais alcançadas durante o período, forçando troca. A janela útil
  vai da elevação ao primeiro uso das credenciais obtidas.
- **Por que não Identify:** o ativo, a vulnerabilidade e o caminho de exploração já estão
  identificados na Etapa 1 (T06 e CA05), com o componente e o campo nomeados. Repetir a
  função aqui seria marcá-la sem resultado esperado novo.
- **Por que não Recover:** não há o que restaurar. Reverter o `nivelAcesso` é escrever um
  valor de volta em um campo - operação trivial que não repara nada do que foi feito com
  o privilégio. O que de fato precisaria de recuperação são as credenciais expostas, e
  essa recuperação pertence a R01 (substituição de senhas e armazenamento com hash), não a
  R06. Assumir Recover aqui daria a impressão falsa de que a elevação é reversível em seus
  efeitos, quando o contrário é o ponto: **em R06 tudo tem de ser feito antes**.

#### R03 (@lorenzoficher)

- **Govern:** o UC10 diz que somente médicos registram óbito, e o Tópico 9 diz que o
  registro de eventos críticos está fora do escopo. São duas decisões de governança em
  sentidos opostos, e nenhuma delas tem dono. Antes de qualquer controle técnico é preciso
  definir quem pode registrar óbito, quem responde pela trilha de auditoria, por quanto
  tempo ela é retida e quem tem permissão para consultá-la - uma trilha que qualquer perfil
  possa ler recria, na privacidade, o problema que resolve na responsabilização.
- **Protect:** é o núcleo do tratamento, e com um sentido diferente do que tem nos demais
  riscos. Em R01 e R06, proteger é **impedir** um acesso; aqui é **produzir a prova** no
  instante do ato - autoria vinda da sessão autenticada, carimbo de tempo do servidor e
  trilha somente de acréscimo. Nenhum desses controles impede o registro de um óbito
  indevido; todos tornam impossível que ele seja anônimo.
- **Detect:** hoje não há nada a observar, porque nada é gravado. Uma vez existindo a
  trilha, a detecção passa a ter objeto: registro com data e hora informadas muito
  anteriores ao carimbo do servidor, registro fora da escala de trabalho do médico, ou
  falha na gravação da própria trilha. Note-se que **R03 não tem regra dedicada** entre as
  três do roteiro da Etapa 6 - as regras cobrem R01, R02 e R06 -, de modo que essa
  detecção é entregue como controle deste plano, com evidência própria, e não como
  dependência daquela etapa.
- **Respond:** contestada a autoria, a resposta é um procedimento de apuração que consulta
  a trilha, preserva a evidência antes de qualquer correção e comunica o resultado ao
  médico envolvido e à direção clínica. Sem esse procedimento definido, a existência da
  trilha não se converte em capacidade de resposta - alguém precisa saber onde olhar e o
  que fazer com o que encontrar.
- **Recover:** marcado, e por uma razão que **nenhum outro risco deste registro tem**: R03
  é o único cujo efeito atravessou a fronteira da instituição antes da dúvida aparecer. A
  recuperação aqui é concreta e específica - reabrir o prontuário que o registro encerrou e
  **retificar o dado já transmitido ao «system» Sistema Governamental**, o que exige saber
  o que foi enviado e quando, informação que hoje não existe. O limite precisa ficar
  explícito: o que se recupera é o registro e o seu efeito externo, nunca a prova que não
  foi capturada. Um óbito registrado por engano pode ser corrigido; a impossibilidade de
  saber quem o registrou, não.
- **Por que não Identify:** o ativo, a operação e a lacuna já estão nomeados na Etapa 1 -
  `Obito.registrarObito(data, hora)` em T03, o fluxo completo em CA03 e a rastreabilidade
  como ativo **não modelado** na seção 8.3.2. O tratamento de R03 não depende de nenhum
  levantamento adicional, diferente de R05, em que a cota de conexões só pode ser
  calibrada depois de medir a capacidade do SGBD. Marcar Identify aqui seria preencher a
  tabela sem resultado esperado novo.

> **Pendente:** mapeamento e justificativa de R04, pelo respectivo responsável (evitar marcar todas as funções sem justificar).

## 14.4 Plano de tratamento

| Risco | Estratégia | Controles propostos | Funções relacionadas | Responsáveis | Evidências e verificação |
| --- | --- | --- | --- | --- | --- |
| R01 | Reduzir | **R01-C1** - armazenar `senhaLogin` com hash e salt por algoritmo próprio para senhas (Argon2id, ou bcrypt com custo ≥ 12), migrando as senhas existentes na próxima autenticação de cada profissional; **R01-C2** - autenticação multifator no login e reautenticação antes de operações sensíveis (prescrever, autorizar alta, registrar óbito); **R01-C3** - bloqueio temporário da conta após 5 tentativas malsucedidas em 15 minutos, com alerta gerado; **R01-C4** - encerramento automático da sessão após 10 minutos de inatividade, tratando o terminal compartilhado como o padrão e não como exceção; **R01-C5** - política de senha com comprimento mínimo, proibição de reuso e verificação contra listas públicas de senhas vazadas | Govern, Protect, Detect, Respond, Recover | @lilydias24 | Amostra da tabela `Funcionario` exibindo apenas hash, sem senha em claro; testes com caso válido e caso malicioso da prática de armazenamento seguro de senhas (Etapa 4); registro de configuração do MFA e da política de bloqueio; log de tentativas malsucedidas e de bloqueios efetivados; alerta da regra 1 do roteiro de detecção (Etapa 6) disparando em cenário simulado |
| R02 | Reduzir | **R02-C1** - a operação de alteração passa a registrar o responsável obtido da sessão autenticada no servidor (nunca informado pelo cliente), cumprindo a regra do UC03; **R02-C2** - validação de papel no servidor: apenas médico, e médico vinculado ao paciente; **R02-C3** - validação de faixa terapêutica por medicamento, com bloqueio de valores fora da faixa; **R02-C4** - versionamento da prescrição em trilha imutável (valor anterior, novo valor, autor, data/hora); **R02-C5** - segunda assinatura de outro profissional + reautenticação para alterar prescrição ativa | Govern, Protect, Detect, Respond | @ARTHUR9011 | Testes com caso válido e caso malicioso (Etapa 4); log de auditoria consultável com autor e valor anterior; alerta da regra 2 do roteiro de detecção (Etapa 6) disparando em alteração fora de faixa ou sem segunda assinatura |
| R03 | Reduzir | **R03-C1** - `registrarObito` passa a obter o responsável da **sessão autenticada no servidor**, nunca de parâmetro enviado pelo cliente, com validação de papel médico e de vínculo com a internação do paciente, convertendo a regra textual do UC10 em verificação executada; **R03-C2** - separação de dois campos hoje confundidos em um: `dataHoraRegistro`, carimbada pelo servidor com relógio sincronizado e não editável, e `dataHoraObito`, informada clinicamente - divergência entre as duas acima de um limiar definido exige justificativa registrada; **R03-C3** - trilha de auditoria **somente de acréscimo** para o registro de óbito (autor, sessão, terminal, carimbo do servidor, causa CID, valor informado e identificador de correlação), com permissão de escrita segregada da permissão de operar o SIGH, de modo que nenhum perfil da aplicação possa alterar ou excluir uma entrada; **R03-C4** - registro probatório da transmissão ao «system» Sistema Governamental - o que foi enviado, quando e qual o retorno - e procedimento documentado de retificação, suprindo a integração sem requisito funcional apontada na seção 8.2; **R03-C5** - reautenticação e confirmação por uma segunda identidade autorizada antes da publicação, justificada pelo fato de a operação ser irreversível e encerrar o prontuário; a gravação da trilha é condição da operação, e sua falha reverte o registro em vez de produzir um óbito sem rastro | Govern, Protect, Detect, Respond, Recover | @lorenzoficher | Consulta à trilha exibindo autor, sessão, terminal e carimbo do servidor para um óbito de teste; teste que envia responsável e data/hora forjados no corpo da requisição e comprova que a trilha registrou a identidade da sessão e o relógio do servidor; tentativa de alterar e de excluir uma entrada da trilha a partir de um perfil da aplicação, ambas recusadas; teste de registro com `dataHoraObito` retroativa comprovando divergência sinalizada e justificativa exigida; simulação de falha na gravação da trilha comprovando que nenhum `Obito` é persistido; e execução do procedimento de retificação, reabrindo o prontuário e registrando a comunicação ao Sistema Governamental |
| R04 | | | | | |
| R05 | Reduzir | **R05-C1** - pool de conexões do SGBD com **cota por microsserviço**, de modo que o Serviço de Atendimento Médico (onde reside o RF25) não consuma as conexões de que o Serviço de Internação precisa; **R05-C2** - *rate limiting* no API Gateway por sessão e por endpoint, aplicado aos endpoints de relatório e de consulta de prontuário, incluindo o `buscarPacientePorIdentificador(idPaciente)`; **R05-C3** - réplica de leitura dedicada a relatórios, listagens administrativas e exportações, retirando essa carga da instância que atende a operação assistencial; **R05-C4** - *timeout* e modo degradado na chamada ao «system» Convênio (RF06): o atendimento é registrado e a validação de cobertura fica pendente para conferência posterior, em vez de bloquear o fluxo; **R05-C5** - alerta de saturação quando o uso do pool passar de 80%, com regra de degradação previamente definida que suspende relatórios e exportações e preserva prontuário, prescrição e mapa de leitos | Identify, Protect, Detect, Respond, Recover | @PPrauchner | Teste de carga simulando o fechamento de faturamento concorrente com o pico assistencial, verificando que os módulos assistenciais continuam respondendo; painel de conexões por microsserviço mostrando a cota em vigor; teste de indisponibilidade do Convênio confirmando que o atendimento prossegue em modo degradado; registro do alerta de 80% disparando antes da queda no teste de carga |
| R06 | Reduzir | **R06-C1** - revalidação de autorização **no servidor**, no Serviço de Funcionários: o perfil que decide vem da sessão autenticada e o `nivelAcesso` recebido no corpo da requisição é descartado antes de qualquer validação; alteração de perfil solicitada por quem não é Diretor retorna HTTP 403; **R06-C2** - `nivelAcesso` imutável pelo próprio titular: a mudança só ocorre por fluxo de aprovação de nível superior, nunca no salvamento do próprio cadastro; **R06-C3** - trilha de auditoria imutável de toda alteração de perfil, com autor, valor anterior, valor novo e data/hora carimbados pelo servidor - suprindo a lacuna que o Tópico 9 deixou aberta; **R06-C4** - alerta automático ao Diretor e à Segurança da Informação a cada elevação de perfil, no momento em que ela ocorre | Govern, Protect, Detect, Respond | @PPrauchner | Os dois testes da Etapa 4 (caso válido de promoção por sessão Diretor e caso não autorizado por sessão Supervisor, este esperando 403 e o campo inalterado); trilha de auditoria consultável exibindo autor e valor anterior de cada alteração; regra 3 do roteiro de detecção (Etapa 6) disparando em uma elevação simulada |

> **Observação para a ordem de implementação (14.5), @mariasanchez0’s:** o **R06-C1** é o
> controle da trilha que **reduz mais de um risco ao mesmo tempo**. A checagem que ele
> institui - papel obtido da sessão no servidor, e não do que o cliente enviou - é a mesma
> de que o **R02-C2** depende para garantir que só médicos alterem tratamentos. Como 14.5
> lista "controles que reduzem vários riscos" entre os critérios de ordenação, ele é
> candidato às primeiras posições, ao lado do controle de hash e salt apontado pela
> @lilydias24.

## 14.5 Ordem inicial de implementação

> Seção compilada pelo **@mariasanchez0’s**, com justificativa - depende dos controles de todos os riscos.

*(Pendente. Observação de @lilydias24 para a compilação: **R01-C1** - hash e salt - não depende de nenhum outro item do plano e é pré-requisito dos demais controles de R01, o que o torna candidato natural às primeiras posições. Vale considerar também que R01 é habilitador de R02, R03 e R04, de modo que seus controles reduzem a probabilidade efetiva desses riscos mesmo antes de os controles próprios deles serem implantados.)*

## 14.6 Estimativa do risco residual

| Risco | Nível inicial | Nível residual esperado | Condição para aceitar o residual |
| --- | --- | --- | --- |
| R01 | Crítico (16) | Alto (8) | Controles R01-C1 a R01-C5 comprovadamente operantes (evidências de 14.4); regra 1 de detecção da Etapa 6 ativa e monitorada; revisão trimestral dos logs de autenticação e de bloqueio |
| R02 | Crítico (12) | Médio (4) | Controles R02-C1 a R02-C5 comprovadamente operantes (evidências de 14.4); alerta da Etapa 6 ativo; revisão da classificação se a segunda assinatura for flexibilizada na rotina |
| R03 | Crítico (12) | Médio (6) | Controles R03-C1 a R03-C5 comprovadamente operantes (evidências de 14.4), com a trilha consultável e a segregação de escrita demonstrada; procedimento de retificação junto ao Sistema Governamental documentado e testado; tratamento de R01 em curso, porque a força da autoria não supera a da autenticação que a sustenta; revisão da estimativa se o registro em contingência durante indisponibilidade (encadeamento com R05) deixar de ser exceção |
| R04 | | | |
| R05 | Crítico (12) | Médio (6) | Controles R05-C1 a R05-C5 comprovadamente operantes (evidências de 14.4), com o teste de carga executado sobre a cota e a réplica já em produção; alerta de 80% ativo e com destinatário definido; revisão da estimativa se o recorte incorporar novos módulos, uma nova unidade hospitalar (RNF02) ou uma nova integração externa síncrona |
| R06 | Alto (8) | Médio (4) | Controles R06-C1 a R06-C4 comprovadamente operantes, com os dois testes da Etapa 4 passando e a trilha de auditoria consultável; regra 3 da Etapa 6 ativa e com destinatário definido; revisão da estimativa se o fluxo de aprovação de R06-C2 ganhar exceção de rotina ou se o tratamento de R01 (armazenamento de `senhaLogin`) não avançar |

### Justificativa do residual de R01 (@lilydias24)

**Probabilidade (4 → 2).** Cada controle fecha um dos caminhos que hoje estão abertos: com hash e salt (R01-C1), um vazamento do banco deixa de entregar credenciais utilizáveis; com MFA (R01-C2), a senha isolada passa a ser insuficiente; com bloqueio por tentativas (R01-C3), a força bruta interna deixa de ser viável; com expiração de sessão (R01-C4), o terminal aberto entre plantões deixa de ser porta de entrada; e com a política de senha (R01-C5), o reuso de credencial vazada deixa de valer. Resta o caminho que nenhum desses controles fecha - **phishing capaz de capturar também o segundo fator, ou um dispositivo de MFA comprometido** -, o que corresponde a "possível, mas dependente de uma vulnerabilidade ou condição específica" na escala 13.1.

Não desce a 1, diferente do residual de R02, e a comparação explica por quê: em R02 a barreira final é **outra pessoa** - a segunda assinatura exige o conluio de dois profissionais. Em R01, o segundo fator continua sendo algo que o mesmo titular carrega, e por isso pode ser obtido pela mesma manobra que obtém a senha. Um segundo fator não é uma segunda pessoa.

**Impacto (4, inalterado).** Os cinco controles são preventivos e de detecção: reduzem a chance de o acesso acontecer, não o dano de um acesso que se concretize. Quem entra na conta continua alcançando o prontuário completo e as operações irreversíveis. Reduzir o impacto exigiria mudanças de outra natureza - segregação mais fina de permissões dentro do próprio perfil médico e segunda assinatura obrigatória em operações irreversíveis -, que pertencem ao requisito RS01 e às decisões de arquitetura da Etapa 3.

**Condição para aceitar o residual Alto:** manter a regra 1 de detecção da Etapa 6 ativa e efetivamente monitorada, revisar trimestralmente os logs de autenticação e de bloqueio, e reavaliar a classificação caso a segunda assinatura em operações irreversíveis venha a ser implementada - é a única mudança capaz de tirar este risco do impacto 4.

### Justificativa do residual de R02 (@ARTHUR9011)

**Probabilidade (3 → 1).** Com os controles R02-C1 a R02-C5, uma alteração indevida que chegue à administração passa a exigir condições incomuns: uma conta de médico vinculada ao paciente, reautenticada, um valor dentro da faixa terapêutica e a confirmação de um segundo profissional - na prática, o conluio de dois profissionais ou o comprometimento simultâneo de duas contas (cenário que remete ao residual de R01).

**Impacto (4, inalterado).** Se ainda assim o evento ocorrer, o dano continua físico e potencialmente fatal - nenhum controle reduz a gravidade clínica de uma dose errada administrada. O que muda é a visibilidade: com autor e valor anterior versionados, a adulteração deixa de ser indistinguível de uma prescrição legítima, mas não deixa de ser dano.

**Condição para aceitar o residual Médio:** os controles precisam estar comprovadamente operantes (coluna de evidências de 14.4), e a classificação deve ser refeita se a segunda assinatura ganhar exceções de rotina (ex.: emergências) ou se o alerta de detecção da Etapa 6 ficar inativo.

### Justificativa do residual de R03 (@lorenzoficher)

**Probabilidade (4 → 2).** É a maior queda de probabilidade do registro, e a razão é
estrutural: em R03 o valor 4 não vinha da capacidade de um atacante, e sim de um controle
que simplesmente **não existe**. Com a autoria obtida da sessão (R03-C1), o carimbo de
tempo do servidor (R03-C2) e a trilha somente de acréscimo com escrita segregada
(R03-C3), o registro não atribuível deixa de ser o resultado padrão da operação e passa a
exigir condição específica - o comprometimento de uma conta de médico ou uma falha do
próprio mecanismo de auditoria, que por R03-C5 reverte a operação em vez de deixá-la sem
rastro. É a definição do valor 2 em 13.1.

Não cai a 1, e são duas as razões, ambas permanentes. A primeira é que **o momento clínico
do óbito continua sendo informado por uma pessoa**: o servidor carimba quando o registro
foi feito, não quando a morte ocorreu, e essa é uma limitação da realidade, não do
projeto - a divergência justificada de R03-C2 reduz o espaço para um carimbo clínico
conveniente, mas não o fecha. A segunda é que a trilha prova **qual sessão** registrou, e
não qual pessoa estava no teclado: enquanto `senhaLogin` permanecer em texto simples e sem
MFA, a autoria vale exatamente o que valer a autenticação que a sustenta. É a mesma
dependência que o @PPrauchner registrou no residual de R06, e vale aqui com igual força:
**o residual de R03 pressupõe o tratamento de R01 em curso.**

**Impacto (3, inalterado).** Os cinco controles atuam sobre a existência da prova, não
sobre a gravidade do que acontece quando ela falta. Se o evento ainda assim ocorrer, o
registro continua encerrando o prontuário, continua produzindo efeito legal e continua
seguindo ao Sistema Governamental - e o médico titular continua sem meio de se defender.
O que R03-C4 acrescenta é a possibilidade de **retificar** o efeito externo, o que reduz a
duração do prejuízo, mas não a sua natureza. Reduzir o impacto de R03 exigiria mudar quem
suporta a consequência de um óbito mal registrado, e isso não é matéria de controle
técnico.

**Condição para aceitar o residual Médio:** além das evidências de 14.4, três condições
específicas. A trilha precisa ter destinatário e leitor definidos - uma trilha que ninguém
consulta é custo de armazenamento, não controle. O procedimento de retificação do R03-C4
precisa ter sido executado ao menos uma vez em teste, porque é o único controle do plano
cuja falha só apareceria durante um incidente real. E a estimativa deve ser refeita se o
registro em contingência durante indisponibilidade deixar de ser exceção: como observou o
@PPrauchner em R05, a janela de queda fabrica registros digitados depois com data e hora
informadas por quem digita, e um fluxo de contingência frequente reintroduz a probabilidade
4 por uma porta que os controles de R03 não fecham.

### Justificativa do residual de R05 (@PPrauchner)

**Probabilidade (3 → 2).** Com a cota por microsserviço (R05-C1), o *rate limiting* no
Gateway (R05-C2) e a réplica de leitura (R05-C3), o cenário mais provável do risco - a
carga administrativa do fechamento de faturamento derrubando o módulo assistencial -
deixa de existir por construção: a origem da carga volta a importar para o efeito. O que
resta é o evento que depende de condição específica, isto é, volume acima do que a cota
foi dimensionada para absorver ou falha na própria instância do banco. Não cai a 1 porque
o SGBD continua sendo **um só**: a réplica de leitura não elimina o ponto único de
escrita, e essa é uma mudança de arquitetura que a Etapa 3 discute, não um controle desta
etapa.

**Impacto (4 → 3).** Este é o único risco da trilha em que o impacto **também** cai, e a
diferença merece ser dita, porque contraria o padrão dos demais residuais deste documento
(em R02 e em R06 o impacto permanece 4). A razão é que o dano de R05 é de **alcance e
duração**, não físico e irreversível: com o modo degradado do R05-C4 e a regra de
priorização do R05-C5, a queda deixa de ser simultânea em todos os módulos e passa a
atingir primeiro relatórios, exportações e validação de convênio - o prontuário, a
prescrição em curso e o mapa de leitos continuam disponíveis. Sai da faixa "afeta muitos
usuários e compromete operações críticas" para "interrupção limitada, com possibilidade
de recuperação". Não cai a 2 porque a indisponibilidade total continua possível na falha
do banco, e a janela ainda produz registros digitados a posteriori.

**Condição para aceitar o residual Médio:** os cinco controles precisam estar
comprovadamente operantes segundo a coluna de evidências de 14.4 - com destaque para o
teste de carga, que é o único que demonstra a cota funcionando sob a condição real. A
estimativa deve ser refeita se o recorte crescer, se o RNF02 for exercido com uma nova
unidade hospitalar ou se qualquer nova integração externa entrar de forma síncrona no
fluxo de atendimento, repetindo o problema que o R05-C4 corrige no Convênio.

### Justificativa do residual de R06 (@PPrauchner)

**Probabilidade (2 → 1).** Com a revalidação no servidor (R06-C1) e a imutabilidade do
campo pelo próprio titular (R06-C2), a lacuna que a probabilidade 2 pressupunha - a
validação existir apenas na interface - deixa de existir, e o vetor do CA05 passa a
retornar 403. A elevação passa a exigir condições incomuns: o comprometimento de uma
conta de Diretor, o conluio de quem aprova, ou uma falha no próprio servidor de
autorização. É exatamente a definição do valor 1 em 13.1. Não chega a zero porque nenhum
controle proposto elimina o caminho legítimo da promoção - ele apenas passa a ter dono e
registro.

**Impacto (4, inalterado).** Se a elevação ainda assim ocorrer, o alcance é o mesmo: o
`nivelAcesso` continua sendo o único mecanismo de autorização do modelo, e as credenciais
de todos os perfis continuam armazenadas em texto simples enquanto o tratamento de R01
não estiver implementado. Nenhum dos quatro controles reduz a gravidade do que um Diretor
indevido consegue fazer - eles reduzem a chance de alguém chegar lá e o tempo até que se
perceba. O que muda é a visibilidade: com R06-C3 e R06-C4, a elevação deixa de ser
silenciosa e permanente, e passa a ser um evento datado, com autor e valor anterior. Isso
encurta a janela de exploração, mas não o dano por unidade de tempo. **A redução do
impacto de R06 depende de R01, não de R06** - é uma dependência a levar para a
priorização de 13.6.

**Condição para aceitar o residual Médio:** os dois testes da Etapa 4 precisam estar
passando, a trilha de auditoria precisa ser consultável e a regra 3 da Etapa 6 precisa
estar ativa e endereçada a alguém - um alerta sem destinatário não é controle. A
estimativa deve ser refeita se o fluxo de aprovação do R06-C2 ganhar exceções de rotina
(por exemplo, promoções emergenciais fora do fluxo), ou se o armazenamento de
`senhaLogin` continuar em texto simples após a implementação dos controles de R01 - nesse
caso o impacto 4 se mantém indefinidamente, e é honesto registrar que o residual Médio
pressupõe aquele tratamento em curso.

## 15. Considerações finais (Etapa 2)

> Rascunho de responsabilidade do **@PPrauchner**, com revisão de todos.

> **Rascunho provisório.** Esta seção sintetiza os **quatro riscos registrados até
> aqui** - R01, R02, R05 e R06. **R03 (Repudiation) e R04 (Information Disclosure)
> ainda não foram registrados em 13.4**, e a priorização geral (13.6) e a ordem de
> implementação (14.5) ainda não foram compiladas. Tudo o que segue vale sobre esse
> recorte parcial e deve ser revisto quando as duas trilhas pendentes entrarem no
> documento - inclusive as afirmações sobre quais riscos ocupam o topo e quais
> funções do NIST predominam, que podem mudar de ordem.

**Riscos mais importantes.** Entre os quatro registrados, três são o núcleo da
atenção, por razões que não se repetem. **R01 (16, Crítico)** é o de maior pontuação
da escala e o único que combina a probabilidade máxima com o impacto máximo: com
`senhaLogin` em texto simples na classe `Funcionario`, fator único e sem bloqueio
por tentativas, o obstáculo entre o atacante e a conta é saber a senha - e as
justificativas de 13.5 mostram quatro caminhos baratos para obtê-la. **R02 (12,
Crítico)** é o único cujo dano não é informacional: entre a `dosagemMedicamento`
alterada e o prejuízo existe apenas a enfermagem cumprindo o que a tela mostra, e o
efeito se torna irreversível no instante da administração. **R05 (12, Crítico)** é o
único que **não exige ator malicioso** - o fechamento de faturamento do RF25,
rodando no Serviço de Atendimento Médico por não existir microsserviço Financeiro,
disputa as conexões do mesmo SGBD de que o Serviço de Internação precisa; o uso
legítimo já produz a condição do risco. **R06 (8, Alto)** fica abaixo na pontuação,
mas é registrado aqui porque a fórmula não o mede bem: ele é o risco que multiplica
os outros, e 13.5 já argumenta que ele pede urgência acima do que um 8 sugere.

**Razões que determinaram a priorização.** Três critérios ordenaram os quatro
riscos, e nenhum deles é a pontuação isolada. O primeiro é o **encadeamento**: R01 e
R06 são riscos **habilitadores** - uma conta assumida ou um perfil promovido
destravam R02, R03 e R04, e os casos de abuso CA02, CA03 e CA04 citam nominalmente a
conta assumida como caminho de entrada alternativo. Tratá-los reduz a probabilidade
efetiva de riscos cujos próprios controles ainda nem foram implantados. O segundo é
a **irreversibilidade**: onde o dano é físico (R02) ou já consumado (R06), não
existe tratamento posterior, e todo o esforço tem de ser deslocado para antes do
evento; onde há restauração possível (R05), a urgência é alta mas a janela de
correção existe. O terceiro é a **assimetria entre probabilidade e impacto**,
observada por 13.7 e confirmada pelos quatro registros: a probabilidade vem quase
sempre de controle ausente - fator único, validação apenas na interface, ausência de
cota de conexões -, enquanto o impacto vem da natureza do ativo, que é prontuário,
prescrição e credencial. Como o impacto quase não se reduz por engenharia (três dos
quatro residuais de 14.6 mantêm o impacto 4), a priorização recai sobre os riscos
onde a probabilidade ainda pode cair muito.

**Estratégias de tratamento predominantes.** Os quatro riscos registrados escolheram
**Reduzir**, e o que interessa não é a unanimidade, e sim o fato de as três outras
estratégias serem descartadas pelas **mesmas razões estruturais** em todos eles.
*Evitar* está fora porque a função de origem é essencial ao SIGH: não se elimina a
autenticação de profissionais (R01), a alteração de prescrição (R02), o acesso
concorrente dos módulos ao banco (R05) nem a graduação de acesso do `Administrador`
(R06) - no caso de R06, retirar o `nivelAcesso` pioraria a situação, porque ele é o
único mecanismo de autorização que o modelo tem. *Compartilhar* está fora porque a
consequência é clínica e indelegável: um provedor de identidade externo assume a
implementação da autenticação, não a responsabilidade do hospital sobre o prontuário,
e o caso de R05 é ainda mais eloquente - a parcela já compartilhada, a validação de
cobertura pelo «system» Convênio (RF06), hoje **amplia** o risco por ser síncrona e
sem modo degradado. *Aceitar* está fora porque três dos quatro riscos são Críticos e
o quarto expõe as credenciais de todos os perfis. A conclusão que o grupo tira daí é
que o SIGH não tem risco de sobra a negociar nesta etapa: todo o tratamento é
engenharia de redução, e a discussão real não é *se* reduzir, é *em que ordem* - o
que remete a 14.5.

**Funções do NIST mais relevantes para o sistema.** **Protect** e **Detect** aparecem
nos quatro riscos registrados, e a razão é a mesma que sustenta a estratégia
Reduzir: os controles de 14.4 atuam sobre condições que o modelo do SIGH deixou
abertas. **Govern** aparece em três (R01, R02 e R06) e a exceção é informativa - R05
não a marca porque a política já existe e é explícita nos RNF01, RNF02 e RNF03; ali
o que falta não é decisão nem dono, é contrapartida de projeto, e por isso a lacuna
é arquitetural e migra para a Etapa 3. Mas a assimetria mais reveladora é a de
**Recover**, marcada apenas em R01 e R05. Nos riscos de dano físico ou informacional
já consumado - a dose administrada em R02, o privilégio já exercido em R06 - não
existe o que restaurar: reverter o `nivelAcesso` é escrever um valor de volta em um
campo, operação que não repara nada do que foi feito com ele. Isso empurra todo o
tratamento desses dois riscos para antes do evento e é o que explica por que
**Identify** só aparece em R05, o único risco cujo tratamento ainda depende de um
levantamento que não foi feito - capacidade do SGBD central, consumo por
microsserviço e inventário de dependências externas, sem o qual cota e *rate
limiting* não têm como ser calibrados.

**Controles considerados essenciais.** Três se destacam entre os do plano de 14.4.
O **R01-C1** - armazenar `senhaLogin` com hash e salt - é essencial por ser
pré-requisito: enquanto as senhas estiverem em texto simples, o impacto de R06
permanece 4 mesmo com todos os controles próprios de R06 implantados, como a
justificativa do residual de R06 registra. O **R06-C1** - revalidação de autorização
no servidor, com o perfil vindo da sessão autenticada e o `nivelAcesso` do corpo da
requisição descartado - é essencial por alcance: é a mesma checagem de que o
**R02-C2** depende para garantir que só médicos vinculados alterem tratamentos, o
que faz dele o único controle da análise que reduz dois riscos com uma implementação
só. E a **trilha de auditoria imutável** é essencial por recorrência: ela reaparece
como R01-C3, R02-C4 e R06-C3 sob nomes diferentes, supre a lacuna que o Tópico 9
deixou aberta ao excluir do escopo o registro de eventos críticos de acesso indevido,
e é o que a §8.7 da Etapa 1 chamou de "ativo faltante mais caro do recorte". O que
os três têm em comum é serem controles de **base**, não de cobertura: cada um habilita
a eficácia de outros, e é por isso que a compilação de 14.5 deve considerá-los antes
dos demais.

**Principais dificuldades encontradas.** A primeira foi **quantificar sem histórico
operacional**: as escalas de 13.1 e 13.2 pedem probabilidade e impacto, mas o SIGH
não tem incidentes registrados nem base de comparação, de modo que cada valor teve de
ser ancorado em uma condição verificável do próprio modelo - um campo, uma assinatura
de operação, um requisito não funcional -, e não em intuição. A segunda foi que **a
pontuação não ordena bem**: R06 vale 8 e R02 vale 12, mas R06 desbloqueia T01, T02 e
T03 de uma vez, e essa propriedade não cabe em nenhuma das duas dimensões. O grupo
optou por manter a pontuação fiel à escala publicada e levar as agravantes para a
priorização de 13.6, em vez de inflar números - decisão que o próprio enunciado
autoriza em 13.3 ao advertir que dois riscos de mesma pontuação podem receber
prioridades diferentes. A terceira foi **não confundir os quatro termos**: várias
linhas de 13.4 nasceram descrevendo a vulnerabilidade no lugar do evento de risco, e
a separação entre `senhaLogin` em texto simples (vulnerabilidade), assumir a
identidade do profissional (ataque), Spoofing (ameaça) e a exposição resultante
(risco) precisou ser refeita explicitamente. A quarta foi **sincronizar seções
compartilhadas**: 13.4, 13.5, 14.1, 14.3, 14.4 e 14.6 são tabelas de linha por
integrante, e cada um edita a mesma região do arquivo - a convenção de uma branch por
tarefa com Pull Request foi adotada durante esta etapa justamente por isso.

**Limitações da avaliação.** São quatro, e todas restringem o alcance do que está
escrito acima. **(1) O SIGH não está implementado.** A análise foi lida do modelo, e
não do código: só se pode afirmar que o modelo **não especifica** determinada
verificação, nunca que o sistema não a faz. R02 e R06 dependem inteiramente da
hipótese de que a validação existe apenas na interface - plausível diante do modelo,
não verificável nesta etapa. **(2) Os residuais de 14.6 são estimativas.** O
enunciado é explícito ao proibir afirmar que o risco foi reduzido porque um controle
foi proposto; a redução só se confirma após implementação, testes e evidências, e a
coluna "condição para aceitar o residual" existe exatamente para tornar esse
pressuposto verificável. **(3) Dois riscos estão fora da síntese.** R03 e R04 não
foram registrados, e ambos são consequência direta dos habilitadores já analisados -
R05 fabrica a condição de R03 ao produzir registros digitados depois da janela de
indisponibilidade, e R06 alcança o cadastro completo que interessa a R04. É provável
que a entrada deles reforce a priorização atual, mas isso é hipótese, não resultado.
**(4) As escalas de 1 a 4 comprimem diferenças reais.** Quatro faixas de
probabilidade e quatro de impacto não distinguem riscos de naturezas muito distintas
que caem na mesma célula, e o caso de R06 já mostra o efeito. A avaliação, além
disso, cobre apenas o recorte de cinco módulos, não o SIGH inteiro.

**Pontos que precisarão ser detalhados nas próximas etapas.** A **Etapa 3** recebe as
duas lacunas que não são controle, e sim arquitetura: o **SGBD único** de R05 - a
réplica de leitura do R05-C3 tira carga da instância, mas não elimina o ponto único
de escrita - e a segregação de permissões dentro do próprio perfil médico, apontada
pelo residual de R01 como a única mudança capaz de tirar aquele risco do impacto 4. A
**Etapa 4** recebe os testes com caso válido e caso malicioso já nomeados na coluna de
evidências de 14.4: o armazenamento com hash e salt do R01-C1, e os dois de R06 -
promoção legítima por sessão de Diretor, e tentativa por sessão de Supervisor
esperando HTTP 403 com o campo inalterado. A **Etapa 5**, liderada pelo Integrante 5,
recebe a verificação prática desses controles e a produção das evidências que 14.6
exige como condição para aceitar cada residual. A **Etapa 6** recebe as três regras de
detecção já citadas nominalmente em 14.3 e 14.4 - tentativas de autenticação (R01),
alteração de dosagem fora de faixa ou sem segunda assinatura (R02) e alteração de
`nivelAcesso` (R06) -, às quais deve somar-se o alerta de saturação de 80% do pool de
conexões do R05-C5, o único indicador **antecedente** da análise: ele avisa antes da
queda, e não depois. E a **Etapa 7** recebe o encaixe desses controles no pipeline. No
próprio documento, permanecem em aberto os exemplos do SIGH em 13.2, o registro de
R03 e R04, a priorização de 13.6 e a ordem de 14.5.

> *Rascunho do Integrante 5, escrito sobre R01, R02, R05 e R06; revisão prevista
> quando R03 e R04 forem registrados e quando 13.6 e 14.5 forem compiladas.*