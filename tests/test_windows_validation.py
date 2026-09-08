import os
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from dashboard import server


EXPECTED_C91_TEST_COUNT = 89


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
        for prohibited in ("new-item","remove-item","set-acl","stop-process","start-process","invoke-webrequest","invoke-restmethod"):
            self.assertNotIn(prohibited,script)

    def test_preflight_binds_external_head_branch_main_and_checkpoint(self):
        script=Path("validation/windows/c8-preflight.ps1").read_text(encoding="utf-8").casefold()
        self.assertRegex(script,r"\[parameter\(mandatory=\$true\)\].*\$expectedhead")
        self.assertRegex(script,r"\[parameter\(mandatory=\$false\)\].*\$expectedbranch\s*=\s*'main'")
        self.assertIn("$expectedrepositoryurl = 'https://github.com/mhx-digital/cold-wallets.git'",script)
        self.assertIn("git@github.com:mhx-digital/cold-wallets.git",script)
        self.assertIn("$operationalchecksummanifest = 'audit_output\\59-c91-checksums.txt'",script)
        self.assertIn("$checksummanifests = @($operationalchecksummanifest)",script)
        for required in ("refs/heads/main","refs/remotes/origin/main","expectedheadlower","originmain"):
            self.assertIn(required,script)
        self.assertNotIn("$expectedmain",script)
        self.assertNotIn("5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f",script)
        self.assertNotIn("audit/cold-wallet-security-architecture-20260907",script)
        self.assertNotIn("5fdb89b362641931a67e41dc6a78d3c573d6edb1",script)
        self.assertNotIn("$checksummanifests = @('audit_output\\57-c9-checksums.txt')",script)
        for condition in ("expected branch mismatch","head mismatch","local main mismatch","origin/main mismatch","worktree must be clean","additional git worktree rejected","operational checksum mismatch"):
            self.assertIn(condition,script)

    def test_preflight_rejects_detached_bad_remote_dirty_missing_and_divergent_origin(self):
        script=Path("validation/windows/c8-preflight.ps1").read_text(encoding="utf-8").casefold()
        for required in (
            "'symbolic-ref', '--quiet', '--short', 'head'",
            "detached head rejected",
            "origin remote mismatch",
            "origin/main is missing",
            "origin/main mismatch",
            "'status', '--porcelain=v1', '--untracked-files=all'",
            "'worktree', 'list', '--porcelain'",
            "additional git worktree rejected",
        ):
            self.assertIn(required,script)
        for prohibited in ("'fetch'","git fetch","git pull","git clone","git clean","reset --hard"):
            self.assertNotIn(prohibited,script)

    def test_preflight_uses_git_blobs_for_operational_manifest_and_marks_57_historical(self):
        script=Path("validation/windows/c8-preflight.ps1").read_text(encoding="utf-8").casefold()
        self.assertIn("get-gitblobsha256",script)
        self.assertIn("'cat-file', 'blob'",script)
        self.assertNotIn("get-filehash",script)
        self.assertIn("historicalchecksummanifests = @('audit_output/57-c9-checksums.txt')",script)

    def test_preflight_manifest_paths_are_confined_and_unique(self):
        script=Path("validation/windows/c8-preflight.ps1").read_text(encoding="utf-8").casefold()
        for required in ("[system.io.path]::ispathrooted","getfullpath","startswith($rootprefix","reparse point rejected","duplicate checksum path rejected","empty checksum manifest rejected"):
            self.assertIn(required,script)

    def test_c91_report_and_manifest_authenticate_operational_chain(self):
        report=Path("audit_output/58-c91-windows-main-handoff.md").read_text(encoding="utf-8").casefold()
        manifest_path=Path("audit_output/59-c91-checksums.txt")
        manifest=manifest_path.read_text(encoding="utf-8")
        self.assertIn("manifest 59 is the operational checksum manifest",report)
        self.assertIn("manifest 57 is historical evidence",report)
        required_paths=(
            "audit_output/57-c9-checksums.txt",
            "audit_output/58-c91-windows-main-handoff.md",
            ".github/workflows/ci.yml",
            "CHANGELOG.md",
            "broadcaster/store.py",
            "coordinator/proposal_store.py",
            "coordinator/disposable_store.py",
            "validation/windows/c8-preflight.ps1",
            "validation/windows/C8-RUNBOOK.md",
            "tests/test_bitcoin_psbt.py",
            "tests/test_governance.py",
            "tests/test_windows_validation.py",
        )
        paths=[]
        for line in manifest.splitlines():
            match=re.fullmatch(r"([0-9a-f]{64})  (.+)",line)
            self.assertIsNotNone(match,line)
            paths.append(match.group(2))
        self.assertEqual(len(paths),len(set(paths)))
        self.assertNotIn("audit_output/59-c91-checksums.txt",paths)
        for path in required_paths:
            self.assertIn(path,paths)

    def test_workflow_validates_operational_manifest_59_without_deploy_surface(self):
        workflow=Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("sha256sum -c audit_output/59-c91-checksums.txt",workflow)
        self.assertNotIn("sha256sum -c audit_output/57-c9-checksums.txt",workflow)
        self.assertIn(f'EXPECTED_TEST_COUNT: "{EXPECTED_C91_TEST_COUNT}"',workflow)
        self.assertIn("permissions:\n  contents: read",workflow)
        self.assertNotIn("pull_request_target",workflow)
        self.assertNotRegex(workflow,r"(?m)^\s*(?:id-token|packages|deployments|secrets):\s*write")

    def test_runbook_targets_main_after_c91_merge(self):
        runbook=Path("validation/windows/C8-RUNBOOK.md").read_text(encoding="utf-8").casefold()
        for required in (
            "git clone https://github.com/mhx-digital/cold-wallets.git cold-wallets-c91",
            "git fetch --prune origin",
            "git checkout main",
            "git rev-parse origin/main",
            "-expectedhead '<sha final da main apos pr c9.1>'",
            "-expectedbranch 'main'",
            "manifest 57 is historical evidence",
        ):
            self.assertIn(required,runbook)
        self.assertRegex(runbook,r"manifest 59 is the current operational\s+checksum manifest")
        for prohibited in (
            "audit/cold-wallet-security-architecture-20260907",
            "pr #1",
            "5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f",
            "<c8.2_remote_head>",
            "manifest 54",
        ):
            self.assertNotIn(prohibited,runbook)
        self.assertEqual(runbook.count(f"-expectedtestcount {EXPECTED_C91_TEST_COUNT}"),3)
        self.assertIn(f"other than {EXPECTED_C91_TEST_COUNT}",runbook)

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
        runbook_text=Path("validation/windows/C8-RUNBOOK.md").read_text(encoding="utf-8")
        self.assertEqual(runbook_text.casefold().count(f"-expectedtestcount {EXPECTED_C91_TEST_COUNT}"),3)
        for parameter in ("-PythonExecutable","-PythonVersion","-RuntimeLock","-BuildLock","-PsbtLock","-Wheelhouse","-WheelhouseManifest"):
            self.assertEqual(len(re.findall(rf"(?m)^\s+{re.escape(parameter)}(?:\s|$)",runbook_text)),3)


if __name__=="__main__": unittest.main()
