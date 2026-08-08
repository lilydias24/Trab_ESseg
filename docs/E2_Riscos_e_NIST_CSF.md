# Etapa 2 - Análise, Priorização e Tratamento de Riscos com o NIST CSF 2.0

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @ARTHUR9011
> A numeração das seções segue a do enunciado (13.1 a 15). Cada integrante transforma a própria ameaça STRIDE da [Etapa 1](E1_Casos_de_abuso_e_Stride.md) em risco, mantendo a mesma trilha do início ao fim.

| Seção | Responsável | Situação |
| --- | --- | --- |
| 13.1 Critérios de probabilidade | @ARTHUR9011 + @lorenzoficher | Escala base definida |
| 13.2 Critérios de impacto | @ARTHUR9011 + @lorenzoficher | Escala base definida |
| 13.3 Cálculo e classificação | @ARTHUR9011 | Concluída |
| 13.4 Registro de riscos | Todos (1 risco por pessoa) | R01 concluído; R02-R06 pendentes |
| 13.5 Justificativas | Todos | R01 concluída; demais pendentes |
| 13.6 Priorização geral | @mariasanchez0’s (compila) | Pendente |
| 13.7 Conclusão da análise | @ARTHUR9011 | Pendente |
| 14.1 Estratégia de tratamento | Todos | R01 concluída; demais pendentes |
| 14.2 Funções do NIST CSF | @lorenzoficher | Tabela base definida |
| 14.3 Mapeamento risco → NIST | Todos | R01 concluído; demais pendentes |
| 14.4 Plano de tratamento | Todos | R01 concluído; demais pendentes |
| 14.5 Ordem de implementação | @mariasanchez0’s | Pendente |
| 14.6 Risco residual | Todos | R01 concluído; demais pendentes |
| 15. Considerações finais | @PPrauchner (rascunho) + revisão de todos | Pendente |

---

## 13.1 Critérios de probabilidade

| Valor | Classificação | Critério |
| --- | --- | --- |
| 1 | Baixa | O evento depende de condições incomuns, acesso muito específico ou grande capacidade técnica |
| 2 | Média-baixa | O evento é possível, mas depende de uma vulnerabilidade ou condição específica |
| 3 | Média-alta | O evento é plausível e pode ocorrer em situações comuns de uso ou ataque |
| 4 | Alta | O evento pode ocorrer com facilidade, frequência ou durante condições previsíveis do sistema |

> **Pendente (Integrantes 2 e 3):** acrescentar a cada faixa um exemplo concreto do contexto do SIGH.

## 13.2 Critérios de impacto

| Valor | Classificação | Critério |
| --- | --- | --- |
| 1 | Baixo | Causa pequeno transtorno e pode ser corrigido rapidamente |
| 2 | Moderado | Causa interrupção ou inconsistência limitada, com possibilidade de recuperação |
| 3 | Alto | Causa prejuízo relevante aos usuários, ao negócio, à administração ou à privacidade |
| 4 | Muito alto | Pode afetar muitos usuários, comprometer operações críticas ou causar prejuízo grave |

> **Pendente (Integrantes 2 e 3):** acrescentar a cada faixa um exemplo concreto do contexto do SIGH.

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
| R02 | T02 - Tampering | @ARTHUR9011 | | | | | | |
| R03 | T03 - Repudiation | @lorenzoficher | | | | | | |
| R04 | T04 - Information Disclosure | @mariasanchez0’s | | | | | | |
| R05 | T05 - Denial of Service | @PPrauchner | | | | | | |
| R06 | T06 - Elevation of Privilege | @PPrauchner | | | | | | |

## 13.5 Justificativas das avaliações

### R01

**Probabilidade.** 
**Impacto** 
**Quem é afetado.** 
**Por que Crítico é adequado.** 

> **Pendente:** justificativas de R02 a R06, cada uma pelo respectivo responsável.

## 13.6 Priorização geral

> Seção compilada por **@mariasanchez0’s**, com validação coletiva - ordem de tratamento considerando pontuação, gravidade das consequências, usuários afetados, importância do ativo, possibilidade de recuperação, dependências e urgência.

*(Pendente - depende do preenchimento de R02 a R06.)*

### 13.7 Conclusão da análise de riscos

> Seção do **@ARTHUR9011** (líder da etapa), com validação coletiva. Não consta com número próprio no enunciado, mas o exemplo entregue pelo professor traz uma conclusão fechando a análise antes de entrar no tratamento - encerramento do raciocínio de probabilidade × impacto, dizendo quais riscos exigem atenção inicial e em que condições a classificação deve ser revisada.

*(Pendente.)*

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
| R02 | | |
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
| R02 | | | | | | |
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

> **Pendente:** mapeamento e justificativa de R02 a R06, cada um pelo respectivo responsável (evitar marcar todas as funções sem justificar).

## 14.4 Plano de tratamento

| Risco | Estratégia | Controles propostos | Funções relacionadas | Responsáveis | Evidências e verificação |
| --- | --- | --- | --- | --- | --- |
| R01 | | | | | |
| R02 | | | | | |
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
| R02 | | | |
| R03 | | | |
| R04 | | | |
| R05 | | | |
| R06 | | | |

### Justificativa do residual de R01 (@lilydias24)

**Probabilidade**
**Impacto**
**Condição para aceitar o residual Alto:** 

## 15. Considerações finais (Etapa 2)

> Rascunho de responsabilidade do **@PPrauchner**, com revisão de todos.

- **Riscos mais importantes:**
- **Razões da priorização:**
- **Estratégias de tratamento predominantes:**
- **Funções do NIST mais relevantes:**
- **Controles considerados essenciais:**
- **Principais dificuldades e limitações da avaliação:**
- **Pontos a detalhar nas próximas etapas:**
