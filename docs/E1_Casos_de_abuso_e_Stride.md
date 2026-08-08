# Etapa 1 - Casos de Abuso e Modelagem de Ameaças com STRIDE

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lilydias24
> A numeração das seções segue a do enunciado (8.1 a 8.7).
> **Material de apoio:** escopo, requisitos, atores e campos sensíveis em `contexto/SIGH - Recorte ESSEG.md`; leitura dos diagramas em `contexto/SIGH - Contexto dos diagramas.md`; imagens em `diagrams/` (índice em `diagrams/README.md`).

| Seção | Responsável | Situação |
| --- | --- | --- |
| 8.1 Identificação do sistema | @lilydias24 | Concluída |
| 8.2 Descrição do sistema | @lilydias24 | Concluída |
| 8.3 Usuários, ativos e pontos de interação | @ARTHUR9011 | Concluída |
| 8.4 Visão geral da arquitetura/fluxo | @lorenzoficher | Concluída |
| 8.5 Modelagem STRIDE | Todos (1 categoria por pessoa) | T01, T02, T03, T05 e T06 concluídas; T04 pendente |
| 8.5.1 Interpretação da análise | @lilydias24 | Pendente (após as demais ameaças) |
| 8.6 Casos de abuso | Todos (1 caso por pessoa) | CA01, CA02 e CA03 concluídos; CA04, CA05 pendentes |
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

| Perfil | Principais ações no SIGH | Dados e operações que alcança |
| --- | --- | --- |
| **Médico** | Registra anamnese e prescrições (RF07), prescreve medicamentos (RF22), gerencia tratamento (UC03), registra consulta (UC05), autoriza alta (UC06), registra óbito (UC10) | Prontuário completo, `Tratamento`, `PrescricaoMedicamento`, alta hospitalar e `Obito` - inclui as duas operações irreversíveis do recorte |
| **Enfermeiro** | Realiza triagem (UC01), controla leitos (RF08), registra baixa hospitalar (UC08), atualiza prontuário, registra exame (UC09), gerencia estoque e vencimentos de medicamentos (RF21, RF23) | Prontuário, `LeitoHospitalar`/`Ocupacao`, `Exame`, estoque de `Medicamento` |
| **Recepcionista** | Agenda consultas (RF04), gerencia o cadastro de pacientes, emite faturas e controla pagamentos (RF25) | Dados cadastrais de `Paciente`, `Consulta`, faturamento (`valorConsulta`, `valorExame`) |
| **Administrador** | Cadastra profissionais, gerencia escalas e medicamentos; opera sob `nivelAcesso` («enum»: Diretor, GerenteGeral, GerenteSetor, Supervisor) | Dados de `Funcionario`, incluindo `nomeLogin` e `senhaLogin` de todos os perfis |
| **«system» Convênio** | Valida a cobertura de procedimentos (RF06), «extend» de Gerenciar Pacientes | Recebe dados de `Paciente` e do procedimento - fronteira de confiança externa |
| **«system» Sistema Governamental** | Recebe o registro de óbito | Dados de `Obito`; integração sem requisito funcional documentado |
| **«system» Sistema de Laboratório** | Envia resultados de exames (RF28) | Dados de `Exame`; citado em requisito, mas não modelado nos diagramas |

**Três observações de segurança sobre os perfis:**

1. **Só o Administrador tem nível de acesso graduado.** Os demais perfis são subclasses de `Funcionario` sem qualquer atributo de permissão: o que um médico pode fazer é definido pela classe a que ele pertence, não por uma verificação por operação. Não há, no modelo, distinção entre "médico responsável por este paciente" e "qualquer médico do hospital".
2. **A autenticação é o único portão.** Como não existe nível de permissão dentro de cada perfil, quem passa pelo login alcança tudo o que aquele perfil alcança - o que faz de T01 (Spoofing) o habilitador das demais ameaças.
3. **Não existe perfil de auditoria.** Nenhum ator do modelo tem como atribuição revisar o que os outros fizeram, e o Tópico 9 do documento original coloca o registro de eventos críticos de acesso indevido fora do escopo. Não há quem observe.

### 8.3.2 Ativos importantes

| Ativo | Onde está no modelo | Por que precisa ser protegido |
| --- | --- | --- |
| Credenciais dos profissionais | `Funcionario.nomeLogin`, `Funcionario.senhaLogin` | Aparecem como texto simples; são a porta de entrada de todos os demais ativos (**T01**) |
| Nível de acesso administrativo | `Administrador.nivelAcesso` («enum») | Define o alcance das operações administrativas; se validado apenas na interface, é elevação de privilégio (**T06**) |
| Dados pessoais e clínicos do paciente | `Paciente.cpfPaciente`, `dataNascimento`, `tipoSanguineo`, `contatoEmergencial`, `convenio`, além de histórico, alergias e comorbidades | Dado pessoal sensível pela LGPD (art. 5º, II) e protegido por sigilo médico (**T04**) |
| Prescrição e plano de tratamento | `PrescricaoMedicamento.dosagemMedicamento`, `intervaloConsumo`, `medicamentos`; `Tratamento` | Alteração indevida tem efeito físico direto sobre o paciente (**T02**) |
| Registro de óbito | `Obito` (causa, data, hora) | Operação irreversível: bloqueia o prontuário e produz efeitos legais fora do sistema (**T03**) |
| Ocupação de leitos | `LeitoHospitalar.pacienteAlocado`, `disponivel`; `Ocupacao` | Alocação concorrente e indisponibilidade afetam a operação assistencial (**T05**) |
| Dados financeiros do atendimento | `Consulta.valorConsulta`, `Exame.valorExame`, faturas e pagamentos (RF25) | Fraude de faturamento e exposição de dados de convênio (**T04**) |
| Rastreabilidade das operações | **Não modelado** | A ausência de trilha de auditoria é, ela própria, um ativo faltante: sem ela nenhuma das ameaças acima pode ser comprovada depois (**T03**) |

