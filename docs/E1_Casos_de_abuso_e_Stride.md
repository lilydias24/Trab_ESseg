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
| T01 | Spoofing | Credenciais de acesso da classe `Funcionario` (`nomeLogin`, `senhaLogin`) - módulo de autenticação, transversal aos 5 módulos | Um atacante de posse do par login/senha de um médico autentica-se no SIGH como o profissional legítimo. O modelo de domínio guarda `senhaLogin` como atributo simples da classe `Funcionario`, sem indicação de hash ou salt, e a autenticação se resume à comparação direta dos dois campos: não há segundo fator, bloqueio por tentativas malsucedidas nem vínculo da sessão a um terminal | Acesso integral ao prontuário de qualquer paciente e execução de operações privativas do perfil médico (prescrever, dar alta, registrar óbito) atribuídas ao profissional legítimo. Um dump da tabela `Funcionario` compromete todas as contas de uma vez |
| T02 | Tampering | | | |
| T03 | Repudiation | | | |
| T04 | Information Disclosure | | | |
| T05 | Denial of Service | | | |
| T06 | Elevation of Privilege | | | |

### T01 - Spoofing na conta de `Funcionario` (@lilydias24)

**Onde está no modelo.** No diagrama de classes do SIGH, a classe `Funcionario` (superclasse de Médico, Enfermeiro, Recepcionista e Administrador) possui os atributos `nomeLogin` e `senhaLogin` como campos de texto comuns, sem qualquer indicação de transformação criptográfica. Não existe no modelo nenhuma entidade, operação ou componente dedicado a políticas de credencial (expiração, complexidade, histórico, bloqueio).

**O que a documentação do próprio SIGH confirma.** Dois pontos evitam que esta ameaça dependa de suposição:

- O **RNF05 - Segurança** exige que "as informações médicas devem ser protegidas por criptografia", mas o modelo de domínio guarda `senhaLogin` em texto simples. O requisito de proteção existe no papel e não chegou ao projeto - a ameaça está na distância entre os dois.
- O **Tópico 9** do documento original declara fora de escopo a biometria/reconhecimento facial e o **registro de eventos críticos de acesso indevido**. O sistema, portanto, assume não ter autenticação forte nem trilha de detecção de acesso indevido: um login com credencial roubada não encontra barreira nem deixa alarme.

**Por que isso é uma ameaça de Spoofing.** A identidade de um profissional no SIGH é comprovada por um único fator - saber a senha. Como consequência:

1. **A senha é reutilizável e permanente.** Sem política de expiração ou verificação de complexidade, uma senha fraca ou reaproveitada de outro serviço continua válida indefinidamente.
2. **Um vazamento do banco entrega credenciais em claro.** Como o modelo não prevê hash nem salt, o comprometimento do SGBD central (que a arquitetura de componentes mostra ser único para todos os módulos) expõe diretamente as senhas de todos os profissionais - inclusive as de Administrador.
3. **Não há barreira após a obtenção da senha.** Ausência de MFA, de reautenticação para operações sensíveis, de bloqueio após tentativas malsucedidas e de vínculo com dispositivo/terminal significa que qualquer pessoa com o par correto entra sem atrito - inclusive por força bruta a partir da própria rede do hospital.
4. **O ambiente favorece o vetor.** Postos de enfermagem usam terminais compartilhados e plantões trocam de turno; senhas observadas por cima do ombro, anotadas ou deixadas em sessão aberta são vetores realistas, não hipotéticos.

**Impacto.** Confidencialidade: leitura irrestrita de prontuários, alergias, prescrições e dados financeiros. Integridade e segurança do paciente: possibilidade de prescrever medicamento, autorizar alta ou registrar óbito em nome de um médico. Responsabilização: como o SIGH registra o autor pela sessão autenticada, as ações do atacante ficam atribuídas ao profissional legítimo, encadeando com **T03 (Repudiation)** e, se a conta assumida for de Administrador, com **T06 (Elevation of Privilege)**.

### 8.5.1 Interpretação da análise

> Rascunho de **@lilydias24**, a ser escrito quando T02 a T06 estiverem preenchidas - parágrafo de leitura conjunta da tabela, mostrando que as ameaças atingem partes diferentes do sistema (identidade, integridade dos dados clínicos, rastreabilidade, confidencialidade, disponibilidade e autorização) e por que nenhuma delas se resolve com um único controle.

## 8.6 Casos de abuso

