"""Offline Ethereum signer policy. No network modules are imported."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from coordinator.eth_envelope import proposal_id, validate

class SigningError(ValueError): pass
class CryptoBackend(Protocol):
    def address_for_key(self,key: str)->str: ...
    def sign_type2(self,transaction: dict,key: str)->tuple[str,str,str]: ...

@dataclass(frozen=True)
class SigningPolicy:
    chain_id: int=1
    max_gas_limit: int=500_000
    max_fee_per_gas: int=500_000_000_000
    max_total_cost: int=10**20
    allow_calldata: bool=False

def independent_summary(envelope: dict,policy: SigningPolicy,now: int|None=None):
    validate(envelope,now=now)
    if int(envelope["chainId"])!=policy.chain_id: raise SigningError("chain ID rejected")
    gas=int(envelope["gasLimit"]); fee=int(envelope["maxFeePerGasWei"]); value=int(envelope["valueWei"])
    if gas>policy.max_gas_limit or fee>policy.max_fee_per_gas: raise SigningError("fee policy exceeded")
    if envelope["data"]!="0x" and not policy.allow_calldata: raise SigningError("calldata rejected")
    gas_cost=gas*fee; total=value+gas_cost
    if total>policy.max_total_cost: raise SigningError("total cost policy exceeded")
    return {"proposalId":proposal_id(envelope),"network":envelope["network"],"from":envelope["from"],"to":envelope["to"],"valueWei":value,"nonce":int(envelope["nonce"]),"maxGasCostWei":gas_cost,"maxTotalCostWei":total,"calldata":envelope["data"]!="0x"}

def sign(envelope: dict,key: str,*,confirmation: str,backend: CryptoBackend,policy: SigningPolicy=SigningPolicy(),now: int|None=None):
    summary=independent_summary(envelope,policy,now)
    if confirmation!=summary["proposalId"]: raise SigningError("confirmation does not match proposal")
    expected=backend.address_for_key(key)
    if expected.casefold()!=envelope["from"].casefold(): raise SigningError("key does not match sender")
    transaction={"type":2,"chainId":policy.chain_id,"nonce":summary["nonce"],"to":envelope["to"],"value":summary["valueWei"],"gas":int(envelope["gasLimit"]),"maxFeePerGas":int(envelope["maxFeePerGasWei"]),"maxPriorityFeePerGas":int(envelope["maxPriorityFeePerGasWei"]),"data":envelope["data"]}
    raw,tx_hash,recovered=backend.sign_type2(transaction,key)
    if recovered.casefold()!=expected.casefold(): raise SigningError("signature recovery mismatch")
    return {"schema":"cold-wallets.eth-signed","version":1,"chainId":str(policy.chain_id),"proposalId":summary["proposalId"],"envelopeHash":summary["proposalId"],"rawTransaction":raw,"transactionHash":tx_hash,"recoveredAddress":recovered}
