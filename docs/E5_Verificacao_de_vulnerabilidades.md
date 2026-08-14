# Etapa 5 - Verificação de Vulnerabilidades

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @PPrauchner
> É exigida **1 sessão de teste**. Como o SIGH não está implementado, a verificação é feita no **OWASP Juice Shop** com o **OWASP ZAP**. Evidências em `evidencias/etapa-5/capturas-de-tela/`.

| Item | Responsável | Situação |
| --- | --- | --- |
| Condução da sessão (setup Juice Shop + ZAP, captura de evidências) | @PPrauchner | Concluída (sessão executada em 13/08/2026; relatório e capturas versionados) |
| Análise dos 3 achados e correção proposta (com CWE/OWASP) | @mariasanchez0 | Concluída |
| Complemento da tabela final (coluna OWASP Top 10:2025) | @lorenzoficher | Concluído (seção 5) |
| Revisão cruzada - @lorenzoficher | @lorenzoficher | Concluída (seção 5) - 4 achados: RV01 e RV02 altos, pendentes de correção pela @mariasanchez0 |
| Revisão cruzada - @lilydias24 | @lilydias24 | Pendente |

---

## 1. Configuração da sessão

- **Alvo:** OWASP Juice Shop **20.2.0**, executado localmente em
  `http://localhost:3000`, a partir da distribuição oficial Node
  (`juice-shop-20.2.0_node24_win32_x64`), com integridade conferida pelo MD5
  publicado no release (`20d9213200cc4bfd25841531530a7272`). Aplicação
  deliberadamente vulnerável, criada para treinamento - é a hipótese expressamente
  autorizada pelo §23 do enunciado. **Nenhum sistema de terceiros foi tocado.**
- **Ferramenta e versão:** OWASP ZAP **2.17.0** (pacote *crossplatform*, executado
  sobre Java 25), em modo linha de comando com o **Automation Framework**. O plano
  usado está versionado em
  [`plano-automacao-zap.yaml`](../evidencias/etapa-5/plano-automacao-zap.yaml), para
  que a sessão possa ser repetida por qualquer integrante. O plano versionado recebeu
  dois acertos **posteriores à sessão**, sem nova execução: o `reportDir` passou de
  `C:/tmp/zap-out` (absoluto, de Windows) para `./zap-out`, relativo ao diretório de
  onde o ZAP é chamado, e o terceiro job de relatório
  (`risk-confidence-html`) foi removido, porque gerava um artefato que não está
  versionado aqui. Assim, rodar o plano produz exatamente os dois relatórios abaixo.
- **Tipo de varredura:** varredura completa em quatro fases encadeadas -
  *spider* tradicional (18 s), *AJAX spider* com Edge headless (34 s, 142 URLs, e é
  ele que alcança a interface Angular), varredura **passiva** sobre todo o tráfego
  capturado e varredura **ativa** (2 min 02 s), com teto de 2 minutos por regra.
  Foram mapeados **39 endpoints** do alvo.
- **Data da sessão:** 13 de agosto de 2026, relatório gerado às 21:52.
- **Escopo e limitações:**
  - O contexto `juice-shop` restringiu a varredura a `http://localhost:3000`;
    imagens, fontes, vídeo e `socket.io` foram excluídos por não acrescentarem
    superfície de análise.
  - O relatório lista quatro *sites*, mas **só `localhost:3000` tem alertas**. Os
    três domínios `*.microsoft.com` são telemetria do próprio Edge headless usado
    pelo AJAX spider, que passou pelo proxy do ZAP; por estarem fora do contexto,
    não foram varridos e aparecem com zero alertas. É ruído de instrumentação, não
    resultado.
  - A varredura foi feita **sem autenticação**: só a superfície acessível a um
    usuário anônimo foi coberta. As áreas que exigem login - e portanto boa parte
    das falhas de autorização, que são justamente o tema da trilha R06/RS03 - ficaram
    fora do alcance desta sessão.
  - O teto de 2 minutos por regra ativa limita as regras mais lentas (injeção cega
    baseada em tempo, por exemplo). O objetivo, conforme o §25, é **interpretar os
    resultados da ferramenta**, não esgotar a exploração.
  - Nenhum dado foi extraído e não houve exploração manual além da reprodução do
    achado V01 descrita abaixo, com a carga mínima necessária para separar
    verdadeiro de falso positivo. Cabe registrar, porém, que o spider **alcançou
    conteúdo restrito por conta própria**: a captura do alvo, abaixo, mostra o
    Juice Shop anunciando os desafios *Confidential Document* e *Error Handling*
    como resolvidos, disparados pela varredura ao percorrer `/ftp/`. É consequência
    de varrer sem exclusão de caminho um alvo desenhado para ser vulnerável - não
    houve intenção nem uso do conteúdo -, mas dizer "nenhum acesso indevido" seria
    impreciso diante da própria evidência versionada.