### 8.3.3 Pontos de interação e componentes

| Elemento | Função | Observação de segurança |
| --- | --- | --- |
| Desktop Cliente | Interface usada por todos os perfis humanos | Único ponto de entrada dos usuários; roda em terminais compartilhados nos postos de atendimento |
| API Gateway | Centraliza e roteia as chamadas para os 7 microsserviços | Ponto obrigatório de passagem - e, por isso, ponto único de falha (**T05**) |
| Firewall por serviço | Componente que antecede o DAO de cada serviço | É o limite de confiança (*trust boundary*) declarado no diagrama de componentes |
| Serviço de Paciente | Cadastro, prontuário, tratamento e prescrição | Concentra a prescrição por não existir serviço de Farmácia (**T02**, **T04**) |
| Serviço de Atendimento Médico | Consultas, exames e cobrança | Concentra o faturamento por não existir serviço Financeiro (**T04**) |
| Serviço de Internação Médica | Leitos, internação, alta e baixa hospitalar | |
| Serviço de Agenda | Agendamento de consultas e escalas de trabalho | |
| Serviço de Acompanhamento Médico | Evolução clínica do paciente internado | |
| Serviço de Funcionários | Cadastro de profissionais e credenciais | Guarda `senhaLogin`; alvo direto de **T01** |
| SGBD central | Banco de dados único para todos os serviços | Ponto de falha compartilhado (**T05**) e alvo único de vazamento (**T04**) |
| «system» Convênio, Governamental e Laboratório | Integrações externas | Fronteiras de confiança que saem do controle do hospital |

**Dois limites de confiança que deveriam existir e não existem:** Farmácia/Medicamentos e Financeiro/Cobrança têm requisitos funcionais próprios (RF21-RF24 e RF25), mas não têm microsserviço próprio no diagrama de componentes. Na prática, dados de prescrição e de faturamento circulam dentro dos serviços de Paciente e de Atendimento sem separação - o que faz com que uma falha em qualquer um deles alcance um conjunto de dados maior do que deveria.

## 8.4 Visão geral da arquitetura ou fluxo

> Seção de responsabilidade do **@lorenzoficher**.

O SIGH é construído como uma arquitetura de **microsserviços**. São 7 serviços, cada um dividido nas mesmas 5 camadas (Visão, Controle, Negócio, Persistência e BancoDeDados), todos conectados a um **API Gateway central** que atende o Desktop Cliente usado pelos profissionais.

| Serviço | Responsabilidade no recorte |
| --- | --- |
| Serviço de Paciente | Cadastro, prontuário, tratamento e prescrição de medicamentos |
| Serviço de Atendimento Médico | Consultas, exames e cobrança |
| Serviço de Internação Médica | Internação, leitos, alta e baixa hospitalar, registro de óbito |
| Serviço de Agenda | Agendamento de consultas e escalas de trabalho |
| Serviço de Acompanhamento Médico | Evolução clínica do paciente internado |
| Serviço de Funcionários | Cadastro de profissionais e credenciais de acesso |
| Serviço de Refeições | *Fora do recorte do ESSEG* |

### 8.4.1 Diagrama de componentes

![Diagrama de componentes do SIGH](../diagrams/estrutura/Diagramas_SIGH%20-%20Componentes.png)

Cada serviço expõe seu DAO «persistent» (`PacienteDAO`, `AtendimentoPacienteDAO`, `InternacaoPacienteDAO`, `AgendaFuncionarioDAO`, `FuncionarioDAO`, entre outros) atrás de um **componente Firewall próprio**. Esses firewalls são os limites de confiança (*trust boundaries*) declarados no projeto: é onde a arquitetura decide o que pode atravessar de um serviço para outro. Todos os DAOs, porém, terminam no **mesmo SGBD**.

### 8.4.2 Diagrama de implantação

![Diagrama de implantação do SIGH](../diagrams/estrutura/Diagramas_SIGH%20-%20Implantacao.png)

A implantação confirma fisicamente a separação lógica: os módulos de Pacientes, de Funcionários e de Infraestrutura rodam em **servidores de aplicação distintos**, ligados por TCP/IP a um servidor de comunicação (proxy + API Gateway) e a um servidor de firewall, e daí a um **único servidor de banco de dados**.

