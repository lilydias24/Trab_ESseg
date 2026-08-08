# Etapa 1 - Casos de Abuso e Modelagem de Ameaças com STRIDE

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lilydias24
> A numeração das seções segue a do enunciado (8.1 a 8.7).
> **Material de apoio:** escopo, requisitos, atores e campos sensíveis em `contexto/SIGH - Recorte ESSEG.md`; leitura dos diagramas em `contexto/SIGH - Contexto dos diagramas.md`; imagens em `diagrams/` (índice em `diagrams/README.md`).

| Seção | Responsável | Situação |
| --- | --- | --- |
| 8.1 Identificação do sistema | @lilydias24 | Concluída |
| 8.2 Descrição do sistema | @lilydias24 | Concluída |
| 8.3 Usuários, ativos e pontos de interação | @ARTHUR9011 | Pendente |
| 8.4 Visão geral da arquitetura/fluxo | @lorenzoficher | Pendente |
| 8.5 Modelagem STRIDE | Todos (1 categoria por pessoa) | T01 concluída; T02-T06 pendentes |
| 8.5.1 Interpretação da análise | @lilydias24 | Pendente (após T02-T06) |
| 8.6 Casos de abuso | Todos (1 caso por pessoa) | CA01 concluído; CA02-CA05 pendentes |
| 8.7 Considerações finais | @lilydias24 (rascunho) + revisão de todos | Pendente (após 8.3-8.6) |

---

## 8.1 Identificação do sistema

