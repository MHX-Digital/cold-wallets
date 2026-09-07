"""
Validacao de enderecos Bitcoin e Ethereum.
Previne envio para enderecos invalidos.

Uso:
    from address_validation import validate_eth_address, validate_btc_address

    valid, msg = validate_eth_address("0x...")
    if not valid:
        print(f"[ERRO] {msg}")
"""

import hashlib
import re


_BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_BECH32_ALPHABET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
_BECH32_INDEX = {char: index for index, char in enumerate(_BECH32_ALPHABET)}
_BECH32 = 1
_BECH32M = 0x2BC830A3


def validate_eth_address(address: str) -> tuple:
    """Valida endereco Ethereum (formato + checksum EIP-55)."""
    if not address:
        return False, "Endereco vazio"

    if not address.startswith("0x"):
        return False, "Endereco ETH deve comecar com 0x"

    if len(address) != 42:
        return False, f"Endereco ETH deve ter 42 caracteres (tem {len(address)})"

    if not re.match(r'^0x[0-9a-fA-F]{40}$', address):
        return False, "Endereco ETH contem caracteres invalidos"

    # Verifica checksum EIP-55 (se mixed case)
    addr_hex = address[2:]
    if addr_hex != addr_hex.lower() and addr_hex != addr_hex.upper():
        try:
            from eth_utils import is_checksum_address
            if not is_checksum_address(address):
                return False, "Checksum EIP-55 invalido"
        except ImportError:
            try:
                # EIP-55 usa Keccak-256 (nao SHA3-256)
                from eth_hash.auto import keccak
                addr_lower = addr_hex.lower()
                hash_hex = keccak(addr_lower.encode()).hex()
                for i, c in enumerate(addr_hex):
                    if c.isalpha():
                        expected_upper = int(hash_hex[i], 16) >= 8
                        if expected_upper and c.islower():
                            return False, "Checksum EIP-55 invalido"
                        if not expected_upper and c.isupper():
                            return False, "Checksum EIP-55 invalido"
            except ImportError:
                pass  # Accept address if no checksum library available

    return True, "OK"


def _decode_base58check(address: str) -> bytes | None:
    value = 0
    try:
        for char in address:
            value = value * 58 + _BASE58_ALPHABET.index(char)
    except ValueError:
        return None

    decoded = value.to_bytes((value.bit_length() + 7) // 8, "big") if value else b""
    decoded = b"\x00" * (len(address) - len(address.lstrip("1"))) + decoded
    if len(decoded) < 5:
        return None
    payload, checksum = decoded[:-4], decoded[-4:]
    expected = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    return payload if checksum == expected else None


def _bech32_polymod(values: list[int]) -> int:
    generators = (0x3B6A57B2, 0x26508E6D, 0x1EA119FA,
                  0x3D4233DD, 0x2A1462B3)
    checksum = 1
    for value in values:
        top = checksum >> 25
        checksum = ((checksum & 0x1FFFFFF) << 5) ^ value
        for index, generator in enumerate(generators):
            if (top >> index) & 1:
                checksum ^= generator
    return checksum


def _bech32_hrp_expand(hrp: str) -> list[int]:
    return [ord(char) >> 5 for char in hrp] + [0] + [ord(char) & 31 for char in hrp]


def _convert_bits(values: list[int], from_bits: int, to_bits: int) -> bytes | None:
    accumulator = 0
    bits = 0
    result = bytearray()
    max_value = (1 << to_bits) - 1
    for value in values:
        if value < 0 or value >> from_bits:
            return None
        accumulator = (accumulator << from_bits) | value
        bits += from_bits
        while bits >= to_bits:
            bits -= to_bits
            result.append((accumulator >> bits) & max_value)
    if bits >= from_bits or ((accumulator << (to_bits - bits)) & max_value):
        return None
    return bytes(result)


def _decode_segwit_address(address: str) -> tuple[int, bytes] | None:
    if not 14 <= len(address) <= 90:
        return None
    if any(ord(char) < 33 or ord(char) > 126 for char in address):
        return None
    if address.lower() != address and address.upper() != address:
        return None

    normalized = address.lower()
    separator = normalized.rfind("1")
    if separator < 1 or separator + 7 > len(normalized):
        return None
    hrp = normalized[:separator]
    if hrp != "bc":
        return None
    try:
        data = [_BECH32_INDEX[char] for char in normalized[separator + 1:]]
    except KeyError:
        return None

    polymod = _bech32_polymod(_bech32_hrp_expand(hrp) + data)
    if polymod not in (_BECH32, _BECH32M):
        return None
    witness_version = data[0]
    if witness_version > 16:
        return None
    program = _convert_bits(data[1:-6], 5, 8)
    if program is None or not 2 <= len(program) <= 40:
        return None
    if witness_version == 0:
        if polymod != _BECH32 or len(program) not in (20, 32):
            return None
    elif polymod != _BECH32M:
        return None
    return witness_version, program


def validate_btc_address(address: str) -> tuple:
    """Validate a Bitcoin mainnet Base58Check or SegWit address."""
    if not address:
        return False, "Endereco vazio"

    if not isinstance(address, str):
        return False, "Endereco BTC deve ser texto"

    # Native SegWit mainnet. Mixed case, checksum, witness version/program and
    # the Bech32-vs-Bech32m rule are all enforced by the decoder.
    if address.lower().startswith("bc1"):
        decoded = _decode_segwit_address(address)
        if decoded is None:
            return False, "Endereco SegWit mainnet invalido"
        witness_version, _ = decoded
        encoding = "bech32" if witness_version == 0 else "bech32m"
        return True, f"OK ({encoding})"

    # Explicitly reject known non-mainnet SegWit HRPs.
    if address.lower().startswith(("tb1", "bcrt1")):
        return False, "Endereco BTC nao pertence a mainnet"

    # Base58 - Legacy (1...) ou P2SH (3...)
    if address.startswith(("1", "3")):
        if not 26 <= len(address) <= 35:
            return False, f"Endereco Base58Check com tamanho invalido ({len(address)})"
        payload = _decode_base58check(address)
        if payload is None or len(payload) != 21:
            return False, "Checksum Base58Check invalido"
        expected_version = 0x00 if address.startswith("1") else 0x05
        if payload[0] != expected_version:
            return False, "Versao Base58Check incompativel com mainnet"
        return True, "OK (base58check)"

    if address.startswith(("m", "n", "2")):
        return False, "Endereco BTC nao pertence a mainnet"

    return False, "Endereco BTC mainnet deve comecar com 1, 3 ou bc1"
