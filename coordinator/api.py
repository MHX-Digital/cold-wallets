"""Strict watch-only API facade. It has no signer or remote broadcast dependency."""
from __future__ import annotations
import hashlib,json,threading
from broadcaster.store import BroadcastStore
from coordinator.service import CoordinatorService,public_capabilities
from transport.artifacts import pack,unpack

class ApiError(ValueError): pass

class WatchOnlyApi:
    def __init__(self,service: CoordinatorService,broadcast_store: BroadcastStore):
        self.service=service; self.broadcasts=broadcast_store; self._lock=threading.RLock()
    def _once(self,key,operation,payload,callback):
        if not isinstance(key,str) or not (16<=len(key)<=128): raise ApiError("valid Idempotency-Key required")
        digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest(); identity=(key,operation)
        with self._lock:
            prior=self.service.proposals.get_idempotent(*identity)
            if prior:
                if prior[0]!=digest: raise ApiError("idempotency key reused with different payload")
                return prior[1]
            result=callback(); self.service.proposals.put_idempotent(key,operation,digest,result); return result
    def create_ethereum(self,payload,key):
        allowed={"from","to","valueWei","nonce","gasLimit","maxFeePerGasWei","maxPriorityFeePerGasWei","data","sources","confirmNetwork"}
        if not isinstance(payload,dict) or set(payload)!=allowed or payload["confirmNetwork"]!="ethereum-mainnet": raise ApiError("Ethereum request schema mismatch")
        fields={name:value for name,value in payload.items() if name!="confirmNetwork"}
        return self._once(key,"create-ethereum",payload,lambda:self.service.create_ethereum(fields))
    def get_proposal(self,proposal_id):
        envelope,state,tx_hash=self.service.proposals.get(proposal_id)
        return {"proposal":envelope,"state":state,"transactionHash":tx_hash}
    def export(self,payload,key):
        if not isinstance(payload,dict) or set(payload)!={"proposalId"}: raise ApiError("export schema mismatch")
        return self._once(key,"export",payload,lambda:pack(self.service.proposals.get(payload["proposalId"])[0]))
    def import_signed(self,payload,key):
        if not isinstance(payload,dict) or set(payload)!={"artifact"}: raise ApiError("import schema mismatch")
        signed=unpack(payload["artifact"],expected_schema="cold-wallets.eth-signed")
        def perform():
            decoded=self.service.import_ethereum_signed_payload(signed)
            return {name:decoded[name] for name in ("transactionHash","from","chainId","nonce","to","value")}
        return self._once(key,"import",payload,perform)
    def register_local(self,payload,key):
        if not isinstance(payload,dict) or set(payload)!={"proposalId"}: raise ApiError("register schema mismatch")
        def perform():
            envelope,state,tx_hash=self.service.proposals.get(payload["proposalId"])
            if state!="SIGNED_VALIDATED" or not tx_hash: raise ApiError("proposal is not validated")
            row=self.broadcasts.receive(tx_hash,envelope["network"],"ethereum",payload["proposalId"])
            if row[2]=="RECEIVED": self.broadcasts.transition(tx_hash,"VALIDATED")
            return {"transactionHash":tx_hash,"state":self.broadcasts.get(tx_hash)[2],"remoteBroadcast":False}
        return self._once(key,"register-local",payload,perform)
    def get_broadcast(self,tx_hash):
        row=self.broadcasts.details(tx_hash)
        if not row: raise ApiError("unknown broadcast operation")
        return {"transactionHash":row[0],"network":row[1],"state":row[2],"attempts":row[3],"protocol":row[4],"proposalId":row[5],"uncertain":bool(row[8])}
    def reserve(self,payload,key):
        if not isinstance(payload,dict) or set(payload)!={"requestId"}: raise ApiError("reserve schema mismatch")
        row=self._once(key,"reserve",payload,lambda:self.service.reserve_address(payload["requestId"]))
        return {"id":row[0],"address":row[1],"protocol":row[2],"network":row[3],"state":row[5]}
    def get_disposable(self,identifier):
        return self.service.disposable.get(identifier)
    def status(self): return public_capabilities()
