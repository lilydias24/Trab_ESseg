"""Controle de autorização no servidor para o `nivelAcesso` do Administrador.

Etapa 4 do ESSEG - Prática 2, de responsabilidade de @PPrauchner.
Atende ao risco R06 (Elevation of Privilege) e ao requisito RS03 da Etapa 3.

Referência: OWASP Authorization Cheat Sheet
https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

O que este módulo demonstra
--------------------------
1. Identidade, perfil e `nivelAcesso` vêm da **sessão autenticada**; os campos
   homônimos recebidos no corpo são **descartados antes de qualquer validação**
   (cláusula 1 de RS03). Descartar, e não validar: validar um valor controlado
   pelo cliente ainda é confiar nele.
2. A decisão de autorização é explícita, no servidor e **fora** do componente
   que executa a operação - é o Serviço de Autorização da DA02 -, com **negação
   por padrão**: operação sem regra declarada é recusada (cláusula 2).
3. `nivelAcesso` não é gravável pela via de salvamento do cadastro; a mudança de
   perfil é operação própria, exige alçada de Diretor e o titular nunca é
   autorizado sobre o próprio registro (cláusula 3).
4. A recusa é HTTP 403 e precede a persistência, sem efeito parcial (cláusula 4).
5. Alterações efetivadas **e** recusadas vão para a trilha de auditoria, com
   autor, valor anterior, valor novo, terminal e data/hora carimbados pelo
   servidor (cláusula 5). O alerta da cláusula 7 é só das elevações
   **efetivadas** - rebaixamento é registrado e não notifica; as tentativas
   alimentam a Regra 3 da Etapa 6 por outros gatilhos - daí as duas consultas
   distintas na trilha.
6. O valor de destino da alteração de perfil sai de um conjunto fechado
   (`NIVEIS_DE_ACESSO`); a ausência do parâmetro e o alvo fora do cadastro são
   recusados como HTTP 400 (`ErroDeEntrada`), não como 403 nem como erro de
   servidor. Não é cláusula de RS03 - é a higiene de entrada que impede a
   decisão do servidor de operar sobre um nível ou um registro que ela não
   conhece.

O que este módulo não é: um framework de autorização. É o menor modelo capaz de
tornar essas decisões visíveis - uma sessão, um cadastro em memória, um decisor
e uma trilha somente de acréscimo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

# Campos que o cliente pode enviar mas que só a sessão tem autoridade para
# afirmar. São removidos do corpo na entrada do serviço.
CAMPOS_DE_SESSAO = ("idFuncionario", "perfil", "nivelAcesso")

# Campos de autenticação nunca retornam em resposta administrativa: eles residem
# no serviço de autenticação instituído pela DA03 (cláusula 8).
CAMPOS_DE_AUTENTICACAO = ("nomeLogin", "senhaLogin")

# A via de salvamento do cadastro grava dados funcionais e nada mais. É uma
# allowlist, e não uma lista de proibidos: campo novo no cadastro nasce não
# gravável por esta via, do mesmo modo que operação nova nasce recusada. Sem
# isso, `registro.update(corpo)` deixaria o corpo da requisição reescrever
# `senhaLogin` - a elevação de R06 pela porta ao lado, sobre o que RS01 protege.
CAMPOS_FUNCIONAIS_GRAVAVEIS = ("nome", "setor")

# Alçadas que podem salvar o cadastro de um terceiro. Perfil `Administrador`
# sozinho não basta: sem vínculo com o alvo, qualquer Supervisor gravaria sobre
# o registro do Diretor (cláusula 3 - quem solicita não é quem aprova).
ALCADAS_SOBRE_TERCEIROS = ("GerenteGeral", "Diretor")

# Conjunto fechado de níveis do modelo de domínio. É allowlist de valores, e não
# só de campos: sem ela, uma sessão autorizada gravaria qualquer string como
# nível - `"SuperDiretor"`, `""` - e a própria decisão de `decidir`, que compara
# `nivel_acesso` com literais, passaria a operar sobre um valor que não conhece.
NIVEIS_DE_ACESSO = ("Supervisor", "GerenteSetor", "GerenteGeral", "Diretor")

LIMITE_DE_LISTAGEM = 50
CODIGO_NAO_AUTORIZADO = 403
CODIGO_ENTRADA_INVALIDA = 400


class ErroAutorizacao(Exception):
    """Recusa de autorização. Corresponde à resposta HTTP 403 da cláusula 4."""

    codigo_http = CODIGO_NAO_AUTORIZADO


class ErroDeEntrada(Exception):
    """Recusa por requisição malformada. Corresponde a HTTP 400, não a 403.

    A distinção não é cosmética: 403 diz "você não pode", 400 diz "o pedido não
    faz sentido". Tratar parâmetro ausente como erro de autorização mentiria na
    trilha; deixá-lo virar `KeyError` devolveria 500 - erro de servidor para
    entrada malformada de cliente.
    """

    codigo_http = CODIGO_ENTRADA_INVALIDA


@dataclass(frozen=True)
class Sessao:
    """Identidade emitida pelo serviço de autenticação (DA03).

    É a única fonte de perfil e de `nivelAcesso` aceita pelo servidor. Imutável
    porque a sessão não pode ser reescrita pelo conteúdo de uma requisição.
    """

    id_funcionario: str
    perfil: str
    nivel_acesso: str
    terminal: str


@dataclass(frozen=True)
class Decisao:
    permitida: bool
    motivo: str


def descartar_campos_de_sessao(corpo: dict) -> tuple[dict, dict]:
    """Remove do corpo os campos que só a sessão pode afirmar.

    Devolve o corpo já limpo e o que foi descartado, **com os valores** - o
    segundo é o que permite registrar a tentativa em vez de ignorá-la em
    silêncio (RS03-CA04). Guardar o valor não é confiar nele: nenhuma decisão
    o consulta, e a cláusula 5 exige registrar o valor novo pretendido também
    nas alterações recusadas. É o campo `claimedLevel` do contrato de eventos
    da Regra 3 da Etapa 6, que separa reenvio de rotina de tentativa de
    gravação comparando-o com o nível vigente.
    """
    descartados = {campo: corpo[campo] for campo in CAMPOS_DE_SESSAO if campo in corpo}
    limpo = {chave: valor for chave, valor in corpo.items() if chave not in CAMPOS_DE_SESSAO}
    return limpo, descartados


class TrilhaDeAuditoria:
    """Trilha somente de acréscimo, no papel do Serviço de Auditoria (DA01)."""

    def __init__(self) -> None:
        self._entradas: list[dict] = []

    def registrar(
        self,
        sessao: Sessao,
        operacao: str,
        id_alvo: str | None,
        resultado: str,
        motivo: str = "",
        valor_anterior: str | None = None,
        valor_novo: str | None = None,
        campos_descartados: tuple[str, ...] = (),
        nivel_afirmado: str | None = None,
    ) -> None:
        self._entradas.append(
            {
                # O carimbo é do servidor, nunca do cliente: em R06 a data da
                # mudança de perfil é justamente o que não se consegue
                # reconstruir depois.
                "momento_servidor": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "autor": sessao.id_funcionario,
                "perfil_autor": sessao.nivel_acesso,
                "terminal": sessao.terminal,
                "operacao": operacao,
                "alvo": id_alvo,
                "resultado": resultado,
                "motivo": motivo,
                "valor_anterior": valor_anterior,
                "valor_novo": valor_novo,
                "campos_descartados": campos_descartados,
                # O `nivelAcesso` que o corpo afirmava, preservado como
                # afirmação do cliente e não como fato do servidor. É o
                # `claimedLevel` da Regra 3 da Etapa 6.
                "nivel_afirmado": nivel_afirmado,
            }
        )

    def entradas(self) -> tuple[dict, ...]:
        return tuple(self._entradas)

    def alertas_de_elevacao(self) -> tuple[dict, ...]:
        """Alerta da cláusula 7 de RS03: só elevações **efetivadas**.

        A cláusula manda alertar Diretor e Segurança da Informação no momento da
        elevação. Uma tentativa recusada não é elevação, e prometer alerta nela
        seria prometer um limiar que a Regra 3 não tem: recusa entra na regra
        pelos gatilhos de repetição, não por notificação imediata.

        Rebaixamento também não é elevação. Alterar perfil para baixo fica
        registrado na trilha, mas não notifica por este caminho - é o Gatilho A
        da Regra 3 tal como a Etapa 6 o define.
        """
        return tuple(
            e
            for e in self._entradas
            if e["operacao"] == "alterarPerfil"
            and e["resultado"] == "EFETIVADA"
            and NIVEIS_DE_ACESSO.index(e["valor_novo"])
            > NIVEIS_DE_ACESSO.index(e["valor_anterior"])
        )

    def eventos_para_regra_3(self) -> tuple[dict, ...]:
        """Tudo que a Regra 3 da Etapa 6 consome, em qualquer dos dois caminhos.

        As duas faces do ataque de RS03-CA02 alimentam a regra, como diz o
        critério: a operação própria de alteração de perfil (efetivada ou
        recusada) e a tentativa de gravar `nivelAcesso` pela via de salvamento,
        que não gera 403 e ficaria invisível se a regra olhasse só a operação.
        """
        return tuple(
            e
            for e in self._entradas
            if e["operacao"] == "alterarPerfil"
            or "nivelAcesso" in e["campos_descartados"]
        )


class ServicoDeAutorizacao:
    """Ponto único de decisão de acesso, conforme a DA02.

    Fica fora do serviço que executa a operação: se a decisão morasse dentro
    dele, seria alcançável pelo mesmo caminho que se quer barrar.
    """

    def decidir(self, sessao: Sessao, operacao: str, id_alvo: str | None) -> Decisao:
        if operacao == "alterarPerfil":
            if sessao.nivel_acesso != "Diretor":
                return Decisao(False, "alteracao de perfil exige alcada de Diretor")
            if id_alvo == sessao.id_funcionario:
                return Decisao(False, "o titular nao tem alcada sobre o proprio registro")
            return Decisao(True, "sessao com alcada de Diretor sobre outro funcionario")

        if operacao == "salvarCadastro":
            if sessao.perfil != "Administrador":
                return Decisao(False, "operacao administrativa exige perfil Administrador")
            # O perfil diz que a operação existe para esta sessão; o alvo diz
            # sobre quem ela vale. Sem o segundo teste, a autorização seria de
            # menu, não de recurso.
            if id_alvo != sessao.id_funcionario and sessao.nivel_acesso not in ALCADAS_SOBRE_TERCEIROS:
                return Decisao(False, "salvar cadastro de terceiro exige alcada de GerenteGeral")
            return Decisao(True, "dados funcionais dentro da alcada administrativa")

        if operacao == "listarCadastro":
            if sessao.nivel_acesso not in ("GerenteGeral", "Diretor"):
                return Decisao(False, "listagem em massa exige alcada de GerenteGeral")
            return Decisao(True, "listagem autorizada, sujeita a limite de volume")

        # Negação por padrão: um endpoint administrativo novo, que ninguém
        # lembrou de declarar aqui, nasce recusado - nunca liberado por omissão.
        return Decisao(False, "operacao sem regra de autorizacao declarada")


class ServicoDeFuncionarios:
    """Componente que executa a operação, depois de autorizada em outro lugar."""

    limite_de_listagem = LIMITE_DE_LISTAGEM

    def __init__(
        self,
        cadastro: dict[str, dict],
        autorizacao: ServicoDeAutorizacao,
        trilha: TrilhaDeAuditoria,
    ) -> None:
        self._cadastro = cadastro
        self._autorizacao = autorizacao
        self._trilha = trilha

    def executar(self, sessao: Sessao, operacao: str, id_alvo: str | None, corpo: dict):
        """Entrada única do serviço - o endpoint, com ou sem interface na frente.

        A ordem das três primeiras linhas é o requisito: descartar o que veio do
        cliente, decidir, e só então executar. Persistir antes de decidir seria
        o efeito parcial que a cláusula 4 proíbe.
        """
        corpo, descartados = descartar_campos_de_sessao(corpo)
        decisao = self._autorizacao.decidir(sessao, operacao, id_alvo)

        if not decisao.permitida:
            self._trilha.registrar(
                sessao, operacao, id_alvo, "RECUSADA", decisao.motivo,
                campos_descartados=tuple(descartados),
                nivel_afirmado=descartados.get("nivelAcesso"),
            )
            # A mensagem não diz qual campo ou perfil existe: a resposta de
            # recusa não pode virar fonte de enumeração.
            raise ErroAutorizacao("operacao nao autorizada")

        if operacao in ("alterarPerfil", "salvarCadastro"):
            if id_alvo is None:
                # Operação sobre registro sem dizer qual registro é pedido
                # malformado, não recusa de alçada: 400, e antes de qualquer
                # escrita.
                raise ErroDeEntrada("operacao exige identificacao do registro alvo")
            if id_alvo not in self._cadastro:
                # Mesmo caso: alvo que não existe é pedido malformado. Sem este
                # guarda, a busca no cadastro levantaria `KeyError` - erro de
                # servidor para entrada de cliente. A mensagem não confirma nem
                # nega a existência do identificador, para não virar enumeração.
                raise ErroDeEntrada("operacao exige identificacao do registro alvo")

        if operacao == "alterarPerfil":
            return self._alterar_perfil(sessao, id_alvo, corpo, decisao)
        if operacao == "salvarCadastro":
            return self._salvar_cadastro(sessao, id_alvo, corpo, descartados)
        if operacao == "listarCadastro":
            return self._listar_cadastro(sessao)
        # Despacho também nega por omissão. Se este `return` fosse a listagem,
        # bastaria declarar uma regra nova em `decidir` e esquecer o ramo aqui
        # para a chamada cair numa leitura em massa do cadastro - exatamente o
        # que a cláusula 8 trata como caminho de dano.
        raise ErroAutorizacao("operacao nao autorizada")

    def nivel_acesso_de(self, id_funcionario: str) -> str:
        return self._cadastro[id_funcionario]["nivelAcesso"]

    def credencial_de(self, id_funcionario: str) -> str:
        """Só para o teste conferir que a via de salvamento não a alcançou."""
        return self._cadastro[id_funcionario]["senhaLogin"]

    def _alterar_perfil(
        self, sessao: Sessao, id_alvo: str, corpo: dict, decisao: Decisao
    ) -> dict:
        """Efetiva a alteração de perfil já autorizada.

        Levanta `ErroDeEntrada` (HTTP 400) se `novoNivelAcesso` não vier no corpo
        ou trouxer valor fora de `NIVEIS_DE_ACESSO`. Não é `ErroAutorizacao`: a
        alçada foi verificada e aprovada antes daqui - o que falha é o pedido.
        """
        registro = self._cadastro[id_alvo]
        anterior = registro["nivelAcesso"]
        # O valor novo é parâmetro da operação própria de alteração de perfil -
        # `novoNivelAcesso`, e não o `nivelAcesso` do corpo do salvamento, que já
        # foi descartado na entrada. O primeiro é o que a operação autorizada
        # concede a um terceiro; o segundo seria o cliente afirmando a própria
        # alçada. É a cláusula 3 tomando forma no código.
        if "novoNivelAcesso" not in corpo:
            raise ErroDeEntrada("parametro novoNivelAcesso ausente")
        novo = corpo["novoNivelAcesso"]
        # Estar autorizado a alterar o perfil de alguém não é estar autorizado a
        # inventar um perfil: a validação vem depois da decisão porque é sobre o
        # valor, não sobre quem pede.
        if novo not in NIVEIS_DE_ACESSO:
            raise ErroDeEntrada("nivel de acesso fora do conjunto conhecido")
        registro["nivelAcesso"] = novo
        self._trilha.registrar(
            sessao, "alterarPerfil", id_alvo, "EFETIVADA", decisao.motivo,
            valor_anterior=anterior, valor_novo=novo,
        )
        return self._sem_campos_de_autenticacao(registro)

    def _salvar_cadastro(
        self, sessao: Sessao, id_alvo: str, corpo: dict, descartados: dict
    ) -> dict:
        registro = self._cadastro[id_alvo]
        # `registro.update(corpo)` gravaria qualquer chave que o cliente
        # inventasse, inclusive `senhaLogin`. A gravação é restrita à allowlist
        # de dados funcionais; o resto é ignorado e fica registrado, pela mesma
        # razão que os campos de sessão: erro silencioso não vira evidência.
        gravaveis = {
            chave: valor
            for chave, valor in corpo.items()
            if chave in CAMPOS_FUNCIONAIS_GRAVAVEIS
        }
        ignorados = tuple(chave for chave in corpo if chave not in CAMPOS_FUNCIONAIS_GRAVAVEIS)
        registro.update(gravaveis)
        self._trilha.registrar(
            sessao, "salvarCadastro", id_alvo, "EFETIVADA",
            "dados funcionais gravados",
            # `valor_anterior` é o nível vigente, do servidor; `nivel_afirmado` é
            # o que o corpo dizia. A Regra 3 compara os dois para separar reenvio
            # de rotina - valores iguais - de tentativa de gravar o campo.
            valor_anterior=registro["nivelAcesso"],
            campos_descartados=tuple(descartados) + ignorados,
            nivel_afirmado=descartados.get("nivelAcesso"),
        )
        return self._sem_campos_de_autenticacao(registro)

    def _listar_cadastro(self, sessao: Sessao) -> list[dict]:
        pagina = [
            self._sem_campos_de_autenticacao(registro)
            for registro in list(self._cadastro.values())[: self.limite_de_listagem]
        ]
        self._trilha.registrar(
            sessao, "listarCadastro", None, "EFETIVADA",
            f"{len(pagina)} registros retornados",
        )
        return pagina

    @staticmethod
    def _sem_campos_de_autenticacao(registro: dict) -> dict:
        return {
            chave: valor
            for chave, valor in registro.items()
            if chave not in CAMPOS_DE_AUTENTICACAO
        }


def cadastro_de_exemplo() -> dict[str, dict]:
    """Recorte mínimo do cadastro de `Funcionario`, com os campos que importam."""
    return {
        "F001": {
            "nome": "Helena Duarte", "setor": "Diretoria", "nivelAcesso": "Diretor",
            "nomeLogin": "hduarte", "senhaLogin": "<registro scrypt da Pratica 1>",
        },
        "F002": {
            "nome": "Marcos Vieira", "setor": "Internacao", "nivelAcesso": "GerenteGeral",
            "nomeLogin": "mvieira", "senhaLogin": "<registro scrypt da Pratica 1>",
        },
        "F003": {
            "nome": "Rita Camargo", "setor": "Farmacia", "nivelAcesso": "Supervisor",
            "nomeLogin": "rcamargo", "senhaLogin": "<registro scrypt da Pratica 1>",
        },
    }
