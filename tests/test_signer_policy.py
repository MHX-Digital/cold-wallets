import ast, unittest
from pathlib import Path
from coordinator.eth_envelope import proposal_id
from signer.ethereum import SigningError, SigningPolicy, independent_summary, sign

class Backend:
    address="0x"+"11"*20
    def address_for_key(self,key): return self.address
    def sign_type2(self,tx,key): return "0x02aa","0xhash",self.address

def envelope():
    e={"schema":"cold-wallets.eth-tx","version":1,"network":"ethereum-mainnet","chainId":"1","type":"2","from":Backend.address,"to":"0x"+"22"*20,"valueWei":"3","nonce":"0","gasLimit":"21000","maxFeePerGasWei":"100","maxPriorityFeePerGasWei":"2","data":"0x","createdAt":1,"expiresAt":2000000000,"sources":[]}; e["proposalId"]=proposal_id(e); return e

class SignerTests(unittest.TestCase):
    def test_confirmation_and_independent_costs(self):
        e=envelope(); summary=independent_summary(e,SigningPolicy(),now=2)
        self.assertEqual(summary["maxGasCostWei"],2100000); self.assertEqual(summary["maxTotalCostWei"],2100003)
        with self.assertRaises(SigningError): sign(e,"ephemeral",confirmation="wrong",backend=Backend(),now=2)
        out=sign(e,"ephemeral",confirmation=e["proposalId"],backend=Backend(),now=2)
        self.assertEqual(out["recoveredAddress"],e["from"]); self.assertNotIn("key",out)
    def test_key_fee_and_calldata_policies(self):
        e=envelope(); bad=Backend(); bad.address="0x"+"33"*20
        with self.assertRaises(SigningError): sign(e,"ephemeral",confirmation=e["proposalId"],backend=bad,now=2)
        e=envelope(); e["data"]="0x00"; e["proposalId"]=proposal_id(e)
        with self.assertRaises(SigningError): independent_summary(e,SigningPolicy(),now=2)
        e=envelope(); e["maxFeePerGasWei"]="500000000001"; e["proposalId"]=proposal_id(e)
        with self.assertRaises(SigningError): independent_summary(e,SigningPolicy(),now=2)
    def test_signer_imports_no_network_modules(self):
        tree=ast.parse(Path("signer/ethereum.py").read_text())
        names={a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names}
        names|={n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module}
        self.assertFalse(names & {"requests","socket","urllib","dashboard","broadcaster","transport"})

if __name__=="__main__": unittest.main()