### 8.4.3 Fluxo principal de dados

O caminho é o mesmo para qualquer operação do sistema, e está detalhado nos diagramas de sequência versionados em `diagrams/sequencia/`:

```
Profissional → Desktop Cliente → API Gateway → Firewall do serviço → Serviço (Visão → Controle → Negócio → Persistência) → DAO → SGBD central
```

Tomando o DS01 (Realizar Triagem) como exemplo: o Enfermeiro opera o Desktop Cliente, que chama o API Gateway, que roteia para o Serviço de Paciente, onde ocorrem `buscarPacientePorIdentificador(idPaciente)` e em seguida o registro da triagem. Nenhuma chamada alcança um serviço sem passar pelo Gateway.

### 8.4.4 O que a arquitetura revela para a análise de ameaças

Três características desta arquitetura sustentam ameaças específicas desta etapa, e por isso são registradas aqui em vez de ficarem implícitas:

1. **O API Gateway é passagem obrigatória.** Toda comunicação entre o cliente e qualquer serviço atravessa um único ponto. Isso concentra a superfície de rede e faz do Gateway um alvo natural de indisponibilidade (**T05**).
2. **O SGBD é único e centralizado**, mesmo com bancos logicamente separados por serviço. É simultaneamente um ponto de falha compartilhado por todos os módulos (**T05**) e um alvo único cujo comprometimento alcança credenciais, prontuários, prescrições e faturamento de uma só vez (**T01**, **T04**).
3. **Faltam dois limites de confiança.** Farmácia/Medicamentos e Financeiro/Cobrança têm requisitos funcionais próprios (RF21-RF24 e RF25), mas **não têm microsserviço próprio** no diagrama de componentes: residem implicitamente dentro dos serviços de Paciente e de Atendimento. Não existe firewall entre "acessar o prontuário" e "alterar a prescrição", nem entre "registrar a consulta" e "ver o faturamento" - o que amplia o raio de impacto de qualquer falha nesses dois serviços (**T02**, **T04**).

> **Observação sobre o recorte:** os diagramas versionados em `diagrams/estrutura/` são os originais do projeto, e por isso ainda incluem o Serviço de Refeições e os ramos de Cirurgias e Nutrição, que estão fora do escopo do ESSEG. A leitura acima considera apenas os 5 módulos do recorte.


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
| T02 | Tampering | `PrescricaoMedicamento` (`dosagemMedicamento`, `intervaloConsumo`, `medicamentos`) e `Tratamento`, dentro do Serviço de Paciente | A dosagem ou o intervalo de consumo de uma prescrição ativa é alterado por quem não deveria poder alterá-la. A operação `atualizarTratamentosDoPaciente(tratamento)` não recebe parâmetro de responsável e a regra "apenas médicos autorizados podem alterar tratamentos" (UC03) existe só como texto do caso de uso; não há validação de faixa terapêutica, nem versionamento do valor anterior, nem segunda conferência antes da administração | Dano físico direto ao paciente por superdosagem ou subdosagem, potencialmente fatal. Como a alteração sobrescreve o registro sem guardar o valor anterior nem o autor, o próprio ato apaga a evidência - o hospital descobre o erro pelo efeito no paciente, não pelo sistema |
| T03 | Repudiation | `Obito.registrarObito(data, hora)`, no Serviço de Internação Médica | O registro de óbito é gravado sem que o sistema guarde quem o executou. A operação recebe apenas data e hora - não recebe o responsável -, e esses dois valores são informados por quem chama, não carimbados pelo servidor. A regra "somente médicos podem registrar óbito" (UC10) existe apenas como texto do caso de uso, e o Tópico 9 coloca o registro de eventos críticos fora do escopo do sistema | Depois de gravado, não há como provar quem registrou o óbito, de onde, nem em que momento real. O autor pode negar, e o médico titular não consegue demonstrar que não foi ele. Como o registro encerra e bloqueia o prontuário e é transmitido ao «system» Sistema Governamental, o efeito sai do hospital antes de qualquer conferência |
| T04 | Information Disclosure | | | |
| T05 | Denial of Service | SGBD único e centralizado, atrás do API Gateway, compartilhado pelos 7 microsserviços (diagrama de implantação) | Todos os DAOs terminam no mesmo banco. Uma carga anormal originada em um módulo não assistencial - a emissão de faturas e o controle de pagamentos (RF25) percorrendo os atendimentos do período, ou chamadas repetidas a `buscarPacientePorIdentificador(idPaciente)` variando o identificador sequencial - esgota as conexões do SGBD e degrada ao mesmo tempo prontuário, prescrição e ocupação de leitos. O API Gateway agrava: é passagem obrigatória de toda chamada, de modo que indisponibilizá-lo derruba os 7 serviços sem sequer tocar no banco | Perda simultânea de acesso a prontuário, prescrição e ocupação de leitos, com pacientes internados no prédio; o atendimento volta ao papel e a reconciliação posterior gera inconsistência e registros sem carimbo de tempo confiável. Contraria diretamente o RNF03, que exige operação 24h/7d com recuperação automática de falhas |
| T06 | Elevation of Privilege | `Administrador.nivelAcesso` («enum»: Diretor, GerenteGeral, GerenteSetor, Supervisor), no Serviço de Funcionários | O `nivelAcesso` é o único atributo de permissão do modelo e decide quais opções administrativas a interface monta. Um Administrador de nível Supervisor, autenticado com a própria conta, edita o próprio cadastro e acrescenta `nivelAcesso: Diretor` ao corpo da requisição de salvamento; o serviço persiste o valor sem verificar se o solicitante tem alçada sobre esse campo, porque a validação existe apenas na montagem da tela | Alcance integral das operações administrativas - cadastro de profissionais, escalas e medicamentos - e leitura de `nomeLogin` e `senhaLogin` de todos os perfis, o que habilita T01 em massa sem roubo de credencial; criação de contas com perfil de Médico capazes de prescrever e registrar óbito. Sem trilha de auditoria (Tópico 9), a mudança de perfil não deixa rastro nem tem quem a observe. Violação de sigilo médico e de dado pessoal sensível de saúde (LGPD, art. 11) |

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

