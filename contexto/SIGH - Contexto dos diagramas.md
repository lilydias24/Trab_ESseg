# **SIGH \- Documentação de Contexto dos Diagramas (Lucid)**

*Compilado a partir dos documentos Lucid do grupo (Diagramas\_SIGH, DAtividades\_SIGH e DSequência SIGH), cruzados com o enunciado original em PDF do trabalho de APS. Serve como material de contexto para o grupo aplicar STRIDE e a análise de riscos do ESSEG sobre o SIGH.*

# **1\. Documentos-fonte no Lucid**

Os três documentos localizados no Lucid do grupo:

[Diagramas\_SIGH \- Casos de Uso, Classes, Pacotes, Componentes, Mapeamento relacional e Implantação](https://lucid.app/lucidchart/9dc2a6ef-b83e-4415-81e1-d242371140fe/edit)

[DAtividades\_SIGH \- Diagramas de atividade (ACT01 a ACT10)](https://lucid.app/lucidchart/0141484c-dde8-472d-97c3-ad20c215a69b/edit)

[DSequência SIGH \- Diagramas de sequência (DS01 a DS10, DS1.1 e DS1.2)](https://lucid.app/lucidchart/b26b5fc3-6c18-4dae-a730-236478997840/edit)

*Observação técnica: as imagens exportadas destes diagramas foram exibidas no chat para conferência visual, mas não há como incorporá-las automaticamente a este .docx \- os links acima abrem os documentos originais no Lucid, prontos para exportar como PNG/SVG e versionar no repositório do ESSEG.*

# **2\. Diagrama de Casos de Uso**

O diagrama de casos de uso do Lucid é mais completo que a versão exportada no PDF original: inclui explicitamente o ator externo «System» Sistema Governamental, ligado a Registrar Óbito \- o que não aparecia com clareza no PDF.

## 2.1 Atores identificados

| Ator | Tipo | Principais casos de uso ligados |
| ----- | ----- | ----- |
| Recepcionista | Humano | Gerenciar Pacientes, Agendar Consultas, Registrar Visitas Familiares |
| Enfermeiro | Humano | Realizar Triagem, Registrar Baixa Hospitalar, Gerenciar Leitos, Gerenciar Transferências Hospitalares, Atualizar Prontuário, Registrar Exame |
| Médico | Humano | Autorizar Alta Hospitalar, Registrar Cirurgia, Agendar Cirurgias, Registrar Consulta, Gerenciar Tratamento, Prescrever Exames, Registrar Óbito |
| Administrador | Humano | Gerenciar Equipes Médicas, Gerenciar Escalas de Trabalho, Gerenciar Funcionários, Gerenciar Medicamentos |
| Nutricionista | Humano (fora do escopo filtrado) | Gerenciar Dietas, Gerenciar Refeições |
| «System» Convênio | Sistema externo | Validar Plano de Convênio (‹‹extend›› de Gerenciar Pacientes) |
| «System» Sistema Governamental | Sistema externo | Recebe o registro de Registrar Óbito |

## 2.2 Relações «extend» relevantes

* Gerenciar Pacientes → Validar Plano de Convênio

* Atualizar Prontuário → Registrar Exame

* Registrar Consulta → Gerenciar Tratamento

* Registrar Consulta → Agendar Cirurgias

Essas relações são úteis para casos de abuso encadeados \- ex.: um caso de abuso em 'Gerenciar Pacientes' pode se propagar para 'Validar Plano de Convênio' se a integração com o convênio não validar a origem da chamada.

# **3\. Modelo de Domínio (classes)**

O Lucid tem duas versões do diagrama de classes: uma 'Modelo Conceitual' (atributos apenas) e uma 'Modelo de Domínio' mais completa, com métodos/operações \- esta é a mais útil para threat modeling, pois expõe as operações que o sistema expõe (equivalentes a endpoints/casos de uso técnicos).

## 3.1 Classes e campos sensíveis relevantes ao escopo filtrado

| Classe | Campos sensíveis | Observação de segurança |
| ----- | ----- | ----- |
| Funcionario (superclasse de Médico, Enfermeiro, Recepcionista, Administrador) | nomeLogin, senhaLogin, cpfFuncionario, telefoneFuncionario | Senha aparece como atributo de texto na classe \- não há indicação de hashing/criptografia no modelo. Ponto central para ameaças de Spoofing. |
| Administrador | nivelAcesso («enum» Diretor, GerenteGeral, GerenteSetor, Supervisor) | Base para Elevation of Privilege \- verificar se a aplicação valida nivelAcesso em cada operação sensível. |
| Paciente | cpfPaciente, dataNascimento, tipoSanguineo, contatoEmergencial, convenio | Dado pessoal/sensível de saúde \- ativo central para Information Disclosure. |
| PrescricaoMedicamento / Tratamento | dosagemMedicamento, intervaloConsumo, medicamentos | Alteração indevida tem impacto direto na segurança física do paciente \- ativo crítico para Tampering. |
| Consulta / Exame | valorConsulta, valorExame, medicoResponsavel | Envolve dado financeiro por atendimento \- relevante para o módulo de Faturamento. |
| Obito | causa/motivo, data, hora | Operação irreversível (bloqueia o prontuário) \- ótimo caso de Repudiation/Tampering. |
| LeitoHospitalar / Ocupacao | pacienteAlocado, disponivel | Concorrência de alocação de leito é superfície para Tampering/DoS lógico. |

## 3.2 Operações relevantes expostas pelo domínio

* Paciente.buscarPacientePorIdentificador(idPaciente) \- busca por ID sequencial; validar se há checagem de autorização (risco de IDOR/Information Disclosure)

* Paciente.atualizarTratamentosDoPaciente(tratamento) \- ponto de Tampering se não exigir reautenticação do papel médico

* LeitoHospitalar.alocarPaciente / desalocarPaciente \- pontos de condição de corrida (dois enfermeiros podem tentar alocar o mesmo leito)

* Obito.registrarObito(data, hora) \- não há campo de 'responsável' explícito nas operações, apenas na regra de negócio textual ("somente médicos podem registrar óbito") \- vale verificar se isso é reforçado no código ou só na documentação

# **4\. Arquitetura de microsserviços (Pacotes \+ Componentes)**

O diagrama de pacotes confirma a arquitetura de microsserviços citada no texto do trabalho original, com 7 serviços identificados, cada um dividido em 5 camadas (Visão, Controle, Negócio, Persistência, BancoDeDados):

* Serviço de Paciente

* Serviço de Atendimento Médico

* Serviço de Internação Médica

* Serviço de Agenda

* Serviço de Acompanhamento Médico

* Serviço de Funcionários

* Serviço de Refeições

Todos os serviços se conectam a um único API Gateway central, que por sua vez atende o Desktop Cliente.

## 4.1 Achado importante para a modelagem de ameaças

Não existe um microsserviço próprio para Farmácia/Medicamentos nem para Financeiro/Cobrança no diagrama de componentes \- apesar de esses módulos terem requisitos funcionais dedicados no documento original (RF21-RF24 e RF25). Ou seja, a arquitetura documentada cobre bem os módulos de Paciente, Atendimento e Internação, mas farmácia e faturamento parecem estar implicitamente dentro de outro serviço (provavelmente Paciente ou Atendimento), sem um limite de confiança (trust boundary) próprio.

Para o ESSEG, isso pode ser tratado de duas formas: (a) assumir que Medicamento/Prescrição e Consulta/Cobrança residem dentro do Serviço de Paciente e do Serviço de Atendimento Médico respectivamente, ou (b) registrar essa ausência de separação como um achado da própria análise de ameaças \- a falta de isolamento entre dados financeiros/farmacêuticos e dados clínicos gerais é, em si, uma condição que amplia o impacto de Information Disclosure.

## 4.2 Componentes internos observados (Diagrama de Componentes)

Cada serviço é protegido por um componente Firewall próprio antes de expor sua Fachada/DAO \- por exemplo: PacienteDAO, AtendimentoPacienteDAO, InternacaoPacienteDAO, AgendaFuncionarioDAO, FuncionarioDAO, RefeicaoDAO, AcompanhamentoPacienteDAO, todos com marcação ‹‹persistent›› e conectados ao SGBD central.

# **5\. Diagrama de Implantação**

Confirma fisicamente a separação em módulos: Módulo de Pacientes, Módulo de Funcionários e Módulo de Infraestrutura (que agrupa Internação e Refeições) rodam em Servidores de Aplicação distintos, todos se conectando via TCP/IP a um Servidor de Comunicação (Servidor Proxy \+ API Gateway) e a um Servidor de Firewall \- e daí a um Servidor de Banco de Dados único (SGBD).

Ponto relevante: o SGBD é único e centralizado, mesmo com bancos logicamente separados por serviço \- reforça o Servidor de Banco de Dados como ativo crítico único de Denial of Service e ponto de falha compartilhado entre todos os módulos analisados.

# **6\. Mapeamento de Classes em Tabelas Relacionais**

Diferente do que constava no PDF entregue (onde a seção aparecia vazia), o Lucid tem esse diagrama preenchido, com chaves primárias e estrangeiras explícitas (ex.: PK\_Administrador, FK\_Administrador\_Acesso, PK\_Paciente, FK\_MedicamentoPrescricaoMedicamento\_Medicamento). Vale a pena abrir o link do Lucid para conferir o mapeamento completo antes de detalhar ativos de banco de dados na seção 8.3 do documento do ESSEG.

# **7\. Diagramas de Atividade e Sequência**

Os documentos DAtividades\_SIGH (11 páginas) e DSequência SIGH (12 páginas) têm exatamente uma página por caso de uso do PDF original \- ACT01 a ACT10, e DS01 a DS10 mais DS1.1/DS1.2 (representação externa/interna de Realizar Triagem). Isso confirma que não há atividades ou sequências adicionais além das já documentadas no PDF do trabalho original.

| Caso de uso | Está no escopo filtrado do ESSEG? | Diagramas associados |
| ----- | ----- | ----- |
| UC01 – Realizar Triagem | Sim | ACT01, DS01, DS1.1, DS1.2 |
| UC02 – Agendar Consultas | Sim | ACT02, DS02 |
| UC03 – Gerenciar Tratamento | Sim | ACT03, DS03 |
| UC04 – Agendar Cirurgia | Não (módulo Cirurgias excluído) | ACT04, DS04 |
| UC05 – Registrar Consulta | Sim | ACT05, DS05 |
| UC06 – Autorizar Alta Hospitalar | Sim | ACT06, DS06 |
| UC07 – Registrar Cirurgia | Não (módulo Cirurgias excluído) | ACT07, DS07 |
| UC08 – Registrar Baixa Hospitalar | Sim | ACT08, DS08 |
| UC09 – Registrar Exame | Sim | ACT09, DS09 |
| UC10 – Registrar Óbito | Sim | ACT10, DS10 |

Os diagramas de sequência são especialmente úteis para escrever o "fluxo de abuso" dos casos de abuso (seção 8.6 do ESSEG), pois já mostram a chamada técnica passo a passo até o API Gateway \- por exemplo, DS01 mostra Enfermeiro → Desktop Cliente → API Gateway → Paciente/Triagem com as chamadas buscarPacientePorIdentificador e registrarTriagem.

# **8\. Inconsistências e lacunas identificadas (consolidado)**

* O sumário do PDF original pula o \[DS08\] no índice, mas o diagrama existe normalmente no corpo \- erro apenas de indexação.

* A seção 'Diagrama de Classes \- Conceitual' (item 5 do PDF) aparecia vazia; no Lucid ela de fato existe como um diagrama mais simples (só atributos), diferente do 'Modelo de Domínio' (item 8, com atributos e operações).

* A seção 'Mapeamento de Classes em Tabelas Relacionais' (item 12 do PDF) aparecia vazia no PDF, mas está preenchida no Lucid \- o grupo pode reaproveitar direto de lá.

* O ator «System» Sistema Governamental não tem nenhum RF documentado explicando a integração (diferente de Convênio e Sistema de Laboratório, que têm RF06 e RF28) \- lacuna do documento original.

* «System» Sistema de Laboratório aparece no RF28, mas não aparece no diagrama de Casos de Uso nem no de Componentes \- a integração com laboratório parece ter sido descrita em texto, mas não modelada nos diagramas.

* Não há microsserviço dedicado para Farmácia/Medicamentos nem para Financeiro/Cobrança na arquitetura de componentes, apesar de existirem requisitos funcionais específicos para esses módulos (ver seção 4.1 acima).

# **9\. Como usar este documento**

Este arquivo é material de apoio/contexto \- não substitui o documento oficial do ESSEG (docs/modelagem-de-ameacas.md). Use-o para:

* Preencher a seção 8.4 (arquitetura) com base nos diagramas de Componentes e Implantação

* Preencher a seção 8.3 (ativos) com base na tabela de campos sensíveis da seção 3.1 deste documento

* Escrever os fluxos de abuso (8.6) usando os diagramas de sequência como referência técnica

* Justificar ameaças de Spoofing e Elevation of Privilege citando a ausência de hashing visível em senhaLogin e a presença do enum nivelAcesso

---

### **Verificação \- Diagramas úteis para o ESSEG (por seção do enunciado)**

| Diagrama | Uso no ESSEG |
| ----- | ----- |
| **Diagrama de Componentes** | O mais valioso de todos. Já mostra os *trust boundaries* (cada serviço com seu próprio Firewall) e o API Gateway centralizando tudo \- praticamente pronto para virar a base do item **8.4 (visão geral da arquitetura)** |
| **Diagrama de Implantação** | Ótimo complemento ao de Componentes: mostra a superfície de rede (TCP/IP entre navegador, firewall, gateway, servidores de aplicação, banco). Excelente para justificar ameaças de **Denial of Service** no Gateway/Servidor de Comunicação |
| **Diagrama de Casos de Uso** | Útil para extrair os atores e recortar visualmente só os casos de uso dos 5 módulos escolhidos \- dá pra editar e remover os ramos de Cirurgia, Nutrição, Restaurantes etc. |
| **Diagrama de Classes \- Modelo de Domínio** | Útil para o item **8.3 (ativos)** \- mostra exatamente quais campos existem (ex. senhaLogin, cpfPaciente, nivelAcesso), o que ajuda a justificar com precisão os riscos de Information Disclosure |
| **Diagramas de Sequência** DS01, DS02, DS03, DS06, DS08, DS09, DS10 | Muito úteis para casos de abuso: mostram passo a passo a chamada até o API Gateway, ótimo pra descrever o "fluxo de abuso" de forma tecnicamente precisa |
| **Diagramas de Atividade** ACT01, ACT02, ACT03, ACT06, ACT08, ACT09, ACT10 | Mesma utilidade que os de sequência, mas em nível mais funcional/visual \- bons para ilustrar o STRIDE junto ao fluxo normal |
| **\[DS1.1\]/\[DS1.2\] Triagem (Representação Externa/Interna)** | Interessante para mostrar a comunicação *entre* microsserviços (Serviço de Paciente ↔ Serviço de Atendimento), reforçando a análise do Gateway como ponto único de falha |

