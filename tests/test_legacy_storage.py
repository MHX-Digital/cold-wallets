import tempfile, unittest, uuid
from pathlib import Path
from storage.legacy import LegacyStorageError, dry_run

class LegacyStorageTests(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(prefix=f"cold-wallets-test-{uuid.uuid4().hex}-"); self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def test_metadata_only_dry_run(self):
        marker="TEST-ONLY-NOT-A-KEY"; (self.root/"fixture.json").write_text('{"private_key":"'+marker+'"}')
        result=dry_run(self.root,explicit_test_root=self.root)
        self.assertEqual(result[0]["status"],"candidate"); self.assertNotIn(marker,repr(result))
    def test_rejects_non_explicit_root(self):
        with self.assertRaises(LegacyStorageError): dry_run(self.root,explicit_test_root=self.root/"other")

if __name__=="__main__": unittest.main()