### T02 - Tampering na prescrição de medicamentos (@ARTHUR9011)

**Onde está no modelo.** A classe `PrescricaoMedicamento` guarda `dosagemMedicamento`, `intervaloConsumo` e `medicamentos`, e se liga ao `Tratamento` do paciente. A alteração passa pela operação `Paciente.atualizarTratamentosDoPaciente(tratamento)`, exposta pelo Serviço de Paciente. O caso de uso UC03 (Gerenciar Tratamento) define três regras de negócio: apenas médicos autorizados podem alterar tratamentos, **todo tratamento deve conter o responsável que o alterou**, e não pode haver dois tratamentos ativos para o mesmo problema.

**Onde a regra se perde.** As três regras estão escritas na descrição do caso de uso, mas nenhuma aparece no modelo que a implementaria:

- **O responsável não é parâmetro.** `atualizarTratamentosDoPaciente(tratamento)` recebe apenas o tratamento. A regra "todo tratamento deve conter o responsável que o alterou" não tem onde ser cumprida na assinatura da operação - é a mesma lacuna que existe em `Obito.registrarObito(data, hora)` (**T03**), aqui com consequência clínica imediata.
- **O papel não é verificado na operação.** "Apenas médicos autorizados" depende de a validação acontecer no servidor. Se a restrição estiver só na interface - ocultando o botão em vez de recusar a chamada -, qualquer perfil que alcance o Serviço de Paciente alcança a prescrição.
- **Não há faixa terapêutica.** `dosagemMedicamento` e `intervaloConsumo` são campos livres. Nada no modelo impede gravar uma dose dez vezes maior ou um intervalo de 4 em 4 horas onde deveria ser de 12 em 12.
- **A alteração é destrutiva.** O modelo não prevê versionamento nem histórico: o novo valor substitui o anterior. Não existe "valor antes" para comparar.

**Por que isso é Tampering, e não outra categoria.** O ativo não é lido nem negado: é **modificado**, e o sistema aceita a modificação como legítima. O que distingue esta ameaça das demais do recorte é que o dado adulterado não fica no sistema - ele sai dele. Uma prescrição é executada por uma pessoa sobre outra pessoa: entre o campo alterado e o dano existe apenas a enfermagem cumprindo o que a tela mostra.

**Por que a arquitetura agrava.** Não existe microsserviço de Farmácia. A prescrição vive dentro do Serviço de Paciente, sem limite de confiança próprio, junto do cadastro e do prontuário. Quem alcança o serviço por qualquer caminho alcança também a prescrição - não há uma segunda barreira entre "ver o paciente" e "mudar o remédio dele".

**Impacto.** Segurança do paciente: superdosagem ou subdosagem com dano físico direto, podendo ser fatal, e irreversível assim que o medicamento é administrado. Rastreabilidade: sem autor e sem valor anterior, a apuração recai sobre quem administrou, não sobre quem alterou - o que encadeia diretamente com **T03 (Repudiation)**. Encadeamento de entrada: a alteração é ainda mais fácil a partir de uma conta assumida (**T01**) ou por um perfil que não deveria ter a permissão (**T06**).

### T03 - Repudiation no registro de óbito (@lorenzoficher)

**Onde está no modelo.** A classe `Obito` guarda causa, data e hora, e a operação exposta pelo domínio é `Obito.registrarObito(data, hora)`. O caso de uso UC10 define três regras: somente médicos podem registrar óbito, a causa deve seguir a CID, e após o registro o paciente não pode mais receber atendimentos - o prontuário é encerrado e bloqueado. O ator externo «system» Sistema Governamental recebe esse registro.

**Três lacunas que tornam o registro irrefutável apenas na aparência:**

