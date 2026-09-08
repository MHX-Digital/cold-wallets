import os
import re
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

    def test_preflight_binds_external_head_branch_main_and_checkpoint(self):
        script=Path("validation/windows/c8-preflight.ps1").read_text(encoding="utf-8").casefold()
        self.assertRegex(script,r"\[parameter\(mandatory=\$true\)\].*\$expectedhead")
        self.assertIn("$expectedmain = '5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f'",script)
        self.assertIn("$expectedbranch = 'audit/cold-wallet-security-architecture-20260907'",script)
        self.assertIn("audit_output\\54-c821-checksums.txt",script)
        self.assertNotIn("$checksumManifests = @('audit_output\\50-c81-checksums.txt'",script)
        self.assertNotIn("$checksumManifests = @('audit_output\\52-c82-checksums.txt'",script)
        self.assertNotIn("audit_output\\41-c72-checksums.txt",script)
        self.assertNotIn("5fdb89b362641931a67e41dc6a78d3c573d6edb1",script)
        for condition in ("audit branch mismatch","head mismatch","main/base mismatch","worktree must be clean","additional git worktree rejected","checkpoint checksum mismatch"):
            self.assertIn(condition,script)

    def test_preflight_manifest_paths_are_confined_and_unique(self):
        script=Path("validation/windows/c8-preflight.ps1").read_text(encoding="utf-8").casefold()
        for required in ("[system.io.path]::ispathrooted","getfullpath","startswith($rootprefix","reparse point rejected","duplicate checksum path rejected","empty checksum manifest rejected"):
            self.assertIn(required,script)

    def test_matrix_uses_only_owned_temp_root_and_offline_locks(self):
        script=Path("validation/windows/c8-python-matrix.ps1").read_text(encoding="utf-8").casefold()
        for required in ("requires native windows","--isolated","--no-index","--require-hashes","--no-build-isolation","^cold-wallets-c8-[0-9a-f]{32}$","finally"):
            self.assertIn(required,script)
        self.assertIn("remove-item -literalpath $runroot",script)
        self.assertNotIn("pip_cache_dir = $null",script)
        for prohibited in ("invoke-webrequest","curl ","docker ","tor.exe","bitcoind.exe"):
            self.assertNotIn(prohibited,script)

    def test_matrix_confines_locks_and_uses_exact_wheelhouse_manifest(self):
        script=Path("validation/windows/c8-python-matrix.ps1").read_text(encoding="utf-8").casefold()
        self.assertRegex(script,r"\[parameter\(mandatory=\$true\)\]\[string\]\$wheelhousemanifest")
        for required in ("lock outside repository requirements rejected","wheelhouse manifest must be inside repository requirements","cold-wallets.windows-wheelhouse","wheelhouse contains an unapproved or missing item","unapproved wheelhouse file rejected","wheelhouse hash mismatch"):
            self.assertIn(required,script)
        self.assertIn("$runtimeLockPath".casefold(),script)
        self.assertNotRegex(script,r"-r\s+\$(?:runtime|build|psbt)lock(?:\s|$)")

    def test_matrix_restores_environment_and_rejects_skips(self):
        script=Path("validation/windows/c8-python-matrix.ps1").read_text(encoding="utf-8").casefold()
        runbook=Path("validation/windows/C8-RUNBOOK.md").read_text(encoding="utf-8")
        for name in ("pip_no_index","pip_config_file","pip_index_url","pip_extra_index_url","http_proxy","https_proxy","all_proxy","no_proxy","pythondontwritebytecode"):
            self.assertIn(name,script)
        self.assertIn("$previousenvironment[$name]",script)
        self.assertIn("setenvironmentvariable($name, $previousenvironment[$name], 'process')",script)
        self.assertRegex(script,r"(?i)\[parameter\(mandatory=\$true\)\]\[validaterange\(1,10000\)\]\[int\]\$expectedtestcount")
        self.assertNotRegex(script,r"(?i)\$expectedtestcount\s*=\s*\d+")
        self.assertIn("$summaries.count -ne 1",script)
        self.assertIn("missing or ambiguous windows unittest summary",script)
        self.assertIn("unexpected windows test count",script)
        self.assertIn("relevant skips are not accepted",script)
        self.assertIn("test failures or errors are not accepted",script)
        self.assertIn("^cold-wallets-c8-[0-9a-f]{32}$",script)
        self.assertNotIn("79",runbook)
        self.assertNotIn("<C8.2_REMOTE_HEAD>",runbook)
        self.assertIn("-ExpectedHead '<HEAD FINAL PUBLICADO>'",runbook)
        self.assertIn("-ExpectedMain '5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f'",runbook)
        self.assertIn("manifest 54 authenticates the immutable historical manifests 50 and 52",runbook.casefold())
        self.assertEqual(runbook.count("-ExpectedTestCount 83"),3)
        for parameter in ("-PythonExecutable","-PythonVersion","-RuntimeLock","-BuildLock","-PsbtLock","-Wheelhouse","-WheelhouseManifest"):
            self.assertEqual(len(re.findall(rf"(?m)^\s+{re.escape(parameter)}(?:\s|$)",runbook)),3)


if __name__=="__main__": unittest.main()
