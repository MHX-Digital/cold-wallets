import base64,copy,json,tempfile,unittest,uuid
from pathlib import Path
from unittest.mock import patch

from storage.authenticated import MAX_PLAINTEXT,SCRYPT_N,StorageBackendUnavailable,StorageError,open_sealed,read_vault,seal,write_vault
from storage.backup import BackupError,create_backup,restore_backup
from transport.artifacts import ArtifactError,read,write


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

    def test_all_authenticated_fields_and_randomness(self):
        random_values=[b"\x01"*16,b"\x02"*12,b"\x03"*16,b"\x04"*12]
        try:
            with patch("storage.authenticated.secrets.token_bytes",side_effect=random_values) as rng:
                envelope=seal(self.data,self.password,{"purpose":"synthetic-fixture"})
                second=seal(self.data,self.password,{"purpose":"synthetic-fixture"})
        except StorageBackendUnavailable: self.skipTest("hash-locked PyCryptodome environment required")
        self.assertEqual(rng.call_count,4)
        self.assertNotEqual(envelope["kdf"]["salt"],second["kdf"]["salt"])
        self.assertNotEqual(envelope["cipher"]["nonce"],second["cipher"]["nonce"])
        self.assertNotIn(self.data, json.dumps(envelope,sort_keys=True).encode())
        def flip(value):
            raw=bytearray(base64.b64decode(value)); raw[0]^=1; return base64.b64encode(raw).decode()
        mutations=(
            lambda e:e.__setitem__("tag",flip(e["tag"])),
            lambda e:e["cipher"].__setitem__("nonce",flip(e["cipher"]["nonce"])),
            lambda e:e["kdf"].__setitem__("salt",flip(e["kdf"]["salt"])),
            lambda e:e["metadata"].__setitem__("purpose","altered"),
        )
        for mutation in mutations:
            changed=copy.deepcopy(envelope); mutation(changed)
            with self.assertRaisesRegex(StorageError,"authentication failed") as caught: open_sealed(changed,self.password)
            self.assertNotIn(self.password.decode(),str(caught.exception)); self.assertNotIn(self.data.decode(),str(caught.exception))

    def test_kdf_and_size_limits_are_checked_before_work(self):
        try: envelope=seal(self.data,self.password,{"purpose":"synthetic-fixture"})
        except StorageBackendUnavailable: self.skipTest("hash-locked PyCryptodome environment required")
        changed=copy.deepcopy(envelope); changed["kdf"]["n"]=SCRYPT_N*1024
        with patch("storage.authenticated.hashlib.scrypt",side_effect=AssertionError("KDF must not run")) as derive:
            with self.assertRaisesRegex(StorageError,"KDF policy mismatch"): open_sealed(changed,self.password)
            derive.assert_not_called()
        changed=copy.deepcopy(envelope); changed["ciphertext"]="A"*(4*((MAX_PLAINTEXT+2)//3)+4)
        with patch("storage.authenticated.hashlib.scrypt",side_effect=AssertionError("KDF must not run")) as derive:
            with self.assertRaisesRegex(StorageError,"invalid ciphertext"): open_sealed(changed,self.password)
            derive.assert_not_called()

    def test_atomic_vault_write_failure_leaves_no_partial_file(self):
        try: seal(self.data,self.password,{"purpose":"synthetic-fixture"})
        except StorageBackendUnavailable: self.skipTest("hash-locked PyCryptodome environment required")
        target=self.root/"vault"/"fixture.cw-vault"
        with patch("transport.artifacts.os.replace",side_effect=OSError("synthetic interruption")):
            with self.assertRaisesRegex(OSError,"synthetic interruption"):
                write_vault(target.parent,target.name,self.data,self.password,{"purpose":"synthetic-fixture"})
        self.assertFalse(target.exists()); self.assertEqual(list(target.parent.glob(".cw-write-*.tmp")),[])
    def test_backup_restore_and_negative_paths(self):
        try: write_vault(self.root/"vault","fixture.cw-vault",self.data,self.password,{"purpose":"synthetic-fixture"})
        except StorageBackendUnavailable: self.skipTest("hash-locked PyCryptodome environment required")
        create_backup(self.root/"vault","fixture.cw-vault",self.root/"backup","fixture.cw-backup",authorized_root=self.root)
        restored=restore_backup(self.root/"backup","fixture.cw-backup",self.root/"restore","fixture.cw-vault",self.password,authorized_root=self.root)
        self.assertEqual(read_vault(restored.parent,restored.name,self.password),self.data)
        with self.assertRaises(FileExistsError): restore_backup(self.root/"backup","fixture.cw-backup",self.root/"restore","fixture.cw-vault",self.password,authorized_root=self.root)
        with self.assertRaises(BackupError): restore_backup(self.root/"backup","fixture.cw-backup",self.root/"../escape","fixture.cw-vault",self.password,authorized_root=self.root)

    def test_backup_tamper_truncation_version_symlink_and_interruption(self):
        try: write_vault(self.root/"vault","fixture.cw-vault",self.data,self.password,{"purpose":"synthetic-fixture"})
        except StorageBackendUnavailable: self.skipTest("hash-locked PyCryptodome environment required")
        create_backup(self.root/"vault","fixture.cw-vault",self.root/"backup","fixture.cw-backup",authorized_root=self.root)
        payload=read(self.root/"backup","fixture.cw-backup",expected_schema="cold-wallets.backup")
        bad=copy.deepcopy(payload); bad["vaultSha256"]="0"*64
        write(self.root/"backup","checksum.cw-backup",bad)
        with self.assertRaisesRegex(BackupError,"checksum mismatch"): restore_backup(self.root/"backup","checksum.cw-backup",self.root/"restore-a","fixture.cw-vault",self.password,authorized_root=self.root)
        bad=copy.deepcopy(payload); bad["version"]=0
        write(self.root/"backup","version.cw-backup",bad)
        with self.assertRaisesRegex(BackupError,"unsupported backup"): restore_backup(self.root/"backup","version.cw-backup",self.root/"restore-b","fixture.cw-vault",self.password,authorized_root=self.root)
        truncated=self.root/"backup"/"truncated.cw-backup"; truncated.write_bytes(b'{"payload":')
        with self.assertRaises(ArtifactError): restore_backup(self.root/"backup",truncated.name,self.root/"restore-c","fixture.cw-vault",self.password,authorized_root=self.root)
        link=self.root/"backup-link"; link.symlink_to(self.root/"backup",target_is_directory=True)
        with self.assertRaises(BackupError): restore_backup(link,"fixture.cw-backup",self.root/"restore-d","fixture.cw-vault",self.password,authorized_root=self.root)
        target=self.root/"restore-e"/"fixture.cw-vault"
        with patch("transport.artifacts.os.replace",side_effect=OSError("synthetic interruption")):
            with self.assertRaisesRegex(OSError,"synthetic interruption"):
                restore_backup(self.root/"backup","fixture.cw-backup",target.parent,target.name,self.password,authorized_root=self.root)
        self.assertFalse(target.exists()); self.assertEqual(list(target.parent.glob(".cw-write-*.tmp")),[])


if __name__=="__main__": unittest.main()
