# SIGH - Análise de Segurança (ESSEG)

> Trabalho da disciplina de Engenharia de Software Seguro (ESSEG). Análise de segurança incremental do **SIGH - Sistema Integrado de Gestão Hospitalar**, desenvolvida ao longo das etapas propostas pela disciplina.

## Integrantes

- Arthur Provenzi Parizotto (@ARTHUR9011)
- Emilly Nascimento Dias (@lilydias24)
- Lorenzo Ponsi Ficher (@lorenzoficher)
- Maria Eduarda Sanchez Chessio (@mariasanchez0)
- Pietro Mendes Prauchner (@PPrauchner)

## Sobre o projeto

Este repositório contém a análise de segurança do **SIGH (Sistema Integrado de Gestão Hospitalar)**, em um recorte com 5 módulos: Cadastro/Prontuário de Pacientes, Atendimento Médico/Consultas, Internação e Leitos, Farmácia/Prescrição de Medicamentos e Financeiro/Cobrança. O trabalho é composto por etapas incrementais, cada uma adicionando uma nova camada de análise sobre o mesmo sistema.

## Documentos por etapa

Cada etapa fica em seu próprio arquivo, para que as contribuições de cada integrante sejam identificáveis por commit sem conflito com o trabalho dos demais.

| Etapa | Documento | Líder |
| --- | --- | --- |
| 1 - Casos de Abuso e Modelagem STRIDE | [`E1_Casos_de_abuso_e_Stride.md`](docs/E1_Casos_de_abuso_e_Stride.md) | @lilydias24 |
| 2 - Riscos, Priorização e NIST CSF 2.0 | [`E2_Riscos_e_NIST_CSF.md`](docs/E2_Riscos_e_NIST_CSF.md) | @ARTHUR9011 |
| 3 - Projeto de uma Arquitetura Segura | [`E3_Arquitetura_segura.md`](docs/E3_Arquitetura_segura.md) | @lorenzoficher |
| 4 - Código Seguro e Testes de Segurança | [`E4_Codigo_seguro_e_testes.md`](docs/E4_Codigo_seguro_e_testes.md) | @mariasanchez0 |
| 5 - Verificação de Vulnerabilidades | [`E5_Verificacao_de_vulnerabilidades.md`](docs/E5_Verificacao_de_vulnerabilidades.md) | @PPrauchner |
| 6 - Monitoramento e Detecção de Intrusões | [`E6_Monitoramento_e_deteccao.md`](docs/E6_Monitoramento_e_deteccao.md) | @lilydias24 |
| 7 - DevSecOps e Vídeo Final | [`E7_DevSecOps_e_video.md`](docs/E7_DevSecOps_e_video.md) | @ARTHUR9011 |

> Cada arquivo abre com uma tabela indicando o responsável e a situação de cada seção, seguindo a divisão de trabalho combinada pelo grupo.

## Justificativa da escolha do sistema

O SIGH foi escolhido porque combina, em um único sistema, os elementos que a disciplina pede para uma boa análise STRIDE: múltiplos perfis de usuário com diferentes níveis de permissão (Médico, Enfermeiro, Recepcionista, Administrador), um sistema externo integrado (validação de convênio), dados de alta sensibilidade (prontuário, prescrições, dados financeiros) e operações irreversíveis de alto impacto (ex.: registro de óbito, alta hospitalar). Além disso, o grupo já possui a modelagem completa do sistema (casos de uso, diagrama de classes/domínio, componentes) produzida em trabalho anterior da graduação, o que permite basear cada ameaça em elementos reais do modelo (campos, operações, arquitetura) em vez de suposições genéricas.

## Material de apoio

A análise não parte do zero: a modelagem completa do SIGH já foi produzida em trabalho anterior da graduação. Esse material está versionado em [`contexto/`](contexto/README.md) para que cada ameaça possa ser justificada com campos, operações e componentes reais - e não com suposições genéricas.

| Onde | O que tem |
| --- | --- |
| [`contexto/README.md`](contexto/README.md) | De onde veio cada arquivo de contexto (o material de apoio do grupo, não versionado) e a divergência de formatação já registrada |
| [`contexto/SIGH - Recorte ESSEG.md`](contexto/SIGH%20-%20Recorte%20ESSEG.md) | Escopo dos 5 módulos, requisitos funcionais e não funcionais mantidos, atores, casos de uso e a tabela de campos sensíveis por classe |
| [`contexto/SIGH - Contexto dos diagramas.md`](contexto/SIGH%20-%20Contexto%20dos%20diagramas.md) | Leitura de cada diagrama sob a ótica de segurança e as lacunas identificadas no documento original |
| [`diagrams/`](diagrams/README.md) | Os 25 diagramas exportados do Lucid, com um índice indicando qual serve a qual seção |

