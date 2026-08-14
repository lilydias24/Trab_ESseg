# Etapa 3 - Projeto de uma Arquitetura Segura

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @lorenzoficher
> São exigidos **3 requisitos de segurança**, e não um por integrante. O grupo levou adiante os riscos mais críticos e que cobrem categorias distintas de controle: autenticação, integridade de dados e autorização.

| Item | Responsável | Situação |
| --- | --- | --- |
| RS01 - requisito e vulnerabilidade | @lilydias24 | Concluído (aguarda revisão cruzada) |
| RS02 - requisito e vulnerabilidade | @ARTHUR9011 | Concluído (aguarda revisão cruzada) |
| RS03 - requisito e vulnerabilidade | @PPrauchner | Concluído; revisão cruzada com as Etapas 4 e 6 feita (critérios de CA02, CA03 e CA04 conciliados); apoia-se na DA02 |
| Diagrama da arquitetura segura | @lorenzoficher | Concluído (seções 3.1 a 3.3 e PNG versionado) |
| Decisão de arquitetura 1 (ligada ao diagrama) | @lorenzoficher | Concluída (DA01) |
| Decisão de arquitetura 2 (ligada a RS03) | @mariasanchez0 | Concluída (DA02) |
| Decisão de arquitetura 3 (reforço de autenticação) | @lilydias24 | Concluída (DA03; ponto de contato com a DA01 sinalizado) |
| Conciliação entre DA01 e DA03 | @lorenzoficher | Concluída (responde ao ponto levantado na DA03) |

---

## 1. Requisitos de segurança

| ID | Risco de origem | Requisito de segurança | Critério de verificação | Responsável |
| --- | --- | --- | --- | --- |
| RS01 | R01 - Spoofing | O sistema deve exigir autenticação multifator no login e reautenticação antes de operações sensíveis envolvendo a conta de `Funcionario` | Operação sensível pedida sem segundo fator válido ou fora da janela de reautenticação é recusada, e o valor persistido em `senhaLogin` não é diretamente reutilizável (RS01-CA01 a RS01-CA09) | @lilydias24 |
| RS02 | R02 - Tampering | Toda alteração de prescrição ativa deve ser autorizada e validada no servidor, confirmada por segundo profissional e registrada com autoria e versionamento em trilha de auditoria imutável | Alteração sem autorização no servidor, fora da faixa terapêutica ou sem o segundo confirmador não publica versão vigente, e a tentativa fica registrada na auditoria (RS02-CA01 a RS02-CA08) | @ARTHUR9011 |
| RS03 | R06 - Elevation of Privilege | O sistema deve validar `nivelAcesso` no servidor em toda operação administrativa, e não apenas ocultar opções na interface | Sessão sem alçada não consegue elevar `nivelAcesso` por caminho algum: pela via de salvamento do cadastro o campo é descartado e a tentativa registrada; pela operação própria de alteração de perfil a requisição é recusada com HTTP 403. Vale igualmente quando enviada direto ao endpoint, sem passar pela interface (RS03-CA01 a RS03-CA08) | @PPrauchner |

> A coluna *Critério de verificação* foi acrescentada porque o §18.1 do enunciado a exige
> na tabela de requisitos - o requisito precisa ser "específico e verificável", e é essa
> coluna que demonstra o segundo adjetivo. Cada célula resume em uma linha os critérios
> detalhados na subseção do requisito correspondente; nenhum critério novo foi criado aqui.

> Os três requisitos estão detalhados abaixo, cada um na subseção do seu responsável.

### RS01 - Autenticação forte e reautenticação em operações sensíveis (@lilydias24)

**Risco de origem.** R01 - uso das credenciais legítimas de um profissional para assumir
sua identidade no SIGH. O requisito atua sobre as duas condições que dão ao risco
probabilidade 4: a senha guardada de forma diretamente reutilizável e o fato de saber a
senha ser suficiente para agir como o titular.

**Enunciado completo.** O SIGH deve:

1. persistir `senhaLogin` apenas como valor derivado por função própria para senhas
   (Argon2id, ou scrypt/bcrypt quando aquele não estiver disponível), com **salt
   aleatório e distinto por credencial**, nunca em texto simples nem por função de
   propósito geral como MD5 ou SHA-256 isolado;
2. verificar a credencial por comparação em tempo constante e, quando os parâmetros de
   custo forem reforçados, regravar o registro de forma transparente na primeira
   autenticação bem-sucedida, sem exigir troca de senha;
3. exigir **segundo fator no login**, vinculado à pessoa e não ao terminal, uma vez que
   os postos de atendimento são compartilhados;
4. exigir **reautenticação com segundo fator**, dentro de uma janela curta e explícita,
   imediatamente antes de prescrever medicamento, autorizar alta e registrar óbito - as
   três operações que a Etapa 1 identificou como de efeito clínico ou irreversível;
5. aplicar bloqueio temporário progressivo por conta **e** por origem após tentativas
   malsucedidas, sem que a mensagem de erro permita distinguir conta existente de
   inexistente;
6. encerrar a sessão por inatividade e vinculá-la ao dispositivo e à zona de rede em que
   foi aberta, exigindo nova autenticação quando esse vínculo mudar;
7. emitir evento de segurança para toda tentativa de autenticação, reautenticação,
   bloqueio, desbloqueio e alteração de credencial, com autoria e data/hora fornecidas
   pelo servidor; e
8. oferecer um caminho de exceção assistencial (*break-glass*) para quando o segundo
   fator estiver indisponível durante o atendimento, com acesso em escopo reduzido, por
   tempo limitado, mediante identificação de um segundo profissional e com registro
   destacado para revisão obrigatória.

**Comportamento esperado.** A falha é fechada: sem credencial válida, sem segundo fator
válido ou sem reautenticação dentro da janela, a operação sensível não é executada e
nenhum efeito parcial é persistido. A identidade nunca é aceita do corpo enviado pelo
Desktop Cliente - vem sempre da sessão autenticada no servidor. Nem a senha em claro, nem
o valor derivado, nem os códigos do segundo fator podem aparecer em log, em mensagem de
erro ou em resposta de API.

A cláusula 8 existe por uma razão específica deste sistema, e precisa ser lida junto com
as demais: **um hospital não pode tratar o bloqueio de acesso como resultado seguro por
padrão.** Impedir um médico de prescrever durante uma emergência transfere o dano para o
paciente - exatamente o bem que as outras cláusulas protegem. Por isso a exceção é
prevista, delimitada e auditada, em vez de acontecer informalmente pelo empréstimo de
credencial entre colegas, que é justamente o comportamento descrito em CA01.

**Limite reconhecido do requisito.** O segundo fator reduz a probabilidade do risco, mas
não substitui uma segunda pessoa: continua sendo algo que o próprio titular carrega e
pode ser obtido pela mesma manobra que obtém a senha (*phishing* em tempo real). É por
isso que o residual de R01 permanece Alto na [Etapa 2](E2_Riscos_e_NIST_CSF.md) mesmo com
RS01 implementado, e por isso a cláusula 4 se limita a reautenticar, sem exigir
coassinatura - exigir segunda identidade em operação irreversível é uma decisão que o
grupo pode tomar depois, e que teria de ser pesada contra o custo assistencial de travar
uma alta ou um registro de óbito.

**Critérios de verificação.** O requisito é considerado atendido quando os cenários
abaixo forem demonstrados por testes automatizados e pela consulta aos eventos de
segurança:

| ID | Cenário | Resultado verificável |
| --- | --- | --- |
| RS01-CA01 | Profissional cadastra a senha e autentica com ela, apresentando o segundo fator | Autenticação aceita; o valor persistido em `senhaLogin` não contém a senha e difere do de outra conta com a mesma senha |
| RS01-CA02 | Atacante de posse do conteúdo da tabela `Funcionario` reenvia o valor armazenado como se fosse a senha | Autenticação recusada; o vazamento não é diretamente reutilizável |
| RS01-CA03 | Senha correta apresentada sem o segundo fator | Autenticação recusada e nenhuma sessão é aberta |
| RS01-CA04 | Sessão válida tenta prescrever, autorizar alta ou registrar óbito fora da janela de reautenticação | Operação recusada; nenhum efeito parcial persistido |
| RS01-CA05 | Sequência de tentativas malsucedidas contra a mesma conta e contra várias contas da mesma origem | Bloqueio progressivo aplicado nos dois eixos; as mensagens não distinguem conta existente de inexistente |
| RS01-CA06 | Sessão permanece inativa além do limite, ou é reapresentada de outro dispositivo ou zona de rede | Sessão encerrada e nova autenticação exigida |
| RS01-CA07 | Parâmetros de custo são reforçados e o profissional autentica em seguida | Registro regravado com os novos parâmetros, de forma transparente, sem troca de senha |
| RS01-CA08 | Fluxo de exceção assistencial é acionado sem o segundo fator | Acesso concedido em escopo e prazo reduzidos, com segundo profissional identificado e registro destacado para revisão |
| RS01-CA09 | Log e resposta de erro são inspecionados após uma falha de autenticação | Nenhuma senha, valor derivado ou código de segundo fator aparece |