1. **A operação não recebe o responsável.** `registrarObito(data, hora)` guarda o que aconteceu, mas não quem fez acontecer. A regra "somente médicos podem registrar óbito" está na descrição do caso de uso e não tem onde ser verificada nem, sobretudo, onde ser **registrada**. Uma regra que não deixa rastro não pode ser auditada depois.
2. **A data e a hora são informadas, não carimbadas.** Como ambas chegam por parâmetro, quem registra escolhe o momento que será gravado - inclusive retroativo. O campo que deveria ancorar o registro no tempo é fornecido pela mesma parte cuja conduta ele deveria comprovar.
3. **Não existe trilha de auditoria.** O Tópico 9 do documento original coloca explicitamente fora do escopo do SIGH o **registro de eventos críticos de acesso indevido**. Não há log de operação, de terminal ou de sessão para reconstruir o que a aplicação não guardou.

**Por que isso é Repudiation, e não Tampering.** A ameaça aqui não é alterar um dado existente: é a **ausência de prova** sobre um dado corretamente gravado. O registro de óbito fica no sistema, íntegro e válido - só não é possível atribuí-lo a ninguém. Isso funciona nos dois sentidos, e ambos prejudicam o hospital: quem registrou pode negar, e quem não registrou não pode se defender.

**Por que a irreversibilidade agrava.** Diferente de outras operações, esta encerra o prontuário e bloqueia novos atendimentos. Quando a dúvida sobre a autoria aparece, o registro já produziu efeito administrativo dentro do hospital e já foi transmitido ao Sistema Governamental - uma integração que, como observado na seção 8.2, **não tem requisito funcional documentado**, de modo que nem se sabe se o que trafega leva identificação de responsável. Um registro que não se consegue atribuir já saiu do domínio onde poderia ser contestado.

**Impacto.** Impossibilidade de responsabilização em uma operação de efeito legal e civil. Exposição do médico titular, que responde por um ato que não tem como provar não ter praticado (encadeando com **T01**, quando o acesso vem de conta assumida). E, de forma mais silenciosa: um óbito registrado por engano, ou registrado para encerrar um caso ou liberar um leito, torna-se **indistinguível** de um óbito legítimo - o sistema não oferece nada que permita separar um do outro.

### T05 - Denial of Service por concentração no banco central (@PPrauchner)

**Onde está no modelo.** O diagrama de componentes mostra que os DAOs de todos os serviços - `PacienteDAO`, `AtendimentoPacienteDAO`, `InternacaoPacienteDAO`, `AgendaFuncionarioDAO`, `FuncionarioDAO` - terminam no **mesmo SGBD**, e o diagrama de implantação confirma fisicamente: servidores de aplicação distintos para os módulos de Pacientes, Funcionários e Infraestrutura, ligados por TCP/IP a **um único servidor de banco de dados**. Os dois diagramas estão versionados em `diagrams/estrutura/` e já foram descritos na seção 8.4 pelo @lorenzoficher; o que interessa aqui é a consequência de segurança, não a repetição da leitura. Além do banco, há um segundo ponto de concentração no mesmo caminho: o **API Gateway**, que a seção 8.4.4 registra como passagem obrigatória de toda comunicação entre o Desktop Cliente e qualquer serviço.

**O que a documentação do próprio SIGH confirma.** Esta ameaça não depende de suposição sobre capacidade de hardware: ela nasce de três requisitos não funcionais que a arquitetura projetada contradiz.

- O **RNF01 - Desempenho** exige que o sistema suporte **alto volume de acessos simultâneos**, mas todo acesso, de qualquer um dos 7 serviços, disputa o mesmo conjunto de conexões do SGBD único.
- O **RNF02 - Escalabilidade** exige capacidade de expansão para **outras unidades hospitalares**. Escalar os servidores de aplicação é possível no desenho atual; escalar o banco não - ele é um só, e é onde a carga efetivamente termina.
- O **RNF03 - Disponibilidade** exige operação **24h/7d com métodos de recuperação automática de falhas**, enquanto o diagrama de implantação não prevê réplica, banco secundário nem caminho alternativo ao Gateway. Não há do que recuperar automaticamente: a recuperação exigida pelo requisito não tem componente que a sustente no projeto.

A ameaça está, portanto, **na distância entre o requisito e o projeto** - o mesmo tipo de argumento que a @lilydias24 usou em T01 ao confrontar o RNF05 com o `senhaLogin` em texto simples. Aqui, três requisitos apontam para redundância e capacidade elástica, e o projeto entrega um ponto único.

**Por que isso é Denial of Service, e não outra categoria.** O dado não é lido indevidamente, não é alterado e não é negado a um usuário específico: é o **serviço inteiro** que deixa de existir, ao mesmo tempo, para todos os perfis. Um enfermeiro que precisa consultar `LeitoHospitalar.disponivel` e um médico que precisa abrir o prontuário de um internado falham pela mesma causa, no mesmo instante. E há uma distinção que separa T05 de todas as outras ameaças deste recorte: **ela não exige ator malicioso.** T01 exige quem roube uma credencial, T02 exige quem altere a prescrição, T06 exige quem manipule a requisição de perfil. T05 dispara sozinha - o uso legítimo em pico, um fechamento de faturamento concorrente com o horário de maior movimento assistencial, produz exatamente a condição que um atacante buscaria produzir. É por isso que ela precisa aparecer na análise mesmo em um hospital sem inimigos.

