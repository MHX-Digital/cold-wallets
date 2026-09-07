"""Recoverable Bitcoin broadcaster using reimport strategy; no raw tx persisted."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from broadcaster.store import BroadcastStateError, BroadcastStore, bitcoin_txid

class Remote(Protocol):
    def send(self,raw_hex: str)->dict: ...
    def lookup(self,tx_hash: str)->str: ...

@dataclass(frozen=True)
class BroadcastResult:
    tx_hash: str
    state: str

class BroadcastService:
    def __init__(self,store: BroadcastStore,remote: Remote): self.store=store; self.remote=remote
    def submit_bitcoin(self,raw_hex: str,proposal_id: str)->BroadcastResult:
        tx_hash=bitcoin_txid(raw_hex); row=self.store.receive_bitcoin(raw_hex,proposal_id=proposal_id)
        state=row[2]
        if state in {"BROADCAST","CONFIRMED"}: return BroadcastResult(tx_hash,state)
        if state=="BROADCAST_UNKNOWN": return self.reconcile_bitcoin(raw_hex)
        if state=="RECEIVED": self.store.transition(tx_hash,"VALIDATED")
        self.store.transition(tx_hash,"BROADCASTING")
        try: response=self.remote.send(raw_hex)
        except TimeoutError:
            self.store.transition(tx_hash,"BROADCAST_UNKNOWN"); return BroadcastResult(tx_hash,"BROADCAST_UNKNOWN")
        if not isinstance(response,dict): self.store.transition(tx_hash,"FAILED_RETRYABLE"); return BroadcastResult(tx_hash,"FAILED_RETRYABLE")
        if response.get("status")=="already_known" or response.get("tx_hash")==tx_hash:
            self.store.transition(tx_hash,"BROADCAST"); return BroadcastResult(tx_hash,"BROADCAST")
        if response.get("terminal"): self.store.transition(tx_hash,"FAILED_TERMINAL"); return BroadcastResult(tx_hash,"FAILED_TERMINAL")
        self.store.transition(tx_hash,"FAILED_RETRYABLE"); return BroadcastResult(tx_hash,"FAILED_RETRYABLE")
    def reconcile_bitcoin(self,raw_hex: str)->BroadcastResult:
        tx_hash=bitcoin_txid(raw_hex); row=self.store.get(tx_hash)
        if not row or row[2]!="BROADCAST_UNKNOWN": raise BroadcastStateError("operation is not uncertain")
        result=self.remote.lookup(tx_hash)
        if result in {"known","confirmed"}: self.store.transition(tx_hash,"BROADCAST"); return BroadcastResult(tx_hash,"BROADCAST")
        if result=="absent": self.store.transition(tx_hash,"FAILED_RETRYABLE"); return BroadcastResult(tx_hash,"FAILED_RETRYABLE")
        return BroadcastResult(tx_hash,"BROADCAST_UNKNOWN")