### RS02 - Integridade e rastreabilidade da prescrição ativa (@ARTHUR9011)

**Risco de origem.** R02 - alteração indevida de `dosagemMedicamento` ou
`intervaloConsumo` de uma `PrescricaoMedicamento` ativa, executada pela enfermagem como
se fosse a versão legítima. O requisito atua antes de a mudança chegar à administração
do medicamento, porque o dano clínico não pode ser desfeito pelo sistema depois desse
momento.

**Enunciado completo.** Toda solicitação de alteração de uma prescrição ativa deve ser
processada no servidor e somente pode produzir uma nova versão vigente quando, no mesmo
fluxo controlado e antes da publicação, o SIGH:

1. obtiver o autor da sessão autenticada, sem aceitar identidade informada pelo cliente;
2. confirmar que o autor é médico e está vinculado ao atendimento do paciente;
3. validar `dosagemMedicamento` e `intervaloConsumo` contra a faixa terapêutica cadastrada
   para o medicamento;
4. exigir reautenticação do autor e confirmação de um segundo profissional autorizado,
   diferente do autor da mudança;
5. confirmar que a versão-base ainda é a vigente, preservar a versão anterior e
   acrescentar atomicamente a nova versão e seu registro à trilha de auditoria; e
6. tornar a nova versão disponível para administração somente depois que todas as
   verificações e o registro de auditoria forem concluídos com sucesso.

**Comportamento esperado.** A trilha deve ser somente de acréscimo e registrar, no
mínimo, o identificador da prescrição, do paciente, da versão-base e da nova versão,
medicamento, dose e intervalo anteriores e novos, justificativa, autor, segundo
confirmador, data/hora fornecida pelo servidor e identificador de correlação da operação.
Nenhum desses dados de autoria pode vir do corpo enviado pelo Desktop Cliente. Se
autorização, vínculo, faixa terapêutica, reautenticação, confirmação independente,
controle de concorrência ou gravação da auditoria falhar, a operação deve falhar de forma
fechada: a versão vigente permanece inalterada, nenhuma atualização parcial é persistida
e a tentativa recusada é registrada para detecção. A confirmação humana pode ocorrer
antes da transação de publicação; nesse caso, ela fica vinculada à versão proposta, e as
regras e a versão-base são verificadas novamente imediatamente antes da publicação
atômica, sem manter uma transação de banco aberta durante a espera.

Neste requisito, **confirmação** ou **coassinatura** significa uma aprovação eletrônica
atribuída a outra sessão autenticada e vinculada à versão exata da prescrição. Ela não é
tratada como assinatura digital criptográfica baseada em certificado. Se o grupo optar
por uma assinatura digital nesse sentido estrito, será necessária uma decisão de
arquitetura própria para identidade do signatário, gestão e revogação de chaves,
formato assinado e verificação de longo prazo.

**Critérios de verificação.** O requisito é considerado atendido quando os seguintes
cenários forem demonstrados por testes automatizados e pela consulta à auditoria:

| ID | Cenário | Resultado verificável |
| --- | --- | --- |
| RS02-CA01 | Médico vinculado informa valores dentro da faixa, reautentica e recebe confirmação válida de outro profissional | Uma nova versão torna-se vigente e a anterior permanece consultável; a auditoria contém todos os campos obrigatórios |
| RS02-CA02 | Perfil não médico tenta alterar a prescrição | A solicitação é recusada, a versão vigente não muda e a tentativa fica registrada |
| RS02-CA03 | Médico não vinculado ao paciente tenta alterar a prescrição | A solicitação é recusada, a versão vigente não muda e a tentativa fica registrada |
| RS02-CA04 | Dose ou intervalo está fora da faixa terapêutica | A solicitação é recusada antes de ficar disponível para administração e a divergência fica registrada |
| RS02-CA05 | Reautenticação está ausente/inválida, não há segundo confirmador ou autor e confirmador são a mesma pessoa | A solicitação é recusada e nenhuma nova versão é criada |
| RS02-CA06 | O registro da auditoria falha durante a alteração | Toda a transação é revertida; a prescrição anterior continua vigente e não há versão parcial |
| RS02-CA07 | Um usuário da aplicação tenta alterar ou excluir uma versão já registrada | A operação é recusada e a trilha preserva integralmente o histórico |
| RS02-CA08 | Duas alterações concorrentes tentam partir da mesma versão-base | No máximo uma delas torna-se vigente; a outra recebe conflito, não sobrescreve dados e precisa passar novamente pelas validações e pela confirmação sobre a nova base |

### RS03 - Autorização de operação administrativa decidida no servidor (@PPrauchner)

**Risco de origem.** R06 - um `Administrador` de nível Supervisor persiste
`nivelAcesso: Diretor` no próprio cadastro e passa a operar com alçada de Diretor sobre o
Serviço de Funcionários. O requisito atua sobre a condição exata que dá a R06 sua
probabilidade 2 na [Etapa 2](E2_Riscos_e_NIST_CSF.md): a decisão de autorização existir
apenas na montagem da interface, de modo que o campo trafega no salvamento comum do
cadastro (CA05, passo 3) e nada no servidor verifica se quem pediu tem alçada sobre ele.

Vale fixar por que este requisito não é uma variação de RS01. Em R06 **a identidade não
foi falsificada, foi promovida**: o ator autentica com a própria senha e a sessão é
legítima do início ao fim. Autenticar melhor - que é o que RS01 faz - não impede nada
aqui, porque nunca houve dúvida sobre quem é o usuário. A dúvida é sobre o que ele pode.

**Enunciado completo.** Toda operação administrativa do Serviço de Funcionários -
alteração de perfil, cadastro de profissional, gestão de escalas e de medicamentos e
listagem em massa do cadastro - só pode ser executada quando o SIGH:

1. obtiver perfil e `nivelAcesso` do solicitante **da sessão autenticada** emitida pelo
   serviço de autenticação (DA03), **descartando** identidade, papel e `nivelAcesso`
   recebidos no corpo, na URL ou em cabeçalho da requisição **antes** de qualquer
   validação - e não apenas ignorando-os na decisão;
2. submeter a operação a uma decisão de autorização **explícita e no servidor**, tomada
   fora do componente que a executa (Serviço de Autorização da seção 3.1), com **negação
   por padrão**: operação administrativa sem regra correspondente é recusada, nunca
   permitida por omissão;
3. tratar `nivelAcesso` como campo **não gravável pela via de salvamento do cadastro**: a
   mudança de perfil só ocorre por operação própria de alteração de perfil, exigindo
   alçada de Diretor, e o titular **nunca** é autorizado sobre o próprio registro - quem
   solicita a promoção não é quem a aprova;
4. recusar a requisição não autorizada com **HTTP 403**, sem executar efeito parcial
   algum: a verificação precede a persistência e a operação inteira é revertida se
   qualquer etapa falhar; a resposta não revela quais campos ou perfis existem;
5. registrar na trilha de auditoria imutável (DA01) tanto as alterações **efetivadas**
   quanto as **recusadas**, com autor obtido da sessão, perfil vigente no momento,
   valor anterior, valor novo, terminal de origem e data/hora carimbados pelo servidor;
6. **reavaliar a autorização a cada requisição** e reemitir a identidade de sessão quando
   o perfil mudar: sessão aberta antes da promoção não carrega a alçada nova, e sessão de
   perfil rebaixado perde a alçada antiga imediatamente, sem depender de novo login;
7. emitir alerta ao Diretor e à Segurança da Informação **no momento** de toda elevação de
   perfil efetivada, e não em relatório posterior - é a fonte da Regra 3 da
   [Etapa 6](E6_Monitoramento_e_deteccao.md); e
8. aplicar a mesma decisão às **leituras em massa** do cadastro, com limite de volume e
   registro por consulta. A cláusula existe porque em CA05 o dano não vem da promoção em
   si, e sim do que ela permite ler em seguida - o cadastro completo de todas as unidades,
   com `nomeLogin` e `senhaLogin` de todos os perfis - e porque esse mesmo volume, sobre o
   SGBD único, é o caminho de indisponibilidade de R05.

**Comportamento esperado.** A falha é fechada e a decisão é do servidor, sempre: ocultar
a opção na interface deixa de ser um controle e passa a ser conveniência de usabilidade.
O `nivelAcesso` que chega do Desktop Cliente é **descartado**, não validado - a diferença
importa, porque validar um valor controlado pelo cliente ainda é confiar nele. Nenhuma
credencial de outro funcionário aparece em resposta de listagem administrativa: o cadastro
retorna dados funcionais, não os campos de autenticação, que residem no serviço de
autenticação a partir da DA03.

