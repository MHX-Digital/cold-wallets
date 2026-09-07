import unittest
from signer.bitcoin_psbt import PsbtError, inspect_psbt, sign_psbt

class PsbtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try: from embit import ec,script,transaction,psbt
        except ImportError: raise unittest.SkipTest("hashed embit environment required")
        cls.secret=bytes.fromhex("01"*32); key=ec.PrivateKey(cls.secret); dest=ec.PrivateKey(bytes.fromhex("02"*32))
        coinbase=transaction.TransactionInput(bytes(32),0xffffffff)
        prev=transaction.Transaction(vin=[coinbase],vout=[transaction.TransactionOutput(100000,script.p2wpkh(key.get_public_key()))])
        tx=transaction.Transaction(vin=[transaction.TransactionInput(prev.txid(),0)],vout=[transaction.TransactionOutput(99000,script.p2wpkh(dest.get_public_key()))])
        proposal=psbt.PSBT(tx); proposal.inputs[0].witness_utxo=prev.vout[0]; proposal.inputs[0].non_witness_utxo=prev
        cls.encoded=proposal.to_string(); cls.destination=tx.vout[0].script_pubkey.address()
    def test_validate_sign_finalize_and_zeroize(self):
        _,summary=inspect_psbt(self.encoded,network="main",expected_outputs={self.destination},max_fee=1000)
        secret=bytearray(self.secret); result=sign_psbt(self.encoded,secret,confirmation=summary["proposalId"],network="main",expected_outputs={self.destination},max_fee=1000)
        self.assertTrue(result["rawTransaction"]); self.assertEqual(secret,bytearray(32)); self.assertNotIn("key",result)
    def test_wrong_output_fee_confirmation_and_key(self):
        _,summary=inspect_psbt(self.encoded,network="main",expected_outputs={self.destination},max_fee=1000)
        for kwargs in ({"expected_outputs":{"bad"},"max_fee":1000},{"expected_outputs":{self.destination},"max_fee":999}):
            with self.assertRaises(PsbtError): inspect_psbt(self.encoded,network="main",**kwargs)
        with self.assertRaises(PsbtError): sign_psbt(self.encoded,bytearray(self.secret),confirmation="bad",network="main",expected_outputs={self.destination},max_fee=1000)
        with self.assertRaises(PsbtError): sign_psbt(self.encoded,bytearray(bytes.fromhex("03"*32)),confirmation=summary["proposalId"],network="main",expected_outputs={self.destination},max_fee=1000)
    def test_truncated_and_network_rejected(self):
        with self.assertRaises(PsbtError): inspect_psbt(self.encoded[:-5],network="main",expected_outputs={self.destination},max_fee=1000)
        with self.assertRaises(PsbtError): inspect_psbt(self.encoded,network="unknown",expected_outputs={self.destination},max_fee=1000)

if __name__=="__main__": unittest.main()
