# Etapa 2 - Análise, Priorização e Tratamento de Riscos com o NIST CSF 2.0

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @ARTHUR9011
> A numeração das seções segue a do enunciado (13.1 a 15). Cada integrante transforma a própria ameaça STRIDE da [Etapa 1](E1_Casos_de_abuso_e_Stride.md) em risco, mantendo a mesma trilha do início ao fim.

| Seção | Responsável | Situação |
| --- | --- | --- |
| 13.1 Critérios de probabilidade | @ARTHUR9011 + @lorenzoficher | Concluída (exemplos do SIGH adicionados) |
| 13.2 Critérios de impacto | @ARTHUR9011 + @lorenzoficher | Escala base definida |
| 13.3 Cálculo e classificação | @ARTHUR9011 | Concluída |
| 13.4 Registro de riscos | Todos (1 risco por pessoa) | R01 e R02 concluídos; R03-R06 pendentes |
| 13.5 Justificativas | Todos | R01 e R02 concluídas; demais pendentes |
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
| R01 | T01 - Spoofing | @lilydias24 | Uso das credenciais legítimas de um profissional para assumir sua identidade no SIGH e executar consultas ao prontuário e operações clínicas em nome dele | `senhaLogin` armazenada como texto simples na classe `Funcionario`, contrariando o RNF05; autenticação de fator único, sem MFA nem reautenticação em operações sensíveis; sem bloqueio após tentativas malsucedidas; sessões sem expiração por inatividade em terminais compartilhados; o Tópico 9 exclui do escopo o registro de eventos críticos de acesso indevido | 4 | 4 | 16 | Crítico |
| R02 | T02 - Tampering | @ARTHUR9011 | Alteração indevida da `dosagemMedicamento` ou do `intervaloConsumo` de uma prescrição ativa, executada pela enfermagem como se fosse a prescrição original | `atualizarTratamentosDoPaciente(tratamento)` não recebe o responsável; a regra "apenas médicos autorizados" (UC03) não é validada no servidor; não há faixa terapêutica para os campos; a alteração sobrescreve o registro sem versionamento nem autor | 3 | 4 | 12 | Crítico |
| R03 | T03 - Repudiation | @lorenzoficher | | | | | | |
| R04 | T04 - Information Disclosure | @mariasanchez0’s | | | | | | |
| R05 | T05 - Denial of Service | @PPrauchner | | | | | | |
| R06 | T06 - Elevation of Privilege | @PPrauchner | | | | | | |

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

> **Pendente:** justificativas de R03 a R06, cada uma pelo respectivo responsável.

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
