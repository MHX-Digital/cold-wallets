import tempfile, threading, unittest, uuid
from pathlib import Path

from broadcaster.ethereum import EthereumBroadcastError, EthereumBroadcastService
from broadcaster.store import BroadcastStore
from coordinator.eth_envelope import proposal_id
from signer.ethereum import EthAccountBackend, sign


class FakeRpc:
    def __init__(self,response=None,receipt=None): self.response=response; self.receipt=receipt; self.sends=0
    def send_raw(self,_raw):
        self.sends+=1
        if self.response is TimeoutError: raise TimeoutError
        if self.response is ConnectionError: raise ConnectionError
        return self.response
    def lookup_receipt(self,_hash): return self.receipt


class EthereumBroadcasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try: from eth_account import Account
        except ImportError: raise unittest.SkipTest("hashed eth-account environment required")
        cls.key="0x"+"00"*31+"01"; cls.address=Account.from_key(cls.key).address
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix=f"cold-wallets-test-{uuid.uuid4().hex}-")
        self.path=Path(self.temp.name)/"broadcast.sqlite"
        self.envelope={"schema":"cold-wallets.eth-tx","version":1,"network":"ethereum-mainnet","chainId":"1","type":"2","from":self.address,"to":"0x"+"22"*20,"valueWei":"3","nonce":"0","gasLimit":"21000","maxFeePerGasWei":"100","maxPriorityFeePerGasWei":"2","data":"0x","createdAt":1,"expiresAt":2000000000,"sources":[]}
        self.envelope["proposalId"]=proposal_id(self.envelope)
        self.signed=sign(self.envelope,self.key,confirmation=self.envelope["proposalId"],backend=EthAccountBackend(),now=2)
    def tearDown(self): self.temp.cleanup()
    def service(self,rpc): return EthereumBroadcastService(BroadcastStore(self.path),rpc)
    def test_accept_duplicate_and_concurrent_requests(self):
        rpc=FakeRpc({"transactionHash":self.signed["transactionHash"]}); service=self.service(rpc); results=[]
        threads=[threading.Thread(target=lambda:results.append(service.submit(self.signed,self.envelope,now=2))) for _ in range(2)]
        [thread.start() for thread in threads]; [thread.join() for thread in threads]
        self.assertEqual(results,["BROADCAST","BROADCAST"]); self.assertEqual(rpc.sends,1)
    def test_unknown_requires_reconciliation_and_survives_restart(self):
        rpc=FakeRpc(TimeoutError); service=self.service(rpc)
        self.assertEqual(service.submit(self.signed,self.envelope,now=2),"BROADCAST_UNKNOWN")
        rpc.receipt={"status":1,"confirmed":True}
        restarted=self.service(rpc)
        self.assertEqual(restarted.submit(self.signed,self.envelope,now=2),"CONFIRMED"); self.assertEqual(rpc.sends,1)
    def test_already_known_terminal_and_retryable_classification(self):
        self.assertEqual(self.service(FakeRpc({"status":"already_known"})).submit(self.signed,self.envelope,now=2),"BROADCAST")
        for status,expected in (("insufficient_funds","FAILED_TERMINAL"),("replacement_underpriced","FAILED_RETRYABLE")):
            path=Path(self.temp.name)/f"{status}.sqlite"; service=EthereumBroadcastService(BroadcastStore(path),FakeRpc({"status":status}))
            self.assertEqual(service.submit(self.signed,self.envelope,now=2),expected)
    def test_mutation_chain_and_remote_hash_mismatch_fail_closed(self):
        mutated=dict(self.envelope); mutated["to"]="0x"+"33"*20; mutated["proposalId"]=proposal_id(mutated)
        with self.assertRaises(EthereumBroadcastError): self.service(FakeRpc()).submit(self.signed,mutated,now=2)
        malformed=dict(self.signed); malformed["rawTransaction"]="0x02ff"
        with self.assertRaises(EthereumBroadcastError): self.service(FakeRpc()).submit(malformed,self.envelope,now=2)
        wrong_chain=dict(self.signed); wrong_chain["chainId"]="2"
        with self.assertRaises(EthereumBroadcastError): self.service(FakeRpc()).submit(wrong_chain,self.envelope,now=2)
        self.assertEqual(self.service(FakeRpc({"transactionHash":"0x"+"00"*32})).submit(self.signed,self.envelope,now=2),"FAILED_TERMINAL")
    def test_replaced_dropped_reverted_and_reorg_states(self):
        for receipt,expected in (({"replaced":True},"REPLACED"),({"dropped":True},"DROPPED"),({"status":0},"FAILED_TERMINAL")):
            path=Path(self.temp.name)/(expected+".sqlite"); rpc=FakeRpc(TimeoutError,receipt); service=EthereumBroadcastService(BroadcastStore(path),rpc)
            service.submit(self.signed,self.envelope,now=2); self.assertEqual(service.reconcile(self.signed["transactionHash"]),expected)


if __name__=="__main__": unittest.main()
