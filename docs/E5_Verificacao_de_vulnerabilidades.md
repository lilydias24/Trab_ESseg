# Etapa 5 - Verificação de Vulnerabilidades

> **Sistema:** SIGH - Sistema Integrado de Gestão Hospitalar
> **Líder da etapa:** @PPrauchner
> É exigida **1 sessão de teste**. Como o SIGH não está implementado, a verificação é feita no **OWASP Juice Shop** com o **OWASP ZAP**. Evidências em `evidencias/etapa-5/capturas-de-tela/`.

| Item | Responsável | Situação |
| --- | --- | --- |
| Condução da sessão (setup Juice Shop + ZAP, captura de evidências) | @PPrauchner | Concluída (sessão executada em 13/08/2026; relatório e capturas versionados) |
| Análise dos 3 achados e correção proposta (com CWE/OWASP) | @mariasanchez0 | Concluída |
| Revisão cruzada e complemento da tabela final | @lilydias24 e @lorenzoficher | Pendente |

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
  que a sessão possa ser repetida por qualquer integrante.
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

| ID | Achado | Severidade (ZAP) | Evidência | Possível impacto | CWE/OWASP | Correção proposta |
| --- | --- | --- | --- | --- | --- | --- |
| V01 | **SQL Injection** em `GET /rest/products/search`, parâmetro `q`. Carga `'(` produz `HTTP 500` com `SQLITE_ERROR: near "(": syntax error` | Alto (confiança Baixa segundo o ZAP - **verificado como verdadeiro positivo**, ver abaixo) | [captura 03](../evidencias/etapa-5/capturas-de-tela/03-sqli-erro-sqlite.png); `pluginid` 40018 no [JSON](../evidencias/etapa-5/relatorio-zap-juiceshop.json) | Leitura, adulteração ou exclusão de dados no banco por trás do endpoint, caso a exploração avance além do erro de sintaxe já confirmado | CWE-89; WASC-19 | Consultas parametrizadas (prepared statements) e resposta de erro genérica, sem stack trace nem versão de framework |
| V02 | **Content Security Policy (CSP) Header Not Set** - 5 instâncias, incluindo a raiz da aplicação | Médio (confiança Alta) | [captura 02](../evidencias/etapa-5/capturas-de-tela/02-zap-relatorio-alertas.png); `pluginid` 10038 | Amplia o efeito de qualquer XSS presente na aplicação, por faltar a camada do navegador que conteria um script injetado | CWE-693; WASC-15 | Cabeçalho `Content-Security-Policy` restritivo (`default-src 'self'`, sem `unsafe-inline`/`unsafe-eval`) em todas as respostas |
| V03 | **Cross-Domain Misconfiguration** - resposta traz `Access-Control-Allow-Origin: *`, em 3 instâncias | Médio (confiança Média) | [captura 02](../evidencias/etapa-5/capturas-de-tela/02-zap-relatorio-alertas.png); `pluginid` 10098 | Qualquer origem pode ler resposta autenticada via requisição cross-site, ampliando furto de sessão ou dado por site malicioso | CWE-264; WASC-14 | Allowlist de origens confiáveis no `Access-Control-Allow-Origin`, nunca combinado com `Access-Control-Allow-Credentials: true` |

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
cliente é, por si, um segundo problema.*

### Alertas descartados desta análise

O §25 permite explicar por que os demais resultados foram descartados. Os cinco
alertas restantes não entraram entre os três analisados:

| Alerta | Risco | Por que foi descartado |
| --- | --- | --- |
| Private IP Disclosure (`192.168.99.100:3000`) | Baixo | Endereço interno devolvido por `/rest/admin/application-configuration`. É exposição real, mas de baixo alcance e, neste caso, um valor de configuração de exemplo do próprio Juice Shop, não da infraestrutura em que a sessão rodou |
| Timestamp Disclosure - Unix | Baixo | **Provável falso positivo.** O ZAP reconhece qualquer inteiro de 10 dígitos como *timestamp*; o valor sinalizado (`1666666667`) é uma constante do código, não um carimbo de tempo real |
| Information Disclosure - Suspicious Comments | Informativo | A "evidência" é a palavra `SELECT` dentro de `chunk-DAJ4olp_.js`, um bundle Angular minificado. Padrão textual, não vazamento |
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

### V01 - SQL Injection em `/rest/products/search`

- **O que foi encontrado:**
- **Por que é um problema:**
- **Correção proposta:**
- **Relação com CWE/OWASP:**

### V02 - Content Security Policy (CSP) Header Not Set

- **O que foi encontrado:**
- **Por que é um problema:**
- **Correção proposta:**
- **Relação com CWE/OWASP:**

### V03 - Cross-Domain Misconfiguration (`Access-Control-Allow-Origin: *`)

- **O que foi encontrado:**
- **Por que é um problema:**
- **Correção proposta:**
- **Relação com CWE/OWASP:**

## 4. Considerações da etapa

*(Pendente - o que a sessão mostrou, limitações da ferramenta e relação com os riscos
já registrados na [Etapa 2](E2_Riscos_e_NIST_CSF.md). Depende da análise da seção 3.)*
