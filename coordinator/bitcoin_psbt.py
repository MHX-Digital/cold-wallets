"""Watch-only validation for the deliberately narrow Bitcoin PSBT scope."""
from __future__ import annotations
import base64, binascii, hashlib

MAX_PSBT_BYTES=1024*1024


class PsbtError(ValueError): pass


def _lib():
    try: from embit import networks,psbt
    except ImportError as exc: raise PsbtError("reviewed embit dependency is unavailable") from exc
    return networks,psbt


def inspect_psbt(encoded: str,*,network: str,expected_outputs: set[str],max_fee: int,max_fee_rate: int=1_000):
    networks,psbt=_lib()
    if network!="main": raise PsbtError("only Bitcoin mainnet is supported")
    try:
        raw=base64.b64decode(encoded,validate=True)
        if not raw.startswith(b"psbt\xff") or len(raw)>MAX_PSBT_BYTES: raise PsbtError("invalid PSBT size or magic")
        proposal=psbt.PSBT.parse(raw); proposal.verify()
        if proposal.serialize()!=raw: raise PsbtError("non-canonical or trailing PSBT data")
    except (psbt.PSBTError,ValueError,binascii.Error,IndexError,EOFError,PsbtError) as exc: raise PsbtError("invalid or unverifiable PSBT") from exc
    if proposal.version not in {None,0}: raise PsbtError("only PSBT v0 is supported")
    if any(getattr(item,"final_scriptsig",None) or getattr(item,"final_scriptwitness",None) for item in proposal.inputs): raise PsbtError("PSBT already finalized")
    for item in proposal.inputs:
        if item.utxo is None or item.non_witness_utxo is None: raise PsbtError("full prevout data required")
        if item.sighash_type not in {None,1}: raise PsbtError("only SIGHASH_ALL is allowed")
        if item.vout<0 or item.vout>=len(item.non_witness_utxo.vout): raise PsbtError("prevout index is invalid")
        prevout=item.non_witness_utxo.vout[item.vout]
        if item.txid!=item.non_witness_utxo.txid(): raise PsbtError("prevout transaction ID mismatch")
        if item.witness_utxo.serialize()!=prevout.serialize(): raise PsbtError("witness and non-witness UTXO mismatch")
        if item.witness_utxo.script_pubkey.script_type()!="p2wpkh": raise PsbtError("only native P2WPKH inputs are supported")
    net=networks.NETWORKS[network]; outputs=[]
    for output in proposal.tx.vout:
        try: address=output.script_pubkey.address(net)
        except Exception as exc: raise PsbtError("unsupported output script") from exc
        outputs.append({"address":address,"value":output.value})
    if len(outputs)!=1 or len(expected_outputs)!=1: raise PsbtError("send-all requires exactly one output")
    if {item["address"] for item in outputs}!=expected_outputs: raise PsbtError("unexpected output set")
    fee=proposal.fee(); estimated_weight=len(proposal.tx.serialize())*4+2+109*len(proposal.inputs); vsize=(estimated_weight+3)//4
    if fee<=0 or fee>max_fee or fee/vsize>max_fee_rate: raise PsbtError("fee policy exceeded")
    digest=hashlib.sha256(proposal.serialize()).hexdigest()
    return proposal,{"proposalId":digest,"network":"bitcoin-mainnet","inputs":len(proposal.inputs),"outputs":outputs,"fee":fee,"estimatedVsize":vsize,"feeRate":fee/vsize}
