import copy,tempfile,unittest,uuid
from pathlib import Path

from storage.authenticated import StorageBackendUnavailable,StorageError,open_sealed,read_vault,seal,write_vault
from storage.backup import BackupError,create_backup,restore_backup


class AuthenticatedStorageContractTests(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(prefix=f"cold-wallets-test-{uuid.uuid4().hex}-"); self.root=Path(self.temp.name); self.password=b"test-password-only"; self.data=b"TEST-ONLY-NOT-A-REAL-KEY"
    def tearDown(self): self.temp.cleanup()
    def test_backend_is_real_or_fails_closed(self):
        try: envelope=seal(self.data,self.password,{"purpose":"synthetic-fixture"})
        except StorageBackendUnavailable: return
        self.assertEqual(open_sealed(envelope,self.password),self.data)
    def test_authenticated_roundtrip_tamper_password_and_downgrade(self):
        try: envelope=seal(self.data,self.password,{"purpose":"synthetic-fixture"})
        except StorageBackendUnavailable: self.skipTest("hash-locked PyCryptodome environment required")
        self.assertEqual(open_sealed(envelope,self.password),self.data)
        for mutation in (lambda e:e.__setitem__("ciphertext",e["ciphertext"][:-2]+"AA"),lambda e:e["metadata"].__setitem__("purpose","tampered"),lambda e:e.__setitem__("version",0)):
            changed=copy.deepcopy(envelope); mutation(changed)
            with self.assertRaises(StorageError): open_sealed(changed,self.password)
        with self.assertRaises(StorageError): open_sealed(envelope,b"wrong-password")
    def test_backup_restore_and_negative_paths(self):
        try: write_vault(self.root/"vault","fixture.cw-vault",self.data,self.password,{"purpose":"synthetic-fixture"})
        except StorageBackendUnavailable: self.skipTest("hash-locked PyCryptodome environment required")
        create_backup(self.root/"vault","fixture.cw-vault",self.root/"backup","fixture.cw-backup",authorized_root=self.root)
        restored=restore_backup(self.root/"backup","fixture.cw-backup",self.root/"restore","fixture.cw-vault",self.password,authorized_root=self.root)
        self.assertEqual(read_vault(restored.parent,restored.name,self.password),self.data)
        with self.assertRaises(FileExistsError): restore_backup(self.root/"backup","fixture.cw-backup",self.root/"restore","fixture.cw-vault",self.password,authorized_root=self.root)
        with self.assertRaises(BackupError): restore_backup(self.root/"backup","fixture.cw-backup",self.root/"../escape","fixture.cw-vault",self.password,authorized_root=self.root)


if __name__=="__main__": unittest.main()