![Tela inicial do OWASP Juice Shop 20.2.0 em `localhost:3000`, alvo da sessão, com dois banners do próprio aplicativo anunciando desafios resolvidos pela varredura](../evidencias/etapa-5/capturas-de-tela/01-juiceshop-alvo.png)

*O alvo da sessão, no navegador, antes da leitura do relatório. Os banners verdes são
do próprio Juice Shop: ele sinaliza quando um desafio embutido é atingido, e foram a
varredura automática do ZAP - não um operador - que os disparou. A listagem vazia em
"All Products" é efeito do carregamento assíncrono no instante da captura, e não
indica alvo sem dados: os 39 endpoints mapeados constam do relatório.*

### Resultado bruto da sessão

O ZAP registrou **8 tipos de alerta** sobre o alvo, assim distribuídos:

| Nível de risco (ZAP) | Nº de alertas |
| --- | --- |
| Alto | 1 |
| Médio | 2 |
| Baixo | 2 |
| Informativo | 3 |
| Falsos positivos marcados | 0 |

![Resumo dos alertas no relatório do ZAP, com um alerta Alto, dois Médios, dois Baixos e três Informativos, seguido da tabela de alertas e do detalhe do SQL Injection](../evidencias/etapa-5/capturas-de-tela/02-zap-relatorio-alertas.png)

*Relatório do ZAP 2.17.0 gerado ao fim da sessão. O bloco "Summary of Alerts" traz a
contagem por nível de risco; a tabela "Alerts" lista os oito tipos encontrados; e o
"Alert Detail" mostra o achado de maior risco, com URL, parâmetro, carga usada e
evidência.*

O relatório completo está versionado em duas formas:
[HTML](../evidencias/etapa-5/relatorio-zap-juiceshop.html) para leitura e
[JSON](../evidencias/etapa-5/relatorio-zap-juiceshop.json) para conferência campo a
campo.

## 2. Achados

Os três achados levados à análise são os de maior risco atribuído pela ferramenta.
As colunas *Possível impacto* e *Correção proposta* são a análise da @mariasanchez0’s
(seção 3); as demais registram o que a sessão produziu.

