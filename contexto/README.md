# Material de contexto do SIGH

Esta pasta guarda o material de apoio que sustenta a análise: é a modelagem do
SIGH produzida pelo grupo em trabalho anterior da graduação, recortada para o
escopo do ESSEG. **Não é entregável** — os documentos avaliados são os de
[`../docs/`](../docs/). O material está aqui para que cada ameaça, risco e
controle possa citar campo, operação e componente reais do sistema.

## Origem de cada arquivo

Os dois arquivos foram exportados do material de apoio do grupo (Google Docs,
não versionado). Os nomes no repositório são mais curtos que os das fontes:

| Arquivo neste repositório | Documento de origem (material de apoio do grupo) |
| --- | --- |
| [`SIGH - Recorte ESSEG.md`](SIGH%20-%20Recorte%20ESSEG.md) | `SIGH - Recorte de Documentação para o ESSEG` |
| [`SIGH - Contexto dos diagramas.md`](SIGH%20-%20Contexto%20dos%20diagramas.md) | `SIGH - Documentação de Contexto dos Diagramas (Lucid)` |

Quem for atualizar o material de apoio deve espelhar a alteração no arquivo
correspondente da tabela acima — os dois lados continuam existindo e a
divergência não é detectada automaticamente.

## Divergência conhecida em relação à fonte

`SIGH - Recorte ESSEG.md` **não é mais idêntico à fonte**: o export cru do Google
Docs trazia as tabelas de requisitos funcionais e não funcionais colapsadas em uma
única linha, hífens escapados (`\-`) espalhados pelo texto e todos os cabeçalhos em
nível 1. O arquivo passou por um passe de limpeza de formatação — uma linha por
requisito, escapes removidos e hierarquia de títulos corrigida. **Nenhum conteúdo
técnico foi alterado**: os mesmos RF01–RF25, RNF01–RNF08, atores, ativos e casos de
uso continuam presentes, com o mesmo texto.

`SIGH - Contexto dos diagramas.md` continua idêntico à fonte.
