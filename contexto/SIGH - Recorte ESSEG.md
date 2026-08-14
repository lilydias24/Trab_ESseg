# **SIGH \- Recorte de Documentação para o ESSEG** 

# **1\. Descrição geral (adaptada)**

O Sistema Integrado de Gestão Hospitalar (SIGH) é um software para gerenciar os principais aspectos operacionais de um hospital, cobrindo o cadastro e prontuário de pacientes, o atendimento médico e agendamento de consultas, o controle de internações e leitos, a farmácia e prescrição de medicamentos e a administração financeira e cobrança. O sistema integra diferentes setores do hospital, permitindo o fluxo de informações entre médicos, enfermeiros, administrativos e sistemas externos (convênios e laboratórios), com foco em qualidade e segurança no atendimento ao paciente.

# **2\. Módulos incluídos e excluídos do escopo**

## *2.1 Incluídos (base da análise de segurança)*

| Módulo | Por que foi mantido |
| :---- | :---- |
| Cadastro e Gerenciamento de Pacientes | Dado mais sensível do sistema (histórico médico, alergias, medicações) \- base para Information Disclosure |
| Gestão de Atendimento Médico e Consultas | Múltiplos perfis interagindo (recepcionista, enfermeiro, médico) \+ integração externa (convênio) \- base para Spoofing e Tampering |
| Gestão de Internações e Unidades Hospitalares | Operações de alta impacto (alta hospitalar, alocação de leitos) \- base para Tampering e Repudiation |
| Farmácia e Gestão de Medicamentos | Prescrição incorreta tem impacto direto na segurança do paciente \- base para Tampering e Elevation of Privilege |
| Administração Financeira e Cobrança | Dados de pagamento e faturamento \- base para Tampering e Information Disclosure |

## *2.2 Excluídos deste recorte*

Cirurgias e Procedimentos, Emergências e Atendimento Pré-Hospitalar, Ambulâncias/Transporte, Pesquisa Científica, Telemedicina, Nutrição Hospitalar, Restaurantes/Lojas internas.

Se o grupo quiser aumentar a análise depois, Cirurgias é o módulo excluído com maior potencial.

# **3\. Requisitos funcionais mantidos**

### Tópico 1 \- Cadastro e Gerenciamento de Pacientes

| RF01 | Registro completo de pacientes, incluindo histórico médico, alergias, medicações em uso e comorbidades. \- **Obrigatório** \- Médico, Enfermeiro | | RF02 | Armazenamento de exames laboratoriais, radiológicos e outros diagnósticos. \- **Obrigatório** \- Médico, Enfermeiro | | RF03 | Monitoramento de vacinas e tratamentos em andamento. \- **Obrigatório** \- Médico |

### Tópico 2 \- Gestão de Atendimento Médico e Consultas

| RF04 | Agendamento de consultas médicas presenciais. \- **Obrigatório** \- Recepcionista | | RF05 | Classificação automática da urgência com base em sintomas informados pelo paciente. \- **Importante** \- Enfermeiro | | RF06 | Integração com convênios médicos e validação de cobertura de procedimentos. \- **Obrigatório** \- «system» Convênio | | RF07 | Interface para médicos registrarem anamneses, prescrições e encaminhamentos. \- **Obrigatório** \- Médico |

### Tópico 3 \- Gestão de Internações e Unidades Hospitalares

| RF08 | Controle de disponibilidade e ocupação de leitos (enfermaria, UTI, isolamento, maternidade, pediatria etc.). \- **Obrigatório** \- Enfermeiro | | RF09 | Registro detalhado de pacientes internados, incluindo evolução clínica e protocolos de tratamento. \- **Obrigatório** \- Médico, Enfermeiro | | RF10 | Painel de gestão de altas médicas, facilitando a liberação e alocação de novos pacientes. \- **Importante** \- Enfermeiro |

### Tópico 8 \- Farmácia e Gestão de Medicamentos

| RF21 | Controle de estoque de medicamentos, insumos e equipamentos hospitalares. \- **Obrigatório** \- Enfermeiro | | RF22 | Registro e rastreamento de prescrição de medicamentos para cada paciente. \- **Obrigatório** \- Médico | | RF23 | Monitoramento de vencimentos e restrições de uso de determinados fármacos. \- **Obrigatório** \- Enfermeiro | | RF24 | Integração com farmácias externas para compra e reposição de insumos críticos. \- **Obrigatório** \- Enfermeiro |