**Por que a arquitetura agrava.** Três características se somam. Primeira: o SGBD é único, então a **origem** da carga é irrelevante para o **efeito** - a emissão de faturas (RF25), que reside no Serviço de Atendimento Médico por não haver microsserviço Financeiro próprio, consome as mesmas conexões de que o Serviço de Internação precisa para alocar um leito. Não existe cota, isolamento nem prioridade entre um módulo administrativo e um módulo assistencial. Segunda: o API Gateway é ponto obrigatório de passagem, o que dá ao atacante um alvo que derruba os 7 serviços sem exigir acesso ao banco. Terceira: a operação `Paciente.buscarPacientePorIdentificador(idPaciente)` usa **identificador sequencial**, o que torna trivial gerar volume de consultas válidas e indistinguíveis de uso legítimo - o mesmo traço que sustenta a exposição de dados em T04 serve aqui como gerador de carga.

Há ainda um segundo caminho, de origem externa: o **«system» Convênio** valida a cobertura de procedimentos (RF06, «extend» de Gerenciar Pacientes) dentro do fluxo de atendimento. O modelo não prevê *timeout* nem modo degradado nessa chamada. Se o convênio ficar lento ou indisponível, o atendimento do hospital trava junto - uma indisponibilidade que o hospital sofre sem que ninguém ataque o hospital, e que está fora do seu controle.

**Impacto.** Assistencial, em primeiro lugar: a indisponibilidade acontece com pacientes internados no prédio, e o que fica inacessível é prontuário, alergias, prescrição em curso e mapa de leitos. Operacional: o atendimento volta ao papel enquanto durar a janela. E de rastreabilidade, que é o encadeamento menos óbvio e o mais duradouro - tudo o que foi feito no papel entra no sistema **depois**, digitado por quem teve tempo, com data e hora informadas por quem digita. Isso reproduz, em escala e de forma legítima, exatamente a condição que sustenta **T03 (Repudiation)**: registros sem autor confiável e sem carimbo de tempo do servidor. Uma indisponibilidade de algumas horas deixa, no prontuário, um rastro que não se consegue auditar por semanas.

### T06 - Elevation of Privilege pelo `nivelAcesso` do Administrador (@PPrauchner)

**Onde está no modelo.** A classe `Administrador` é a única subclasse de `Funcionario` com um atributo de permissão: `nivelAcesso`, um «enum» com os valores Diretor, GerenteGeral, GerenteSetor e Supervisor. Ele reside no **Serviço de Funcionários**, o mesmo que guarda `nomeLogin` e `senhaLogin` de todos os perfis. O modelo não expõe nenhuma operação dedicada a alterar esse campo com regra própria: ele é um atributo do cadastro, salvo junto com o restante dos dados do funcionário. A ameaça é um Administrador de nível **Supervisor** que edita o próprio cadastro e envia `nivelAcesso: Diretor` no corpo da requisição de salvamento, sendo o valor persistido porque nada no servidor verifica se o solicitante tem alçada sobre aquele campo específico.

**O que a documentação do próprio SIGH confirma.** A fundação desta ameaça é a **observação 1 da seção 8.3**, do @ARTHUR9011: *só o Administrador tem nível de acesso graduado; os demais perfis são subclasses de `Funcionario` sem qualquer atributo de permissão*. A consequência precisa ser dita com todas as letras, porque é ela que dá a gravidade: **`nivelAcesso` é o único mecanismo de autorização que existe no modelo inteiro do SIGH.** Elevá-lo não é contornar uma barreira entre várias - é contornar *a* barreira. Fora dele, o que um usuário pode fazer decorre apenas da classe a que pertence, verificada no login (observação 2 da mesma seção).

Dois pontos adicionais do documento original completam a condição:

- O **Tópico 9** coloca explicitamente fora do escopo do SIGH o **registro de eventos críticos de acesso indevido**, e a seção 8.3 registra que **não existe perfil de auditoria**. A elevação não deixa rastro *e* não tem quem a observe: nenhum ator do modelo tem como atribuição revisar alterações de perfil.
- As regras de autorização dos casos de uso - "apenas médicos autorizados podem alterar tratamentos" (UC03), "somente médicos podem registrar óbito" (UC10) - existem como **texto da descrição**, sem contrapartida nos parâmetros das operações. Um sistema que não reforça autorização nas operações clínicas dificilmente a reforça na alteração do próprio campo de autorização.

**Por que isso é Elevation of Privilege, e não Spoofing.** Em T01, o atacante usa a identidade **de outra pessoa**: ele é um estranho vestindo o crachá de um médico. Aqui, o ator **age com a identidade própria**, legitimamente autenticado, com a senha que é dele - o que muda é o conjunto de permissões atado a essa identidade. A distinção não é acadêmica: ela muda a detecção. No caso de credencial roubada existe, ao menos em tese, uma anomalia observável (o médico logado em dois lugares, em horário improvável). Na elevação, o log - se existisse - registraria um Diretor legítimo fazendo o que Diretores fazem. **Não há anomalia a observar**, porque a identidade nunca foi falsificada; foi promovida.

