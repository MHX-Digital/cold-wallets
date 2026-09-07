import time, unittest
from coordinator.eth_envelope import EnvelopeError, proposal_id, validate

class EnvelopeTests(unittest.TestCase):
    def base(self):
        e={"schema":"cold-wallets.eth-tx","version":1,"network":"ethereum-mainnet","chainId":"1","type":"2","from":"0x"+"11"*20,"to":"0x"+"22"*20,"valueWei":"0","nonce":"0","gasLimit":"21000","maxFeePerGasWei":"100","maxPriorityFeePerGasWei":"2","data":"0x","createdAt":1,"expiresAt":2000000000,"sources":[]}
        e["proposalId"]=proposal_id(e); return e
    def test_valid_and_mutation_rejected(self):
        e=self.base(); self.assertIs(validate(e, now=2), e)
        e["to"]="0x"+"33"*20
        with self.assertRaises(EnvelopeError): validate(e, now=2)
    def test_strict_values(self):
        for key,val in (("chainId",1),("valueWei","01"),("type","1"),("data","0X00"),("maxPriorityFeePerGasWei","101")):
            e=self.base(); e[key]=val
            with self.assertRaises(EnvelopeError): validate(e, now=2)
    def test_unknown_missing_expired(self):
        e=self.base(); e["extra"]=1
        with self.assertRaises(EnvelopeError): validate(e, now=2)
        e=self.base(); e["expiresAt"]=1; e["proposalId"]=proposal_id(e)
        with self.assertRaises(EnvelopeError): validate(e, now=2)

if __name__ == "__main__": unittest.main()