| ID | Achado | Severidade (ZAP) | Evidência | Possível impacto | CWE/WASC (ZAP) | OWASP Top 10:2025 | Correção proposta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| V01 | **SQL Injection** em `GET /rest/products/search`, parâmetro `q`. Carga `'(` produz `HTTP 500` com `SQLITE_ERROR: near "(": syntax error` | Alto (confiança Baixa segundo o ZAP - **verificado como verdadeiro positivo**, ver abaixo) | [captura 03](../evidencias/etapa-5/capturas-de-tela/03-sqli-erro-sqlite.png); `pluginid` 40018 no [JSON](../evidencias/etapa-5/relatorio-zap-juiceshop.json) e no *Alert Detail* do [HTML](../evidencias/etapa-5/relatorio-zap-juiceshop.html), com URL, parâmetro, carga e `evidence: HTTP/1.1 500 Internal Server Error` | Leitura, adulteração ou exclusão de dados no banco por trás do endpoint, caso a exploração avance além do erro de sintaxe já confirmado | CWE-89; WASC-19 | [A05:2025 - Injection](https://owasp.org/Top10/2025/A05_2025-Injection/) | Consultas parametrizadas (prepared statements) e resposta de erro genérica, sem stack trace nem versão de framework |
| V02 | **Content Security Policy (CSP) Header Not Set** - 5 instâncias, incluindo a raiz da aplicação | Médio (confiança Alta) | `pluginid` 10038 no [JSON](../evidencias/etapa-5/relatorio-zap-juiceshop.json) e no *Alert Detail* do [HTML](../evidencias/etapa-5/relatorio-zap-juiceshop.html): 5 instâncias `GET` - `/`, `/ftp/eastere.gg`, `/ftp/encrypt.pyc`, `/ftp/package-lock.json.bak` e `/sitemap.xml`. O campo `evidence` vem vazio porque o achado é a **ausência** do cabeçalho na resposta | Amplia o efeito de qualquer XSS presente na aplicação, por faltar a camada do navegador que conteria um script injetado | CWE-693; WASC-15 | [A02:2025 - Security Misconfiguration](https://owasp.org/Top10/2025/A02_2025-Security_Misconfiguration/) | Cabeçalho `Content-Security-Policy` restritivo (`default-src 'self'`, sem `unsafe-inline`/`unsafe-eval`) em todas as respostas |
| V03 | **Cross-Domain Misconfiguration** - resposta traz `Access-Control-Allow-Origin: *`, em 3 instâncias | Médio (confiança Média) | `pluginid` 10098 no [JSON](../evidencias/etapa-5/relatorio-zap-juiceshop.json) e no *Alert Detail* do [HTML](../evidencias/etapa-5/relatorio-zap-juiceshop.html): 3 instâncias `GET` - `/`, `/scripts.js` e `/styles.css` -, todas com `evidence: Access-Control-Allow-Origin: *` | Qualquer origem pode ler resposta autenticada via requisição cross-site, ampliando furto de sessão ou dado por site malicioso | CWE-264 (ZAP); CWE-942 pela análise da seção 3; WASC-14 | [A02:2025 - Security Misconfiguration](https://owasp.org/Top10/2025/A02_2025-Security_Misconfiguration/) | Allowlist de origens confiáveis no `Access-Control-Allow-Origin`, nunca combinado com `Access-Control-Allow-Credentials: true` |

A coluna **CWE/WASC (ZAP)** traz a classificação como a ferramenta a devolve: CWE e WASC
são os dois identificadores presentes no relatório do ZAP; o §25 aceita "OWASP **ou**
CWE". A coluna **OWASP Top 10:2025** foi acrescentada depois, no complemento da tabela
final (seção 5), quando a análise da seção 3 passou a existir e o mapeamento pôde ser
fechado - antes disso a tabela registrava só o que a ferramenta afirma, e não o que o
grupo conclui. A distinção entre as duas colunas é deliberada e vale para a leitura do
V03, em que a CWE do ZAP (CWE-264, categoria-mãe) é menos precisa que a da análise
(CWE-942). A captura 02 mostra apenas o *Summary of Alerts*, a
lista de nomes e o *Alert Detail* do V01; por isso V02 e V03 são referenciados
diretamente ao relatório, onde constam URL, método e evidência de cada instância.

### Verificação do V01: verdadeiro positivo, não falso positivo

O ZAP marcou o SQL Injection com **confiança Baixa**, e o §26 do enunciado cobra
justamente a "capacidade de reconhecer limitações e possíveis falsos positivos". Por
isso o alerta foi verificado antes de entrar na tabela, com a carga mínima necessária:

- `?q=apple` (consulta normal) → `HTTP 200`
- `?q='` (aspas simples isolada) → `HTTP 200`, `{"status":"success","data":[]}` - o
  que **não** confirmaria nada sozinho
- `?q='(` (a carga do ZAP) → `HTTP 500`, e a resposta traz
  `Error: SQLITE_ERROR: near "(": syntax error`

A mensagem é do motor SQLite, não da aplicação: a entrada do usuário chegou ao
interpretador SQL sem escape e alterou a sintaxe da consulta. **O alerta é um
verdadeiro positivo.** Nenhum dado foi extraído - a confirmação parou no ponto em que
o erro de sintaxe prova a injeção, conforme o §25 ("não é necessário explorar
completamente as vulnerabilidades").

![Página de erro do Juice Shop mostrando "OWASP Juice Shop (Express ^4.22.1)" e "500 Error: SQLITE_ERROR: near "(": syntax error"](../evidencias/etapa-5/capturas-de-tela/03-sqli-erro-sqlite.png)

*Resposta ao payload `'(`. Além de confirmar a injeção, a página revela o framework e
a versão (`Express ^4.22.1`) - tratamento de erro que devolve detalhe interno ao
cliente é, por si, um segundo problema. A captura foi recortada no corpo do erro e
**não inclui a barra de endereços**: sozinha, ela não liga o `HTTP 500` à URL
`/rest/products/search?q='(`. Essa ligação está no relatório do ZAP, que registra a
URL completa, o parâmetro, a carga e a evidência da resposta.*

### Alertas descartados desta análise

O §25 permite explicar por que os demais resultados foram descartados. Os cinco
alertas restantes não entraram entre os três analisados:

| Alerta | Risco | Por que foi descartado |
| --- | --- | --- |
| Private IP Disclosure (`192.168.99.100:3000`) | Baixo | Endereço interno devolvido por `/rest/admin/application-configuration`. É exposição real, mas de baixo alcance e, neste caso, um valor de configuração de exemplo do próprio Juice Shop, não da infraestrutura em que a sessão rodou |
| Timestamp Disclosure - Unix | Baixo | **Provável falso positivo.** O ZAP reconhece qualquer inteiro de 10 dígitos como *timestamp*. As **5 instâncias** foram conferidas no JSON: três valores distintos (`1666666667`, `1839622642` e `1528301887`), todos em conteúdo estático (raiz da página, `/sitemap.xml`, `/styles.css`), os dois primeiros repetidos em recursos diferentes. Nenhum acompanha a data da sessão, e `1839622642` corresponde a 2028-04-17 - data futura, incompatível com carimbo de tempo real. Não foi inspecionado o código-fonte do Juice Shop para confirmar a origem de cada valor |
| Information Disclosure - Suspicious Comments | Informativo | As **4 instâncias** foram conferidas no JSON: os padrões `\bSELECT\b` (em `chunk-DAJ4olp_.js`), `\bDB\b` (`chunk-eYAgyLdn.js`) e `\bQUERY\b` (`hacking-instructor-BXwB7EFQ.js` e `main.js`), todos dentro de bundles JavaScript minificados. São coincidências de padrão textual em código empacotado, não comentários vazando informação |
| Modern Web Application | Informativo | Não é vulnerabilidade: o ZAP apenas registra que o alvo é uma SPA e que links podem depender de JavaScript |
| User Agent Fuzzer | Informativo | Resultado de teste, não achado: o ZAP variou o cabeçalho `User-Agent` e comparou respostas |

Vale registrar que **o ZAP não marcou nenhum alerta como falso positivo por conta
própria** (linha "False Positives: 0" do relatório) - a triagem acima é leitura do
grupo, não da ferramenta. É exatamente a diferença entre rodar a ferramenta e
interpretar o resultado.

## 3. Análise dos achados

### V01 - SQL Injection em `/rest/products/search`

- **O que foi encontrado:** o endpoint `GET /rest/products/search`, parâmetro `q`, aceita
  a carga `'(` e devolve `HTTP 500` com a mensagem `SQLITE_ERROR: near "(": syntax error`,
  exposta diretamente ao cliente. A verificação manual da seção 1 confirmou: uma consulta
  comum (`?q=apple`) responde normalmente, uma aspas isolada (`?q='`) não quebra a
  sintaxe, e é só a carga do ZAP que produz o erro - evidência de que o parâmetro chega ao
  interpretador SQL sem escape nem parametrização.
- **Por que é um problema:** um parâmetro de busca que altera a sintaxe da consulta é, por
  definição, controlado pelo atacante além do que a aplicação previu. O ZAP marcou
  confiança **Baixa** porque só observou o erro de sintaxe, sem extrair dado - mas o mesmo
  caminho que quebra a consulta é o que, com uma carga um pouco mais elaborada, costuma
  permitir ler colunas de outras tabelas nesse tipo de aplicação. Não foi isso que se fez
  aqui - o §25 do enunciado autoriza parar na confirmação -, mas a mensagem de erro já
  entrega ao atacante o motor de banco e a versão do framework (`Express ^4.22.1`, visível
  na captura), o que reduz o custo de qualquer tentativa seguinte.
- **Correção proposta:** substituir a concatenação por **consultas parametrizadas**
  (prepared statements), de modo que o valor de `q` nunca seja interpretado como parte da
  instrução SQL - a recomendação central do
  [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html).
  Como reforço, validar o formato esperado do parâmetro (allowlist de caracteres) antes de
  chegar à camada de dados, e substituir a página de erro atual por uma resposta genérica
  que não devolva stack trace, motor de banco nem versão de framework.
- **Relação com CWE/OWASP:** CWE-89 (SQL Injection) e, mais amplamente, CWE-20 (Improper
  Input Validation) - o mesmo par que a Etapa 3 já cataloga para o SIGH na seção de
  vulnerabilidades de RS02. No OWASP Top 10:2025, o achado se encaixa em
  **A05:2025 - Injection**. É a mesma classe de falha que a Etapa 3 já previa de forma
  hipotética: RS02 exige validar `dosagemMedicamento` e `intervaloConsumo` contra faixa
  terapêutica no servidor (R02-C3) precisamente porque um parâmetro aceito sem validação,
  se chegar a uma consulta montada por concatenação, produz este mesmo tipo de falha. O
  Juice Shop não é o SIGH, mas demonstra, num sistema real, o que a Etapa 2 só podia
  argumentar sobre o modelo.

### V02 - Content Security Policy (CSP) Header Not Set

- **O que foi encontrado:** cinco respostas do alvo - incluindo a raiz da aplicação - não
  trazem o cabeçalho `Content-Security-Policy`. O ZAP sinalizou com confiança Alta; é uma
  verificação estrutural (presença ou ausência de um cabeçalho HTTP), sem necessidade de
  confirmação manual como no V01.
- **Por que é um problema:** o CSP é a barreira do navegador contra o que uma página pode
  carregar e executar. Sem ele, se existir **qualquer** ponto de injeção de script na
  aplicação (XSS refletido, armazenado ou baseado em DOM), o navegador executa o script
  injetado sem restrição de origem. O CSP não fecha o XSS em si - é uma camada de
  contenção que reduz o dano quando uma falha primária passar despercebida, o mesmo papel
  que uma segunda barreira cumpre nas fraquezas que este grupo já descreveu para o SIGH em
  R01 e R04.
- **Correção proposta:** definir um `Content-Security-Policy` restritivo em todas as
  respostas HTML, começando por `default-src 'self'` e evitando `unsafe-inline`/
  `unsafe-eval`; expandir por allowlist apenas os domínios efetivamente necessários.
  Recomenda-se implantar primeiro em modo `Content-Security-Policy-Report-Only` para medir
  o que quebraria, conforme o
  [OWASP Content Security Policy Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html).
- **Relação com CWE/OWASP:** CWE-693 (Protection Mechanism Failure) - categoria abrangente
  por natureza, porque o achado é sobre a **ausência** de uma camada de proteção, não
  sobre uma falha específica que ela protegeria. No OWASP Top 10:2025, o achado se encaixa
  em **A02:2025 - Security Misconfiguration**, categoria que subiu da 5ª para a 2ª posição
  nesta edição - cabeçalho de segurança ausente é exatamente o tipo de lacuna que essa
  subida reflete.

### V03 - Cross-Domain Misconfiguration (`Access-Control-Allow-Origin: *`)

- **O que foi encontrado:** três instâncias da resposta trazem
  `Access-Control-Allow-Origin: *`, liberando CORS para qualquer origem. O ZAP sinalizou
  com confiança Média.
- **Por que é um problema:** o CORS existe para que o navegador aplique, por padrão, a
  política de mesma origem e só a afrouxe quando o servidor autoriza explicitamente uma
  origem confiável. Um `*` remove essa fronteira por completo: qualquer site, inclusive um
  malicioso hospedado em outro domínio, pode fazer uma requisição a partir do navegador da
  vítima e ler a resposta como se fosse a própria aplicação. É, em escala de navegador, o
  mesmo problema estrutural que a Etapa 1 e a Etapa 2 já descrevem para o **R04** no SIGH:
  a **ausência de uma fronteira de confiança** onde deveria haver uma - lá é entre
  Farmácia/Financeiro e o restante dos serviços; aqui é entre a aplicação e qualquer
  origem externa. Nos dois casos, o dado não é roubado por invasão: é entregue porque o
  sistema não distingue quem tem direito de recebê-lo.
- **Correção proposta:** substituir o `*` por uma lista de origens confiáveis, validada no
  servidor a cada requisição; nunca combinar `Access-Control-Allow-Origin` amplo com
  `Access-Control-Allow-Credentials: true`; e limitar o cabeçalho às rotas que de fato
  precisam de acesso entre origens. Orientação consolidada no
  [OWASP HTML5 Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html),
  seção de Cross-Origin Resource Sharing.
- **Relação com CWE/OWASP:** CWE-264 (categoria-mãe de controle de acesso) e, mais
  precisamente, CWE-942 (Permissive Cross-domain Policy with Untrusted Domains). No OWASP
  Top 10:2025, o achado se encaixa em **A02:2025 - Security Misconfiguration**, junto com
  o V02 - os dois achados Médios desta sessão são, na raiz, o mesmo tipo de falha: uma
  configuração de proteção deixada no padrão mais permissivo, não uma falha de lógica de
  negócio.


## 4. Considerações da etapa

A sessão confirmou, num sistema real, um padrão que a Etapa 2 só podia argumentar sobre o
modelo do SIGH: a ausência de uma segunda barreira depois do ponto óbvio de proteção é o
que transforma uma falha pontual em exposição ampla. O achado de maior risco, V01, é
validação de entrada ausente na camada mais crítica (a consulta ao banco) - a mesma classe
de fraqueza que RS02 já previa fechar via faixa terapêutica e validação no servidor
(R02-C3). Os achados V02 e V03 são configuração permissiva por padrão, não lógica de
negócio quebrada - e V03 em particular reproduz, em nível de cabeçalho HTTP, o mesmo
problema estrutural que sustenta o R04 deste grupo: a ausência de uma fronteira onde uma
era esperada.

Duas limitações merecem registro, para que os achados não sejam lidos além do que provam.
Primeiro, a varredura foi **não autenticada** - cobriu só a superfície acessível a um
usuário anônimo, o que significa que a maior parte das falhas de autorização pós-login (o
tema central da trilha R06/RS03) ficou fora do alcance desta sessão; nenhuma conclusão
sobre controle de acesso autenticado pode ser tirada daqui. Segundo, confiança **Baixa** do
ZAP no V01 não é sinônimo de falso positivo - é sinônimo de "a ferramenta não tem certeza
sozinha", e foi por isso que a verificação manual da seção 1 foi necessária antes de tratar
o achado como real; o inverso também vale, e por isso os cinco alertas descartados na seção
2 foram justificados individualmente, não descartados em bloco.

O ponto mais importante para o trabalho como um todo é metodológico: **o Juice Shop não é
o SIGH.** Esta sessão não prova nem refuta nada sobre a implementação do SIGH, porque o
SIGH não tem implementação - prova que a **classe** de vulnerabilidade que a Etapa 1 e a
Etapa 2 anteciparam a partir do modelo (validação de entrada ausente, fronteiras de
confiança inexistentes) é real e testável em sistemas do mesmo tipo, quando o código
existe. É a diferença entre "o modelo sugere que isso pode acontecer" e "isso acontece,
neste outro sistema, exatamente pela razão que o modelo sugeriu".

## 5. Revisão cruzada e complemento da tabela final - @lorenzoficher

Revisão por quem não conduziu a sessão nem escreveu a análise. Confere três coisas: se a
evidência versionada sustenta o que o texto afirma, se as classificações CWE/OWASP estão
corretas, e se as pontes traçadas para as Etapas 1 a 3 se sustentam. A metade da
@lilydias24 segue pendente.

**O complemento da tabela final está feito:** a coluna *OWASP Top 10:2025* foi
acrescentada à tabela da seção 2, que até aqui só registrava a classificação da
ferramenta. Conferi a numeração da edição 2025 contra as categorias que o grupo já cita
nas Etapas 3 e 7 - **A05 - Injection** para o V01 e **A02 - Security Misconfiguration**
para o V02 e o V03 -, e a afirmação da seção 3 de que *Security Misconfiguration* subiu
da 5ª para a 2ª posição nesta edição está correta.

### 5.1 O que foi conferido e está correto

Registro primeiro o que resistiu à conferência, porque uma revisão que só lista defeitos
não informa o que já pode ser levado ao vídeo sem receio:

- **A aritmética dos alertas fecha.** 8 tipos no relatório = 1 Alto + 2 Médios + 2 Baixos
  + 3 Informativos; 3 analisados (o Alto e os dois Médios) + 5 descartados (os dois Baixos
  e os três Informativos). As contagens de instância (5 no V02, 3 no V03) conferem com as
  URLs listadas uma a uma.
- **A verificação do V01 é metodologicamente sólida.** A sequência `?q=apple` → 200,
  `?q='` → 200, `?q='(` → 500 com `SQLITE_ERROR` isola a variável corretamente: mostra que
  não é o alvo que quebra com qualquer entrada, e que é a alteração de sintaxe que produz o
  erro. A conclusão de verdadeiro positivo está justificada, e a decisão de parar aí está
  amparada no §25.
- **A triagem dos cinco descartados é individual e verificável**, com os valores conferidos
  no JSON. O argumento de que `1839622642` corresponde a 2028 e por isso não é carimbo de
  tempo real é o tipo de checagem que separa interpretar de repassar a ferramenta.
- **WASC-19, WASC-15 e WASC-14** correspondem, respectivamente, a SQL Injection,
  Application Misconfiguration e Server Misconfiguration. Corretos.

### 5.2 Achados da revisão

| # | Onde | Tipo | Gravidade |
| --- | --- | --- | --- |
| RV01 | V03, coluna *Possível impacto* | Erro técnico | Alta |
| RV02 | V01, seções 3 e 4 | Ponte indevida com a Etapa 2 | Alta |
| RV03 | V01, "Relação com CWE/OWASP" | Afirmação falsa sobre a Etapa 3 | Média |
| RV04 | V02, contagem de instâncias | Achado maior não registrado | Média |

#### RV01 - O impacto declarado do V03 não é o que um `*` produz

A coluna *Possível impacto* do V03 afirma: *"Qualquer origem pode ler **resposta
autenticada** via requisição cross-site, ampliando furto de sessão ou dado por site
malicioso."*

**Isso não é o que acontece.** Quando `Access-Control-Allow-Origin` vale `*`, o navegador
**não** envia credenciais na requisição entre origens; e a combinação de `*` com
`Access-Control-Allow-Credentials: true` é rejeitada pelo próprio navegador, não aceita.
Um curinga, sozinho, **não permite ler resposta autenticada** - permite ler a resposta
que um usuário anônimo já obteria, que o atacante poderia buscar do próprio servidor sem
envolver a vítima.

O mais revelador é que a **correção proposta na mesma linha já sabe disso**: ela recomenda
*"nunca combinar `Access-Control-Allow-Origin` amplo com `Access-Control-Allow-Credentials:
true`"*. Se o curinga sozinho bastasse para expor resposta autenticada, essa ressalva não
teria função. A linha se contradiz entre a coluna de impacto e a de correção.

Onde o `*` de fato importa é em recurso protegido por **posição de rede** e não por
credencial - uma aplicação interna alcançável do navegador da vítima, cujo servidor confia
em quem chega. Não é o caso das três instâncias desta sessão: `/`, `/scripts.js` e
`/styles.css` são conteúdo estático público, em que o efeito prático é próximo de zero.

> **Correção sugerida.** Reescrever o impacto para: *"qualquer origem pode ler a resposta
> como usuário anônimo; o curinga não expõe resposta autenticada, porque o navegador não
> envia credenciais nesse modo. O risco se materializa em recursos protegidos por posição
> de rede, ou caso a configuração seja estendida a rotas autenticadas com
> `Allow-Credentials`."* O achado continua válido - a configuração está errada e é
> perigosa se propagada a rotas autenticadas -, mas a severidade **analisada** hoje está
> acima do que a evidência sustenta.

Vale dizer por que este achado importa além do V03: é uma afirmação que qualquer avaliador
confere em trinta segundos, e ela está na tabela que a etapa entrega.

#### RV02 - O V01 é ancorado no R02-C3, que trata de outro problema

As seções 3 e 4 ligam o V01 ao SIGH duas vezes, dizendo que é *"a mesma classe de fraqueza
que RS02 já previa fechar via faixa terapêutica e validação no servidor (R02-C3)"*.

Conferindo o R02-C3 na [Etapa 2](E2_Riscos_e_NIST_CSF.md), ele é: *"validação de faixa
terapêutica por medicamento, com bloqueio de valores fora da faixa"*. É validação
**semântica** de um valor clínico - saber se 500 mg é uma dose plausível para aquele
medicamento. Injeção de SQL é falha **sintática**: o valor escapa do lugar de dado e vira
instrução. São problemas diferentes com controles que não se substituem: consulta
parametrizada não sabe nada sobre dosagem, e faixa terapêutica não impede injeção alguma.
Uma dose perfeitamente dentro da faixa pode carregar carga de injeção; uma consulta
parametrizada aceita sem reclamar uma dose dez vezes maior que a máxima.

E a ponte esconde um resultado melhor do que ela. **Conferi: a Etapa 3 não menciona
injeção em lugar nenhum** - zero ocorrências de `CWE-89`, "SQL Injection" ou "consulta
parametrizada" no documento inteiro. Ou seja, a sessão encontrou, num sistema real, uma
classe de vulnerabilidade para a qual a arquitetura segura do SIGH **não tem requisito**.

Isso é mais valioso do que o paralelo forçado, e é exatamente o que os §25 e §26 pedem:
interpretar o resultado. A varredura não confirmou o que o grupo já previa - ela mostrou
uma lacuna na Etapa 3 que nenhuma das sete seções anteriores tinha apontado.

> **Correção sugerida.** Trocar a ponte pelo achado: o V01 demonstra uma classe de falha
> **não coberta** pelos três requisitos de segurança da Etapa 3, que tratam de
> autenticação (RS01), integridade da prescrição (RS02) e autorização administrativa
> (RS03), nenhum deles de tratamento de entrada na fronteira com o banco. O único ponto de
> contato real é a **CWE-20**, que a Etapa 3 cataloga para RS02 - e CWE-20 é ancestral
> comum, não controle compartilhado.

#### RV03 - "o mesmo par que a Etapa 3 já cataloga" é falso para a CWE-89

A seção 3 do V01 afirma que CWE-89 e CWE-20 são *"o mesmo par que a Etapa 3 já cataloga
para o SIGH na seção de vulnerabilidades de RS02"*.

Conferido na [Etapa 3](E3_Arquitetura_segura.md): RS02 cataloga **CWE-862, CWE-602,
CWE-20 e CWE-778**. A CWE-89 não está lá - e nem poderia, porque o SIGH não tem código
onde uma injeção pudesse ser catalogada. Só a CWE-20 é comum aos dois documentos.

É correção de uma frase, mas é o tipo de afirmação sobre outro documento do próprio
trabalho que um avaliador confere abrindo a outra aba.

#### RV04 - As 5 instâncias do V02 medem outra coisa, e três delas escondem um achado maior

Duas observações sobre a mesma linha.

**A contagem superestima o achado.** O CSP só tem efeito sobre documentos que o navegador
renderiza como HTML. Das cinco instâncias, `/ftp/eastere.gg`, `/ftp/encrypt.pyc`,
`/ftp/package-lock.json.bak` e `/sitemap.xml` não são HTML - apenas a raiz `/` é. A
correção proposta acerta ao dizer *"em todas as respostas HTML"*, mas então o número que
a acompanha não mede o que ela corrige: o achado real é 1 instância relevante, não 5.

**E o que essas URLs revelam é mais grave que o cabeçalho ausente nelas.** Três delas são
arquivos de backup e de código servidos publicamente: `package-lock.json.bak` e
`encrypt.pyc`. A seção 1 desta própria etapa já registra que o spider disparou o desafio
*Confidential Document* percorrendo `/ftp/` por conta própria - a evidência está versionada
e comentada. Mas essa exposição aparece no documento **apenas como contagem de instância de
outro achado**: não está entre os três analisados e não está na tabela de descartados,
porque o ZAP não levantou alerta próprio para ela.

Que a ferramenta não tenha alertado é, ele mesmo, um resultado a registrar sob o §26: o
scanner encontrou o conteúdo, o aplicativo confirmou o acesso com um banner na tela, e
ainda assim nenhum alerta foi emitido. É o caso mais claro desta sessão de *falso
negativo* - o oposto do falso positivo que o V01 obrigou a investigar, e um bom contraponto
para o vídeo.

> **Encaminhamento.** Acrescentar uma observação na seção 2, sem promover o item a quarto
> achado (a sessão analisa os três de maior severidade **atribuída pela ferramenta**, e o
> critério deve ser mantido): registrar a exposição de `/ftp/` como resultado da sessão
> não alertado pelo ZAP, apoiado na captura 01 já versionada.

### 5.3 Limites desta revisão

- Não repeti a sessão do ZAP. Conferi o texto contra o relatório JSON/HTML e as capturas
  já versionados, não contra uma nova execução.
- As correções propostas em RV01 e RV02 são de **redação e de leitura do achado**; nenhuma
  delas altera quais vulnerabilidades foram encontradas, nem a severidade atribuída pela
  ferramenta.
- A revisão da @lilydias24 segue pendente e pode alcançar pontos que este recorte não
  cobriu - em especial as seções 1 e 2, que examinei quanto à consistência interna, mas não
  quanto à reprodutibilidade do plano de automação.
