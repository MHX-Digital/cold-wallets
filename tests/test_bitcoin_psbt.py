import unittest
from signer.bitcoin_psbt import PsbtError, inspect_psbt, sign_psbt
from bitcoin_backend import diagnose

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
    def test_validate_and_signing_is_fail_closed_for_unapproved_backend(self):
        _,summary=inspect_psbt(self.encoded,network="main",expected_outputs={self.destination},max_fee=1000)
        diagnostic=diagnose()
        self.assertEqual(diagnostic.backend_type,"native")
        self.assertEqual(diagnostic.artifact_sha256,"602c643b17d7d863e801d4a4eca12711b2724698d0e2d822711fd724cf9b74c1")
        self.assertFalse(diagnostic.signing_enabled)
        secret=bytearray(self.secret)
        with self.assertRaisesRegex(PsbtError,"not approved"):
            sign_psbt(self.encoded,secret,confirmation=summary["proposalId"],network="main",expected_outputs={self.destination},max_fee=1000)
    def test_wrong_output_fee_confirmation_and_key(self):
        _,summary=inspect_psbt(self.encoded,network="main",expected_outputs={self.destination},max_fee=1000)
        for kwargs in ({"expected_outputs":{"bad"},"max_fee":1000},{"expected_outputs":{self.destination},"max_fee":999}):
            with self.assertRaises(PsbtError): inspect_psbt(self.encoded,network="main",**kwargs)
        with self.assertRaises(PsbtError): sign_psbt(self.encoded,bytearray(self.secret),confirmation="bad",network="main",expected_outputs={self.destination},max_fee=1000)
    def test_truncated_and_network_rejected(self):
        with self.assertRaises(PsbtError): inspect_psbt(self.encoded[:-5],network="main",expected_outputs={self.destination},max_fee=1000)
        with self.assertRaises(PsbtError): inspect_psbt(self.encoded,network="unknown",expected_outputs={self.destination},max_fee=1000)

    def test_zero_fee_extra_output_and_inconsistent_prevout_rejected(self):
        from embit import ec,psbt,script,transaction
        key=ec.PrivateKey(self.secret); destination=ec.PrivateKey(bytes.fromhex("02"*32))
        previous=transaction.Transaction(vin=[transaction.TransactionInput(bytes(32),0xffffffff)],vout=[transaction.TransactionOutput(100000,script.p2wpkh(key.get_public_key()))])
        for values in ([100000],[98000,1000]):
            outputs=[transaction.TransactionOutput(value,script.p2wpkh(destination.get_public_key())) for value in values]
            proposal=psbt.PSBT(transaction.Transaction(vin=[transaction.TransactionInput(previous.txid(),0)],vout=outputs))
            proposal.inputs[0].witness_utxo=previous.vout[0]; proposal.inputs[0].non_witness_utxo=previous
            with self.assertRaises(PsbtError): inspect_psbt(proposal.to_string(),network="main",expected_outputs={self.destination},max_fee=5000)
        proposal=psbt.PSBT.from_string(self.encoded)
        proposal.inputs[0].witness_utxo=transaction.TransactionOutput(99999,proposal.inputs[0].witness_utxo.script_pubkey)
        with self.assertRaises(PsbtError): inspect_psbt(proposal.to_string(),network="main",expected_outputs={self.destination},max_fee=1000)

if __name__=="__main__": unittest.main()
