# SIGH - Análise de Segurança (ESSEG)

> Trabalho da disciplina de Engenharia de Software Seguro (ESSEG). Análise de segurança incremental do **SIGH - Sistema Integrado de Gestão Hospitalar**, desenvolvida ao longo das etapas propostas pela disciplina.

## Integrantes

- Arthur Provenzi Parizotto (@ARTHUR9011)
- Emilly Nascimento Dias (@lilydias24)
- Lorenzo Ponsi Ficher (@lorenzoficher)
- Maria Eduarda Sanchez Chessio (@usuario-github-4)
- Pietro Mendes Prauchner (@usuario-github-5)

## Sobre o projeto

Este repositório contém a análise de segurança do **SIGH (Sistema Integrado de Gestão Hospitalar)**, em um recorte com 5 módulos: Cadastro/Prontuário de Pacientes, Atendimento Médico/Consultas, Internação e Leitos, Farmácia/Prescrição de Medicamentos e Financeiro/Cobrança. O trabalho é composto por etapas incrementais, cada uma adicionando uma nova camada de análise sobre o mesmo sistema:

- **Etapa 1** - Casos de Abuso e Modelagem de Ameaças com STRIDE
- **Etapa 2** - Análise, Priorização e Tratamento de Riscos com o NIST CSF 2.0

O documento principal da análise está em [`docs/modelagem-de-ameacas.md`](docs/modelagem-de-ameacas.md).

## Justificativa da escolha do sistema

O SIGH foi escolhido porque combina, em um único sistema, os elementos que a disciplina pede para uma boa análise STRIDE: múltiplos perfis de usuário com diferentes níveis de permissão (Médico, Enfermeiro, Recepcionista, Administrador), um sistema externo integrado (validação de convênio), dados de alta sensibilidade (prontuário, prescrições, dados financeiros) e operações irreversíveis de alto impacto (ex.: registro de óbito, alta hospitalar). Além disso, o grupo já possui a modelagem completa do sistema (casos de uso, diagrama de classes/domínio, componentes) produzida em trabalho anterior da graduação, o que permite basear cada ameaça em elementos reais do modelo (campos, operações, arquitetura) em vez de suposições genéricas.

## Estrutura do repositório

```
projeto-esseg/
├── README.md                        # Este arquivo
├── docs/
│   └── modelagem-de-ameacas.md      # Documento principal (todas as etapas)
├── diagramas/                        # Diagramas exportados (contexto, componentes, casos de uso etc.) + arquivos-fonte
└── imagens/                          # Outras imagens de apoio usadas no documento
```

> Todos os arquivos-fonte dos diagramas (ex. exportados do Lucid) serão versionados junto com a imagem exportada - não usando apenas links externos.

## Status do trabalho

- [x] Etapa 1 - Seção 8.1/8.2 (Identificação e descrição do sistema) - @lilydias24
- [ ] Etapa 1 - Seção 8.3 (Usuários, ativos e pontos de interação) - Integrante 2
- [ ] Etapa 1 - Seção 8.4 (Diagrama de arquitetura/fluxo) - Integrante 3
- [ ] Etapa 1 - Seção 8.5 (STRIDE, 5 ameaças) - 1 concluída (Spoofing - @lilydias24), 4 pendentes
- [ ] Etapa 1 - Seção 8.6 (Casos de abuso) - 1 concluído (CA01 - @lilydias24), 4 pendentes
- [ ] Etapa 1 - Seção 8.7 (Considerações finais) - rascunho pendente (@lilydias24, após conclusão dos itens acima)
- [ ] Etapa 2 - Riscos e NIST CSF 2.0

## Como contribuir (para o grupo)

1. Clone o repositório: `git clone <https://github.com/lilydias24/Trab_ESseg.git>`
2. Crie/edite os arquivos localmente ou direto pelo GitHub
3. Faça commits pequenos e frequentes, com mensagens específicas descrevendo a contribuição (ex. `Adiciona ameaça de spoofing na conta do funcionário`), evitando mensagens genéricas como `ajustes` ou `trabalho`
4. Envie (`git push`) para o repositório do grupo

## Info

Este é um trabalho acadêmico desenvolvido para fins didáticos e não representa a implementação real de nenhum sistema existente.
