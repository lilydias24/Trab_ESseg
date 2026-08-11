# Etapa 7 - DevSecOps e Vídeo Final

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @ARTHUR9011

| Item | Responsável | Situação |
| --- | --- | --- |
| Pipeline DevSecOps (8 momentos + 3 condições de bloqueio) | @ARTHUR9011 (rascunho), @lorenzoficher (revisão) | Pendente |
| Roteiro do vídeo - parte de cada trilha | Todos | Pendente |
| Organização do roteiro em documento único | @mariasanchez0’s | Pendente |
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
| 8 | Monitorar, responder e retroalimentar | Centralizar logs, ativar as três regras, tratar incidentes e devolver achados ao backlog, ao STRIDE e ao registro de riscos | [Etapa 6](E6_Monitoramento_e_deteccao.md) e risco residual da Etapa 2 | Donos das regras; @lilydias24 consolida o roteiro; dono da trilha trata a causa |

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
integridade divergente não pode ser liberado por exceção: é necessário revogar/corrigir e
executar novamente o pipeline.

## 2. Roteiro do vídeo

Cada integrante escreve a parte referente à própria trilha: o que fez, qual decisão tomou e qual foi o resultado.

| Bloco | Conteúdo | Responsável | Situação |
| --- | --- | --- | --- |
| Abertura e apresentação do SIGH | | @lilydias24 | Pendente |
| Trilha Spoofing → R01 → RS01 → hash de senha → regra 1 | | @lilydias24 | Pendente |
| Trilha Tampering → R02 → RS02 → regra 2 | | @ARTHUR9011 | Pendente |
| Trilha Repudiation → R03 e arquitetura segura | | @lorenzoficher | Pendente |
| Trilha Information Disclosure → R04, priorização e achados do ZAP | | @mariasanchez0’s | Pendente |
| Trilha DoS/EoP → R05 e R06 → RS03 → autorização → regra 3 | | @PPrauchner | Pendente |
| Encerramento e conclusões | | @mariasanchez0’s (organiza) | Pendente |

## 3. Vídeo final

- **Duração:** 5 a 8 minutos
- **Link:** *(a publicar - responsabilidade do @ARTHUR9011)*