**Limite reconhecido do requisito.** RS03 fecha o caminho de CA05, mas não fecha a
promoção legítima indevida: uma conta de Diretor comprometida, ou o conluio de quem
aprova, continua produzindo uma elevação válida - agora datada, atribuída e alertada, o
que muda a detecção, não a possibilidade. E o requisito **não reduz o impacto de R06**: se
a elevação ocorrer, o alcance permanece o mesmo enquanto `senhaLogin` estiver em texto
simples, porque o dano de R06 se realiza sobre as credenciais que RS01 protege. Por isso o
residual de R06 na [Etapa 2](E2_Riscos_e_NIST_CSF.md) mantém impacto 4 mesmo com todos os
controles próprios implantados: **a redução do impacto de R06 depende de RS01, não de
RS03.** Os dois requisitos precisam avançar juntos.

**Critérios de verificação.** O requisito é considerado atendido quando os cenários abaixo
forem demonstrados por testes automatizados e pela consulta à trilha de auditoria. Os dois
primeiros são exatamente os testes escritos na [Etapa 4](E4_Codigo_seguro_e_testes.md).

| ID | Cenário | Resultado verificável |
| --- | --- | --- |
| RS03-CA01 | Sessão com `nivelAcesso = Diretor` promove outro funcionário a GerenteSetor | Alteração aceita; a trilha registra autor, valor anterior, valor novo e data/hora do servidor |
| RS03-CA02 | Sessão com `nivelAcesso = Supervisor` tenta se promover a Diretor pelos dois caminhos: primeiro enviando o próprio cadastro com `nivelAcesso: "Diretor"` no corpo (passo 3 do CA05), depois chamando a operação própria de alteração de perfil | Pela via de salvamento, o campo é **descartado antes de qualquer validação**: os demais dados seguem o fluxo normal, `nivelAcesso` permanece `Supervisor` e a tentativa de gravá-lo é registrada. Pela operação própria, a requisição é recusada com **HTTP 403**, sem efeito parcial. Em nenhum dos dois há promoção, e ambos alimentam a Regra 3 |
| RS03-CA03 | **Cada uma das duas requisições** de CA02 é enviada **direto ao endpoint**, sem passar pela interface | **Cada uma** produz o desfecho que produziria pela interface: descarte do campo com registro na via de salvamento, **HTTP 403** na operação própria de alteração de perfil - o desfecho não depende da tela ter ou não montado a opção |
| RS03-CA04 | Requisição legítima de alteração de dados funcionais traz `nivelAcesso` alterado junto no corpo, sem intenção de promoção | Mesmo desfecho da via de salvamento em CA02, o que é o ponto: os dados funcionais são gravados, o `nivelAcesso` permanece inalterado e a tentativa de gravá-lo é registrada. O servidor não distingue intenção - trata o campo pela origem da requisição, não pelo propósito de quem a enviou |
| RS03-CA05 | Diretor tenta elevar o **próprio** `nivelAcesso` | HTTP 403 - a alçada não alcança o próprio registro, e a promoção exige aprovador distinto do solicitante |
| RS03-CA06 | Novo endpoint administrativo entra no serviço sem regra de autorização declarada | Toda chamada é recusada por omissão de regra, e não permitida - a negação por padrão é verificada, não presumida |
| RS03-CA07 | Sessão aberta antes de uma promoção legítima chama operação exclusiva do perfil novo; e sessão de perfil rebaixado chama operação do perfil antigo | A primeira é recusada até a identidade de sessão ser reemitida; a segunda é recusada imediatamente |
| RS03-CA08 | Sessão administrativa percorre o cadastro completo de funcionários de todas as unidades | O limite de volume é aplicado, nenhum campo de autenticação é retornado e cada consulta fica registrada |

> **Correção aos critérios de CA02 e CA04.** Na redação anterior os dois descreviam a
> mesma entrada - corpo de salvamento do cadastro trazendo `nivelAcesso` alterado - com
> resultados incompatíveis: CA02 esperava HTTP 403 e CA04 esperava gravação dos dados
> funcionais com o campo ignorado. Nenhum servidor pode satisfazer os dois, porque a
> requisição é a mesma; só a intenção difere, e intenção não é observável.
>
> A implementação da [Etapa 4](E4_Codigo_seguro_e_testes.md) expôs a contradição ao
> tentar codificar ambos. O critério foi reescrito segundo a cláusula 3, que já dava a
> resposta: `nivelAcesso` **não é gravável pela via de salvamento do cadastro**, e a
> mudança de perfil é **operação própria**. São dois caminhos distintos, com desfechos
> distintos - descarte com registro num, HTTP 403 no outro -, e CA02 passa a exercitar
> os dois. CA04 deixa de ser um caso concorrente e passa a ser o que sempre deveria ter
> sido: a demonstração de que o desfecho da via de salvamento **não depende da
> intenção** de quem enviou a requisição.
>
> CA03 foi ajustado na mesma linha. Como CA02 passou a ter duas requisições, "a mesma
> requisição" e "resultado idêntico" ficaram sem antecedente único; o critério agora diz
> que **cada uma das duas** é enviada direto ao endpoint e **cada uma** mantém o desfecho
> que teria pela interface. É o que CA03 sempre afirmou: o controle não depende da tela.
>
> A menção ao disparo do alerta também foi ajustada. A cláusula 7 alerta nas elevações
> **efetivadas**; tentativas recusadas entram na [Regra 3](E6_Monitoramento_e_deteccao.md)
> por outros gatilhos - repetição, ou imediatamente quando a requisição não passa pela
> interface. Dizer que "o alerta da Regra 3 dispara" numa recusa isolada prometia um
> limiar que a regra não tem.

## 2. Vulnerabilidades catalogadas (CWE/OWASP)

| Requisito | Vulnerabilidade relacionada | Referência | Responsável |
| --- | --- | --- | --- |
| RS01 | Senha persistida em texto simples, autenticação de fator único, ausência de limite de tentativas e sessão sem expiração | CWE-256, CWE-308, CWE-307, CWE-613 e CWE-287 | @lilydias24 |
| RS02 | Ausência de autorização no servidor, confiança em validações do cliente, entrada clínica sem validação e auditoria insuficiente | CWE-862, CWE-602, CWE-20 e CWE-778; OWASP A01, A06 e A09:2025 | @ARTHUR9011 |
| RS03 | Autorização ausente no servidor, campo de privilégio gravável pelo próprio titular junto com o cadastro e gestão indevida de privilégio | CWE-862, CWE-915, CWE-269 e CWE-639; OWASP A01:2025 e ASVS V4 | @PPrauchner |

> Os três mapeamentos estão detalhados abaixo, cada um na subseção do seu responsável.

### Vulnerabilidades relacionadas a RS01 (@lilydias24)

Como o SIGH não está implementado, os itens abaixo são **fraquezas potenciais indicadas
pelo modelo**, e não vulnerabilidades confirmadas em código. A primeira delas, porém, é
menos hipotética que as demais: `senhaLogin` aparece como atributo de texto simples no
modelo de domínio, e o RNF05 exige criptografia para as informações médicas - a
contradição está documentada no próprio projeto.