## Trilha individual

Cada integrante acompanha uma mesma categoria STRIDE do início ao fim do trabalho: a ameaça modelada na Etapa 1 vira o risco quantificado e tratado na Etapa 2, e segue nas etapas seguintes como requisito, prática de código e regra de detecção.

| Integrante | Categoria STRIDE | Ameaça | Risco | Módulo/ativo do SIGH |
| --- | --- | --- | --- | --- |
| @lilydias24 | Spoofing | T01 | R01 | Credenciais de `Funcionario` (`nomeLogin`/`senhaLogin`) |
| @ARTHUR9011 | Tampering | T02 | R02 | `PrescricaoMedicamento` / `Tratamento` |
| @lorenzoficher | Repudiation | T03 | R03 | `Obito.registrarObito()` |
| @mariasanchez0 | Information Disclosure | T04 | R04 | Isolamento entre Farmácia e Financeiro |
| @PPrauchner | Denial of Service + Elevation of Privilege | T05 e T06 | R05 e R06 | SGBD central e `enum nivelAcesso` |

## Estrutura do repositório

```
Trab_ESseg/
├── README.md                                  # Este arquivo
├── docs/                                      # Documentos entregáveis, um por etapa
│   ├── E1_Casos_de_abuso_e_Stride.md
│   ├── E2_Riscos_e_NIST_CSF.md
│   ├── E3_Arquitetura_segura.md
│   ├── E4_Codigo_seguro_e_testes.md
│   ├── E5_Verificacao_de_vulnerabilidades.md
│   ├── E6_Monitoramento_e_deteccao.md
│   └── E7_DevSecOps_e_video.md
├── contexto/                                  # Material de apoio (não é entregável)
│   ├── README.md                              # Origem dos arquivos e divergências em relação à fonte
│   ├── SIGH - Recorte ESSEG.md                # Escopo, requisitos, atores e ativos do recorte
│   └── SIGH - Contexto dos diagramas.md       # Leitura dos diagramas para uso no STRIDE
├── diagrams/                                  # Diagramas do SIGH exportados do Lucid
│   ├── README.md                              # Índice: qual diagrama serve a qual seção
│   ├── estrutura/                             # Casos de uso, classes, pacotes, componentes, implantação, mapeamento
│   ├── atividade/                             # ACT01 a ACT10, menos ACT04 e ACT07
│   └── sequencia/                             # DS01 a DS10 (menos DS04 e DS07), DS1.1 e DS1.2
├── codigo/etapa-4/                            # Práticas de código seguro e testes (Etapa 4)
├── evidencias/etapa-5/                        # Relatório do ZAP, plano de automação e capturas (Etapa 5)
├── roteiros/                                  # Roteiros finais compilados, exigidos pelos §27 e §31
│   └── etapa-6-deteccao-de-intrusoes.md       # Roteiro de detecção compilado (Etapa 6)
└── images/                                    # Outras imagens de apoio
```

**Falta ainda** `roteiros/etapa-7-devsecops-e-video-final.md`, exigido pelo §31 do
enunciado. O material da Etapa 7 está hoje reunido em `docs/E7_DevSecOps_e_video.md`,
mas não como arquivo próprio em `roteiros/` - ver a pendência na Etapa 7 abaixo.

> Os diagramas são exportações dos documentos do grupo no Lucid, versionadas de fato no repositório - o enunciado não aceita apenas o link para a ferramenta externa. Os links dos documentos-fonte estão em [`diagrams/README.md`](diagrams/README.md).

## Status do trabalho

### Etapa 1 - Casos de Abuso e STRIDE

- [x] 8.1 Identificação do sistema - @lilydias24
- [x] 8.2 Descrição do sistema - @lilydias24
- [x] 8.3 Usuários, ativos e pontos de interação - @ARTHUR9011
- [x] 8.4 Visão geral da arquitetura/fluxo - @lorenzoficher
- [x] 8.5 Modelagem STRIDE - T01 (@lilydias24), T02 (@ARTHUR9011), T03 (@lorenzoficher), T04 (@mariasanchez0), T05 e T06 (@PPrauchner)
- [x] 8.5.1 Interpretação da análise - @lilydias24
- [x] 8.6 Casos de abuso - CA01 a CA05, um por integrante
- [x] 8.7 Considerações finais - @lilydias24 (rascunho revisado pelo grupo)

