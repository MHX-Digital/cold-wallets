import re
import unittest
from pathlib import Path


class GovernanceTests(unittest.TestCase):
    def test_open_source_governance_and_ci_are_fail_closed(self):
        required = (
            "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", ".gitleaksignore",
            "SUPPORT.md", "CHANGELOG.md", ".github/CODEOWNERS",
            ".github/PULL_REQUEST_TEMPLATE.md", ".github/dependabot.yml",
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            ".github/ISSUE_TEMPLATE/config.yml", ".github/workflows/ci.yml",
        )
        self.assertEqual([name for name in required if not Path(name).is_file()], [])
        license_text = Path("LICENSE").read_text(encoding="utf-8")
        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 MHX Digital", license_text)
        ignores = [line for line in Path(".gitleaksignore").read_text(encoding="utf-8").splitlines() if line and not line.startswith("#")]
        self.assertEqual(ignores, ["ddabbb1063c4deb986d79288ca4db7201dcf5331:tests/test_dashboard_security.py:generic-api-key:191"])
        owners = Path(".github/CODEOWNERS").read_text(encoding="utf-8")
        for scope in ("*", "/signer/", "/coordinator/", "/broadcaster/", "/storage/", "/transport/", "/requirements/", "/validation/", "/.github/workflows/", "/SECURITY.md", "/LICENSE"):
            self.assertRegex(owners, rf"(?m)^{re.escape(scope)}\s+@neomaike$")
        workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("pull_request:\n    branches: [main]", workflow)
        self.assertIn("push:\n    branches: [main]", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn('EXPECTED_TEST_COUNT: "89"', workflow)
        self.assertIn("sha256sum -c audit_output/59-c91-checksums.txt", workflow)
        self.assertNotIn("sha256sum -c audit_output/57-c9-checksums.txt", workflow)
        self.assertIn("--require-hashes", workflow)
        self.assertIn("--no-index", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("timeout-minutes:", workflow)
        self.assertIn("cancel-in-progress: true", workflow)
        self.assertNotIn("pull_request_target", workflow)
        self.assertNotRegex(workflow, r"(?m)^\s*(?:id-token|packages|deployments):\s*write")
        self.assertNotRegex(workflow.casefold(), r"\b(?:tor|helios|bitcoind|docker|deploy)\b")
        uses = re.findall(r"(?m)^\s*uses:\s*([^\s#]+)", workflow)
        self.assertTrue(uses)
        self.assertTrue(all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", item) for item in uses))
        readme = Path("README.md").read_text(encoding="utf-8").casefold()
        security = Path("SECURITY.md").read_text(encoding="utf-8").casefold()
        self.assertIn("no-go for real funds", readme)
        self.assertIn("private vulnerability reporting", security)


if __name__ == "__main__":
    unittest.main()
