# Modelagem de Ameaças e Tratamento de Riscos - SIGH (Sistema Integrado de Gestão Hospitalar)

## Etapa 1 - Casos de Abuso e Modelagem de Ameaças com STRIDE

### 1. Identificação do sistema

- **Nome do sistema:** SIGH - Sistema Integrado de Gestão Hospitalar (recorte de 5 módulos: Cadastro/Prontuário de Pacientes, Atendimento Médico/Consultas, Internação e Leitos, Farmácia/Prescrição de Medicamentos e Financeiro/Cobrança)
- **Integrantes do grupo:** Arthur Provenzi Parizotto, Emilly Nascimento Dias, Lorenzo Ponsi Ficher, Maria Eduarda Sanchez Chessio, Pietro Mendes Prauchner
- **Repositório:** [Trab_ESseg](https://github.com/lilydias24/Trab_ESseg.git)
- **Justificativa para a escolha do sistema:** o SIGH foi escolhido por reunir, em um único sistema, os elementos necessários para uma análise STRIDE completa: múltiplos perfis de usuário com diferentes níveis de permissão (Médico, Enfermeiro, Recepcionista, Administrador), integração com um sistema externo (validação de cobertura de convênio), dados de alta sensibilidade (prontuário médico, prescrições, dados financeiros) e operações irreversíveis de alto impacto, como o registro de óbito e a alta hospitalar. O grupo também já dispõe da modelagem completa do sistema (casos de uso, diagrama de classes/domínio e arquitetura de componentes), produzida em trabalho anterior da graduação, o que permite fundamentar cada ameaça em elementos concretos do modelo - campos de classes, regras de negócio e arquitetura - em vez de suposições genéricas.

### 2. Descrição do sistema

O SIGH é um software voltado à gestão dos principais processos operacionais de um hospital. Ele integra diferentes setores - atendimento, enfermagem, farmácia e administração financeira - permitindo que informações de pacientes circulem entre esses setores de forma coordenada, desde o primeiro cadastro até a cobrança de um atendimento.

**Problema que o sistema resolve:** hoje, hospitais lidam com informações espalhadas entre setores que precisam se comunicar (recepção, enfermagem, corpo médico, farmácia e financeiro). O SIGH centraliza essas informações em um único sistema, reduzindo retrabalho e permitindo que cada profissional tenha acesso ao histórico relevante do paciente no momento do atendimento.

**Quem utiliza o sistema:**
- **Médico** - registra prontuário, prescreve medicamentos, autoriza altas, registra consultas e óbitos;
- **Enfermeiro** - realiza triagem, controla leitos, gerencia estoque de medicamentos, atualiza prontuário e registra exames;
- **Recepcionista** - agenda consultas, emite faturas e gerencia o cadastro de pacientes;
- **Administrador** - cadastra profissionais, gerencia escalas e possui diferentes níveis de acesso (Diretor, Gerente Geral, Gerente de Setor, Supervisor);
- **«system» Convênio** - sistema externo que valida a cobertura de procedimentos para os pacientes.

**Principais funcionalidades:**
- Cadastro e prontuário de pacientes (dados pessoais, histórico médico, alergias, medicações em uso);
- Agendamento e registro de consultas, incluindo integração com convênios médicos;
- Controle de internações, ocupação de leitos e altas hospitalares;
- Prescrição e rastreamento de medicamentos, com controle de estoque na farmácia;
- Emissão de faturas e controle de pagamentos de consultas, exames e internações.

**Informações armazenadas/transmitidas:** dados pessoais e clínicos de pacientes (CPF, data de nascimento, tipo sanguíneo, histórico médico, alergias, prescrições), credenciais de acesso dos profissionais (login e senha), registros de internação e óbito, e dados financeiros de cobrança.

**Recursos que precisam ser protegidos:** as credenciais de login dos profissionais (`nomeLogin`/`senhaLogin`, sem indicação de hashing no modelo de domínio original, o que as torna um ponto crítico para ataques de Spoofing), o prontuário e os dados clínicos dos pacientes, as prescrições de medicamentos, os registros de óbito (operação irreversível) e os dados financeiros/de faturamento.

### 3. Usuários, ativos e pontos de interação

*(Seção de responsabilidade de Integrante 2 - pendente: tabela de perfis de acesso e lista de ativos importantes)*

#### 3.1 Usuários e perfis de acesso

| Usuário/Perfil | Principais ações |
| --- | --- |
| | |

#### 3.2 Ativos importantes

*(Pendente)*

#### 3.3 Pontos de interação e componentes

| Elemento | Função |
| --- | --- |
| | |

### 4. Visão geral da arquitetura ou fluxo

*(Seção de responsabilidade de Integrante 3 - pendente: diagrama de contexto/componentes exportado do Lucid, versionado em `diagramas/`)*

`![Diagrama de contexto](../diagramas/diagrama-contexto.png)`

### 5. Modelagem de ameaças com STRIDE

| ID | Categoria STRIDE | Componente ou ativo | Ameaça identificada | Possível impacto |
| --- | --- | --- | --- | --- |
| T01 | Spoofing | | | |
| T02 | Tampering | | | |
| T03 | Repudiation | | | |
| T04 | Information Disclosure | | | |
| T05 | Denial of Service | | | |
| T06 | Elevation of Privilege | | | |


*(Adicionar quantas linhas forem necessárias por categoria; justificar caso alguma categoria não seja aplicável.)*

### 6. Casos de abuso

#### CA01 — [Título]

- **Ator:**
- **Objetivo:**
- **Condições necessárias:**
- **Fluxo de abuso:**
  1.
  2.
- **Impacto esperado:**
- **Categorias STRIDE relacionadas:**

*(Repetir a estrutura acima para CA02, CA03... - recomenda-se ao menos 1 caso por integrante.)*

### 7. Considerações finais (Etapa 1)

- **Ameaças mais preocupantes:**
- **Ativos mais importantes:**
- **Tipos de abuso de maior impacto:**
- **Principais dificuldades encontradas pelo grupo:**

---

## Etapa 2 - Análise, Priorização e Tratamento de Riscos com o NIST CSF 2.0

*(seções da Etapa 2 - critérios de impacto, registro de riscos, priorização e mapeamento/tratamento com o NIST CSF 2.0 - a serem adicionadas conforme a divisão de trabalho de cada integrante, seguindo a mesma trilha STRIDE definida na Etapa 1.)*

### 8. Critérios de probabilidade

| Valor | Classificação | Critério |
| --- | --- | --- |
| 1 | Baixa | O evento depende de condições incomuns, acesso muito específico ou grande capacidade técnica |
| 2 | Média-baixa | O evento é possível, mas depende de uma vulnerabilidade ou condição específica |
| 3 | Média-alta | O evento é plausível e pode ocorrer em situações comuns de uso ou ataque |
| 4 | Alta | O evento pode ocorrer com facilidade, frequência ou durante condições previsíveis do sistema |


### 9. Critérios de impacto

| Valor | Classificação | Critério |
| --- | --- | --- |
| 1 | Baixo | Causa pequeno transtorno e pode ser corrigido rapidamente |
| 2 | Moderado | Causa interrupção ou inconsistência limitada, com possibilidade de recuperação |
| 3 | Alto | Causa prejuízo relevante aos usuários, ao negócio, à administração ou à privacidade |
| 4 | Muito alto | Pode afetar muitos usuários, comprometer operações críticas ou causar prejuízo grave |

### 10. Cálculo e classificação dos riscos

Pontuação = Probabilidade × Impacto

| Pontuação | Nível do risco |
| --- | --- |
| 1 a 3 | Baixo |
| 4 a 7 | Médio |
| 8 a 11 | Alto |
| 12 a 16 | Crítico |

### 11. Registro de riscos

| ID | Origem STRIDE | Evento de risco | Vulnerabilidade ou condição | Probabilidade | Impacto | Pontuação | Nível |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | Spoofing | | | | | | |
| R02 | Tampering | | | | | | |
| R03 | Repudiation | | | | | | |
| R04 | Information Disclosure | | | | | | |
| R05 | Denial of Service | | | | | | |
| R06 | Elevation of Privilege | | | | | | |

### 12. Justificativas das avaliações

*(Para cada risco: por que a probabilidade e o impacto receberam aqueles valores, quem/o que é afetado, e por que o nível calculado representa adequadamente o contexto.)*

### 13. Priorização dos riscos

*(Ordem de tratamento considerando pontuação, gravidade das consequências, usuários afetados, importância do ativo, possibilidade de recuperação, dependências e urgência.)*

### 14. Estratégias de tratamento

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

### 15. Funções do NIST CSF 2.0

| Função | Finalidade |
| --- | --- |
| Govern | Definir políticas, responsabilidades, prioridades e critérios de decisão |
| Identify | Conhecer ativos, dependências, vulnerabilidades e riscos |
| Protect | Implementar salvaguardas para reduzir a probabilidade ou o impacto |
| Detect | Identificar eventos suspeitos, falhas e possíveis incidentes |
| Respond | Conter, analisar, comunicar e tratar incidentes |
| Recover | Restaurar serviços e dados e reduzir os prejuízos causados |

### 16. Mapeamento dos riscos para as funções do NIST CSF

| Risco | Govern | Identify | Protect | Detect | Respond | Recover |
| --- | :---: | :---: | :---: | :---: | :---: | :---: |
| R01 | | | | | | |
| R02 | | | | | | |
| R03 | | | | | | |
| R04 | | | | | | |
| R05 | | | | | | |
| R06 | | | | | | |

### 17. Plano de tratamento

| Risco | Estratégia | Controles propostos | Funções relacionadas | Responsáveis | Evidências e verificação |
| --- | --- | --- | --- | --- | --- |
| R01 | | | | | |
| R02 | | | | | |
| R03 | | | | | |
| R04 | | | | | |
| R05 | | | | | |
| R06 | | | | | |

### 18. Ordem inicial de implementação

1.
2.
3.

### 19. Estimativa do risco residual

| Risco | Nível inicial | Nível residual esperado | Condição para aceitar o residual |
| --- | --- | --- | --- |
| R01 | | | |
| R02 | | | |
| R03 | | | |
| R04 | | | |
| R05 | | | |
| R06 | | | |

### 20. Considerações finais (Etapa 2)

- **Riscos mais importantes:**
- **Razões da priorização:**
- **Estratégias de tratamento predominantes:**
- **Funções do NIST mais relevantes:**
- **Controles considerados essenciais:**
- **Principais dificuldades e limitações da avaliação:**
- **Pontos a detalhar nas próximas etapas:**

---

