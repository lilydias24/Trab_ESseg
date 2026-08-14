# Etapa 4 - Código Seguro e Testes de Segurança

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @mariasanchez0’s
> São exigidas **2 práticas de código seguro**, escolhidas para cobrir requisitos já definidos na [Etapa 3](E3_Arquitetura_segura.md). O código fica em `codigo/etapa-4/`.

| Prática | Risco/requisito relacionado | Responsável | Situação |
| --- | --- | --- | --- |
| Armazenamento seguro de senhas (hash + salt em `senhaLogin`) | R01 / RS01 | @lilydias24 | Concluída (testes executados) |
| Controle de autorização no servidor (checagem de `nivelAcesso`) | R06 / RS03 | @PPrauchner | Concluída (testes executados) |

Cada responsável entrega: risco e requisito atendidos, **2 testes escritos antes da implementação** (1 caso válido + 1 caso malicioso/não autorizado), pseudocódigo ou implementação simples, resultado esperado e referência ao OWASP Cheat Sheet Series. O @mariasanchez0’s organiza a pasta e revisa os dois PRs.

---

## Prática 1 - Armazenamento seguro de senhas (@lilydias24)

- **Risco e requisito atendidos:** R01 (Spoofing) / RS01, cláusulas 1 e 2
- **Referência OWASP:** [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- **Arquivos:** [`armazenamento_seguro_senha.py`](../codigo/etapa-4/armazenamento_seguro_senha.py) e [`teste_armazenamento_seguro_senha.py`](../codigo/etapa-4/teste_armazenamento_seguro_senha.py)

**O que esta prática ataca.** No modelo de domínio do SIGH, `Funcionario.senhaLogin` é um
atributo de texto simples. O caso de abuso CA01 usa exatamente isso: entre os caminhos
para obter a credencial de um médico está ler diretamente a tabela `Funcionario` após
acesso ao banco. A prática elimina esse caminho específico - não o acesso ao banco, mas o
fato de esse acesso entregar senhas prontas para uso.

### Testes escritos antes da implementação

| # | Cenário | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| 1 | **Caso válido** - a médica cadastra a senha e autentica com ela | `Plantao#Noturno-2026`, informada no cadastro e depois no login | Autenticação aceita; senha incorreta recusada; a senha em claro **não** aparece no valor persistido; duas contas com a mesma senha produzem registros diferentes |
| 2 | **Caso malicioso** - atacante de posse do conteúdo da tabela `Funcionario`, como em CA01 | O próprio valor gravado em `senhaLogin`, reenviado no campo de senha - inteiro, só o hash e só o salt | Todas as tentativas recusadas; senha vazia recusada; registro corrompido recusado sem lançar exceção |

Uma verificação auxiliar cobre a cláusula 2 de RS01: registros gerados com fator de
trabalho menor, ou com algoritmo legado, precisam ser marcados para regravação
transparente na próxima autenticação bem-sucedida.

### Implementação

Implementação executável em Python, sem dependências externas, para que qualquer
integrante consiga conferir o resultado. O registro gravado tem o formato
`scrypt$N$r$p$salt$hash`, guardando o algoritmo e os parâmetros junto do valor - é isso
que permite reforçar o custo depois sem invalidar as senhas já cadastradas.

Três decisões merecem registro:

- **Algoritmo.** O Cheat Sheet recomenda Argon2id em primeiro lugar e aceita scrypt como
  alternativa. Aqui foi usado `hashlib.scrypt`, da biblioteca padrão, porque torna a
  prática verificável sem instalar nada. **Em produção o SIGH deveria usar Argon2id**, e o
  formato do registro já prevê essa troca.
- **Salt por credencial.** Gerado com `secrets.token_bytes(16)`. É o que impede que duas
  pessoas com a mesma senha tenham o mesmo registro e o que inviabiliza tabelas
  pré-computadas.
- **Comparação em tempo constante.** `hmac.compare_digest`, para que o tempo de resposta
  não revele quantos bytes do valor derivado foram acertados.

Durante a execução apareceu uma limitação prática que vale documentar: com `N = 2^15` e
`r = 8`, o scrypt precisa de exatamente 32 MiB, e o OpenSSL recusa a operação nesse limite
se ele não for declarado. Foi preciso informar `maxmem` explicitamente. O custo de memória
não é um efeito colateral a contornar - é ele que torna caro o ataque em GPU.

### Resultado obtido

Execução real, em Python 3.13.7:

```
$ python teste_armazenamento_seguro_senha.py

[OK] Teste 1 - caso valido
     autenticacao com a senha correta.................. aceita
     autenticacao com senha incorreta.................. recusada
     senha em claro presente no registro............... nao
     registros iguais para senhas iguais............... nao (salt por credencial)
     exemplo de valor gravado.......................... scrypt$32768$8$1$3202ChjmCDMZrEd0sxK0qA==$UeN9jZ...

[OK] Teste 2 - caso malicioso (posse do conteudo da tabela Funcionario)
     registro vazado reenviado como senha.............. recusado
     hash isolado reenviado como senha................. recusado
     salt isolado reenviado como senha................. recusado
     senha vazia....................................... recusada
     registro corrompido no banco...................... recusado sem excecao

[OK] Verificacao auxiliar - migracao de parametros
     registro com parametros vigentes.................. nao remigra
     registro com fator de trabalho menor.............. marcado para remigrar
     registro de algoritmo legado...................... marcado para remigrar

Todos os testes passaram.
```

**O que isto comprova e o que não comprova.** Comprova o controle **R01-C1** do plano de
tratamento da [Etapa 2](E2_Riscos_e_NIST_CSF.md) e as cláusulas 1 e 2 de
[RS01](E3_Arquitetura_segura.md): o vazamento da tabela deixa de ser diretamente
reutilizável. **Não** comprova os demais controles de R01 - MFA, bloqueio por tentativas e
expiração de sessão seguem sendo especificação, não código. É por isso que o risco
residual de R01 permanece Alto: esta prática fecha um dos cinco caminhos, e o phishing em
tempo real, que é o caminho remanescente, não passa pelo banco de dados.

---

## Prática 2 - Controle de autorização no servidor (@PPrauchner)

- **Risco e requisito atendidos:** R06 (Elevation of Privilege) / RS03, cláusulas 1 a 5,
  7 e 8; realiza os controles R06-C1, R06-C2 e R06-C3 do plano de tratamento da
  [Etapa 2](E2_Riscos_e_NIST_CSF.md)
- **Referência OWASP:** [Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html);
  OWASP A01:2025 e as CWE mapeadas para RS03 na [Etapa 3](E3_Arquitetura_segura.md) -
  CWE-862, CWE-915, CWE-269 e CWE-639
- **Arquivos:** [`autorizacao_servidor.py`](../codigo/etapa-4/autorizacao_servidor.py) e
  [`teste_autorizacao_servidor.py`](../codigo/etapa-4/teste_autorizacao_servidor.py)

**O que esta prática ataca.** O passo 3 de CA05 é uma única linha: o Supervisor reenvia o
salvamento do próprio cadastro com `nivelAcesso: Diretor` no corpo, e o servidor persiste
o valor porque nada ali verifica se quem pediu tem alçada sobre aquele campo. A ameaça
T06 é o que dá gravidade a isso - `nivelAcesso` é o **único** atributo de autorização do
modelo inteiro do SIGH, de modo que elevá-lo não contorna uma barreira entre várias,
contorna *a* barreira. A prática fecha exatamente esse passo: o campo deixa de ser
gravável pela via do cadastro, e a operação que de fato altera perfil passa por uma
decisão tomada no servidor, fora do componente que executa.

### Testes escritos antes da implementação

Os dois testes foram escritos e executados **antes** de existir uma linha de
`autorizacao_servidor.py` - a primeira execução falhou com `ModuleNotFoundError`, e é essa
falha que define o que a implementação precisava fazer. Eles não foram escolhidos aqui:
são os dois primeiros critérios de verificação de RS03, que a [Etapa 3](E3_Arquitetura_segura.md)
já registrava como "exatamente os testes escritos na Etapa 4".

| # | Cenário | Entrada | Resultado esperado |
| --- | --- | --- | --- |
| 1 | **Caso válido** (RS03-CA01) - Diretor promove outro funcionário a GerenteSetor | Sessão `nivelAcesso = Diretor` (F001), alvo F003, operação `alterarPerfil` com `novoNivelAcesso: "GerenteSetor"` | Alteração aceita; a trilha registra autor, valor anterior, valor novo, terminal e data/hora carimbada pelo servidor |
| 2 | **Caso não autorizado** (RS03-CA02) - Supervisor tenta elevar o próprio `nivelAcesso`, como no passo 3 de CA05 | Sessão `nivelAcesso = Supervisor` (F003) enviando o próprio cadastro com `nivelAcesso: "Diretor"` no corpo, e depois chamando a operação de alteração de perfil sobre o próprio registro | Pela via de salvamento: o campo é descartado antes de qualquer validação, os demais dados seguem o fluxo normal e a tentativa é registrada. Pela operação própria: **HTTP 403**, sem efeito parcial. Em nenhum dos dois o campo deixa de ser `Supervisor`, e os dois alimentam a Regra 3 |

As verificações auxiliares cobrem os demais critérios já especificados no E3, e com eles
as cláusulas que os dois testes principais não alcançam: **RS03-CA04** (dados funcionais
gravados e `nivelAcesso` ignorado, sem erro silencioso - cláusula 3), **RS03-CA05**
(Diretor tentando elevar a si mesmo - cláusula 3), **RS03-CA06** (endpoint novo sem regra
declarada, recusado por omissão - cláusula 2) e **RS03-CA08** (leitura em massa com limite
de volume e sem campos de autenticação na resposta - cláusula 8). O **RS03-CA03**
(requisição enviada direto ao endpoint) está dentro do teste 2: o modelo não tem camada de
interface, todas as chamadas partem do serviço, e é justamente isso que ele precisa
demonstrar.

### Implementação

Implementação executável em Python, apenas com a biblioteca padrão, no mesmo formato da
Prática 1. O modelo é o menor possível: uma `Sessao` imutável, um cadastro em memória, um
`ServicoDeAutorizacao`, um `ServicoDeFuncionarios` e uma `TrilhaDeAuditoria` somente de
acréscimo. Cinco decisões merecem registro:

- **Descartar, não validar.** `descartar_campos_de_sessao` remove `idFuncionario`,
  `perfil` e `nivelAcesso` do corpo **antes** da decisão de autorização, e devolve à parte
  a lista do que removeu. A ordem importa: validar um valor controlado pelo cliente ainda
  é confiar nele. A lista de descartados não é decorativa - é ela que permite registrar a
  tentativa em vez de ignorá-la em silêncio, que é o resultado exigido por RS03-CA04.
- **A decisão mora fora de quem executa.** `ServicoDeAutorizacao.decidir` é consultado por
  `ServicoDeFuncionarios.executar` antes de qualquer despacho, no papel do Serviço de
  Autorização instituído pela DA02. Se a decisão vivesse dentro do serviço, seria
  alcançável pelo mesmo caminho que se quer barrar.
- **Negação por padrão como último `return`.** A função de decisão termina recusando
  qualquer operação que não case com uma regra declarada. É o que faz um endpoint
  administrativo novo nascer fechado - e o teste `exportarFolhaDePagamento`, que não
  existe em lugar nenhum do serviço, comprova que a recusa vem da omissão da regra, e não
  da ausência do código.
- **Dois campos de nome parecido, com autoridade oposta.** O `nivelAcesso` recebido no
  corpo é o cliente afirmando a própria alçada, e é sempre descartado. O
  `novoNivelAcesso` é parâmetro da operação própria de alteração de perfil - o que uma
  chamada já autorizada concede a **outro** funcionário. Separá-los foi necessário porque
  a cláusula 3 exige que o perfil mude por operação própria, e não pela via de salvamento
  do cadastro.
- **Autorização é sobre o recurso, não sobre o menu.** A decisão de `salvarCadastro` não
  se contenta com o perfil da sessão: exige vínculo com o alvo - o próprio registro, ou
  alçada de GerenteGeral para gravar sobre terceiro. E a gravação passa por uma
  **allowlist** de dados funcionais, em vez de aplicar o corpo inteiro sobre o registro.
  Sem os dois limites, uma sessão de Supervisor reescreveria a `senhaLogin` do Diretor
  pela via de salvamento e entraria como ele: R06 se realizando por outro caminho, sobre
  exatamente o ativo que RS01 protege. Campo que o cadastro venha a ganhar nasce **não
  gravável** por esta via, pelo mesmo princípio que faz operação nova nascer recusada.

A recusa levanta `ErroAutorizacao`, com `codigo_http = 403`, antes de qualquer escrita:
não há efeito parcial a reverter porque nada chegou a ser gravado. A mensagem devolvida é
genérica - "operacao nao autorizada" -, para que a resposta de recusa não vire fonte de
enumeração de campos ou de perfis.

### Resultado obtido

Execução real, em Python 3.11.9:

```
$ python teste_autorizacao_servidor.py

[OK] Teste 1 - caso valido (RS03-CA01)
     promocao de outro funcionario por sessao Diretor.. aceita
     nivelAcesso do alvo apos a operacao.............. GerenteSetor
     trilha - autor................................... F001
     trilha - valor anterior / valor novo............. Supervisor -> GerenteSetor
     trilha - data/hora carimbada pelo servidor....... 2026-08-14T05:32:05+00:00
     alerta da clausula 7 (elevacao efetivada)........ emitido

[OK] Teste 2 - caso nao autorizado (RS03-CA02 e RS03-CA03)
     nivelAcesso enviado no salvamento do cadastro.... descartado
     nivelAcesso persistido apos a tentativa.......... Supervisor
     alteracao de perfil sem alcada de Diretor........ recusada com HTTP 403
     requisicao enviada direto ao endpoint............ mesmo resultado
     efeito parcial no cadastro....................... nenhum
     trilha - tentativa recusada registrada........... sim
     eventos que alimentam a Regra 3.................. 2 (as duas faces)
     alerta da clausula 7 (elevacao efetivada)........ nenhum, como esperado

[OK] Verificacoes auxiliares - RS03-CA04 a RS03-CA08
     dados funcionais gravados, nivelAcesso ignorado.. CA04
     Diretor elevando a si mesmo...................... CA05, recusado (403)
     endpoint sem regra declarada..................... CA06, negado por padrao
     salvar cadastro de terceiro sem alcada........... recusado (403)
     senhaLogin pela via de salvamento................ fora da allowlist
     listagem em massa limitada a 50 registros........ CA08
     campos de autenticacao na listagem............... nenhum

Todos os testes passaram.
```

Uma observação de escrita que vale registrar, porque mudou o desenho. Na redação original
do E3, RS03-CA02 esperava **HTTP 403** para o corpo que trazia `nivelAcesso` alterado, e
RS03-CA04 esperava, para uma entrada da mesma forma, que os dados funcionais fossem
**gravados** e o campo apenas ignorado. Nenhum servidor satisfaz os dois, porque a
requisição é a mesma - só a intenção difere, e intenção não é observável. Foi a tentativa
de codificar ambos, aqui, que expôs a contradição.

A revisão cruzada foi feita e **o critério já está conciliado no E3**: a cláusula 3 dava a
resposta desde o início, e CA02 passou a exercitar os **dois caminhos** - descarte com
registro pela via de salvamento, HTTP 403 pela operação própria de alteração de perfil -,
enquanto CA04 deixou de ser caso concorrente e passou a demonstrar que o desfecho da via
de salvamento não depende da intenção. A tabela de testes acima segue a redação
conciliada.

Na mesma revisão caiu a promessa de que "o alerta da Regra 3 dispara" numa recusa isolada.
A cláusula 7 alerta nas elevações **efetivadas**; tentativas alimentam a Regra 3 por
outros gatilhos. Por isso o serviço expõe duas consultas distintas à trilha -
`alertas_de_elevacao` para a cláusula 7 e `eventos_para_regra_3` para os gatilhos da Etapa
6 - e o teste 2 verifica que a recusa **não** dispara o alerta, ao mesmo tempo que as duas
faces do ataque entram na regra.

**O que isto comprova e o que não comprova.** Comprova os controles **R06-C1** (perfil
vindo da sessão, `nivelAcesso` do corpo descartado, 403 para quem não é Diretor),
**R06-C2** (campo imutável pelo titular, mudança só por operação própria) e a parte de
**R06-C3** que depende do serviço: efetivadas e recusadas entram na trilha com autor,
valor anterior, valor novo, terminal e carimbo do servidor. **Não** comprova a
imutabilidade da trilha - aqui ela é uma lista em memória, e a garantia real depende do
Serviço de Auditoria da DA01, com permissão de escrita segregada da permissão de operar o
SIGH. Também não comprova a cláusula 6 (reemissão da identidade de sessão quando o perfil
muda, RS03-CA07), que é responsabilidade do serviço de autenticação da DA03, nem o
**R06-C4**, cujo destinatário e canal de alerta são matéria da
[Etapa 6](E6_Monitoramento_e_deteccao.md): o que existe aqui é a fonte do evento, não a
notificação.

E há um limite que a prática não move, já reconhecido em RS03: ela fecha o caminho de
CA05, mas **não reduz o impacto de R06**. Uma conta de Diretor comprometida, ou o conluio
entre quem solicita e quem aprova, continua produzindo uma elevação válida - agora datada,
atribuída e alertada, o que muda a detecção, não a possibilidade. E enquanto `senhaLogin`
estiver em texto simples, o alcance de uma elevação bem-sucedida permanece o mesmo, porque
o dano de R06 se realiza sobre as credenciais que RS01 protege. É por isso que o residual
de R06 na [Etapa 2](E2_Riscos_e_NIST_CSF.md) mantém impacto 4: esta prática derruba a
probabilidade, e a Prática 1 é que derruba o impacto. As duas só funcionam juntas.
