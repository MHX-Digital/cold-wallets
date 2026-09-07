import unittest

from cold_wallets.address_validation import validate_btc_address


class BitcoinAddressValidationTests(unittest.TestCase):
    def assert_valid(self, address):
        valid, message = validate_btc_address(address)
        self.assertTrue(valid, message)

    def assert_invalid(self, address):
        valid, _ = validate_btc_address(address)
        self.assertFalse(valid)

    def test_known_mainnet_base58check_vectors(self):
        self.assert_valid("1BoatSLRHtKNngkdXEeobR76b53LETtpyT")
        self.assert_valid("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy")

    def test_base58check_checksum_mutation_is_rejected(self):
        self.assert_invalid("1BoatSLRHtKNngkdXEeobR76b53LETtpyU")

    def test_testnet_base58_is_rejected(self):
        self.assert_invalid("mipcBbFg9gMiCh81Kj8tqqdgoZub1ZJRfn")
        self.assert_invalid("2N2JD6wb56AfK4tfmM6PwdVmoYk2dCKf4Br")

    def test_known_bip84_mainnet_vector(self):
        self.assert_valid("bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu")

    def test_segwit_mixed_case_and_checksum_mutation_are_rejected(self):
        self.assert_invalid("bc1Qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu")
        self.assert_invalid("bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyq")

    def test_non_mainnet_segwit_hrp_is_rejected(self):
        self.assert_invalid("tb1qfm7hyk4g9h4a7u7v8z9uf4t4hkr4tq0j6v3x9a")

    def test_malformed_and_non_string_values_are_rejected(self):
        for value in (None, "", 1, "bc1q", "1O0Il"):
            with self.subTest(value=value):
                self.assert_invalid(value)


if __name__ == "__main__":
    unittest.main()