| Referência | Relação concreta com o SIGH |
| --- | --- |
| [CWE-256 - Plaintext Storage of a Password](https://cwe.mitre.org/data/definitions/256.html) | `Funcionario.senhaLogin` é um atributo de texto sem indicação de derivação. É a fraqueza principal de RS01: torna um vazamento do SGBD central imediatamente utilizável contra todas as contas. |
| [CWE-916 - Use of Password Hash With Insufficient Computational Effort](https://cwe.mitre.org/data/definitions/916.html) | Aplicar um hash de propósito geral, sem salt e sem fator de trabalho, resolveria a aparência do problema sem resolver o problema. É a armadilha que a cláusula 1 fecha ao exigir função própria para senhas. |
| [CWE-308 - Use of Single-factor Authentication](https://cwe.mitre.org/data/definitions/308.html) | A autenticação se resume à comparação de `nomeLogin` e `senhaLogin`: quem sabe a senha é o titular, para todos os efeitos do sistema. |
| [CWE-307 - Improper Restriction of Excessive Authentication Attempts](https://cwe.mitre.org/data/definitions/307.html) | O modelo não prevê bloqueio nem atraso após tentativas malsucedidas, o que viabiliza força bruta a partir da própria rede interna. |
| [CWE-613 - Insufficient Session Expiration](https://cwe.mitre.org/data/definitions/613.html) | Sem expiração por inatividade, o terminal compartilhado deixado aberto entre plantões é uma sessão válida à disposição de quem passar. |
| [CWE-287 - Improper Authentication](https://cwe.mitre.org/data/definitions/287.html) | Permanece como categoria-mãe do requisito, útil para a rastreabilidade geral, mas abstrata demais para orientar controle: as cinco fraquezas acima é que dizem o que precisa mudar. |

No **OWASP Top 10**, a relação principal é com a categoria de **falhas de identificação e
autenticação** e, pelo armazenamento da senha, com a de **falhas criptográficas**. O
grupo está citando a edição 2025 (ver o mapeamento de RS02); a numeração exata dessas duas
categorias nessa edição deve ser conferida na lista vigente antes da entrega final, para
não citar identificador de edição diferente. As referências de controle usadas aqui, e
que não dependem dessa numeração, são o
[OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
e o
[OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html),
este último aplicado na prática da [Etapa 4](E4_Codigo_seguro_e_testes.md).

### Rastreabilidade de RS01

RS01 concretiza os controles R01-C1 a R01-C5 definidos no plano de tratamento da
[Etapa 2](E2_Riscos_e_NIST_CSF.md).

| Controle de R01 | Realização em RS01 | Critérios que o verificam | Evidência esperada |
| --- | --- | --- | --- |
| R01-C1 - hash e salt | Cláusulas 1 e 2 | RS01-CA01, RS01-CA02 e RS01-CA07 | Já demonstrada na [Etapa 4](E4_Codigo_seguro_e_testes.md): testes executados de caso válido e de posse do conteúdo da tabela |
| R01-C2 - MFA e reautenticação | Cláusulas 3, 4 e 8 | RS01-CA03, RS01-CA04 e RS01-CA08 | Testes sem segundo fator, fora da janela de reautenticação e pelo fluxo de exceção assistencial |
| R01-C3 - bloqueio por tentativas | Cláusula 5 | RS01-CA05 | Teste de bloqueio por conta e por origem, com mensagens indistinguíveis |
| R01-C4 - expiração de sessão | Cláusula 6 | RS01-CA06 | Teste de inatividade e de reapresentação da sessão em outro dispositivo ou zona |
| R01-C5 - política de senha | Cláusulas 1 e 2, mais a política institucional prevista na função Govern do mapeamento NIST | RS01-CA01 e RS01-CA07 | Política publicada e verificação contra listas públicas de senhas vazadas |

**Contratos necessários para a arquitetura segura.** O diagrama da seção 3 deve permitir
identificar, ainda que em nível lógico:

- um **serviço de autenticação** como emissor único da identidade de sessão, separado
  dos serviços de negócio (ver DA03);
- o armazenamento das credenciais derivadas, isolado do restante do cadastro de
  `Funcionario`, de modo que ler o cadastro não implique ler as credenciais;
- o verificador do segundo fator e o registro da janela de reautenticação, consultáveis
  pelos serviços que executam operações sensíveis;
- o contador de tentativas e o estado de bloqueio, compartilhados entre instâncias para
  que o limite não seja contornado alternando de servidor; e
- o canal de eventos de segurança que alimenta a Regra 1 da
  [Etapa 6](E6_Monitoramento_e_deteccao.md).

### Vulnerabilidades relacionadas a RS02 (@ARTHUR9011)

Como o SIGH não está implementado, os itens abaixo são **fraquezas potenciais indicadas
pelo modelo**, e não vulnerabilidades confirmadas em código. Elas devem ser verificadas
pelos critérios de RS02 e pelos testes de segurança das etapas seguintes.

| Referência | Relação concreta com o SIGH |
| --- | --- |
| [CWE-862 - Missing Authorization](https://cwe.mitre.org/data/definitions/862.html) | A regra do UC03 exige médico autorizado, mas `atualizarTratamentosDoPaciente(tratamento)` não demonstra uma checagem de papel e de vínculo com o paciente no servidor. É a fraqueza principal de RS02. |
| [CWE-602 - Client-Side Enforcement of Server-Side Security](https://cwe.mitre.org/data/definitions/602.html) | Se o Desktop Cliente apenas ocultar a opção para outros perfis, a proteção pode ser contornada por uma chamada modificada. A decisão precisa ser repetida no servidor com dados da sessão. |
| [CWE-20 - Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html) | O modelo não especifica validação de `dosagemMedicamento` e `intervaloConsumo` contra limites terapêuticos antes de persistir a mudança. |
| [CWE-778 - Insufficient Logging](https://cwe.mitre.org/data/definitions/778.html) | A alteração destrutiva sem autor, versão anterior e horário do servidor impede detectar e reconstruir a adulteração. |

No OWASP Top 10:2025, a relação principal é com
[A01 - Broken Access Control](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/),
pois um usuário pode executar uma função fora de sua autorização; o desenho também se
relaciona a
[A06 - Insecure Design](https://owasp.org/Top10/2025/A06_2025-Insecure_Design/),
pela ausência das regras clínicas no fluxo confiável, e a
[A09 - Security Logging and Alerting Failures](https://owasp.org/Top10/2025/A09_2025-Security_Logging_and_Alerting_Failures/),
pela falta de evidência e alerta sobre alterações suspeitas.

A referência anterior a **CWE-345 - Insufficient Verification of Data Authenticity**
permanece útil como conceito geral de autenticidade, mas não como mapeamento principal:
ela é abstrata demais para distinguir as quatro falhas concretas acima e sua própria
ficha recomenda preferir uma fraqueza mais específica quando disponível.

### Rastreabilidade de RS02

RS02 concretiza os controles R02-C1 a R02-C5 definidos no plano de tratamento da
[Etapa 2](E2_Riscos_e_NIST_CSF.md). A tabela evita que um controle seja considerado
implementado apenas porque aparece no texto do requisito.

| Controle de R02 | Realização em RS02 | Critérios que o verificam | Evidência esperada quando houver implementação |
| --- | --- | --- | --- |
| R02-C1 - autor obtido da sessão | Cláusulas 1 e 5; autoria nunca é aceita do cliente | RS02-CA01, RS02-CA02 e RS02-CA06 | Teste que adultera o autor no corpo e comprova que a auditoria registra o usuário da sessão |
| R02-C2 - papel e vínculo validados no servidor | Cláusula 2 e falha fechada | RS02-CA02 e RS02-CA03 | Testes de autorização com perfil não médico e médico não vinculado, ambos sem mudança persistida |
| R02-C3 - faixa terapêutica | Cláusula 3 | RS02-CA04 | Testes de limite inferior, limite superior e valores imediatamente fora dos limites para dose e intervalo |
| R02-C4 - versionamento imutável | Cláusulas 5 e 6; comportamento esperado da auditoria | RS02-CA01, RS02-CA06, RS02-CA07 e RS02-CA08 | Consulta exibindo valor anterior e novo; tentativa de alteração/exclusão recusada; falha de auditoria causando rollback; teste concorrente sem atualização perdida |
| R02-C5 - reautenticação e segunda confirmação | Cláusula 4 | RS02-CA01 e RS02-CA05 | Testes sem reautenticação, sem confirmador e com autor igual ao confirmador, além do fluxo válido com duas identidades |

**Contratos necessários para a arquitetura segura.** O diagrama da seção 3 deve permitir
identificar, ainda que em nível lógico:

- a sessão autenticada como fonte de identidade, papel e instante da reautenticação;
- a política de autorização que verifica papel médico e vínculo com o paciente;
- o catálogo clínico versionado que fornece as faixas terapêuticas;
- o fluxo de confirmação independente vinculado à versão proposta;
- o armazenamento transacional das versões da prescrição, com controle de concorrência
  pela versão-base; e
- a trilha de auditoria somente de acréscimo, separada da permissão de alterar a
  prescrição.

Esses são contratos, e não uma prescrição de quantidade de microsserviços. Eles podem ser
implementados em componentes separados ou no mesmo serviço, desde que as fronteiras de
autorização, transação e auditoria permaneçam explícitas e verificáveis.

**Dependências para as próximas etapas.** Os testes listados nesta seção são critérios
de arquitetura enquanto o SIGH não possui implementação; portanto, não devem ser
apresentados como evidência executada. Quando existir código, o resultado automatizado e
a consulta à auditoria comprovarão os controles. A Regra 2 da Etapa 6 deve consumir tanto
alterações concluídas quanto tentativas recusadas, usando o identificador de correlação,
para detectar valor fora da faixa, autorização inválida ou ausência de confirmação sem
depender de uma alteração insegura ter sido persistida.

### Vulnerabilidades relacionadas a RS03 (@PPrauchner)

Como o SIGH não está implementado, os itens abaixo são **fraquezas potenciais indicadas
pelo modelo**, e não vulnerabilidades confirmadas em código - a mesma ressalva que a
[Etapa 1](E1_Casos_de_abuso_e_Stride.md) registra ao dizer que só é possível afirmar que o
modelo *não especifica* a verificação, nunca que o sistema *não a faz*. Duas delas, porém,
são menos hipotéticas que as demais: `nivelAcesso` é o único atributo de autorização do
modelo inteiro (observação 1 da seção 8.3) e ele aparece como atributo comum do cadastro,
sem operação própria - as duas coisas estão no diagrama de classes, não em uma suposição.

| Referência | Relação concreta com o SIGH |
| --- | --- |
| [CWE-862 - Missing Authorization](https://cwe.mitre.org/data/definitions/862.html) | É a fraqueza principal de RS03. O modelo não expõe nenhuma verificação de alçada no servidor antes de gravar o cadastro de `Funcionario`: a restrição de perfil aparece na montagem da tela, e o firewall declarado antes de cada DAO separa serviço de serviço, sem distinguir qual perfil emitiu a chamada dentro de uma sessão já autenticada. |
| [CWE-915 - Improperly Controlled Modification of Dynamically-Determined Object Attributes](https://cwe.mitre.org/data/definitions/915.html) | É o mecanismo exato de CA05, passo 3: `nivelAcesso` viaja no mesmo salvamento dos demais dados do cadastro, de modo que **alterar o próprio privilégio não exige uma operação diferente de alterar o próprio telefone** - basta um campo a mais no corpo. É a fraqueza que a cláusula 3 fecha ao tirar o campo da via de salvamento. |
| [CWE-269 - Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html) | O modelo não define quem concede, quem aprova nem quem revoga `nivelAcesso`: o enum existe, o fluxo de atribuição não. Sem isso, o titular é, por omissão, autoridade sobre o próprio nível - e uma promoção não tem como ser distinguida de uma correção de cadastro. |
| [CWE-639 - Authorization Bypass Through User-Controlled Key](https://cwe.mitre.org/data/definitions/639.html) | Complementa a leitura em massa da cláusula 8: os identificadores do SIGH são sequenciais - `buscarPacientePorIdentificador(idPaciente)` é o caso citado em CA01 e CA05 -, e o alcance obtido pela elevação se converte em varredura simplesmente variando o identificador, sem nova decisão de autorização por registro acessado. |

Duas fraquezas já mapeadas em outros requisitos valem igualmente aqui e **não são
repetidas** para não inflar a lista: **CWE-602 - Client-Side Enforcement of Server-Side
Security**, mapeada em RS02, descreve com precisão o "ocultar o botão em vez de recusar a
chamada" que RS03 combate; e **CWE-778 - Insufficient Logging**, também de RS02, é o que
torna a elevação silenciosa e permanente, condição registrada em T06 e no Tópico 9 do
documento original.

No **OWASP Top 10:2025**, a relação principal é com
[A01 - Broken Access Control](https://owasp.org/Top10/2025/A01_2025-Broken_Access_Control/),
que é a mesma categoria de RS02 - e a coincidência é informativa, não um problema de
mapeamento: os dois requisitos atacam a mesma classe de falha em pontos diferentes do
sistema, RS02 na operação clínica e RS03 na operação administrativa que **concede** a
permissão de executá-la. O desenho também toca
[A06 - Insecure Design](https://owasp.org/Top10/2025/A06_2025-Insecure_Design/), pela
ausência de um fluxo de atribuição de privilégio no modelo.

As referências de controle usadas aqui, que não dependem da numeração da edição, são o
[OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- de onde vêm a negação por padrão da cláusula 2 e a reavaliação por requisição da
cláusula 6 - e o capítulo **V4 - Access Control** do
[OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/),
que o §20 do enunciado sugere para selecionar requisitos verificáveis e que sustenta os
critérios RS03-CA03 (decisão no servidor, não na interface) e RS03-CA06 (negação por
omissão de regra).

### Rastreabilidade de RS03

RS03 concretiza os controles R06-C1 a R06-C4 definidos no plano de tratamento da
[Etapa 2](E2_Riscos_e_NIST_CSF.md).

| Controle de R06 | Realização em RS03 | Critérios que o verificam | Evidência esperada quando houver implementação |
| --- | --- | --- | --- |
| R06-C1 - revalidação de autorização no servidor, com o `nivelAcesso` do corpo descartado | Cláusulas 1, 2, 4 e 6 | RS03-CA02, RS03-CA03, RS03-CA06 e RS03-CA07 | Os dois testes da [Etapa 4](E4_Codigo_seguro_e_testes.md), mais o teste que envia a requisição direto ao endpoint e o que verifica a recusa por omissão de regra |
| R06-C2 - `nivelAcesso` imutável pelo próprio titular, mudança só por fluxo de aprovação | Cláusula 3 | RS03-CA01, RS03-CA04 e RS03-CA05 | Promoção legítima por sessão Diretor sobre outro funcionário; tentativa sobre o próprio registro recusada; gravação de dados funcionais que ignora o campo de privilégio |
| R06-C3 - trilha imutável de toda alteração de perfil, com autor, valor anterior e novo e data/hora do servidor | Cláusula 5 | RS03-CA01, RS03-CA02 e RS03-CA04 | Consulta à trilha exibindo alterações efetivadas **e** recusadas, com autoria vinda da sessão - garantida pelo Serviço de Auditoria da DA01 |
| R06-C4 - alerta ao Diretor e à Segurança da Informação a cada elevação | Cláusula 7 | RS03-CA01 e RS03-CA02 | Regra 3 da [Etapa 6](E6_Monitoramento_e_deteccao.md) disparando em uma elevação simulada, com destinatário definido. CA01 é o caso que o controle descreve - a elevação **efetivada**; CA02 entra como a tentativa recusada, que a regra observa por outro gatilho |

A cláusula 8 não realiza um controle de R06: ela fecha a continuação do CA05, em que o
privilégio obtido vira varredura do cadastro e, pelo volume sobre o SGBD único, alcança a
disponibilidade tratada em **R05**. Está aqui porque o requisito ficaria incompleto sem
ela - conter a elevação e deixar aberta a leitura em massa que a motiva resolveria metade
do caso de abuso.

**Contratos necessários para a arquitetura segura.** O diagrama da seção 3 deve permitir
identificar, ainda que em nível lógico:

- o **Serviço de Autorização** como componente distinto do Serviço de Funcionários - a
  decisão não pode viver dentro do serviço que ela autoriza, ou volta a ser possível
  alcançá-la pelo mesmo caminho que se quer barrar;
- o ponto do **API Gateway** em que identidade, papel e `nivelAcesso` vindos do cliente
  são descartados, e não apenas ignorados (fronteira 1 da seção 3.2);
- a **operação própria de alteração de perfil**, separada do salvamento do cadastro, com
  o aprovador como identidade distinta do solicitante;
- o **canal de eventos de autorização** - concessões e recusas - alimentando o Serviço de
  Auditoria e, a partir dele, a Regra 3 da Etapa 6; e
- o ponto em que as **credenciais deixam de estar no Serviço de Funcionários** (DA03): sem
  isso, o alcance administrativo continua alcançando `senhaLogin`, e o impacto 4 de R06
  permanece por construção.

**Dependências para as próximas etapas.** Os critérios acima são critérios de arquitetura
enquanto o SIGH não possui implementação, e não devem ser apresentados como evidência
executada. A decisão de arquitetura que sustenta este requisito é a **DA02**, da
@mariasanchez0: ela institui o Serviço de Autorização como ponto único de decisão, que é
o componente pressuposto pelas cláusulas 2 e 6 - sem ele, a revalidação no servidor teria
de ser repetida dentro de cada um dos 7 microsserviços, com as sete divergências que a
própria DA02 rejeita. A cláusula 3 (`nivelAcesso` fora da via de salvamento do cadastro)
é a única que permanece como responsabilidade do Serviço de Funcionários, porque diz
respeito ao que se **grava**, e não a quem decide.

Vale registrar a consequência que a DA02 assume e que atinge esta trilha: o Serviço de
Autorização vira passagem obrigatória de toda operação sensível, somando-se ao API
Gateway, ao Serviço de Autenticação e ao SGBD central como ponto de concentração - a mesma
característica que sustenta **R05**, o outro risco desta trilha. A negação por padrão da
cláusula 2 é justamente o que torna a indisponibilidade desse serviço uma parada de
operação, e não uma passagem livre. É a troca correta, mas ela precisa da redundância e da
política de latência máxima que a DA02 registra como pendência a conciliar com a DA01 e a
DA03.

## 3. Diagrama da arquitetura segura

> Responsável: **@lorenzoficher** - parte de `diagrams/estrutura/Diagramas_SIGH - Componentes.png` (já versionado) e acrescenta o serviço de autenticação instituído pela DA03, o serviço de autorização, o serviço de auditoria instituído pela DA01 e o catálogo clínico. Versionado como `diagrams/estrutura/Diagramas_SIGH - Arquitetura segura.png`.

![Arquitetura segura do SIGH](../diagrams/estrutura/Diagramas_SIGH%20-%20Arquitetura%20segura.png)

O diagrama parte da arquitetura já modelada - Desktop Cliente, API Gateway e 7
microsserviços em 5 camadas sobre um SGBD central - e acrescenta os três componentes que
os requisitos desta etapa exigem, sem redesenhar o que já existe. A leitura abaixo é a
legenda do diagrama e serve para conferir se ele mostra o que precisa mostrar.

### 3.1 Componentes acrescentados

| Componente | O que faz | Requisito que o exige |
| --- | --- | --- |
| **Serviço de Autenticação** | Verifica credenciais, aplica o segundo fator, emite a sessão e responde pela reautenticação em operações sensíveis. Passa a ser a **única** origem de identidade do sistema | RS01; controles R01-C1 a R01-C4 |
| **Serviço de Autorização** | Decide, no servidor, se a sessão pode executar a operação, combinando papel, `nivelAcesso` e vínculo com o paciente. Consultado por todos os serviços de negócio antes de qualquer operação sensível | RS02 e RS03; controles R02-C2, R06-C1 e R03-C1 |
| **Serviço de Auditoria** | Recebe e retém, somente por acréscimo, os eventos de segurança e as versões de dado clínico. Único componente com permissão de escrita no armazenamento de auditoria | RS02; controles R02-C4, R03-C3 e R06-C3 - e é o objeto da decisão DA01 |
| **Catálogo Clínico versionado** | Fornece as faixas terapêuticas por medicamento que a RS02 exige validar | RS02; controle R02-C3 |

### 3.2 Fronteiras de confiança que o diagrama precisa deixar visíveis

1. **Cliente → API Gateway.** Tudo o que vem do Desktop Cliente é entrada não confiável,
   inclusive identidade, papel, autor e data/hora. O diagrama deve deixar claro que esses
   campos são **descartados** no Gateway e reconstruídos a partir da sessão.
2. **Serviços de negócio → Serviço de Autorização.** A decisão de autorização fica fora
   do serviço que executa a operação. É o que impede que "ocultar o botão na interface"
   volte a ser o controle, como em CWE-602.
3. **Serviços de negócio → Serviço de Auditoria.** Seta de **mão única**, rotulada
   `append`. Nenhum serviço de negócio alcança o armazenamento de auditoria diretamente.
4. **Armazenamento de auditoria ≠ SGBD central.** Precisa aparecer como armazenamento
   próprio, e não como mais uma tabela do banco único - é o ponto da DA01.
5. **SIGH → «system» Sistema Governamental.** A transmissão do óbito atravessa a fronteira
   da instituição e deve aparecer com o registro probatório do R03-C4 ao lado.

### 3.3 Fluxo de referência - registro de óbito (UC10)

O caminho abaixo é o que o diagrama deve permitir percorrer com o dedo, e é o mesmo do
DS10 já versionado, agora com os controles no lugar:

```
Desktop Cliente
  │  registrarObito(causaCID, dataHoraObito)          ← sem autor, sem carimbo
  ▼
API Gateway ──────────────► Serviço de Autenticação   ← valida sessão + reautenticação
  │                                                      (descarta autor vindo do cliente)
  ▼
Serviço de Internação Médica
  │  ├──────────────────► Serviço de Autorização      ← papel médico + vínculo? (R03-C1)
  │  ├──────────────────► Serviço de Auditoria        ← append: autor, sessão, terminal,
  │  │                                                   dataHoraRegistro do servidor
  │  │                                                   (R03-C2, R03-C3)
  │  ▼
  │  SGBD central: grava Obito e encerra o prontuário ← só após o append ter sucesso
  ▼
«system» Sistema Governamental                        ← envio + registro probatório (R03-C4)
```

O ponto que o diagrama precisa comunicar em uma olhada: **a gravação do `Obito` acontece
depois do registro de auditoria, e não antes**. Se o append falhar, nada é persistido - é
o que impede que exista um óbito sem rastro, e é a diferença entre auditar e ter auditoria.

## 4. Decisões de arquitetura

O §18.4 do enunciado pede que cada decisão registre **cinco** campos: problema ou risco
tratado, decisão tomada, motivo, componente afetado e resultado esperado. As subseções
abaixo estão no formato de registro de decisão adotado pelo grupo - contexto, decisão,
alternativas consideradas e consequências -, que é mais completo em alternativas descartadas
mas não nomeia em campo próprio o componente afetado nem o resultado esperado. O quadro
abaixo faz essa correspondência para as três decisões, sem substituir o texto de nenhuma
delas: cada linha aponta para a subseção onde a justificativa está desenvolvida.
*(Quadro acrescentado por @PPrauchner; o conteúdo de cada decisão é de seu autor.)*

| Decisão | Problema ou risco tratado | Motivo | Componente afetado | Resultado esperado |
| --- | --- | --- | --- | --- |
| **DA01** - trilha de auditoria como serviço próprio, somente de acréscimo, com armazenamento separado do SGBD central | **R03** (Repudiation) como risco principal; as evidências exigidas por **R01**, **R02** e **R06** dependem da mesma capacidade inexistente | Quem tem permissão de escrita no SGBD central para gravar o registro tem, pela mesma credencial, permissão para alterá-lo - a trilha ficaria sob controle de quem ela audita, que é a condição explorada por R06. E o banco único já é o ponto de concentração de R05 | Novo **Serviço de Auditoria** com armazenamento próprio; os 7 serviços de negócio passam a ter apenas `append`, com buffer local durável; SGBD central deixa de hospedar a trilha | Óbito (UC10) e alta (UC06) só se concluem depois que o evento está durável; apagar o dado e o seu rastro passa a exigir **dois** comprometimentos distintos |
| **DA02** - Serviço de Autorização centralizado como ponto único de decisão de acesso | **R06** (`nivelAcesso` validado só na interface), **R02** (papel médico e vínculo) e **R04** (vínculo profissional-paciente na consulta) | Decisão de autorização tomada na interface é contornável reenviando a requisição (CWE-602, passo 3 do CA05); tomada dentro de cada serviço, seria repetida sete vezes, com sete oportunidades de divergência | Novo **Serviço de Autorização**, entre o API Gateway/Serviço de Autenticação e os 7 serviços de negócio; políticas de papel × `nivelAcesso` × vínculo deixam de viver no código de cada serviço | Uma única implementação atende RS02, RS03 e R04-C2; toda decisão, permitida ou negada, vira evento na auditoria e alimenta a Regra 3 da Etapa 6 |
| **DA03** - serviço de autenticação dedicado como emissor único da identidade de sessão | **R01** (Spoofing); habilita RS02 e RS03, que dependem de o servidor saber quem chama | As credenciais são atributos de `Funcionario`, dentro do serviço de cadastro administrativo: alcançar o cadastro é alcançar as senhas (T06/CA05), e não existe lugar único onde impor MFA, bloqueio e expiração de sessão | Novo **Serviço de Autenticação**; **Serviço de Funcionários** perde a guarda das credenciais; **API Gateway** passa a validar a sessão e propagar identidade verificada; fluxo de login do **Desktop Cliente** é reescrito | Identidade de sessão verificada como única fonte de identidade do sistema; ler o cadastro deixa de implicar ler credenciais, cortando o encadeamento T06 → T01 de CA05 |

As três decisões compartilham a mesma consequência negativa, e o quadro a torna visível de
uma vez: cada uma acrescenta um componente de passagem obrigatória a um sistema que já
tinha o API Gateway e o SGBD único como pontos de concentração - exatamente a característica
que sustenta **R05**. É por isso que a conciliação registrada ao final desta seção não é
formalidade: sem redundância e sem política explícita de indisponibilidade, a arquitetura
segura melhora quatro riscos piorando um quinto.

### DA01 - Trilha de auditoria como serviço próprio, somente de acréscimo e com armazenamento separado do SGBD central - @lorenzoficher

- **Contexto.** A arquitetura atual não tem onde registrar quem fez o quê: os 7
  microsserviços gravam no mesmo SGBD central e o Tópico 9 do documento original coloca o
  registro de eventos críticos fora do escopo. Isso não é uma lacuna de uma trilha só. As
  evidências que **quatro** riscos da Etapa 2 exigem em 14.4 dependem da mesma capacidade
  inexistente: R01 pede log de tentativas e de bloqueios, R02 pede log consultável com
  autor e valor anterior, R03 pede autoria e carimbo de tempo do servidor, R06 pede trilha
  imutável de alteração de perfil. As três regras da Etapa 6 consomem exatamente esses
  eventos. Decidir onde a trilha vive é, portanto, uma decisão de arquitetura do grupo
  inteiro, e não um detalhe da trilha Repudiation.

- **Decisão.** Criar um **Serviço de Auditoria** com armazenamento próprio, distinto do
  SGBD central, exposto aos demais serviços por uma interface de **acréscimo apenas**. As
  contas usadas pelos serviços de negócio têm permissão de `append` e não têm `update` nem
  `delete`; nenhum perfil da aplicação - incluindo Diretor - alcança a alteração ou a
  exclusão de uma entrada. Os campos de autoria e de tempo são preenchidos pelo próprio
  serviço a partir da sessão autenticada e do relógio do servidor, nunca copiados do corpo
  da requisição. Para as operações irreversíveis do recorte - registrar óbito (UC10) e
  autorizar alta (UC06) -, o acréscimo é **condição da operação**: se ele falhar, a
  transação de negócio é revertida.

- **Alternativas consideradas.**
  - *Tabela de auditoria no próprio SGBD central, escrita por cada serviço.* Rejeitada por
    dois motivos independentes. Quem tem permissão de escrita no banco para gravar o
    registro tem, pela mesma credencial, permissão para alterá-lo - a trilha ficaria sob o
    controle de quem ela audita, que é precisamente a condição que R06 explora. E o banco
    único já é o ponto de concentração que sustenta R05: um comprometimento ou uma queda
    alcançaria o dado e a sua prova no mesmo movimento.
  - *Auditoria implementada dentro de cada microsserviço.* Rejeitada por repetir sete vezes
    a mesma implementação, com sete oportunidades de divergência de formato - inviabilizando
    a correlação por `correlationId` de que a Regra 2 da Etapa 6 depende - e por manter a
    trilha dentro da fronteira do componente auditado.
  - *Encaminhar tudo a um SIEM externo como solução única.* Rejeitada como substituto,
    aceita como complemento. Um SIEM é ferramenta de detecção e correlação e costuma
    aplicar amostragem e retenção curta; a trilha exigida por R03 precisa de custódia
    íntegra e de longo prazo, porque serve de prova em apuração de conselho profissional ou
    em juízo. O SIEM consome o que o Serviço de Auditoria retém, não o contrário.

- **Consequências.**
  - *Positivas.* Uma única implementação satisfaz as evidências dos quatro riscos e habilita
    as três regras da Etapa 6. A separação de armazenamento faz com que comprometer o dado
    e apagar o seu rastro passem a exigir **dois** comprometimentos. E a autoria deixa de
    depender do que o cliente envia, o que é o núcleo de RS02 e de R03-C1.
  - *Negativas, e a principal precisa ser dita.* Tornar o acréscimo condição da operação
    cria um **acoplamento de disponibilidade**: se o Serviço de Auditoria cair, as operações
    irreversíveis param. Isso é, em si, um caminho de negação de serviço, e portanto uma
    interação direta com o R05 do @PPrauchner - a decisão que melhora a rastreabilidade
    piora a disponibilidade. A mitigação adotada é um **buffer local durável** em cada
    serviço de negócio: o evento é gravado localmente de forma persistente antes da resposta
    ao usuário e entregue ao Serviço de Auditoria com garantia de entrega, de modo que uma
    indisponibilidade curta não interrompe o atendimento e nenhum evento se perde. A regra
    permanece: nenhuma operação irreversível se conclui sem que o evento esteja **durável em
    algum lugar**.
  - *Custo.* Um componente novo para operar, monitorar e dimensionar, e uma decisão de
    retenção e de acesso que a função Govern do mapeamento de R03 exige tomar - uma trilha
    que qualquer perfil possa consultar recria, na privacidade, o problema que resolve na
    responsabilização.

### DA02 - Serviço de Autorização centralizado como ponto único de decisão de acesso - @mariasanchez0

- **Contexto.** Três exigências diferentes, de três trilhas diferentes, pedem a mesma capacidade que o modelo atual não tem: RS02 exige confirmar papel médico e vínculo com o paciente antes de alterar uma prescrição; RS03 exige validar `nivelAcesso` no servidor em toda operação administrativa; e o plano de tratamento de R04 (Etapa 2) exige verificar vínculo entre o profissional autenticado e o paciente consultado antes de entregar prontuário, farmácia ou dado financeiro. Hoje nenhuma dessas checagens tem dono: o diagrama de componentes mostra 7 microsserviços, cada um livre para decidir sozinho o que aceita como autorização - inclusive aceitá-la do corpo da requisição ou apenas ocultar a opção na interface, que é exatamente o que CWE-602 descreve e o que o passo 3 do CA05 explora. A seção 3.1 já nomeou um **Serviço de Autorização** como componente da arquitetura segura, consultado por todos os serviços de negócio antes de qualquer operação sensível; esta decisão formaliza o que esse componente é, por que ele existe separado dos serviços de negócio e o que ele resolve que sete implementações independentes não resolveriam.

- **Decisão.** Criar um **Serviço de Autorização** dedicado, posicionado depois do API Gateway e do Serviço de Autenticação (DA03), como **único ponto de decisão** sobre se uma sessão pode executar uma operação sobre um recurso. Ele recebe a identidade já verificada pela DA03 (quem é, qual papel, quando reautenticou), o tipo de operação solicitada e o identificador do recurso envolvido, e responde permitir ou negar combinando três fontes: o papel do profissional, o `nivelAcesso` quando o solicitante for Administrador, e o vínculo declarado entre o profissional e o paciente (atendimento em curso, internação ativa ou plantão vigente). As políticas de autorização vivem como regras declaráveis dentro deste serviço - não espalhadas pelo código de cada microsserviço - e toda decisão, permitida ou negada, é registrada no Serviço de Auditoria (DA01), com autor, operação, recurso e resultado. Nenhum serviço de negócio decide autorização por conta própria: ele executa a operação **depois** de receber a permissão, nunca antes nem em paralelo.

- **Alternativas consideradas.**
  - *Manter a autorização embutida em cada um dos 7 microsserviços.* Rejeitada por repetir a mesma checagem sete vezes, com sete oportunidades de divergência - é literalmente o estado atual que produziu T02, T04 e T06, e a mesma razão pela qual a DA03 centralizou a autenticação em vez de deixá-la em cada serviço.
  - *Autorização resolvida na interface do Desktop Cliente, ocultando opções por perfil.* Rejeitada explicitamente: é a vulnerabilidade que RS02 e RS03 existem para fechar (CWE-602), e o passo 3 do CA05 já demonstra como ela se contorna reenviando a requisição sem passar pela tela.
  - *Fundir autorização e autenticação em um único serviço (estender a DA03).* Rejeitada porque as duas mudam em ritmos diferentes: identidade muda raramente (login, MFA), enquanto papel e vínculo mudam a cada atendimento, internação ou troca de plantão. Fundir os dois tornaria o serviço de autenticação também responsável por decidir o que cada sessão pode acessar, ampliando o raio de impacto de qualquer falha nele e contrariando a separação de responsabilidades que a própria DA03 estabelece entre "quem você é" e "o que você pode fazer".
  - *Adotar um motor de políticas de terceiro, hospedado fora do perímetro do hospital.* Não rejeitada, apenas adiada: resolveria bem a expressão declarativa de políticas, mas tornaria toda operação sensível dependente de uma chamada de rede a um serviço fora do controle do hospital - o mesmo problema de disponibilidade e de custódia de dado sensível que a DA01 já rejeitou para a trilha de auditoria. Fica registrada como opção de **implementação interna** do Serviço de Autorização (o motor de políticas hospedado dentro do perímetro), não como serviço terceirizado.

- **Consequências.**
  - *Positivas.* Uma única implementação satisfaz RS02 (papel e vínculo), RS03 (`nivelAcesso`) e o controle R04-C2 (vínculo profissional-paciente) ao mesmo tempo - é a mesma propriedade que a Etapa 2 já atribuiu ao R06-C1 isoladamente, e esta decisão é o que a torna possível na arquitetura: um único serviço, não uma coincidência entre implementações separadas. Toda negativa de acesso fica registrada via DA01, o que dá à Regra 3 da Etapa 6 e à detecção de padrão de consulta de R04-C5 um evento concreto para observar. E fecha definitivamente o CWE-602: a interface pode continuar ocultando opções por conveniência de uso, mas deixa de ser, em qualquer hipótese, o controle de segurança.
  - *Negativas.* O Serviço de Autorização se torna **passagem obrigatória** de toda operação sensível, somando-se ao API Gateway, ao Serviço de Autenticação e ao SGBD central como mais um ponto de concentração - a mesma característica que sustenta R05. Se ele cair, nenhuma prescrição, alta, registro de óbito, alteração de perfil ou consulta vinculada se completa, porque a decisão de negar por padrão (falha fechada, no mesmo regime de RS01 e RS02) impede prosseguir sem resposta do serviço. **Este ponto precisa ser conciliado com a DA01 e a DA03**, no mesmo sentido que a DA03 já sinalizou em relação à DA01: redundância do serviço e uma política explícita de latência máxima antes de recusar, para que uma indisponibilidade curta não pare o hospital inteiro.
  - *Custo.* Definir e manter as políticas de papel × `nivelAcesso` × vínculo como um artefato próprio, versionado e revisável - trabalho concentrado em um lugar, mas que precisa de dono, no mesmo sentido que a função Govern já cobra dos mapeamentos de R04 e R06. E cada um dos 7 serviços de negócio precisa adicionar uma chamada síncrona a este serviço antes de qualquer operação sensível, o que é esforço de integração, mas evita sete implementações divergentes na alternativa descartada.

### DA03 - Serviço de autenticação dedicado como emissor único da identidade de sessão - @lilydias24

- **Contexto.** O diagrama de componentes do SIGH mostra 7 microsserviços, cada um com
  seu firewall antes do DAO, todos atrás de um API Gateway. **Nenhum deles é um serviço
  de autenticação**: as credenciais são atributos de `Funcionario`, dentro do Serviço de
  Funcionários, que é também o serviço de cadastro administrativo. Isso produz três
  efeitos que a análise já registrou: quem alcança o cadastro alcança as credenciais
  (T06/CA05), não existe um lugar único onde impor MFA, bloqueio e expiração de sessão
  (R01), e cada serviço fica livre para decidir sozinho o que aceita como identidade -
  inclusive aceitá-la do corpo da requisição, que é a raiz de T02 e T06.
- **Decisão.** Introduzir um **serviço de autenticação dedicado**, atrás do API Gateway e
  separado do Serviço de Funcionários, como **único emissor** da identidade de sessão. As
  credenciais derivadas, o verificador do segundo fator, o contador de tentativas e o
  estado de bloqueio passam a residir nele. O Gateway valida a sessão a cada requisição e
  propaga aos serviços de negócio uma identidade verificada (quem é, qual papel, quando
  reautenticou). **Os serviços de negócio nunca aceitam identidade vinda do cliente** -
  apenas a que chega por esse canal verificado.
- **Alternativas consideradas.**
  - *Manter a autenticação dentro do Serviço de Funcionários.* Rejeitada: mantém as
    credenciais no mesmo perímetro do cadastro administrativo, que é exatamente o
    caminho que CA05 percorre para ler `senhaLogin` de todos os perfis.
  - *Cada serviço valida credenciais por conta própria.* Rejeitada: multiplica a
    implementação de MFA e bloqueio por sete, e faz o limite de tentativas ser
    contornável alternando o serviço atacado.
  - *Validar a sessão apenas no API Gateway, sem repassar identidade verificada.*
    Rejeitada por não sobreviver a defesa em profundidade: qualquer chamada que alcance
    um serviço por outro caminho ficaria sem verificação, e a decisão de autorização
    dentro do serviço voltaria a depender do que o cliente afirma ser.
  - *Delegar a um provedor de identidade institucional (SSO externo).* Não rejeitada,
    apenas adiada. Resolve bem MFA e política de senha, mas acrescenta dependência
    externa a um sistema com requisito de operação 24h/7d (RNF03) e não transfere a
    responsabilidade do hospital sobre os dados. Fica registrada como evolução possível
    depois que o serviço próprio existir e a fronteira estiver clara.
- **Consequências.**
  - *Positivas.* Cria o lugar único onde RS01 pode ser implementado de fato, e onde as
    cláusulas 3 a 7 passam a ter dono. Separa ler o cadastro de ler as credenciais,
    cortando o encadeamento T06 → T01 descrito em CA05. Fornece a identidade verificada
    de que **RS02 e RS03 também dependem** - os dois exigem que o servidor saiba quem
    está chamando, e nenhum dos dois pode garantir isso sozinho.
  - *Negativas, e esta precisa ficar explícita.* O serviço de autenticação passa a ser
    **passagem obrigatória de toda operação**, somando-se ao API Gateway e ao SGBD único
    como mais um ponto de concentração - a mesma característica que sustenta T05/R05. Se
    ele cair, ninguém entra no sistema, com pacientes internados no prédio. A decisão só
    é aceitável acompanhada de redundância desse serviço e de uma política explícita para
    o que acontece durante sua indisponibilidade, que é o papel da cláusula 8 de RS01
    (*break-glass*). **Este ponto precisa ser conciliado com a DA01**, de responsabilidade
    do @lorenzoficher, que trata do isolamento e do desenho geral da arquitetura segura.
  - *Custo.* Exige migrar as credenciais existentes para fora do Serviço de Funcionários
    e reescrever o fluxo de login do Desktop Cliente - trabalho concentrado, mas feito
    uma vez só, contra sete implementações na alternativa descartada.

### Conciliação entre a DA01 e a DA03 - @lorenzoficher

A DA03 registrou, nas suas consequências negativas, que o serviço de autenticação passa a
ser passagem obrigatória de toda operação, e pediu que esse ponto fosse conciliado com a
DA01. O pedido procede: as duas decisões acrescentam, cada uma, um componente obrigatório
ao mesmo caminho, e o efeito sobre o R05 do @PPrauchner é somado, não paralelo. O que
segue é o que muda na DA01 por causa da DA03, e a regra que resolve a interação.

**Os dois acoplamentos não têm o mesmo tamanho, e tratá-los como iguais seria um erro de
priorização.** O Serviço de Autenticação está no caminho de *toda* operação, inclusive de
uma consulta de prontuário: se ele cai, ninguém entra. O Serviço de Auditoria é condição
apenas das operações irreversíveis - registrar óbito (UC10) e autorizar alta (UC06) - e,
mesmo nessas, o que a DA01 exige não é que o serviço esteja no ar, e sim que o evento
esteja durável, o que o buffer local já garante. Numa indisponibilidade curta, a queda da
autenticação para o hospital; a da auditoria não para nada. A redundância que a DA03 pede
é, portanto, mais urgente que a da DA01, e a ordem de implementação de 14.5 deve refletir
isso.

**O buffer tem limite, e o limite precisa ser declarado em projeto.** A vantagem descrita
acima vale enquanto o buffer local absorver a indisponibilidade. Esgotado o espaço
reservado, a durabilidade deixa de ser garantida e o acoplamento volta inteiro: a operação
irreversível passa a falhar de forma fechada, como manda o R03-C5. A escolha continua
sendo a da DA01 - entre concluir sem prova e não concluir, não se conclui -, mas o ponto
em que ela é exercida não pode ser descoberto durante o incidente. O buffer é dimensionado
para a janela de indisponibilidade que o tratamento de R05 admite como tolerável, e a sua
ocupação recebe alerta próprio, no mesmo regime do R05-C5, para que a reposição do Serviço
de Auditoria ocorra antes do esgotamento e não depois.

**A regra que concilia as duas: a autenticação pode degradar, a auditoria não.** A
cláusula 8 de RS01 prevê o *break-glass* para quando o segundo fator estiver indisponível
durante o atendimento. Esse é exatamente o momento em que a prova vale mais, e não menos,
porque se trata de um acesso que contornou a autenticação normal. O caminho de exceção da
DA03 não é, por isso, exceção ao acréscimo da DA01 - ele **eleva** a exigência probatória
em vez de reduzi-la. É o mesmo regime proposto para a Condição de bloqueio 3 do pipeline
na [Etapa 7](E7_DevSecOps_e_video.md): o único portão sem exceção temporária possível é o
que produz evidência, porque nenhuma trilha futura produz prova sobre o que já passou.

**Disso decorre uma exigência nova para a trilha: registrar a qualidade da identidade, e
não apenas a identidade.** A justificativa do residual de R03 na
[Etapa 2](E2_Riscos_e_NIST_CSF.md) já reconhece que a trilha prova qual sessão registrou,
não quem estava no teclado. A DA03 torna essa dependência concreta e, ao mesmo tempo,
delimitável: como passa a existir um emissor único de identidade, ele pode informar ao
Serviço de Auditoria *como* aquela identidade foi estabelecida - senha e segundo fator,
reautenticação dentro da janela, ou *break-glass* com o segundo profissional
identificado. Sem esse campo, um óbito registrado em *break-glass* e um óbito registrado
com autenticação plena ficam indistinguíveis na trilha, o que recriaria, dentro do
próprio controle, a ambiguidade que o R03 descreve.

**Ordem entre as duas decisões: a DA03 vem antes da DA01, ou junto, nunca depois.** A
autoria que a trilha registra vale exatamente o que valer a autenticação que a sustenta -
uma trilha em operação sobre uma autenticação que ainda guarda `senhaLogin` em texto
simples produz registros bem formados e fracamente atribuíveis. É o mesmo argumento do
residual de R03, agora com componente e responsável definidos.

**O que fica em aberto para o grupo.** A conciliação não elimina o fato de a arquitetura
passar a ter quatro passagens obrigatórias: Gateway, autenticação, SGBD central e, nas
operações irreversíveis, o acréscimo à trilha. A regra de degradação prevista em R05-C5
precisa dizer explicitamente o que é suspenso e o que é preservado durante a saturação, e
o acréscimo à trilha tem de estar no conjunto preservado. Isso é matéria da RS03 e da
DA02, e fica registrado aqui como dependência.
