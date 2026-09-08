"""Strict validation and recoverable broadcasting of signed EIP-1559 artifacts."""
from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Protocol

from broadcaster.store import BroadcastStateError, BroadcastStore
from coordinator.eth_envelope import validate


class EthereumBroadcastError(ValueError):
    pass


@dataclass(frozen=True)
class EthereumBroadcastPolicy:
    chain_id: int = 1
    max_gas_limit: int = 500_000
    max_fee_per_gas: int = 500_000_000_000
    max_total_cost: int = 10**20


class EthereumRemote(Protocol):
    def send_raw(self, raw_transaction: str) -> dict: ...
    def lookup_receipt(self, transaction_hash: str) -> dict | None: ...


def decode_signed(payload: dict, envelope: dict, policy: EthereumBroadcastPolicy, *, now: int | None = None) -> dict:
    required={"schema","version","chainId","proposalId","envelopeHash","rawTransaction","transactionHash","recoveredAddress"}
    if not isinstance(payload,dict) or set(payload)!=required: raise EthereumBroadcastError("signed artifact fields mismatch")
    validate(envelope,now=now)
    if payload["schema"]!="cold-wallets.eth-signed" or payload["version"]!=1: raise EthereumBroadcastError("unsupported signed artifact")
    if payload["chainId"]!=envelope["chainId"]: raise EthereumBroadcastError("signed artifact chain mismatch")
    if payload["proposalId"]!=envelope["proposalId"] or payload["envelopeHash"]!=envelope["proposalId"]: raise EthereumBroadcastError("proposal binding mismatch")
    raw_hex=payload["rawTransaction"]
    if not isinstance(raw_hex,str) or not raw_hex.startswith("0x"): raise EthereumBroadcastError("invalid raw transaction")
    try:
        raw=bytes.fromhex(raw_hex[2:])
        from eth_account import Account
        from eth_account.typed_transactions import TypedTransaction
        from eth_utils import keccak
        from hexbytes import HexBytes
        decoded=TypedTransaction.from_bytes(HexBytes(raw)).as_dict()
        recovered=Account.recover_transaction(raw)
    except Exception as exc: raise EthereumBroadcastError("invalid signed transaction") from exc
    transaction_hash="0x"+keccak(raw).hex()
    expected_to="0x"+bytes(decoded["to"]).hex()
    expected={"type":2,"chainId":int(envelope["chainId"]),"nonce":int(envelope["nonce"]),"value":int(envelope["valueWei"]),"gas":int(envelope["gasLimit"]),"maxFeePerGas":int(envelope["maxFeePerGasWei"]),"maxPriorityFeePerGas":int(envelope["maxPriorityFeePerGasWei"])}
    if any(decoded.get(key)!=value for key,value in expected.items()): raise EthereumBroadcastError("signed transaction differs from proposal")
    if expected_to.casefold()!=envelope["to"].casefold() or bytes(decoded["data"])!=bytes.fromhex(envelope["data"][2:]): raise EthereumBroadcastError("signed destination or calldata differs")
    if not isinstance(payload["recoveredAddress"],str) or recovered.casefold()!=envelope["from"].casefold() or payload["recoveredAddress"].casefold()!=recovered.casefold(): raise EthereumBroadcastError("sender recovery mismatch")
    if not isinstance(payload["transactionHash"],str) or payload["transactionHash"].casefold()!=transaction_hash.casefold(): raise EthereumBroadcastError("transaction hash mismatch")
    if expected["chainId"]!=policy.chain_id: raise EthereumBroadcastError("chain ID rejected")
    total=expected["value"]+expected["gas"]*expected["maxFeePerGas"]
    if expected["gas"]>policy.max_gas_limit or expected["maxFeePerGas"]>policy.max_fee_per_gas or total>policy.max_total_cost: raise EthereumBroadcastError("transaction policy exceeded")
    return {"transactionHash":transaction_hash,"from":recovered,"chainId":expected["chainId"],"nonce":expected["nonce"],"to":expected_to,"value":expected["value"],"rawTransaction":raw_hex}