| ID | Título | STRIDE de origem | Responsável |
| --- | --- | --- | --- |
| CA01 | Uso de credenciais roubadas para assumir a conta de um médico | T01 - Spoofing | @lilydias24 |
| CA02 | *(a definir)* | T02 - Tampering | @ARTHUR9011 |
| CA03 | *(a definir)* | T03 - Repudiation | @lorenzoficher |
| CA04 | *(a definir)* | T04 - Information Disclosure | @mariasanchez0’s |
| CA05 | *(a definir)* | T05/T06 - DoS e Elevation of Privilege | @PPrauchner |

### CA01 - Uso de credenciais roubadas para assumir a conta de um médico

- **Ator:** atacante com acesso à rede interna do hospital - tipicamente alguém de dentro (estagiário, terceirizado, colega de plantão) ou um invasor que já obteve as credenciais de um médico por outro meio.
- **Objetivo:** autenticar-se no SIGH com a identidade de um médico para consultar prontuários e executar operações restritas a esse perfil, fazendo com que os registros apontem o profissional legítimo como autor.
- **Condições necessárias:**
  - `senhaLogin` armazenada sem hash e sem salt no SGBD central, o que torna um dump do banco imediatamente utilizável;
  - autenticação de fator único, sem MFA e sem reautenticação antes de operações sensíveis (prescrição, alta, registro de óbito);
  - ausência de bloqueio de conta e de alerta após sequências de tentativas malsucedidas;
  - ausência de política de complexidade, expiração e não reuso de senha;
  - terminais compartilhados nos postos de atendimento, sem expiração de sessão por inatividade.
- **Fluxo de abuso:**
  1. O atacante obtém o par `nomeLogin`/`senhaLogin` de um médico - observando a digitação em um terminal compartilhado, por phishing, por reuso de uma senha já vazada em outro serviço, ou lendo diretamente a tabela `Funcionario` após acesso ao banco.
  2. Acessa a tela de login do SIGH a partir de um terminal da rede hospitalar, em horário de baixa circulação.
  3. Informa as credenciais; o sistema apenas compara os valores armazenados e abre a sessão com perfil de Médico - sem segundo fator, sem verificação de dispositivo e sem notificar o titular.
  4. Com a sessão ativa, consulta o prontuário de pacientes que não estão sob seus cuidados. O caminho técnico é o mesmo dos diagramas de sequência do SIGH - Desktop Cliente → API Gateway → Serviço de Paciente -, chamando `buscarPacientePorIdentificador(idPaciente)`. Como o identificador é sequencial, basta variá-lo para percorrer prontuários, incluindo histórico, alergias e prescrições em andamento.
  5. Executa ao menos uma operação privativa do perfil médico - `atualizarTratamentosDoPaciente(tratamento)` para registrar ou alterar uma `PrescricaoMedicamento`, a autorização de alta (UC06) ou `Obito.registrarObito(data, hora)` (UC10). Nenhuma dessas operações recebe um parâmetro de responsável: a regra "somente médicos podem registrar óbito" existe apenas como texto na descrição do caso de uso, não nos parâmetros da operação.
  6. Encerra a sessão. Todos os registros gerados constam no sistema como tendo sido feitos pelo médico titular da conta.

  *Referência técnica do fluxo: os diagramas de sequência versionados em `diagrams/sequencia/` (DS03 - Gerenciar Tratamento, DS06 - Autorizar Alta, DS10 - Registrar Óbito) mostram exatamente essas chamadas no caminho legítimo. O abuso não inventa um caminho novo: percorre o mesmo, com a identidade errada.*
  
- **Impacto esperado:**
  - **Confidencialidade:** exposição de dados clínicos e pessoais sensíveis, com violação do sigilo médico e da LGPD (dados de saúde são dados pessoais sensíveis, art. 5º, II).
  - **Segurança do paciente:** uma prescrição ou alta indevida gerada nessa sessão tem consequência assistencial direta e imediata.
  - **Irreversibilidade:** o registro de óbito não tem desfazimento trivial e produz efeitos legais e administrativos fora do sistema.
  - **Responsabilização:** o médico titular responde, perante o hospital e o conselho profissional, por atos que não praticou, e o hospital não consegue provar o contrário com os registros existentes.
- **Categorias STRIDE relacionadas:** **Spoofing** (principal - assunção da identidade do médico); **Information Disclosure** (leitura do prontuário); **Tampering** (alteração de prescrição a partir da conta assumida); **Repudiation** (as ações são indistinguíveis das do titular); **Elevation of Privilege** (caso a conta obtida seja de Administrador).

## 8.7 Considerações finais (Etapa 1)

> Rascunho de responsabilidade de **@lilydias24**, com revisão de todos - a ser escrito após a conclusão de 8.3 a 8.6.

- **Ameaças mais preocupantes:**
- **Ativos mais importantes:**
- **Tipos de abuso de maior impacto:**
- **Principais dificuldades encontradas pelo grupo:**
