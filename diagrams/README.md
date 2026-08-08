# Diagramas do SIGH

Diagramas produzidos pelo grupo no Lucid em trabalho anterior da graduação (APS) e exportados como PNG. O enunciado do ESSEG exige que as imagens estejam **versionadas no repositório**, e não apenas linkadas na ferramenta externa - por isso os arquivos ficam aqui.

Nomes de arquivo sem acento, para evitar problemas de normalização de caracteres entre Windows, OneDrive e Git.

## `estrutura/` - visão geral do sistema

| Arquivo | Conteúdo | Onde é usado |
| --- | --- | --- |
| `Diagramas_SIGH - Casos de Uso.png` | Atores e casos de uso; inclui «system» Convênio e «system» Sistema Governamental | Seção 8.3 (usuários e pontos de interação) |
| `Diagramas_SIGH - Classes.png` | Modelo de domínio com atributos e operações | Seção 8.3 (ativos e campos sensíveis) |
| `Diagramas_SIGH - Pacotes.png` | 7 microsserviços em 5 camadas + API Gateway | Seção 8.4 (arquitetura) |
| `Diagramas_SIGH - Componentes.png` | Firewall por serviço, DAOs «persistent» e SGBD central | Seção 8.4 - **o mais relevante**, mostra os *trust boundaries* |
| `Diagramas_SIGH - Implantacao.png` | Servidores de aplicação, proxy/gateway, firewall e SGBD único | Seção 8.4 e justificativa de Denial of Service (T05) |
| `Diagramas_SIGH - Mapeamento relacional.png` | Mapeamento das classes em tabelas, com PKs e FKs | Seção 8.3 (ativos de banco de dados) |

## `atividade/` - fluxo funcional por caso de uso

`ACT01` Realizar Triagem · `ACT02` Agendar Consultas · `ACT03` Gerenciar Tratamento · `ACT05` Registrar Consulta · `ACT06` Autorizar Alta Hospitalar · `ACT08` Registrar Baixa Hospitalar · `ACT09` Registrar Exame · `ACT10` Registrar Óbito

*(ACT04 e ACT07 pertencem ao módulo de Cirurgias, fora do recorte do ESSEG.)*

## `sequencia/` - chamadas técnicas por caso de uso

`DS01` Realizar Triagem · `DS1.1`/`DS1.2` Triagem (representação externa/interna) · `DS02` Agendar Consultas · `DS03` Gerenciar Tratamento · `DS05` Registrar Consulta · `DS06` Autorizar Alta · `DS08` Registrar Baixa · `DS09` Registrar Exame · `DS10` Registrar Óbito

São a base técnica dos **fluxos de abuso da seção 8.6**: mostram o caminho passo a passo (ator → Desktop Cliente → API Gateway → serviço), permitindo descrever o abuso com precisão em vez de generalidades.

## Documentos-fonte no Lucid

| Documento | Conteúdo |
| --- | --- |
| [Diagramas_SIGH](https://lucid.app/lucidchart/9dc2a6ef-b83e-4415-81e1-d242371140fe/edit) | Casos de Uso, Classes, Pacotes, Componentes, Mapeamento, Implantação |
| [DAtividades_SIGH](https://lucid.app/lucidchart/0141484c-dde8-472d-97c3-ad20c215a69b/edit) | ACT01 a ACT10 |
| [DSequência SIGH](https://lucid.app/lucidchart/b26b5fc3-6c18-4dae-a730-236478997840/edit) | DS01 a DS10, DS1.1 e DS1.2 |

> Ao reexportar um diagrama editado (ex.: o recorte para a seção 8.4 ou a arquitetura segura da Etapa 3), substitua o PNG aqui e mantenha o mesmo nome de arquivo, para não quebrar as referências nos documentos.
