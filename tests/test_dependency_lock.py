import re, unittest
from pathlib import Path

class DependencyLockTests(unittest.TestCase):
    def test_runtime_lock_is_exact_and_hashed(self):
        lines=[line.strip() for line in Path("requirements/runtime-py312-linux.lock").read_text().splitlines() if line.strip() and not line.startswith("--")]
        self.assertGreater(len(lines),20)
        for line in lines:
            self.assertRegex(line,r"^[A-Za-z0-9_.-]+==[^ ]+ --hash=sha256:[0-9a-f]{64}$")
    def test_direct_requirements_are_exact(self):
        for name in ("runtime.in","psbt.in"):
            for line in Path("requirements",name).read_text().splitlines():
                if line.strip(): self.assertRegex(line,r"^[A-Za-z0-9_.-]+(?:\[socks\])?==[^ ]+$")

    def test_build_and_psbt_locks_are_hashed(self):
        for name in ("build-py312.lock","psbt-py312-linux.lock"):
            for line in Path("requirements",name).read_text().splitlines():
                if line.strip(): self.assertRegex(line,r"^[A-Za-z0-9_.-]+==[^ ]+ --hash=sha256:[0-9a-f]{64}$")

if __name__=="__main__": unittest.main()
