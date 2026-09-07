"""Neutral fail-closed provenance policy for the PSBT secp256k1 backend."""
from __future__ import annotations
from dataclasses import asdict,dataclass
from enum import Enum
import hashlib
from pathlib import Path

class BackendPolicyError(RuntimeError): pass
APPROVED_NATIVE_SHA256: frozenset[str]=frozenset()
APPROVED_REPRODUCIBLE_SHA256: frozenset[str]=frozenset()

class BackendState(str,Enum):
    UNAVAILABLE="UNAVAILABLE"
    DETECTED_UNAPPROVED="DETECTED_UNAPPROVED"
    APPROVED_NATIVE="APPROVED_NATIVE"
    APPROVED_REPRODUCIBLE_BUILD="APPROVED_REPRODUCIBLE_BUILD"
    APPROVED_PURE_PYTHON="APPROVED_PURE_PYTHON"

@dataclass(frozen=True)
class BackendDiagnostic:
    status: BackendState
    backend_type: str
    artifact_sha256: str|None
    signing_enabled: bool
    def public(self): return asdict(self)

def diagnose():
    try: from embit.util import secp256k1
    except ImportError: return BackendDiagnostic(BackendState.UNAVAILABLE,"unavailable",None,False)
    implementation=getattr(secp256k1.ecdsa_sign,"__module__","")
    if implementation.endswith("ctypes_secp256k1"):
        from embit.util import ctypes_secp256k1
        candidate=ctypes_secp256k1._find_library(); path=Path(candidate) if candidate else None
        if path is None or not path.is_file(): return BackendDiagnostic(BackendState.DETECTED_UNAPPROVED,"native",None,False)
        digest=hashlib.sha256(path.read_bytes()).hexdigest(); reproducible=digest in APPROVED_REPRODUCIBLE_SHA256; approved=digest in APPROVED_NATIVE_SHA256 or reproducible
        state=BackendState.APPROVED_REPRODUCIBLE_BUILD if reproducible else (BackendState.APPROVED_NATIVE if approved else BackendState.DETECTED_UNAPPROVED)
        return BackendDiagnostic(state,"native",digest,approved)
    return BackendDiagnostic(BackendState.DETECTED_UNAPPROVED,"pure-python",None,False)

def require_approved():
    result=diagnose()
    if not result.signing_enabled: raise BackendPolicyError("PSBT cryptographic backend is not approved")
    return result