### Tópico 10 \- Administração Financeira e Cobrança

| RF25 | Emissão de faturas e controle de pagamentos de consultas, exames e internações. \- **Obrigatório** \- Recepcionista |

### Nota de segurança já identificada no documento original (Tópico 9\)

O documento original marca como fora do escopo do SIGH: monitoramento por câmeras, controle físico de visitantes, biometria/reconhecimento facial e registro de eventos críticos de acesso indevido. O próprio sistema reconhece que não há controle de acesso físico nem autenticação forte especificada \- ponto de partida útil para justificar ameaças de Spoofing e Elevation of Privilege.

# **4\. Requisitos não funcionais (mantidos integralmente)**

| RNF01 \- Desempenho | O sistema deve suportar alto volume de acessos simultâneos. |
| :---- | :---- |
| RNF02 \- Escalabilidade | Deve ser escalável para expansão a outras unidades hospitalares. |
| RNF03 \- Disponibilidade | Deve operar 24h/7d com métodos de recuperação automática de falhas. |
| RNF04 \- Proteção | Nenhum dado crítico pode ser perdido em caso de falha do sistema. |
| RNF05 \- Segurança | As informações médicas devem ser protegidas por criptografia. |
| RNF06 \- Integração | Deve permitir integração com sistemas governamentais de saúde, laboratórios e fornecedores. |
| RNF07 \- Usabilidade | O sistema deve possuir interface intuitiva para uso de profissionais de diferentes níveis de formação. |
| RNF08 \- Acessibilidade | Deve oferecer suporte a acessibilidade para deficientes visuais e auditivos. |

# **5\. Atores do sistema (escopo filtrado \- confirmado no Lucid)**

| Ator | Papel |
| :---- | :---- |
| Médico | Registra prontuário, prescreve medicamentos, autoriza altas, registra consultas, registra óbito |
| Enfermeiro | Realiza triagem, controla leitos, gerencia estoque de medicamentos, registra baixa hospitalar, atualiza prontuário, registra exame |
| Recepcionista | Agenda consultas, emite faturas e controla pagamentos, gerencia cadastro de pacientes |
| Administrador | Cadastra profissionais, gerencia escalas, gerencia medicamentos (nível de acesso: Diretor / Gerente Geral / Gerente de Setor / Supervisor) |
| «system» Convênio | Sistema externo que valida cobertura de procedimentos (‹‹extend›› de Gerenciar Pacientes) |
| «system» Sistema de Laboratório | Sistema externo que envia resultados de exames (citado no RF28, mas não modelado nos diagramas de Casos de Uso/Componentes \- lacuna do documento original) |
| «system» Sistema Governamental | Recebe o registro de óbito \- aparece no diagrama de Casos de Uso do Lucid, mas sem RF próprio documentado |

### Relações «extend» relevantes para casos de abuso encadeados

- Gerenciar Pacientes → Validar Plano de Convênio  
- Atualizar Prontuário → Registrar Exame  
- Registrar Consulta → Gerenciar Tratamento

# **6\. Ativos e campos sensíveis (extraídos do Modelo de Domínio no Lucid)**

| Classe | Campos sensíveis | Observação de segurança |
| :---- | :---- | :---- |
| Funcionario (superclasse de Médico, Enfermeiro, Recepcionista, Administrador) | nomeLogin, senhaLogin, cpfFuncionario, telefoneFuncionario | Senha aparece como atributo de texto simples \- **sem indicação de hashing/criptografia no modelo**. Ponto central para Spoofing. |
| Administrador | nivelAcesso («enum»: Diretor, GerenteGeral, GerenteSetor, Supervisor) | Base para Elevation of Privilege \- verificar se cada operação sensível valida o nível de acesso. |
| Paciente | cpfPaciente, dataNascimento, tipoSanguineo, contatoEmergencial, convenio | Dado pessoal/sensível de saúde \- ativo central para Information Disclosure. |
| PrescricaoMedicamento / Tratamento | dosagemMedicamento, intervaloConsumo, medicamentos | Alteração indevida tem impacto direto na segurança física do paciente \- ativo crítico para Tampering. |
| Consulta / Exame | valorConsulta, valorExame, medicoResponsavel | Dado financeiro por atendimento \- relevante para o módulo de Faturamento. |
| Obito | causa/motivo, data, hora | Operação irreversível (bloqueia o prontuário) \- bom caso de Repudiation/Tampering. |
| LeitoHospitalar / Ocupacao | pacienteAlocado, disponivel | Concorrência de alocação é superfície para Tampering/DoS lógico. |