class EthereumBroadcastService:
    def __init__(self, store: BroadcastStore, remote: EthereumRemote, policy: EthereumBroadcastPolicy=EthereumBroadcastPolicy()):
        self.store=store; self.remote=remote; self.policy=policy; self._lock=threading.RLock()

    def submit(self,payload: dict,envelope: dict,*,now: int|None=None):
        with self._lock:
            return self._submit_locked(payload,envelope,now=now)

    def _submit_locked(self,payload: dict,envelope: dict,*,now: int|None=None):
        tx=decode_signed(payload,envelope,self.policy,now=now); tx_hash=tx["transactionHash"]
        row=self.store.receive(tx_hash,"ethereum-mainnet","ethereum",envelope["proposalId"]); state=row[2]
        if state in {"BROADCAST","CONFIRMED","REPLACED","DROPPED","FAILED_TERMINAL"}: return state
        if state=="BROADCAST_UNKNOWN": return self.reconcile(tx_hash)
        if state=="RECEIVED": self.store.transition(tx_hash,"VALIDATED")
        self.store.transition(tx_hash,"BROADCASTING")
        try: response=self.remote.send_raw(tx["rawTransaction"])
        except (TimeoutError,ConnectionError):
            self.store.transition(tx_hash,"BROADCAST_UNKNOWN",last_error="remote outcome unknown"); return "BROADCAST_UNKNOWN"
        if not isinstance(response,dict):
            self.store.transition(tx_hash,"FAILED_RETRYABLE",last_error="invalid remote response"); return "FAILED_RETRYABLE"
        status=response.get("status"); remote_hash=response.get("transactionHash")
        if status=="already_known" or (isinstance(remote_hash,str) and remote_hash.casefold()==tx_hash.casefold()):
            self.store.transition(tx_hash,"BROADCAST",result="accepted"); return "BROADCAST"
        if remote_hash is not None:
            self.store.transition(tx_hash,"FAILED_TERMINAL",last_error="remote hash mismatch"); return "FAILED_TERMINAL"
        if status=="nonce_too_low":
            self.store.transition(tx_hash,"BROADCAST_UNKNOWN",last_error="nonce status requires reconciliation"); return "BROADCAST_UNKNOWN"
        if status=="replacement_underpriced":
            self.store.transition(tx_hash,"FAILED_RETRYABLE",last_error="replacement rejected"); return "FAILED_RETRYABLE"
        if status=="insufficient_funds":
            self.store.transition(tx_hash,"FAILED_TERMINAL",last_error="insufficient funds"); return "FAILED_TERMINAL"
        self.store.transition(tx_hash,"FAILED_RETRYABLE",last_error="remote rejected transaction"); return "FAILED_RETRYABLE"

    def reconcile(self,tx_hash: str):
        row=self.store.get(tx_hash)
        if not row or row[2] not in {"BROADCAST_UNKNOWN","BROADCAST","CONFIRMED"}: raise BroadcastStateError("operation cannot be reconciled")
        receipt=self.remote.lookup_receipt(tx_hash)
        if receipt is None: return row[2]
        if receipt.get("replaced"):
            self.store.transition(tx_hash,"REPLACED"); return "REPLACED"
        if receipt.get("dropped"):
            self.store.transition(tx_hash,"DROPPED"); return "DROPPED"
        if receipt.get("status")==0:
            target="FAILED_TERMINAL" if row[2]=="BROADCAST_UNKNOWN" else "DROPPED"
            self.store.transition(tx_hash,target,last_error="transaction reverted"); return target
        if row[2]=="BROADCAST_UNKNOWN": self.store.transition(tx_hash,"BROADCAST")
        current=self.store.get(tx_hash)[2]
        if receipt.get("confirmed") and current=="BROADCAST": self.store.transition(tx_hash,"CONFIRMED"); return "CONFIRMED"
        return self.store.get(tx_hash)[2]
