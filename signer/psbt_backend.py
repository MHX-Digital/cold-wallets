"""Fail-closed provenance policy for the embit secp256k1 backend."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path


class BackendPolicyError(RuntimeError):
    pass


# Intentionally empty until binaries are reproduced/reviewed per platform.
APPROVED_NATIVE_SHA256: frozenset[str] = frozenset()


@dataclass(frozen=True)
class BackendDiagnostic:
    status: str
    backend_type: str
    artifact_sha256: str | None
    signing_enabled: bool

    def public(self) -> dict[str, object]:
        return asdict(self)


def diagnose() -> BackendDiagnostic:
    try:
        from embit.util import secp256k1
    except ImportError:
        return BackendDiagnostic("unapproved", "unavailable", None, False)

    implementation = getattr(secp256k1.ecdsa_sign, "__module__", "")
    if implementation.endswith("ctypes_secp256k1"):
        from embit.util import ctypes_secp256k1

        candidate = ctypes_secp256k1._find_library()
        path = Path(candidate) if candidate else None
        if path is None or not path.is_file():
            return BackendDiagnostic("unapproved", "native", None, False)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        approved = digest in APPROVED_NATIVE_SHA256
        return BackendDiagnostic(
            "approved" if approved else "unapproved", "native", digest, approved
        )

    # The fallback has not received an independent cryptographic review either.
    return BackendDiagnostic("unapproved", "pure-python", None, False)


def require_approved() -> BackendDiagnostic:
    result = diagnose()
    if not result.signing_enabled:
        raise BackendPolicyError("PSBT cryptographic backend is not approved")
    return result