### Operações relevantes expostas pelo domínio

- Paciente.buscarPacientePorIdentificador(idPaciente) \- busca por ID sequencial; validar se há checagem de autorização (risco de IDOR/Information Disclosure)  
- Paciente.atualizarTratamentosDoPaciente(tratamento) \- ponto de Tampering se não exigir reautenticação do papel médico  
- LeitoHospitalar.alocarPaciente / desalocarPaciente \- condição de corrida possível (dois enfermeiros podem tentar alocar o mesmo leito)  
- Obito.registrarObito(data, hora) \- a regra "somente médicos podem registrar óbito" está descrita só em texto, não reforçada nos parâmetros da operação \- vale checar se é validada de fato

# **7\. Arquitetura (microsserviços \- confirmado no Lucid)**

7 serviços identificados no diagrama de Pacotes, cada um dividido em 5 camadas (Visão, Controle, Negócio, Persistência, BancoDeDados), todos conectados a um API Gateway central, que atende o Desktop Cliente:

- Serviço de Paciente  
- Serviço de Atendimento Médico  
- Serviço de Internação Médica  
- Serviço de Agenda  
- Serviço de Acompanhamento Médico  
- Serviço de Funcionários  
- Serviço de Refeições *(fora do escopo filtrado)*

Cada serviço tem um componente Firewall próprio antes de expor seu DAO (ex.: PacienteDAO, AtendimentoPacienteDAO, InternacaoPacienteDAO, AgendaFuncionarioDAO, FuncionarioDAO), todos conectados a um SGBD único e centralizado.

## *➯ Achado importante para a modelagem STRIDE :* 

Não existe microsserviço dedicado para Farmácia/Medicamentos nem para Financeiro/Cobrança, apesar de esses módulos terem requisitos funcionais próprios (RF21-24 e RF25). Duas leituras possíveis para o ESSEG:

1. Assumir que Medicamento/Prescrição e Consulta/Cobrança residem dentro do Serviço de Paciente e do Serviço de Atendimento Médico, respectivamente; ou  
2. Registrar essa ausência de separação como achado da própria análise de ameaças \- a falta de isolamento entre dados clínicos, farmacêuticos e financeiros amplia o raio de impacto de qualquer vazamento (bom argumento para justificar Impacto alto em riscos de Information Disclosure na Etapa 2).

## *Diagrama de Implantação:*

Confirma fisicamente a separação: Módulo de Pacientes, Módulo de Funcionários e Módulo de Infraestrutura (Internação \+ Refeições) rodam em Servidores de Aplicação distintos, conectados via TCP/IP a um Servidor de Comunicação (Proxy \+ API Gateway) e a um Servidor de Firewall, e daí a um Servidor de Banco de Dados único (SGBD) \- ponto de falha compartilhado por todos os módulos, relevante para Denial of Service.

# **8\. Casos de uso mantidos**

*(UC04 – Agendar Cirurgia e UC07 – Registrar Cirurgia foram removidos deste recorte, pois pertencem ao módulo de Cirurgias, fora do escopo filtrado.)*

### \[UC01\] Realizar Triagem

| Ator Principal | Enfermeiro |
| :---- | :---- |
| Pré Condições | Paciente previamente cadastrado e presente na unidade. |
| Pós Condições | Dados da triagem registrados no prontuário. |
| Regras de Negócio | Apenas enfermeiros autorizados podem realizar triagens; dados disponíveis imediatamente para médicos; campos obrigatórios: pressão arterial, temperatura, frequência cardíaca. |
| Diagramas associados | ACT01, DS01, DS1.1 (representação externa), DS1.2 (representação interna) |

### \[UC02\] Agendar Consultas

| Ator Principal | Recepcionista |
| :---- | :---- |
| Pré Condições | Paciente previamente cadastrado. |
| Pós Condições | Consulta registrada na agenda do profissional. |
| Regras de Negócio | Não é possível agendar dois horários simultâneos para o mesmo paciente; sistema impede agendamento fora do expediente. |
| Diagramas associados | ACT02, DS02 |

### \[UC03\] Gerenciar Tratamento