> **Etapa 1 concluída** - todas as seções entregues, com contribuição de cada um dos 5 integrantes.

### Etapa 2 - Riscos e NIST CSF 2.0

- [x] 13.1 a 13.3 Critérios e cálculo - escalas definidas e exemplificadas no contexto do SIGH
- [x] 13.4 e 13.5 Registro e justificativa dos riscos - todos os seis riscos concluídos (R04 por @mariasanchez0)
- [x] 13.6 Priorização geral - @mariasanchez0
- [x] 13.7 Conclusão da análise - @ARTHUR9011 (revisada após a conclusão de R04, 13.6 e 14.5)
- [x] 14.1 Estratégias de tratamento - todos os seis riscos concluídos
- [x] 14.2 Funções do NIST CSF - @lorenzoficher
- [x] 14.3 Mapeamento NIST - todos os seis riscos concluídos
- [x] 14.4 Plano de tratamento - todos os seis riscos concluídos
- [x] 14.5 Ordem de implementação - @mariasanchez0
- [x] 14.6 Risco residual - todos os seis riscos concluídos
- [x] 15. Considerações finais - @PPrauchner (revisada sobre os seis riscos, depois de R03, R04, 13.6 e 14.5)

### Etapas 3 a 7

- [ ] Etapa 3 - RS01, RS02 e RS03 revisados (@mariasanchez0): RS01 com correção pequena pendente (numeração OWASP), RS03 com uma frase de esclarecimento sugerida (cláusula 6). Diagrama da arquitetura segura concluído e versionado (@lorenzoficher) - **falta versionar o arquivo-fonte editável**, exigido pelo §18.3 do enunciado. DA01 (@lorenzoficher), DA02 (@mariasanchez0) e DA03 (@lilydias24) concluídas, com o quadro dos cinco campos do §18.4 na abertura da seção 4. Os critérios RS03-CA02 e RS03-CA04, que se contradiziam, foram conciliados depois que a implementação da Etapa 4 expôs a contradição. Conciliação entre a DA02 e as demais decisões concluída (@mariasanchez0): a cota por microsserviço do R05-C1 cobre também o Serviço de Autorização, sem abrir exceção na negação por padrão de RS03
- [x] Etapa 4 - as duas práticas concluídas com testes executados: armazenamento seguro de senhas (@lilydias24) e controle de autorização no servidor (@PPrauchner). Os dois PRs já mesclados à main
- [ ] Etapa 5 - sessão conduzida em 13/08/2026 (@PPrauchner); análise dos 3 achados concluída (@mariasanchez0). Falta apenas a revisão cruzada (@lilydias24 e @lorenzoficher)
- [x] Etapa 6 - as três regras concluídas (1 @lilydias24, 2 @ARTHUR9011, 3 @PPrauchner) e o roteiro compilado em [`roteiros/etapa-6-deteccao-de-intrusoes.md`](roteiros/etapa-6-deteccao-de-intrusoes.md), com convenções comuns, correlação entre regras e tabela de rastreabilidade até a Etapa 1
- [ ] Etapa 7 - pipeline e os sete blocos do roteiro concluídos. Arquivo `roteiros/etapa-7-devsecops-e-video-final.md` criado (§31). **Falta** ajustar a duração (soma hoje passa do teto de 8 min no pior caso) e a gravação/publicação do link

## Como contribuir (para o grupo)

1. Clone o repositório: `git clone https://github.com/lilydias24/Trab_ESseg.git`
2. Edite **apenas o arquivo da etapa** em que sua contribuição se encaixa - assim dois integrantes raramente mexem no mesmo arquivo ao mesmo tempo
3. Faça commits pequenos e frequentes, com mensagens específicas descrevendo a contribuição (ex. `Adiciona ameaça de spoofing na conta do funcionário`), evitando mensagens genéricas como `ajustes` ou `trabalho`
4. Ao concluir uma seção, atualize a tabela de situação no topo do arquivo da etapa e a lista de status deste README
5. Envie (`git push`) para o repositório do grupo

> A avaliação é individual e feita pelos commits: evite subir tudo de uma vez em um único commit e confirme que sua conta do GitHub está corretamente vinculada aos seus commits.

## Info

Este é um trabalho acadêmico desenvolvido para fins didáticos e não representa a implementação real de nenhum sistema existente.
