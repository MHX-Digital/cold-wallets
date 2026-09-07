import os
import unittest
from pathlib import Path
from unittest.mock import patch

from dashboard import server


class WindowsValidationHarnessTests(unittest.TestCase):
    def test_dashboard_port_is_explicit_and_bounded(self):
        with patch.dict(os.environ,{"COLD_WALLETS_PORT":"49152"}):
            self.assertEqual(server._configured_port(),49152)
        for invalid in ("0","65536","not-a-port"):
            with self.subTest(invalid=invalid),patch.dict(os.environ,{"COLD_WALLETS_PORT":invalid}):
                with self.assertRaises(SystemExit): server._configured_port()

    def test_launcher_requires_an_explicit_virtualenv(self):
        launcher=Path("start.bat").read_text(encoding="utf-8").casefold()
        self.assertIn("if not defined cold_wallets_python",launcher)
        self.assertIn("sys.prefix != sys.base_prefix",launcher)
        self.assertIn("cold_wallets_port",launcher)
        self.assertNotIn("set \"python=python\"",launcher)

    def test_preflight_is_read_only_and_redacted(self):
        script=Path("validation/windows/c8-preflight.ps1").read_text(encoding="utf-8").casefold()
        self.assertIn("native windows",script)
        self.assertIn("get-maskedidentifier",script)
        for prohibited in ("new-item","remove-item","set-acl","stop-process","start-process","invoke-webrequest"):
            self.assertNotIn(prohibited,script)

    def test_matrix_uses_only_owned_temp_root_and_offline_locks(self):
        script=Path("validation/windows/c8-python-matrix.ps1").read_text(encoding="utf-8").casefold()
        for required in ("--no-index","--require-hashes","--no-build-isolation","cold-wallets-c8-*","finally"):
            self.assertIn(required,script)
        self.assertIn("remove-item -literalpath $runroot",script)
        self.assertNotIn("pip_cache_dir = $null",script)
        for prohibited in ("invoke-webrequest","curl ","docker ","tor.exe","bitcoind.exe"):
            self.assertNotIn(prohibited,script)


if __name__=="__main__": unittest.main()