| Ator Principal | Médico |
| :---- | :---- |
| Pré Condições | Paciente com prontuário ativo. |
| Pós Condições | Plano de tratamento (e/ou prescrição) registrado ou atualizado. |
| Regras de Negócio | Apenas médicos autorizados podem alterar tratamentos; todo tratamento deve conter o responsável que o alterou; não é possível dois tratamentos ativos simultâneos para o mesmo problema. |
| Diagramas associados | ACT03, DS03 |

### \[UC05\] Registrar Consulta

| Ator Principal | Médico |
| :---- | :---- |
| Pré Condições | Paciente com agendamento válido e prontuário disponível. |
| Pós Condições | Informações da consulta registradas no prontuário. |
| Regras de Negócio | Apenas médicos cadastrados podem realizar consultas; nenhuma consulta pode ser finalizada sem anamnese; exames e prescrições devem ser associados ao atendimento. Pode disparar UC03 (Gerenciar Tratamento) ou UC04 (Agendar Cirurgia). |
| Diagramas associados | ACT05, DS05 |

### \[UC06\] Autorizar Alta Hospitalar

| Ator Principal | Médico |
| :---- | :---- |
| Pré Condições | Paciente internado com prontuário ativo. |
| Pós Condições | Alta autorizada no prontuário; paciente desalocado do leito. |
| Regras de Negócio | Apenas médicos autorizados podem autorizar altas; justificativa obrigatória. |
| Diagramas associados | ACT06, DS06 |

### \[UC08\] Registrar Baixa Hospitalar

| Ator Principal | Enfermeiro |
| :---- | :---- |
| Pré Condições | Paciente registrado no hospital. |
| Pós Condições | Registro de baixa e alocação de leito registrados. |
| Regras de Negócio | Só pode ser registrada pelo enfermeiro responsável; cada leito só pode ser atribuído a um paciente por vez. |
| Diagramas associados | ACT08, DS08 |

### \[UC09\] Registrar Exame

| Ator Principal | Médico/Enfermeiro |
| :---- | :---- |
| Pré Condições | Prontuário ativo; exame previamente solicitado; profissional autenticado e autorizado. |
| Pós Condições | Exame registrado no prontuário; médico solicitante pode acessar os resultados. |
| Diagramas associados | ACT09, DS09 |

### \[UC10\] Registrar Óbito

| Ator Principal | Médico |
| :---- | :---- |
| Pré Condições | Paciente internado ou em acompanhamento. |
| Pós Condições | Registro de óbito salvo; prontuário encerrado e bloqueado para novos atendimentos. |
| Regras de Negócio | Somente médicos podem registrar óbito; causa deve seguir a CID; após o registro, o paciente não pode mais receber atendimentos \- **operação irreversível, alto valor para Tampering e Repudiation**. |
| Diagramas associados | ACT10, DS10 |

# **9\. Documentos-fonte no Lucid (para consulta e exportação de imagens)**

| Documento | Conteúdo | Link |
| :---- | :---- | :---- |
| Diagramas\_SIGH | Casos de Uso, Classes (Conceitual e Modelo de Domínio), Pacotes, Componentes, Mapeamento relacional, Implantação | [https://lucid.app/lucidchart/9dc2a6ef-b83e-4415-81e1-d242371140fe/edit](https://lucid.app/lucidchart/9dc2a6ef-b83e-4415-81e1-d242371140fe/edit) |
| DAtividades\_SIGH | Diagramas de atividade ACT01–ACT10 | [https://lucid.app/lucidchart/0141484c-dde8-472d-97c3-ad20c215a69b/edit](https://lucid.app/lucidchart/0141484c-dde8-472d-97c3-ad20c215a69b/edit) |
| DSequência SIGH | Diagramas de sequência DS01–DS10, DS1.1, DS1.2 | [https://lucid.app/lucidchart/b26b5fc3-6c18-4dae-a730-236478997840/edit](https://lucid.app/lucidchart/b26b5fc3-6c18-4dae-a730-236478997840/edit) |

> Os diagramas dessas páginas precisam ser exportados como imagem (PNG/SVG) e versionados de fato na pasta diagramas/ do repositório do ESSEG \- não é permitido apenas linkar a ferramenta externa.

# **10\. Inconsistências e lacunas identificadas (consolidado)**

- «System» Sistema Governamental não tem RF documentado (diferente de Convênio/RF06 e Laboratório/RF28).  
- «System» Sistema de Laboratório aparece no RF28, mas não aparece nos diagramas de Casos de Uso nem de Componentes.  
- Não há microsserviço dedicado para Farmácia nem para Financeiro na arquitetura de componentes (ver seção 7).

