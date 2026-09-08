import tempfile, threading, unittest, uuid
from pathlib import Path
from coordinator.disposable_store import AddressStoreError, DisposableStore

class DisposableStoreTests(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(prefix=f"cold-wallets-test-{uuid.uuid4().hex}-"); self.path=Path(self.temp.name)/"addresses.sqlite"; self.store=DisposableStore(self.path)
    def tearDown(self): self.temp.cleanup()
    def add(self,n): return self.store.add(f"test-address-{n}","bitcoin","regtest",f"keyref:{n}")
    def test_concurrent_atomic_reservations_and_idempotency(self):
        self.add(1); self.add(2); rows=[]; threads=[threading.Thread(target=lambda i=i:rows.append(self.store.reserve(f"req-{i}",now=1))) for i in range(2)]
        [t.start() for t in threads]; [t.join() for t in threads]
        self.assertEqual(len({r[0] for r in rows}),2); self.assertEqual(self.store.reserve("req-0",now=2)[0],next(r[0] for r in rows if r[6]=="req-0"))
    def test_restart_expiry_and_transitions(self):
        ident=self.add(1); self.store.reserve("req",ttl=1,now=1); self.assertEqual(DisposableStore(self.path).expire(now=2),1)
        ident=self.add(2); self.store.reserve("req2",now=1); self.store.transition(ident,"PRESENTED",now=2); self.store.transition(ident,"DETECTED",now=3); self.assertEqual(self.store.transition(ident,"DETECTED"),"DETECTED")
        with self.assertRaises(AddressStoreError): self.store.transition(ident,"SWEPT")
    def test_rejects_secret_like_key_reference(self):
        with self.assertRaises(AddressStoreError): self.store.add("a","bitcoin","regtest","private-key:test")

if __name__=="__main__": unittest.main()
