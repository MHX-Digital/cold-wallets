"""Strict, deterministic Ethereum transaction proposal envelope."""
from __future__ import annotations
import hashlib, json, re, time
from typing import Any

_INT = re.compile(r"(?:0|[1-9][0-9]*)\Z")
_FIELDS = {"schema","version","network","chainId","type","from","to","valueWei","nonce","gasLimit","maxFeePerGasWei","maxPriorityFeePerGasWei","data","createdAt","expiresAt","proposalId","sources"}
_HASH_FIELDS = ["schema","version","network","chainId","type","from","to","valueWei","nonce","gasLimit","maxFeePerGasWei","maxPriorityFeePerGasWei","data"]

class EnvelopeError(ValueError): pass

def _integer(value: Any, name: str) -> str:
    if not isinstance(value, str) or not _INT.fullmatch(value): raise EnvelopeError(f"invalid {name}")
    return value

def proposal_id(envelope: dict[str, Any]) -> str:
    core = {k: envelope[k] for k in _HASH_FIELDS}
    raw = json.dumps(core, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def validate(envelope: dict[str, Any], now: int | None = None) -> dict[str, Any]:
    if not isinstance(envelope, dict) or set(envelope) != _FIELDS: raise EnvelopeError("schema fields mismatch")
    if envelope["schema"] != "cold-wallets.eth-tx" or envelope["version"] != 1 or envelope["type"] != "2": raise EnvelopeError("unsupported envelope")
    for k in ("chainId","valueWei","nonce","gasLimit","maxFeePerGasWei","maxPriorityFeePerGasWei"): _integer(envelope[k], k)
    if int(envelope["maxPriorityFeePerGasWei"]) > int(envelope["maxFeePerGasWei"]): raise EnvelopeError("priority fee exceeds max fee")
    for k in ("from","to"):
        if not isinstance(envelope[k], str) or not re.fullmatch(r"0x[0-9a-fA-F]{40}", envelope[k]): raise EnvelopeError(f"invalid {k}")
    if not isinstance(envelope["data"], str) or not re.fullmatch(r"0x(?:[0-9a-f]{2})*", envelope["data"]): raise EnvelopeError("invalid data")
    if not isinstance(envelope["sources"], list): raise EnvelopeError("invalid sources")
    if not isinstance(envelope["expiresAt"], int) or not isinstance(envelope["createdAt"], int): raise EnvelopeError("invalid timestamps")
    if (now if now is not None else int(time.time())) >= envelope["expiresAt"]: raise EnvelopeError("envelope expired")
    if envelope["proposalId"] != proposal_id(envelope): raise EnvelopeError("proposal hash mismatch")
    return envelope
