import tempfile, threading, unittest, uuid
from pathlib import Path
from broadcaster.store import BroadcastStateError, BroadcastStore

class BroadcasterTests(unittest.TestCase):
    def setUp(self): self.temp=tempfile.TemporaryDirectory(prefix=f"cold-wallets-test-{uuid.uuid4().hex}-"); self.db=Path(self.temp.name)/"broadcast.sqlite"
    def tearDown(self): self.temp.cleanup()
    def test_duplicate_and_restart_are_idempotent(self):
        store=BroadcastStore(self.db); first=store.receive_bitcoin("0102"); second=store.receive_bitcoin("0102")
        self.assertEqual(first,second); self.assertEqual(BroadcastStore(self.db).get(first[0])[2],"RECEIVED")
    def test_concurrent_receive_is_single_operation(self):
        store=BroadcastStore(self.db); rows=[]
        threads=[threading.Thread(target=lambda:rows.append(store.receive_bitcoin("0102"))) for _ in range(2)]
        [t.start() for t in threads]; [t.join() for t in threads]
        self.assertEqual(len({r[0] for r in rows}),1)
    def test_state_machine_and_retry_limit(self):
        store=BroadcastStore(self.db); tx=store.receive_bitcoin("0102")[0]
        with self.assertRaises(BroadcastStateError): store.transition(tx,"CONFIRMED")
        store.transition(tx,"VALIDATED"); store.transition(tx,"BROADCASTING"); store.transition(tx,"FAILED_RETRYABLE")
        store.transition(tx,"BROADCASTING"); store.transition(tx,"FAILED_RETRYABLE")
        with self.assertRaises(BroadcastStateError): store.transition(tx,"BROADCASTING",max_retries=2)
        self.assertEqual(store.get(tx)[2],"FAILED_TERMINAL")
    def test_corrupt_database_fails_closed(self):
        self.db.write_bytes(b"not sqlite")
        with self.assertRaises(BroadcastStateError): BroadcastStore(self.db)

if __name__=="__main__": unittest.main()
