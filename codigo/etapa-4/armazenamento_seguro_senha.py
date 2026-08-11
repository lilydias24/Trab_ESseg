"""Armazenamento seguro de senhas para o campo senhaLogin da classe Funcionario.

Etapa 4 do ESSEG - Prática 1, de responsabilidade de @lilydias24.
Atende ao risco R01 (Spoofing) e ao requisito RS01 da Etapa 3.

Referência: OWASP Password Storage Cheat Sheet
https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

Escolha do algoritmo
--------------------
O Cheat Sheet recomenda Argon2id como primeira opção e scrypt como alternativa
aceitável quando Argon2id não está disponível. Aqui é usado `hashlib.scrypt`,
da biblioteca padrão, para que a prática seja executável sem instalar nada e
possa ser verificada por qualquer integrante do grupo. Em produção, o SIGH
deveria usar Argon2id; o formato de registro abaixo já guarda o nome e os
parâmetros do algoritmo justamente para permitir essa migração.

O que este módulo garante
-------------------------
1. `senhaLogin` nunca é persistida em texto simples.
2. Cada credencial recebe um salt aleatório próprio, de modo que duas pessoas
   com a mesma senha produzem registros diferentes.
3. A verificação usa comparação em tempo constante.
4. O registro carrega os parâmetros usados, permitindo reforçá-los depois sem
   invalidar as senhas já cadastradas.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

# Parâmetros de custo. N é o fator de trabalho (2**15 = 32768), r e p seguem a
# recomendação do OWASP para scrypt. Aumentar N encarece o ataque por força
# bruta na mesma proporção em que encarece a verificação legítima.
_N = 2**15
_R = 8
_P = 1
_TAMANHO_SALT = 16
_TAMANHO_HASH = 32
_ALGORITMO = "scrypt"
_SEPARADOR = "$"

# O scrypt precisa de 128 * N * r bytes para operar - com os parâmetros acima,
# exatamente 32 MiB. O OpenSSL recusa a operação nesse limite se ele não for
# declarado, então o teto é informado explicitamente com folga. O custo de
# memória é intencional: é ele que torna caro o ataque em GPU.
_MAX_MEM = 64 * 1024 * 1024


def _b64(dados: bytes) -> str:
    return base64.b64encode(dados).decode("ascii")


def _de_b64(texto: str) -> bytes:
    return base64.b64decode(texto.encode("ascii"))


def _derivar(senha: str, salt: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(
        senha.encode("utf-8"),
        salt=salt,
        n=n,
        r=r,
        p=p,
        maxmem=_MAX_MEM,
        dklen=_TAMANHO_HASH,
    )


def gerar_registro_senha(senha: str) -> str:
    """Recebe a senha em claro e devolve o registro a ser gravado em senhaLogin.

    O valor retornado é o único que deve chegar ao banco. A senha em claro não
    é guardada, nem registrada em log, nem devolvida por nenhuma operação.
    """
    if not senha:
        raise ValueError("senha vazia nao pode ser cadastrada")

    salt = secrets.token_bytes(_TAMANHO_SALT)
    derivado = _derivar(senha, salt, _N, _R, _P)
    return _SEPARADOR.join(
        [_ALGORITMO, str(_N), str(_R), str(_P), _b64(salt), _b64(derivado)]
    )


def verificar_senha(senha_informada: str, registro_armazenado: str) -> bool:
    """Confere a senha informada no login contra o registro gravado.

    Devolve False para qualquer registro malformado, em vez de lançar exceção,
    para que uma linha corrompida no banco não vire uma mensagem de erro capaz
    de diferenciar contas existentes de inexistentes.
    """
    try:
        algoritmo, n, r, p, salt_b64, hash_b64 = registro_armazenado.split(_SEPARADOR)
        if algoritmo != _ALGORITMO:
            return False
        derivado = _derivar(senha_informada, _de_b64(salt_b64), int(n), int(r), int(p))
    except (ValueError, TypeError, AttributeError):
        return False

    # compare_digest evita que o tempo de resposta revele quantos bytes do hash
    # foram acertados.
    return hmac.compare_digest(derivado, _de_b64(hash_b64))


def precisa_atualizar_parametros(registro_armazenado: str) -> bool:
    """Indica se o registro foi gerado com parâmetros mais fracos que os atuais.

    Cumpre a cláusula 2 de RS01: na primeira autenticação bem-sucedida após um
    reforço de parâmetros, o sistema regrava o registro de forma transparente,
    sem pedir que o profissional troque a senha.
    """
    try:
        algoritmo, n, r, p, _, _ = registro_armazenado.split(_SEPARADOR)
    except ValueError:
        return True
    return algoritmo != _ALGORITMO or int(n) < _N or int(r) < _R or int(p) < _P
