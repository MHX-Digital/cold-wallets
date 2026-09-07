"""Watch-only application services; signing is structurally absent."""
from __future__ import annotations
import time
from pathlib import Path

from broadcaster.ethereum import EthereumBroadcastPolicy, EthereumBroadcastService, decode_signed
from coordinator.disposable_store import DisposableStore
from coordinator.eth_envelope import proposal_id, validate
from coordinator.proposal_store import ProposalStore
from coordinator.rpc_identity import RpcIdentity
from transport import artifacts


def public_capabilities() -> dict[str,object]:
    return {"role":"online-watch-only-coordinator","workflow":["PREPARE","REVIEW","EXPORT","SIGN_OFFLINE","IMPORT","VALIDATE","TRANSMIT","TRACK"],"broadcastEnabled":False,"broadcastReason":"real broadcast remains disabled pending controlled validation","rpcIdentity":RpcIdentity.PUBLIC_RPC_UNVERIFIED.value,"bitcoinScope":"mainnet PSBT v0 native P2WPKH SIGHASH_ALL send-all","bitcoinSigningEnabled":False}


class CoordinatorService:
    def __init__(self,proposal_store: ProposalStore,disposable_store: DisposableStore):
        self.proposals=proposal_store; self.disposable=disposable_store
    def create_ethereum(self,fields: dict,*,now: int|None=None,ttl: int=900):
        created=int(time.time()) if now is None else now
        envelope={"schema":"cold-wallets.eth-tx","version":1,"network":"ethereum-mainnet","chainId":"1","type":"2","from":fields["from"],"to":fields["to"],"valueWei":fields["valueWei"],"nonce":fields["nonce"],"gasLimit":fields["gasLimit"],"maxFeePerGasWei":fields["maxFeePerGasWei"],"maxPriorityFeePerGasWei":fields["maxPriorityFeePerGasWei"],"data":fields.get("data","0x"),"createdAt":created,"expiresAt":created+ttl,"sources":fields.get("sources",[])}
        envelope["proposalId"]=proposal_id(envelope); validate(envelope,now=created); self.proposals.create(envelope); return envelope
    def export_ethereum(self,root: Path,proposal_id_value: str,name: str):
        envelope,_,_=self.proposals.get(proposal_id_value); return artifacts.write(root,name,envelope)
    def import_ethereum_signed(self,root: Path,name: str,*,now: int|None=None,policy: EthereumBroadcastPolicy=EthereumBroadcastPolicy()):
        signed=artifacts.read(root,name,expected_schema="cold-wallets.eth-signed"); envelope,_,_=self.proposals.get(signed["proposalId"])
        decoded=decode_signed(signed,envelope,policy,now=now); self.proposals.attach_signed(signed["proposalId"],decoded["transactionHash"]); return decoded
    def register_ethereum(self,signed: dict,broadcaster: EthereumBroadcastService,*,now: int|None=None):
        envelope,state,tx_hash=self.proposals.get(signed["proposalId"])
        if state!="SIGNED_VALIDATED" or tx_hash!=signed["transactionHash"]: raise ValueError("signed artifact was not validated")
        return broadcaster.submit(signed,envelope,now=now)
    def reserve_address(self,request_id: str,*,ttl: int=300,now: int|None=None): return self.disposable.reserve(request_id,ttl=ttl,now=now)
    def advance_address(self,address_id: str,new_state: str,*,now: int|None=None): return self.disposable.transition(address_id,new_state,now=now)