- **Nome do sistema:** SIGH - Sistema Integrado de Gestão Hospitalar (recorte de 5 módulos: Cadastro/Prontuário de Pacientes, Atendimento Médico/Consultas, Internação e Leitos, Farmácia/Prescrição de Medicamentos e Financeiro/Cobrança)
- **Integrantes do grupo:** Arthur Provenzi Parizotto, Emilly Nascimento Dias, Lorenzo Ponsi Ficher, Maria Eduarda Sanchez Chessio, Pietro Mendes Prauchner
- **Repositório:** [Trab_ESseg](https://github.com/lilydias24/Trab_ESseg.git)
- **Justificativa para a escolha do sistema:** o SIGH foi escolhido por reunir, em um único sistema, os elementos necessários para uma análise STRIDE completa: múltiplos perfis de usuário com diferentes níveis de permissão (Médico, Enfermeiro, Recepcionista, Administrador), integração com um sistema externo (validação de cobertura de convênio), dados de alta sensibilidade (prontuário médico, prescrições, dados financeiros) e operações irreversíveis de alto impacto, como o registro de óbito e a alta hospitalar. O grupo também já dispõe da modelagem completa do sistema (casos de uso, diagrama de classes/domínio e arquitetura de componentes), produzida em trabalho anterior da graduação, o que permite fundamentar cada ameaça em elementos concretos do modelo - campos de classes, regras de negócio e arquitetura - em vez de suposições genéricas.

## 8.2 Descrição do sistema

O SIGH é um software voltado à gestão dos principais processos operacionais de um hospital. Ele integra diferentes setores - atendimento, enfermagem, farmácia e administração financeira - permitindo que informações de pacientes circulem entre esses setores de forma coordenada, desde o primeiro cadastro até a cobrança de um atendimento.

**Problema que o sistema resolve:** hoje, hospitais lidam com informações espalhadas entre setores que precisam se comunicar (recepção, enfermagem, corpo médico, farmácia e financeiro). O SIGH centraliza essas informações em um único sistema, reduzindo retrabalho e permitindo que cada profissional tenha acesso ao histórico relevante do paciente no momento do atendimento.

**Quem utiliza o sistema:**
- **Médico** - registra prontuário, prescreve medicamentos, autoriza altas, registra consultas e óbitos;
- **Enfermeiro** - realiza triagem, controla leitos, gerencia estoque de medicamentos, atualiza prontuário e registra exames;
- **Recepcionista** - agenda consultas, emite faturas e gerencia o cadastro de pacientes;
- **Administrador** - cadastra profissionais, gerencia escalas e possui diferentes níveis de acesso (Diretor, Gerente Geral, Gerente de Setor, Supervisor);
- **«system» Convênio** - sistema externo que valida a cobertura de procedimentos para os pacientes (RF06, relação «extend» de Gerenciar Pacientes);
- **«system» Sistema Governamental** - sistema externo que recebe o registro de óbito. Aparece no diagrama de casos de uso, mas **não possui requisito funcional documentado** descrevendo a integração - lacuna do documento original, relevante para a análise de ameaças;
- **«system» Sistema de Laboratório** - citado no RF28 como origem dos resultados de exames, mas **não modelado** nos diagramas de casos de uso nem de componentes - segunda lacuna do documento original.

**Principais funcionalidades:**
- Cadastro e prontuário de pacientes (dados pessoais, histórico médico, alergias, medicações em uso);
- Agendamento e registro de consultas, incluindo integração com convênios médicos;
- Controle de internações, ocupação de leitos e altas hospitalares;
- Prescrição e rastreamento de medicamentos, com controle de estoque na farmácia;
- Emissão de faturas e controle de pagamentos de consultas, exames e internações.

**Informações armazenadas/transmitidas:** dados pessoais e clínicos de pacientes (CPF, data de nascimento, tipo sanguíneo, histórico médico, alergias, prescrições), credenciais de acesso dos profissionais (login e senha), registros de internação e óbito, e dados financeiros de cobrança.

**Recursos que precisam ser protegidos:** as credenciais de login dos profissionais (`nomeLogin`/`senhaLogin`, sem indicação de hashing no modelo de domínio original, o que as torna um ponto crítico para ataques de Spoofing), o prontuário e os dados clínicos dos pacientes, as prescrições de medicamentos, os registros de óbito (operação irreversível) e os dados financeiros/de faturamento.

**O que a própria documentação do SIGH já reconhece sobre segurança:**

- O **RNF05 - Segurança** afirma que "as informações médicas devem ser protegidas por criptografia". Esse requisito **contradiz o modelo de domínio**, em que `senhaLogin` aparece como atributo de texto simples da classe `Funcionario`: a proteção é exigida em requisito, mas não aparece no projeto. Essa distância entre o requisito e o modelo é o ponto de partida da ameaça T01.
- O **Tópico 9** do documento original coloca explicitamente fora do escopo do SIGH o controle de acesso físico, a biometria/reconhecimento facial e o **registro de eventos críticos de acesso indevido**. Ou seja, o próprio sistema assume não possuir autenticação forte nem detecção de acesso indevido - condição que sustenta as ameaças de Spoofing (T01) e Elevation of Privilege (T06) sem precisar supor nada.
- O **RNF03 - Disponibilidade** exige operação 24h/7d com recuperação automática de falhas, enquanto o diagrama de implantação mostra um **SGBD único e centralizado** atendendo todos os módulos - tensão que sustenta a ameaça de Denial of Service (T05).

## 8.3 Usuários, ativos e pontos de interação

> Seção de responsabilidade do **@ARTHUR9011**.

### 8.3.1 Usuários e perfis de acesso

| Usuário/Perfil | Principais ações |
| --- | --- |
| | |

### 8.3.2 Ativos importantes

*(Pendente - dados de Paciente, dados de Funcionario, prescrições, registros de óbito, faturamento.)*

### 8.3.3 Pontos de interação e componentes

| Elemento | Função |
| --- | --- |
| | |

## 8.4 Visão geral da arquitetura ou fluxo

> Seção de responsabilidade do **@lorenzoficher**. 

*(Pendente: recorte do diagrama para os 5 módulos do escopo, imagem incorporada abaixo e descrição do fluxo principal de dados.)*


## 8.5 Modelagem de ameaças com STRIDE

Cada integrante é responsável por uma categoria, amarrada a um módulo/ativo concreto do SIGH:

| ID | Categoria STRIDE | Componente ou ativo | Responsável |
| --- | --- | --- | --- |
| T01 | Spoofing | Credenciais de `Funcionario` (`nomeLogin`/`senhaLogin`) | @lilydias24 |
| T02 | Tampering | `PrescricaoMedicamento` / `Tratamento` | @ARTHUR9011 |
| T03 | Repudiation | `Obito.registrarObito()` | @lorenzoficher |
| T04 | Information Disclosure | Ausência de isolamento entre Farmácia e Financeiro | @mariasanchez0’s |
| T05 | Denial of Service | SGBD único centralizado | @PPrauchner |
| T06 | Elevation of Privilege | `enum nivelAcesso` do Administrador | @PPrauchner |

### Quadro consolidado

| ID | Categoria STRIDE | Componente ou ativo | Ameaça identificada | Possível impacto |
| --- | --- | --- | --- | --- |
| T01 | Spoofing | | | |
| T02 | Tampering | | | |
| T03 | Repudiation | | | |
| T04 | Information Disclosure | | | |
| T05 | Denial of Service | | | |
| T06 | Elevation of Privilege | | | |


### 8.5.1 Interpretação da análise

> Rascunho de **@lilydias24**, a ser escrito quando T02 a T06 estiverem preenchidas - parágrafo de leitura conjunta da tabela, mostrando que as ameaças atingem partes diferentes do sistema (identidade, integridade dos dados clínicos, rastreabilidade, confidencialidade, disponibilidade e autorização) e por que nenhuma delas se resolve com um único controle.

## 8.6 Casos de abuso

| ID | Título | STRIDE de origem | Responsável |
| --- | --- | --- | --- |
| CA01 | *(a definir)* | T01 - Spoofing | @lilydias24 |
| CA02 | *(a definir)* | T02 - Tampering | @ARTHUR9011 |
| CA03 | *(a definir)* | T03 - Repudiation | @lorenzoficher |
| CA04 | *(a definir)* | T04 - Information Disclosure | @mariasanchez0’s |
| CA05 | *(a definir)* | T05/T06 - DoS e Elevation of Privilege | @PPrauchner |

### CA01

- **Ator:**
- **Objetivo:**
- **Condições necessárias:**
- **Fluxo de abuso:**
- **Impacto esperado:**
- **Categorias STRIDE relacionadas:** 

## 8.7 Considerações finais (Etapa 1)

> Rascunho de responsabilidade de **@lilydias24**, com revisão de todos - a ser escrito após a conclusão de 8.3 a 8.6.

- **Ameaças mais preocupantes:**
- **Ativos mais importantes:**
- **Tipos de abuso de maior impacto:**
- **Principais dificuldades encontradas pelo grupo:**