**Por que a arquitetura agrava.** O `nivelAcesso` decide, na prática, quais opções a interface monta. Se a verificação vive apenas nessa montagem - ocultar o botão em vez de recusar a chamada -, então o Desktop Cliente é a única coisa entre o usuário e a operação administrativa, e o Desktop Cliente é justamente a parte que o usuário controla. O firewall de cada serviço, declarado no diagrama de componentes como limite de confiança, separa serviço de serviço; ele não distingue **qual perfil** dentro de uma sessão já autenticada emitiu a chamada. Uma vez elevado, o alcance é o do Administrador Diretor: cadastro de profissionais, escalas e medicamentos, e - o mais grave - os campos `nomeLogin` e `senhaLogin` de **todos** os perfis, que a seção 8.3.2 registra como armazenados em texto simples.

**Impacto.** Confidencialidade e comprometimento em cascata: alcançando as credenciais de todos os funcionários, a elevação **habilita T01 em massa**, sem que seja preciso roubar senha alguma - e a partir daí, prescrever (T02) ou registrar um óbito (T03) em nome de um médico real. Integridade da própria autorização: com poder de cadastro de profissionais, o ator cria contas com perfil de Médico, que o sistema tratará como legítimas desde o primeiro login, porque no SIGH o perfil *é* a permissão. Rastreabilidade: sem trilha de auditoria e sem perfil que audite, não há como estabelecer depois **em que momento** o `nivelAcesso` mudou, nem separar o que o Diretor fez do que o Supervisor promovido fez em nome dele - encadeamento direto com **T03 (Repudiation)**. Juridicamente, o acesso indevido a prontuário e prescrição por essa via viola o sigilo médico e o tratamento de dado pessoal sensível de saúde previsto na LGPD (art. 11).

### 8.5.1 Interpretação da análise

> Rascunho de **@lilydias24**, a ser escrito quando T02 a T06 estiverem preenchidas - parágrafo de leitura conjunta da tabela, mostrando que as ameaças atingem partes diferentes do sistema (identidade, integridade dos dados clínicos, rastreabilidade, confidencialidade, disponibilidade e autorização) e por que nenhuma delas se resolve com um único controle.

## 8.6 Casos de abuso

| ID | Título | STRIDE de origem | Responsável |
| --- | --- | --- | --- |
| CA01 | Uso de credenciais roubadas para assumir a conta de um médico | T01 - Spoofing | @lilydias24 |
| CA02 | Alteração indevida da dosagem de um medicamento prescrito | T02 - Tampering | @ARTHUR9011 |
| CA03 | Registro de óbito sem possibilidade de comprovar quem o realizou | T03 - Repudiation | @lorenzoficher |
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

### CA02 - Alteração indevida da dosagem de um medicamento prescrito

- **Ator:** usuário já autenticado no SIGH com acesso ao Serviço de Paciente - por exemplo um profissional que atualiza prontuário como parte da rotina, ou alguém operando uma sessão de médico deixada aberta em terminal de posto (encadeamento com CA01).
- **Objetivo:** alterar a `dosagemMedicamento` ou o `intervaloConsumo` de uma prescrição ativa de modo que a mudança seja executada pela enfermagem como se fosse a prescrição original, sem ser atribuída a ele nem percebida pela equipe.
- **Condições necessárias:**
  - `atualizarTratamentosDoPaciente(tratamento)` não recebe parâmetro de responsável e não exige reautenticação do papel médico;
  - a regra "apenas médicos autorizados podem alterar tratamentos" (UC03) é textual e depende de validação no servidor que o modelo não especifica;
  - `dosagemMedicamento` e `intervaloConsumo` não têm validação de faixa terapêutica;
  - a alteração sobrescreve o registro, sem versionamento do valor anterior nem registro do autor;
  - não há segunda conferência entre a prescrição e a administração do medicamento;
  - a Farmácia não tem microsserviço próprio: a prescrição está no mesmo limite de confiança do prontuário.
- **Fluxo de abuso:**
  1. O ator autentica-se no SIGH - com a própria conta, se seu perfil já alcança o prontuário, ou com credenciais de médico obtidas como descrito em CA01.
  2. Localiza o paciente por `buscarPacientePorIdentificador(idPaciente)`, pelo caminho Desktop Cliente → API Gateway → Serviço de Paciente.
  3. Abre o `Tratamento` ativo e a `PrescricaoMedicamento` associada, com a dosagem e o intervalo em vigor.
  4. Altera o valor - multiplica a dose, ou reduz o intervalo de 12 para 4 horas - e confirma com `atualizarTratamentosDoPaciente(tratamento)`. O sistema aceita: não valida a faixa, não pede reautenticação, não guarda quem alterou nem qual era o valor anterior.
  5. No horário seguinte, a enfermagem administra o medicamento conforme a prescrição exibida na tela, que agora é a alterada. Nada na interface indica que houve mudança.
  6. O efeito adverso se manifesta no paciente. Ao investigar, o hospital encontra apenas a prescrição atual: sem histórico, sem autor da alteração e sem hora da mudança.

  *Referência técnica do fluxo: o diagrama de sequência DS03 (Gerenciar Tratamento), versionado em `diagrams/sequencia/`, mostra exatamente essa cadeia de chamadas no caminho legítimo. O abuso usa o caminho correto com um valor errado - é por isso que ele não dispara nenhuma exceção.*

