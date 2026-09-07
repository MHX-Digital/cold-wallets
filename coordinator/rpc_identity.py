"""Evidence-based identity for Ethereum data backends."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class RpcIdentity(str, Enum):
    PUBLIC_RPC_UNVERIFIED="PUBLIC_RPC_UNVERIFIED"
    HELIOS_UNATTESTED="HELIOS_UNATTESTED"
    HELIOS_ATTESTED="HELIOS_ATTESTED"


@dataclass(frozen=True)
class HeliosEvidence:
    expected_process: bool=False
    expected_version_or_digest: bool=False
    expected_configuration: bool=False
    chain_id_verified: bool=False
    healthcheck_verified: bool=False
    checkpoint_verified: bool=False
    coherent_response: bool=False
    exclusive_path_verified: bool=False


def classify(*, public_rpc: bool, helios: HeliosEvidence | None=None) -> RpcIdentity:
    if public_rpc: return RpcIdentity.PUBLIC_RPC_UNVERIFIED
    if helios is None: return RpcIdentity.HELIOS_UNATTESTED
    if all(vars(helios).values()): return RpcIdentity.HELIOS_ATTESTED
    return RpcIdentity.HELIOS_UNATTESTED
