# Etapa 7 - DevSecOps e Vídeo Final

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @ARTHUR9011

| Item | Responsável | Situação |
| --- | --- | --- |
| Pipeline DevSecOps (8 momentos + 3 condições de bloqueio) | @ARTHUR9011 (rascunho), @lorenzoficher (revisão) | Concluído (observações da revisão incorporadas) |
| Roteiro do vídeo - parte de cada trilha | Todos | Em andamento (Abertura e os cinco blocos de trilha escritos; Information Disclosure aguarda o trecho final do ZAP para fechar) |
| Organização do roteiro em documento único | @mariasanchez0 | Em andamento (os sete blocos reunidos aqui, incluindo o DoS/EoP do @PPrauchner; falta o arquivo próprio em `roteiros/`, exigido pelo §31) |
| Gravação (5-8 min) e publicação do link | Todos; edição por @ARTHUR9011 | Pendente |

---

## 1. Pipeline DevSecOps

Como o SIGH não possui implementação, esta seção especifica o fluxo que deve ser
automatizado quando houver código e infraestrutura. Resultado de ferramenta, relatório e
aprovação descritos abaixo são **evidências exigidas no futuro**, não execuções já
realizadas. O desenho incorpora segurança ao ciclo inteiro, conforme o
[NIST SP 800-218 - SSDF](https://csrc.nist.gov/pubs/sp/800/218/final), e protege também o
próprio ambiente de automação, seguindo o
[OWASP CI/CD Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html).

| # | Momento do ciclo | Prática de segurança | Origem no trabalho | Responsável pela execução |
| --- | --- | --- | --- | --- |
| 1 | Planejar a mudança | Identificar o caso de abuso, atualizar STRIDE quando a superfície mudar, associar o risco e escrever critérios de segurança antes do desenvolvimento | [Etapa 1](E1_Casos_de_abuso_e_Stride.md) e [Etapa 2](E2_Riscos_e_NIST_CSF.md) | Dono da trilha alterada; líder da etapa de riscos valida a rastreabilidade |
| 2 | Projetar e revisar a solução | Converter o risco em requisito verificável, revisar fronteiras de confiança e registrar decisões e consequências arquiteturais | [Etapa 3](E3_Arquitetura_segura.md) | Responsável pelo requisito/decisão e revisor de arquitetura independente |
| 3 | Codificar e testar localmente | Trabalhar em branch; escrever primeiro os testes válido e malicioso; aplicar a prática de código seguro, lint e varredura de segredos antes do envio | [Etapa 4](E4_Codigo_seguro_e_testes.md) | Autor da mudança e responsável pela prática segura relacionada |
| 4 | Validar o pull request no CI | Compilar, executar testes unitários, de integração e segurança, SAST e varredura de segredos; exigir revisão e atenção especial a mudanças no pipeline | Testes da Etapa 4 e critérios RS01-RS03 | Pipeline com conta de serviço de privilégio mínimo; autor corrige e revisor aprova |
| 5 | Verificar dependências e gerar o artefato | Executar SCA, conferir arquivo de lock, licenças e dependências; gerar SBOM; empacotar uma vez e registrar hash, assinatura ou proveniência do artefato | Implementações da Etapa 4 e controles de cadeia de fornecimento do SSDF | Pipeline automático; @ARTHUR9011 mantém a definição do gate e o autor trata os achados |
| 6 | Promover para homologação e testar dinamicamente | Implantar o mesmo artefato em ambiente isolado, injetar segredos fora do repositório, executar regressão de segurança e DAST com ZAP | [Etapa 5](E5_Verificacao_de_vulnerabilidades.md) | @PPrauchner conduz a sessão; @mariasanchez0’s analisa os achados; autor corrige |
| 7 | Aprovar e implantar a versão | Conferir os gates, aprovações e exceções vigentes; promover exatamente o artefato testado; validar configuração, migração e plano de reversão | Riscos residuais da Etapa 2 e correções das Etapas 4-5 | Responsável pela release e aprovador independente designados pelo grupo |
| 8 | Monitorar, responder e retroalimentar | Centralizar logs, ativar as três regras, tratar incidentes e devolver achados ao backlog, ao STRIDE e ao registro de riscos | Serviço de Auditoria da DA01 na [Etapa 3](E3_Arquitetura_segura.md), [Etapa 6](E6_Monitoramento_e_deteccao.md) e risco residual da Etapa 2 | Donos das regras; @lilydias24 consolida o roteiro; dono da trilha trata a causa |

Os nomes da última coluna preservam atribuições já existentes. Onde o repositório ainda
não nomeia uma pessoa, a tabela registra o papel que o grupo precisa designar antes de
operar o pipeline; ela não cria unilateralmente uma nova responsabilidade.

### Evidência e proteção do pipeline

Cada execução deve registrar `pipelineRunId`, commit, branch, autor do disparo, horário
UTC, versão das ferramentas e das regras, resultado de cada etapa, aprovações e hash do
artefato. Relatórios completos ficam em armazenamento controlado; o PR recebe apenas o
resumo necessário, sem credenciais, tokens ou dados clínicos. O artefato é gerado uma
única vez no Momento 5 e promovido pelo mesmo hash nos Momentos 6 e 7, evitando que uma
versão diferente daquela testada chegue à produção.

O histórico das execuções também é uma evidência de segurança e deve ser somente de
acréscimo, seguindo o mesmo princípio da DA01. A conta que administra o CI pode consultar e
reter esse histórico, mas não reescrever nem excluir execuções, resultados ou aprovações;
eventuais correções são novos registros vinculados ao `pipelineRunId` original.

Branch principal, configuração do pipeline e ambientes de release exigem proteção contra
alteração direta. Contas de serviço usam privilégio mínimo, segredos vêm de mecanismo
próprio e componentes externos do pipeline devem ser fixados em versão imutável e
revisados. Essas medidas seguem também o
[OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/), que
recomenda integrar modelagem de ameaças, varredura de segredos, SAST, SCA e DAST ao fluxo.

### Condições de bloqueio do pipeline

| # | Condição | Momento em que é verificada | Justificativa |
| --- | --- | --- | --- |
| 1 | **Bloquear o merge:** build, lint ou teste obrigatório falhou; segredo foi detectado; revisão independente está ausente; ou SAST encontrou vulnerabilidade Alta/Crítica sem tratamento aprovado | Momento 4 - pull request | Código que não compila, viola requisito testado, expõe segredo ou contém falha grave não pode entrar na branch protegida |
| 2 | **Bloquear a promoção:** SBOM ou proveniência está ausente; SCA aponta componente Alta/Crítica explorável; DAST/ZAP aponta achado Alta/Crítica; ou um cenário de segurança associado ao requisito falhou | Momentos 5 e 6 - artefato e homologação | Impede promover dependência vulnerável, artefato sem origem demonstrável ou comportamento inseguro observado no ambiente executável |
| 3 | **Bloquear a implantação:** hash difere do artefato homologado; aprovação obrigatória, plano de reversão ou evidência dos gates está ausente; ou auditoria/monitoramento exigido pelo risco está indisponível | Momento 7 - produção | Preserva integridade da entrega e evita colocar em operação uma versão sem rastreabilidade, recuperação ou capacidade de detectar abuso |

Todos os gates falham de forma fechada: ausência de resultado equivale a falha, não a
aprovação. Uma exceção exige risco identificado, justificativa, escopo, controle
compensatório, responsável que aceita o risco e prazo de expiração; ela fica anexada à
execução e precisa de aprovação independente. Segredo confirmado ou artefato com
integridade divergente não pode ser liberado por exceção. A indisponibilidade de auditoria
ou monitoramento exigido pelo risco também não admite exceção temporária, pois uma trilha
criada depois não recupera a prova do que já ocorreu. Nesses casos, é necessário
revogar/corrigir ou restaurar o controle e executar novamente o pipeline.

### Verificação planejada do pipeline

Os cenários abaixo devem virar testes da configuração quando o pipeline for implementado:

| ID | Cenário | Resultado esperado |
| --- | --- | --- |
| P7-TV01 | Teste de segurança falha em um pull request | Gate 1 impede o merge e relaciona o teste ao requisito violado |
| P7-TV02 | Varredura encontra credencial válida no commit | Gate 1 impede o merge; segredo é revogado antes de nova execução |
| P7-TV03 | Artefato não possui SBOM ou o ZAP encontra achado Alto | Gate 2 impede a promoção para produção e preserva o relatório |
| P7-TV04 | Hash do artefato de produção difere daquele homologado | Gate 3 impede a implantação sem permitir exceção |
| P7-TV05 | Exceção não informa aprovador independente ou expiração | Exceção é inválida e o gate permanece bloqueado |
| P7-TV06 | Todos os controles passam e o mesmo hash percorre homologação e produção | Promoção é liberada e todas as evidências ficam vinculadas ao `pipelineRunId` |
| P7-TV07 | Auditoria ou monitoramento exigido pelo risco está indisponível e é solicitada uma exceção temporária | Gate 3 impede a implantação e rejeita a exceção até que o controle seja restaurado |

### Revisão da especificação (@lorenzoficher)

Revisado o desenho do @ARTHUR9011: os 8 momentos cobrem o ciclo, cada um se ancora em uma
etapa já entregue e os 3 gates falham de forma fechada, o que atende ao que a etapa pede.
Três observações de complemento, nenhuma delas contradizendo o desenho.

1. **O Momento 8 depende de uma decisão de arquitetura, não só de configuração.** Ele
   pressupõe "centralizar logs" e "ativar as três regras", e essa capacidade não existe no
   modelo atual - é o que a **DA01** da [Etapa 3](E3_Arquitetura_segura.md) institui ao
   criar o Serviço de Auditoria com armazenamento separado. Sem essa decisão implementada,
   o Momento 8 não tem de onde ler, e as evidências exigidas em 14.4 para R01, R02, R03 e
   R06 ficam sem origem. Vale explicitar essa dependência na tabela do Momento 8.
2. **A Condição de bloqueio 3 já cobre o essencial da minha trilha, e convém nomeá-lo.**
   Ela bloqueia a implantação quando "auditoria/monitoramento exigido pelo risco está
   indisponível" - isto é, exatamente o R03-C3. Como o R03 é o único risco cujo controle
   perde valor retroativamente (nenhuma trilha futura produz prova sobre o que já passou),
   sugiro que este gate seja o único do desenho **sem exceção temporária possível**, no
   mesmo regime que o texto já reserva a segredo confirmado e a artefato divergente.
3. **O pipeline precisa auditar a si mesmo.** A seção de evidência já registra
   `pipelineRunId`, autor do disparo e aprovações, o que é o suficiente. Observo apenas que
   esse registro deve seguir o mesmo princípio de acréscimo apenas da DA01 - um histórico de
   execuções que o próprio administrador do CI possa reescrever reproduz, no ambiente de
   automação, a lacuna que o R03 descreve no ambiente clínico.

> **Resultado da revisão:** as três observações foram incorporadas à especificação: a DA01
> passou a constar como origem do Momento 8, o histórico do pipeline foi definido como
> somente de acréscimo e a indisponibilidade de auditoria/monitoramento passou a rejeitar
> qualquer exceção temporária no Gate 3.

## 2. Roteiro do vídeo

Cada integrante escreve a parte referente à própria trilha: o que fez, qual decisão tomou e qual foi o resultado.

| Bloco | Conteúdo | Responsável | Situação |
| --- | --- | --- | --- |
| Abertura e apresentação do SIGH | | @lilydias24 | Concluído (incluído no documento único) |
| Trilha Spoofing → R01 → RS01 → hash de senha → regra 1 | | @lilydias24 | Concluído (incluído no documento único) |
| Trilha Tampering → R02 → RS02 → regra 2 | Da alteração sem autoria à prevenção, auditoria e detecção correlacionada | @ARTHUR9011 | Concluído (incluído no documento único) |
| Trilha Repudiation → R03 → DA01 → trilha de auditoria | Da operação sem autor à decisão de arquitetura que produz a prova | @lorenzoficher | Concluído (incluído no documento único) |
| Trilha Information Disclosure → R04, priorização e achados do ZAP | Da ausência de segunda barreira após o login à decisão de arquitetura DA02 e à detecção de padrão de consulta | @mariasanchez0 | Rascunho concluído (aguarda achados do ZAP da Etapa 5 para o trecho final) |
| Trilha DoS/EoP → R05 e R06 → RS03 → autorização → regra 3 | Das duas categorias que se encontram no CA05 à autorização decidida no servidor e à detecção da elevação | @PPrauchner | Concluído |
| Encerramento e conclusões | Síntese das cinco trilhas nas três decisões de arquitetura e no que ainda falta implementar | @mariasanchez0 (organiza) | Rascunho concluído (duração já conferida contra o orçamento total dos sete blocos) |

### Abertura - roteiro de @lilydias24

- **Duração-alvo:** 45 a 55 segundos.
- **Objetivo:** situar o sistema e o método em poucos segundos, para que os cinco blocos
  seguintes possam ir direto ao ponto sem repetir contexto.

**Narração sugerida:**

> O sistema analisado é o SIGH, um sistema integrado de gestão hospitalar que o grupo já
> havia modelado em trabalho anterior. Recortamos cinco módulos: cadastro e prontuário de
> pacientes, atendimento e consultas, internação e leitos, farmácia e prescrição, e
> financeiro. Escolhemos esse sistema porque ele reúne o que uma análise STRIDE precisa -
> vários perfis com permissões diferentes, integração com sistemas externos, dados de
> saúde, que são dados pessoais sensíveis, e operações que não têm desfazimento, como a
> alta hospitalar e o registro de óbito. Como já tínhamos os diagramas de classes,
> componentes e sequência, cada ameaça pôde ser ancorada em um campo, uma operação ou um
> componente reais, e não em suposições. O trabalho foi dividido por categoria do STRIDE:
> cada integrante levou uma categoria do início ao fim - da ameaça ao risco, do risco ao
> requisito, do requisito ao código e à regra de detecção. É isso que vocês vão ver a
> seguir, uma trilha por pessoa.

**Sequência visual e evidência:**

| Tempo | Mostrar na tela | Mensagem principal |
| --- | --- | --- |
| 0-15 s | Seções 8.1 e 8.2 da [Etapa 1](E1_Casos_de_abuso_e_Stride.md) | Qual é o sistema e por que ele foi escolhido |
| 15-30 s | `diagrams/estrutura/Diagramas_SIGH - Componentes.png` | Sete microsserviços, API Gateway e SGBD único |
| 30-45 s | Tabela de trilhas do [README](../README.md) | Uma categoria STRIDE por integrante, do início ao fim |

### Bloco Spoofing - roteiro de @lilydias24

- **Duração-alvo:** 70 a 80 segundos.
- **Objetivo:** mostrar a trilha completa de uma ameaça que é, ao mesmo tempo, a mais
  simples de explicar e a que habilita as demais - e ser honesta sobre o que o tratamento
  não resolve.

**Narração sugerida:**

> Minha trilha começa no T01, o roubo de identidade. No modelo de domínio do SIGH, a
> senha do funcionário é um campo de texto comum, sem hash e sem salt, e saber a senha é
> tudo que o sistema exige para acreditar que você é aquela pessoa. Isso contradiz o
> próprio RNF05 do projeto, que exige criptografia para as informações médicas: a proteção
> estava no requisito e não chegou ao desenho. Na Etapa 2 isso virou o R01, com
> probabilidade 4 e impacto 4 - pontuação 16, o máximo da escala. Ele é o mais alto não só
> pelo dano próprio, mas porque é a porta: os casos de abuso das outras trilhas citam a
> conta assumida como caminho de entrada. Na Etapa 3, a RS01 converteu isso em requisito -
> senha derivada com salt, segundo fator, reautenticação antes de prescrever, dar alta ou
> registrar óbito, bloqueio por tentativas e expiração de sessão. E uma cláusula que
> aprendi a considerar obrigatória em hospital: um caminho de exceção auditado, porque
> impedir um médico de prescrever numa emergência transfere o dano para o paciente. Na
> Etapa 4, implementei o armazenamento seguro: dois testes escritos antes do código, e o
> caso malicioso é o vazamento da tabela do CA01 - o atacante reenvia o valor gravado como
> se fosse a senha, e é recusado. A Regra 1 fecha o ciclo detectando rajadas de falha,
> sucesso logo depois delas e sessões simultâneas em alas diferentes, sem confundir isso
> com a troca de turno num terminal compartilhado. Mesmo assim o risco residual continua
> Alto, e isso é proposital: o segundo fator ainda é algo que a mesma pessoa carrega. Um
> segundo fator não é uma segunda pessoa.

**Sequência visual e evidência:**

| Tempo | Mostrar na tela | Mensagem principal |
| --- | --- | --- |
| 0-15 s | T01 na [Etapa 1](E1_Casos_de_abuso_e_Stride.md) e o campo `senhaLogin` no diagrama de classes | A senha em texto simples contradiz o RNF05 do próprio projeto |
| 15-28 s | Registro de R01 na [Etapa 2](E2_Riscos_e_NIST_CSF.md) | 4 × 4 = 16, Crítico, e habilitador das outras trilhas |
| 28-45 s | Cláusulas e critérios de RS01 na [Etapa 3](E3_Arquitetura_segura.md) | MFA, reautenticação em operação irreversível e exceção assistencial auditada |
| 45-62 s | Saída real dos testes na [Etapa 4](E4_Codigo_seguro_e_testes.md) | O vazamento da tabela deixa de ser reutilizável - teste executado |
| 62-78 s | Gatilhos da Regra 1 na [Etapa 6](E6_Monitoramento_e_deteccao.md) e o residual Alto na Etapa 2 | Detecção que não confunde ataque com troca de turno; e o que o controle não resolve |

Durante a gravação, destacar os identificadores `T01`, `R01`, `RS01`, `R01-C1` e
`Regra 1`. A saída dos testes da Etapa 4 é a única evidência **executada** de toda a
minha trilha - o restante é especificação, e deve ser apresentado como tal. Se for
preciso cortar tempo, manter a pontuação 16, o resultado do caso malicioso e a frase
final sobre o residual; a cláusula de exceção assistencial pode ficar só no documento.

### Bloco Repudiation - roteiro de @lorenzoficher

- **Duração-alvo:** 70 a 80 segundos.
- **Objetivo:** mostrar que a ameaça desta trilha não é um ataque, e sim a ausência de
  prova produzida pelo funcionamento normal do sistema - e que por isso ela é a condição de
  verificação das outras trilhas.

**Narração sugerida:**

> Minha trilha começa no T03, o registro de óbito. A operação `registrarObito` guarda a
> causa, a data e a hora, mas não guarda quem registrou - e a data e a hora chegam por
> parâmetro, escolhidas por quem chama. Some-se a isso que o escopo original do SIGH
> excluiu o registro de eventos críticos, e o resultado é um registro íntegro que ninguém
> consegue atribuir a ninguém. Na Etapa 2 isso virou o R03, e ele é o único risco do
> trabalho com probabilidade 4 sem precisar de atacante: não existe execução dessa operação
> que produza um registro rastreável, então a condição do risco é o uso normal do sistema.
> Impacto 3, pontuação 12, Crítico. O tratamento tem cinco controles, e o que os une é que
> nenhum deles impede o óbito de ser registrado - todos impedem que ele seja anônimo:
> autoria vinda da sessão, carimbo de tempo do servidor separado do momento clínico
> informado, trilha somente de acréscimo, registro do que foi transmitido ao Sistema
> Governamental e confirmação por uma segunda identidade. Na Etapa 3, isso virou a decisão
> DA01: a trilha de auditoria como serviço próprio, com armazenamento separado do banco
> central, em que os serviços podem acrescentar e ninguém pode alterar. Essa decisão não
> atende só a minha trilha - as evidências que o R01, o R02 e o R06 exigem dependem todas
> dessa mesma trilha existir. E ela tem um custo que vale dizer: se a auditoria for condição
> da operação, ela vira um ponto de indisponibilidade, o que conversa direto com o R05 -
> por isso o evento é gravado em buffer durável antes de responder ao usuário. O residual
> cai para Médio, e não para baixo, por uma razão honesta: o servidor carimba quando o
> registro foi feito, não quando a morte aconteceu.

**Sequência visual e evidência:**

| Tempo | Mostrar na tela | Mensagem principal |
| --- | --- | --- |
| 0-15 s | T03 e CA03 na [Etapa 1](E1_Casos_de_abuso_e_Stride.md), com a assinatura `registrarObito(data, hora)` | A operação não recebe o responsável e o tempo é informado, não carimbado |
| 15-30 s | Registro e justificativa de R03 na [Etapa 2](E2_Riscos_e_NIST_CSF.md) | Probabilidade 4 sem atacante: o uso correto do sistema já produz a condição |
| 30-50 s | Controles R03-C1 a R03-C5 em 14.4 | Os controles não impedem o registro; impedem que ele seja anônimo |
| 50-70 s | DA01 e o diagrama da arquitetura segura na [Etapa 3](E3_Arquitetura_segura.md) | Trilha como serviço próprio, append-only, fora do SGBD central - e o trade-off com R05 |
| 70-80 s | Linha do R03 em 14.6 | Residual Médio, com a limitação declarada do carimbo clínico |

Durante a gravação, destacar os identificadores `T03`, `R03`, `DA01` e a expressão
**somente de acréscimo**. Se for necessário reduzir o tempo, o que não pode sair é o
argumento da probabilidade 4 sem atacante e a DA01 - o restante é detalhe. Não apresentar
os critérios de verificação como testes já executados: o SIGH não tem implementação.

### Bloco Tampering - roteiro de @ARTHUR9011

- **Duração-alvo:** 70 a 80 segundos.
- **Objetivo:** mostrar uma trilha contínua entre ameaça, risco, requisito preventivo e
  detecção, sem apresentar critérios planejados como testes já executados.

**Narração sugerida:**

> Minha trilha começa no T02, a adulteração de prescrições. A operação de atualizar
> tratamentos podia sobrescrever dosagem e intervalo sem registrar autor, validar no
> servidor, conferir a faixa terapêutica ou preservar o histórico. Na Etapa 2, transformei
> isso no R02: probabilidade 3, impacto 4 e pontuação 12, um risco Crítico porque a
> alteração pode alcançar o paciente antes da detecção. O tratamento definiu cinco
> controles: identidade da sessão, papel médico e vínculo validados no servidor, faixa
> terapêutica, versionamento imutável e reautenticação com confirmação independente. Na
> Etapa 3, a RS02 converteu os controles em requisito verificável: a operação insegura
> falha de forma fechada, preserva a versão anterior e registra as duas identidades e o
> identificador de correlação. A Regra 2 fecha o ciclo usando eventos publicados e
> recusados. Uma publicação inválida gera alerta Crítico imediato; três recusas suspeitas
> do mesmo autor ou contra a mesma prescrição em dez minutos geram alerta Alto, sem contar
> duplicatas. Assim, a trilha conecta prevenção, rastreabilidade e detecção sem permitir
> que um alerta altere sozinho uma decisão clínica.

**Sequência visual e evidência:**

| Tempo | Mostrar na tela | Mensagem principal |
| --- | --- | --- |
| 0-12 s | T02 em [Etapa 1](E1_Casos_de_abuso_e_Stride.md) | Campos e operação vulneráveis no modelo |
| 12-25 s | Registro e pontuação de R02 em [Etapa 2](E2_Riscos_e_NIST_CSF.md) | Probabilidade 3 × impacto 4 = 12, Crítico |
| 25-50 s | Enunciado, controles e critérios da RS02 em [Etapa 3](E3_Arquitetura_segura.md) | Prevenção no servidor, confirmação, versionamento e auditoria |
| 50-75 s | Gatilhos da Regra 2 em [Etapa 6](E6_Monitoramento_e_deteccao.md) | Um evento inválido publicado gera Crítico; 3 recusas/10 min geram Alto |

Durante a gravação, destacar os identificadores `T02`, `R02`, `RS02` e `Regra 2`, sem
exibir dados clínicos reais. Se for necessário reduzir o tempo, manter pontuação, cinco
controles e dois gatilhos; exemplos detalhados de falso positivo e resposta ficam no
documento, não precisam ser narrados.

### Bloco Information Disclosure - roteiro de @mariasanchez0

- **Duração-alvo:** 60 a 70 segundos.
- **Objetivo:** mostrar que a ameaça desta trilha não exige nenhuma técnica de invasão -
  só a ausência de uma segunda barreira depois do login - e situar o que a Etapa 5 (ZAP)
  deve procurar para testar essa mesma lacuna na prática.

**Narração sugerida:**

> Minha trilha começa no T04, a exposição de informação. No SIGH, Farmácia e Financeiro
> não têm microsserviço próprio - eles moram dentro do Serviço de Paciente e do Serviço
> de Atendimento -, e o identificador do paciente é sequencial, sem verificação de vínculo
> entre quem consulta e quem está sendo consultado. Isso significa que qualquer perfil
> autenticado, não só médico, alcança prontuário, alergias, prescrição, convênio e valor
> cobrado no mesmo movimento, e variar um número é suficiente para percorrer a base
> inteira. Na Etapa 2, isso virou o R04: probabilidade 4, impacto 4, pontuação 16 - empata
> com o risco de maior nota do trabalho, e a razão é a mesma raiz, a ausência de uma
> segunda barreira depois do login. O tratamento tem cinco controles: identificador não
> enumerável, vínculo profissional-paciente verificado no servidor, isolamento entre os
> módulos, dado retornado no mínimo necessário e alerta de padrão de consulta atípico. Na
> Etapa 3, isso puxou uma decisão de arquitetura própria, a DA02: um Serviço de
> Autorização único, que passa a decidir no servidor não só o `nivelAcesso` da RS03, mas
> também esse vínculo - a mesma checagem que o R06 já usa para revalidar autorização,
> agora reaproveitada para leitura de prontuário.

**Sequência visual e evidência:**

| Tempo | Mostrar na tela | Mensagem principal |
| --- | --- | --- |
| 0-15 s | T04 e CA04 na [Etapa 1](E1_Casos_de_abuso_e_Stride.md), com `buscarPacientePorIdentificador(idPaciente)` no diagrama de classes | O identificador sequencial e a ausência de vínculo são a porta de entrada |
| 15-30 s | Registro e justificativa de R04 na [Etapa 2](E2_Riscos_e_NIST_CSF.md) | 4 × 4 = 16, Crítico, empatado com o risco de maior pontuação do trabalho |
| 30-45 s | Controles R04-C1 a R04-C5 em 14.4 e a DA02 na [Etapa 3](E3_Arquitetura_segura.md) | O Serviço de Autorização único decide vínculo e `nivelAcesso` no mesmo lugar |
| 45-65 s | Achados relacionados a controle de acesso na [Etapa 5](E5_Verificacao_de_vulnerabilidades.md), quando disponíveis | Onde a varredura dinâmica confirma, na prática, o mesmo tipo de lacuna |

Durante a gravação, destacar os identificadores `T04`, `R04`, `DA02` e o número **16** ao
lado do de R01, para reforçar visualmente o empate. Se a Etapa 5 já tiver achados de
controle de acesso quebrado (IDOR ou equivalente) no momento da gravação, inserir uma
frase final relacionando o achado ao R04. Se não estiver pronta, manter o bloco como está;
o argumento de R04 e DA02 já fecha a trilha com evidência própria.

> **Pendente:** completar o trecho de achados do ZAP assim que a Etapa 5 (@PPrauchner
> conduz a sessão, @mariasanchez0 analisa) estiver concluída.

### Bloco DoS/EoP - roteiro de @PPrauchner

- **Duração-alvo:** 70 a 80 segundos.
- **Objetivo:** mostrar a única trilha que carrega **duas** categorias do STRIDE e explicar
  por que elas foram levadas juntas - o volume de leitura que a elevação de privilégio
  permite é o mesmo volume que satura o banco. É também o único bloco que precisa fixar a
  distinção que separa esta trilha da de Spoofing: aqui a identidade não foi falsificada,
  foi promovida. Os dois argumentos ocupam o teto da faixa dos blocos de trilha: o bloco é
  narrado no limite de 80 segundos, e não acima dele, porque o orçamento total do vídeo
  precisa caber nos 8 minutos do §32 - a leitura dos RNF01-RNF03 é o que sai primeiro para
  isso.

**Narração sugerida:**

> Minha trilha é a única que leva duas categorias, e elas se encontram no fim. Começa no
> T05, a indisponibilidade: os DAOs dos sete serviços terminam no mesmo SGBD e o API
> Gateway é passagem obrigatória, enquanto o RNF01, o RNF02 e o RNF03 pedem alto volume,
> escalabilidade e operação 24 horas por dia com recuperação automática. A ameaça está na
> distância entre o que os requisitos pediram e o que o projeto entregou. E segue no T06, a
> elevação de privilégio: o `nivelAcesso` do Administrador é o único atributo de
> autorização do modelo inteiro do SIGH, e ele é salvo junto com o resto do cadastro. Um
> Supervisor reenvia o próprio salvamento com `nivelAcesso` igual a Diretor, e o servidor
> grava. No CA05 as duas se costuram: a elevação é o meio, a indisponibilidade é a
> consequência - percorrer o cadastro de todas as unidades é o que o privilégio novo
> permite, e é também o volume que derruba o banco. Na Etapa 2 isso virou o R05, 12 e
> Crítico, e o R06, 8 e Alto. O ponto do R06 é este: a identidade não foi falsificada, foi
> promovida. A sessão é legítima do começo ao fim, então autenticar melhor não impede nada
> - a dúvida nunca foi quem é o usuário, é o que ele pode. Na Etapa 3, a RS03 tirou essa
> decisão da interface: ela passa a ser tomada no servidor, fora do componente que executa
> a operação, com negação por padrão, e a cláusula 8 limita a leitura em massa, que é
> exatamente onde as duas ameaças se encontram. Na Etapa 4 eu implementei isso, e o
> detalhe que mais me custou escrever é o que resume a prática: o `nivelAcesso` que chega
> do cliente é descartado, não validado - validar um valor que o cliente controla ainda é
> confiar nele. A tentativa de gravá-lo fica registrada em vez de sumir em silêncio, e é
> essa trilha que a Regra 3 consome. O gatilho que mais me interessa nela é o que
> correlaciona leitura em massa nos 60 minutos seguintes a uma elevação: é a sequência
> exata do CA05, que na apuração sempre foi lida como dois fatos independentes. E o fecho
> honesto: a RS03 não reduz o impacto do R06. Essa redução depende da RS01, porque o dano
> se realiza sobre as credenciais que ela protege. E o risco residual do R05 só desce até
> certo ponto: enquanto o SGBD for um só, a queda continua possível - isso é limitação de
> arquitetura, não do requisito.

**Sequência visual e evidência:**

| Tempo | Mostrar na tela | Mensagem principal |
| --- | --- | --- |
| 0-12 s | T05 e T06 na [Etapa 1](E1_Casos_de_abuso_e_Stride.md), com o [diagrama de implantação](../diagrams/estrutura/Diagramas_SIGH%20-%20Implantacao.png) | Um SGBD único para os sete serviços; e o `nivelAcesso` como única autorização do modelo |
| 12-26 s | Fluxo de abuso do CA05 na [Etapa 1](E1_Casos_de_abuso_e_Stride.md), passos 3 a 7 | A elevação é o meio, a indisponibilidade é a consequência do uso do privilégio obtido |
| 26-40 s | Registros de R05 e R06 em 13.4 na [Etapa 2](E2_Riscos_e_NIST_CSF.md) | 12 Crítico e 8 Alto - e a identidade promovida, não falsificada |
| 40-56 s | Cláusulas 1, 2, 3 e 8 da RS03 e a DA02 na [Etapa 3](E3_Arquitetura_segura.md) | Decisão no servidor, fora de quem executa, com negação por padrão |
| 56-68 s | Saída dos testes da Prática 2 na [Etapa 4](E4_Codigo_seguro_e_testes.md) | O `nivelAcesso` do cliente é descartado; a tentativa vira 403 registrado |
| 68-80 s | Gatilho E da Regra 3 na [Etapa 6](E6_Monitoramento_e_deteccao.md) e os residuais de R05 e R06 em 14.6 na [Etapa 2](E2_Riscos_e_NIST_CSF.md) | Leitura em massa logo após uma elevação; e o que os controles não resolvem |

Durante a gravação, destacar os identificadores `T05`, `T06`, `CA05`, `R05`, `R06`, `RS03`
e `Regra 3`, e manter a cláusula 8 visível quando a narração disser que as duas categorias
se encontram - é a única evidência de que a costura não é retórica. Os testes da Prática 2
são evidência **executada**; o restante da trilha é especificação e deve ser apresentado
como tal. Se for preciso cortar tempo, o que não pode sair é a frase sobre a identidade
promovida, o "descartado, não validado" e a dependência do impacto de R06 em relação à
RS01; a leitura de RNF01, RNF02 e RNF03 e o segundo caminho de R05 - a chamada síncrona ao
«system» Convênio - podem ficar só no documento.

### Encerramento e conclusões - roteiro de @mariasanchez0 (organiza)

- **Duração-alvo:** 25 a 35 segundos.
- **Objetivo:** fechar o vídeo amarrando as cinco trilhas em uma conclusão só, sem repetir
  o que cada bloco já mostrou.

**Narração sugerida:**

> As cinco trilhas partiram do mesmo método - ameaça, risco, requisito, código e detecção -
> e chegaram a uma conclusão em comum: quase todo o risco do SIGH nasce da mesma
> lacuna, a ausência de uma segunda verificação depois do login, seja para autenticar
> quem está entrando, para autorizar o que essa sessão pode fazer, ou para provar depois
> o que foi feito. Spoofing e Elevation of Privilege habilitam os demais; Tampering e
> Repudiation mostram o dano quando não há verificação nem prova; Information
> Disclosure mostra que a mesma ausência que permite agir também permite ler o que não
> deveria; e Denial of Service mostra que ler demais, sobre um SGBD único, já é
> derrubar - a leitura em massa é o mesmo caminho nas duas pontas. O tratamento
> proposto converge para três decisões de arquitetura -
> autenticação, autorização e auditoria centralizadas - que sozinhas não eliminam o
> risco, mas mudam sua natureza: de ausência de barreira para barreira com dono, testável
> e observável. O que fica declarado, e não escondido, é que o SIGH segue sem
> implementação: o que este trabalho entrega é a especificação, os testes definidos antes
> do código e o critério de verificação - o próximo passo é construir sobre isso.

**Sequência visual e evidência:**

| Tempo | Mostrar na tela | Mensagem principal |
| --- | --- | --- |
| 0-10 s | Tabela de trilhas do [README](../README.md) | As cinco categorias convergem para a mesma causa-raiz |
| 10-22 s | DA01, DA02 e DA03 lado a lado na [Etapa 3](E3_Arquitetura_segura.md) | Autenticação, autorização e auditoria centralizadas fecham o ciclo |
| 22-32 s | Pipeline da [Etapa 7](E7_DevSecOps_e_video.md) | O que falta é implementar e verificar - o método já está pronto |

Durante a gravação, não apresentar nenhuma parte do SIGH como implementada; o vídeo
inteiro descreve especificação e testes definidos antes do código, exceto as **duas
práticas da Etapa 4** - armazenamento de senhas e autorização no servidor -, que têm
execução real. A Etapa 5 também traz evidência executada, mas de **outro sistema**: a
sessão do ZAP rodou sobre o Juice Shop, não sobre o SIGH, e o vídeo precisa dizer isso
com todas as letras.

## 3. Vídeo final

- **Duração:** 5 a 8 minutos
- **Link:** *(a publicar - responsabilidade do @ARTHUR9011)*

### Orçamento de tempo dos sete blocos

O §32 pede preferencialmente entre 5 e 8 minutos, ou seja, no máximo 480 segundos. A soma
dos limites superiores das sete faixas fecha exatamente nesse teto, sem folga: qualquer
bloco gravado acima da própria faixa estoura o vídeo.

| Bloco | Duração-alvo |
| --- | --- |
| Abertura | 45-55 s |
| Spoofing | 70-80 s |
| Repudiation | 70-80 s |
| Tampering | 70-80 s |
| Information Disclosure | 60-70 s |
| DoS/EoP | 70-80 s |
| Encerramento | 25-35 s |
| **Total** | **410-480 s** (6:50 a 8:00) |