- **Impacto esperado:**
  - **Segurança do paciente:** superdosagem ou subdosagem com dano físico direto, potencialmente fatal. É o impacto mais grave do recorte, porque não é mediado por dado - é mediado por corpo, e se torna irreversível no instante em que o medicamento é administrado.
  - **Detecção:** o próprio ato apaga a evidência. Sem valor anterior guardado, não há como distinguir uma prescrição adulterada de uma prescrição legítima.
  - **Responsabilização:** sem autor registrado, a apuração recai sobre o profissional que administrou o medicamento, e não sobre quem alterou a prescrição.
  - **Institucional e legal:** responsabilidade civil do hospital, apuração pelos conselhos profissionais (CFM/COREN) e tratamento indevido de dado de saúde perante a LGPD.
- **Categorias STRIDE relacionadas:** **Tampering** (principal - modificação do dado clínico); **Repudiation** (ausência de autor e de histórico impede provar quem alterou); **Elevation of Privilege** (quando quem altera não tem o papel de médico e a validação só existe na interface); **Spoofing** (quando o acesso vem de uma conta assumida, como em CA01).

### CA03 - Registro de óbito sem possibilidade de comprovar quem o realizou

- **Ator:** profissional com acesso ao Serviço de Internação Médica - o próprio médico responsável pelo paciente, ou alguém operando uma sessão de médico obtida como descrito em CA01.
- **Objetivo:** registrar um óbito - por erro, por pressa, para encerrar um caso ou para liberar um leito - contando com o fato de que o sistema não guarda o autor da operação nem o momento real em que ela ocorreu; ou, tendo registrado, poder negar depois tê-lo feito.
- **Condições necessárias:**
  - `registrarObito(data, hora)` não recebe parâmetro de responsável, e a regra "somente médicos podem registrar óbito" (UC10) existe apenas como texto do caso de uso;
  - data e hora chegam por parâmetro, escolhidos por quem chama, em vez de serem carimbados pelo servidor;
  - não há trilha de auditoria de operação, terminal ou sessão - o Tópico 9 coloca o registro de eventos críticos fora do escopo;
  - o registro encerra e bloqueia o prontuário, dificultando qualquer correção posterior;
  - o dado é transmitido ao «system» Sistema Governamental por uma integração sem requisito funcional documentado.
- **Fluxo de abuso:**
  1. O ator autentica-se no SIGH e abre o prontuário de um paciente internado, pelo caminho Desktop Cliente → API Gateway → Serviço de Internação Médica.
  2. Aciona o registro de óbito, informando a causa segundo a CID e a data e hora que julgar convenientes - inclusive retroativas, já que o sistema aceita os valores enviados.
  3. O sistema grava o `Obito`, encerra o prontuário e bloqueia novos atendimentos para aquele paciente.
  4. O registro é transmitido ao Sistema Governamental, saindo do domínio do hospital.
  5. Semanas depois, a família ou a própria instituição contesta a data, a hora ou a causa, e uma apuração é aberta.
  6. Ao consultar o sistema, a apuração encontra o registro íntegro - mas não encontra quem o criou, de qual terminal, nem em que momento real. Os únicos carimbos temporais existentes são os que foram digitados.

  *Referência técnica do fluxo: o diagrama de sequência DS10 (Registrar Óbito), versionado em `diagrams/sequencia/`, mostra a cadeia de chamadas do caminho legítimo. O abuso aqui não desvia do caminho - o problema é que o caminho não registra quem o percorreu.*

- **Impacto esperado:**
  - **Impossibilidade de responsabilização:** é o núcleo da ameaça. A operação de maior efeito legal do sistema é também a que menos evidência produz.
  - **Exposição do médico titular:** se o registro veio de sua conta, ele não dispõe de nada que demonstre não ter sido o autor - e o hospital não dispõe de nada que o inocente.
  - **Efeito externo já consumado:** o dado foi transmitido ao Sistema Governamental antes de qualquer conferência, e a integração não está documentada a ponto de se saber o que foi enviado.
  - **Encobrimento:** um óbito registrado por engano ou por conveniência administrativa fica indistinguível de um óbito legítimo, o que impede não só a punição como a própria detecção do erro.
- **Categorias STRIDE relacionadas:** **Repudiation** (principal - ausência de autoria e de carimbo confiável de tempo); **Spoofing** (quando o registro parte de uma conta assumida, como em CA01); **Tampering** (a data e a hora escolhidas por quem registra adulteram o próprio conteúdo do registro); **Elevation of Privilege** (se quem registra não é médico e a restrição existe apenas na interface).

## 8.7 Considerações finais (Etapa 1)

> Rascunho de responsabilidade de **@lilydias24**, com revisão de todos - a ser escrito após a conclusão de 8.3 a 8.6.

- **Ameaças mais preocupantes:**
- **Ativos mais importantes:**
- **Tipos de abuso de maior impacto:**
- **Principais dificuldades encontradas pelo grupo:**
