"""Strict offline PSBT v0 boundary backed by embit; no network capability."""
from __future__ import annotations
from coordinator.bitcoin_psbt import PsbtError, inspect_psbt
from signer.psbt_backend import BackendPolicyError, require_approved

def _lib():
    try:
        from embit import ec, finalizer, networks, psbt
    except ImportError as exc: raise PsbtError("reviewed embit dependency is unavailable") from exc
    return ec,finalizer,networks,psbt

def sign_psbt(encoded: str,secret: bytearray,*,confirmation: str,network: str,expected_outputs: set[str],max_fee: int):
    try: require_approved()
    except BackendPolicyError as exc: raise PsbtError(str(exc)) from exc
    ec,finalizer,_,_= _lib(); proposal,summary=inspect_psbt(encoded,network=network,expected_outputs=expected_outputs,max_fee=max_fee)
    if confirmation!=summary["proposalId"]: raise PsbtError("confirmation does not match PSBT")
    try:
        key=ec.PrivateKey(bytes(secret)); signatures=proposal.sign_with(key)
        if signatures<1: raise PsbtError("key does not control any input")
        transaction=finalizer.finalize_psbt(proposal)
        if transaction is None: raise PsbtError("PSBT could not be finalized")
        raw=transaction.serialize().hex(); txid=transaction.txid().hex()
        return {"schema":"cold-wallets.btc-signed","version":1,"network":summary["network"],"proposalId":summary["proposalId"],"rawTransaction":raw,"transactionId":txid}
    finally:
        for index in range(len(secret)): secret[index]=0
