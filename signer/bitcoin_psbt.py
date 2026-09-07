"""Strict offline PSBT v0 boundary backed by embit; no network capability."""
from __future__ import annotations
import hashlib
from signer.psbt_backend import BackendPolicyError, require_approved

class PsbtError(ValueError): pass

def _lib():
    try:
        from embit import ec, finalizer, networks, psbt
    except ImportError as exc: raise PsbtError("reviewed embit dependency is unavailable") from exc
    return ec,finalizer,networks,psbt

def inspect_psbt(encoded: str,*,network: str,expected_outputs: set[str],max_fee: int,max_fee_rate: int=1_000):
    _,_,networks,psbt=_lib()
    if network != "main": raise PsbtError("only Bitcoin mainnet is supported")
    try: proposal=psbt.PSBT.from_string(encoded); proposal.verify()
    except Exception as exc: raise PsbtError("invalid or unverifiable PSBT") from exc
    if proposal.version not in {None,0}: raise PsbtError("only PSBT v0 is supported")
    if any(getattr(i,"final_scriptsig",None) or getattr(i,"final_scriptwitness",None) for i in proposal.inputs): raise PsbtError("PSBT already finalized")
    for item in proposal.inputs:
        if item.utxo is None or item.non_witness_utxo is None: raise PsbtError("full prevout data required")
        if item.sighash_type not in {None,1}: raise PsbtError("only SIGHASH_ALL is allowed")
        if item.vout < 0 or item.vout >= len(item.non_witness_utxo.vout): raise PsbtError("prevout index is invalid")
        prevout=item.non_witness_utxo.vout[item.vout]
        if item.txid != item.non_witness_utxo.txid(): raise PsbtError("prevout transaction ID mismatch")
        if item.witness_utxo.serialize() != prevout.serialize(): raise PsbtError("witness and non-witness UTXO mismatch")
        if item.witness_utxo.script_pubkey.script_type() != "p2wpkh": raise PsbtError("only native P2WPKH inputs are supported")
    net=networks.NETWORKS[network]
    outputs=[]
    for output in proposal.tx.vout:
        try: address=output.script_pubkey.address(net)
        except Exception as exc: raise PsbtError("unsupported output script") from exc
        outputs.append({"address":address,"value":output.value})
    if len(outputs)!=1 or len(expected_outputs)!=1: raise PsbtError("send-all requires exactly one output")
    actual={o["address"] for o in outputs}
    if actual!=expected_outputs: raise PsbtError("unexpected output set")
    fee=proposal.fee()
    estimated_weight=len(proposal.tx.serialize())*4+2+109*len(proposal.inputs)
    vsize=(estimated_weight+3)//4
    if fee<=0 or fee>max_fee or fee/vsize>max_fee_rate: raise PsbtError("fee policy exceeded")
    digest=hashlib.sha256(proposal.serialize()).hexdigest()
    return proposal,{"proposalId":digest,"network":"bitcoin-mainnet","inputs":len(proposal.inputs),"outputs":outputs,"fee":fee,"estimatedVsize":vsize,"feeRate":fee/vsize}

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
