import tempfile, unittest, uuid
from pathlib import Path

from broadcaster.ethereum import EthereumBroadcastService
from broadcaster.store import BroadcastStore
from coordinator.disposable_store import DisposableStore
from coordinator.proposal_store import ProposalStore
from coordinator.rpc_identity import HeliosEvidence, RpcIdentity, classify
from coordinator.service import CoordinatorService, public_capabilities
from signer.ethereum import EthAccountBackend, sign
from transport.artifacts import write


class Rpc:
    def __init__(self): self.sends=0
    def send_raw(self,raw):
        from eth_utils import keccak
        self.sends+=1; return {"transactionHash":"0x"+keccak(bytes.fromhex(raw[2:])).hex()}
    def lookup_receipt(self,_hash): return {"status":1,"confirmed":True}


class CoordinatorFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try: from eth_account import Account
        except ImportError: raise unittest.SkipTest("hashed eth-account environment required")
        cls.key="0x"+"00"*31+"01"; cls.address=Account.from_key(cls.key).address
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix=f"cold-wallets-test-{uuid.uuid4().hex}-"); root=Path(self.temp.name)
        self.artifacts=root/"artifacts"; self.service=CoordinatorService(ProposalStore(root/"proposals.sqlite"),DisposableStore(root/"addresses.sqlite")); self.broadcast_store=BroadcastStore(root/"broadcast.sqlite")
    def tearDown(self): self.temp.cleanup()
    def test_complete_ethereum_artifact_flow_is_bound_and_idempotent(self):
        fields={"from":self.address,"to":"0x"+"22"*20,"valueWei":"3","nonce":"0","gasLimit":"21000","maxFeePerGasWei":"100","maxPriorityFeePerGasWei":"2","sources":[{"backend":"PUBLIC_RPC_UNVERIFIED","observedAt":1,"block":1}]}
        envelope=self.service.create_ethereum(fields,now=1); self.service.export_ethereum(self.artifacts,envelope["proposalId"],"proposal.cw-eth-proposal")
        signed=sign(envelope,self.key,confirmation=envelope["proposalId"],backend=EthAccountBackend(),now=2)
        write(self.artifacts,"signed.cw-eth-signed",signed); decoded=self.service.import_ethereum_signed(self.artifacts,"signed.cw-eth-signed",now=2)
        self.assertEqual(decoded["transactionHash"],signed["transactionHash"])
        rpc=Rpc(); broadcaster=EthereumBroadcastService(self.broadcast_store,rpc)
        self.assertEqual(self.service.register_ethereum(signed,broadcaster,now=2),"BROADCAST")
        self.assertEqual(self.service.register_ethereum(signed,broadcaster,now=2),"BROADCAST"); self.assertEqual(rpc.sends,1)
        persisted=(Path(self.temp.name)/"proposals.sqlite").read_bytes()
        self.assertNotIn(self.key.encode(),persisted)
    def test_disposable_lifecycle_and_rpc_identity(self):
        ident=self.service.disposable.add("synthetic-address","bitcoin","mainnet","keyref:opaque")
        reserved=self.service.reserve_address("request",now=1); self.assertEqual(reserved[0],ident)
        for state in ("PRESENTED","DETECTED","CONFIRMED","SWEEP_PREPARED","SWEPT"): self.assertEqual(self.service.advance_address(ident,state,now=2),state)
        self.assertEqual(classify(public_rpc=True),RpcIdentity.PUBLIC_RPC_UNVERIFIED)
        self.assertEqual(classify(public_rpc=False,helios=HeliosEvidence(expected_process=True)),RpcIdentity.HELIOS_UNATTESTED)
        self.assertEqual(classify(public_rpc=False,helios=HeliosEvidence(*([True]*8))),RpcIdentity.HELIOS_ATTESTED)
        self.assertFalse(public_capabilities()["broadcastEnabled"])


if __name__=="__main__": unittest.main()
