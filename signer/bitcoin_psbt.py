"""Strict offline PSBT v0 boundary backed by embit; no network capability."""
from __future__ import annotations
import hashlib

class PsbtError(ValueError): pass

def _lib():
    try:
        from embit import ec, finalizer, networks, psbt
    except ImportError as exc: raise PsbtError("reviewed embit dependency is unavailable") from exc
    return ec,finalizer,networks,psbt

def inspect_psbt(encoded: str,*,network: str,expected_outputs: set[str],max_fee: int):
    _,_,networks,psbt=_lib()
    if network not in {"main","test","regtest"}: raise PsbtError("unsupported network")
    try: proposal=psbt.PSBT.from_string(encoded); proposal.verify()
    except Exception as exc: raise PsbtError("invalid or unverifiable PSBT") from exc
    if proposal.version not in {None,0}: raise PsbtError("only PSBT v0 is supported")
    if any(getattr(i,"final_scriptsig",None) or getattr(i,"final_scriptwitness",None) for i in proposal.inputs): raise PsbtError("PSBT already finalized")
    for item in proposal.inputs:
        if item.utxo is None or item.non_witness_utxo is None: raise PsbtError("full prevout data required")
        if item.sighash_type not in {None,1}: raise PsbtError("only SIGHASH_ALL is allowed")
    net=networks.NETWORKS[network]
    outputs=[]
    for output in proposal.tx.vout:
        try: address=output.script_pubkey.address(net)
        except Exception as exc: raise PsbtError("unsupported output script") from exc
        outputs.append({"address":address,"value":output.value})
    actual={o["address"] for o in outputs}
    if actual!=expected_outputs: raise PsbtError("unexpected output set")
    fee=proposal.fee()
    if fee<0 or fee>max_fee: raise PsbtError("fee policy exceeded")
    digest=hashlib.sha256(proposal.serialize()).hexdigest()
    return proposal,{"proposalId":digest,"network":network,"inputs":len(proposal.inputs),"outputs":outputs,"fee":fee}

def sign_psbt(encoded: str,secret: bytearray,*,confirmation: str,network: str,expected_outputs: set[str],max_fee: int):
    ec,finalizer,_,_= _lib(); proposal,summary=inspect_psbt(encoded,network=network,expected_outputs=expected_outputs,max_fee=max_fee)
    if confirmation!=summary["proposalId"]: raise PsbtError("confirmation does not match PSBT")
    try:
        key=ec.PrivateKey(bytes(secret)); signatures=proposal.sign_with(key)
        if signatures<1: raise PsbtError("key does not control any input")
        transaction=finalizer.finalize_psbt(proposal)
        if transaction is None: raise PsbtError("PSBT could not be finalized")
        raw=transaction.serialize().hex(); txid=transaction.txid().hex()
        return {"schema":"cold-wallets.btc-signed","version":1,"network":network,"proposalId":summary["proposalId"],"rawTransaction":raw,"transactionId":txid}
    finally:
        for index in range(len(secret)): secret[index]=0
