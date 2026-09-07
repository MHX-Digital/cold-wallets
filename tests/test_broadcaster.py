import tempfile, threading, unittest, uuid
from pathlib import Path
from broadcaster.store import BroadcastStateError, BroadcastStore
from broadcaster.service import BroadcastService

class Remote:
    def __init__(self,response=None,lookup="unknown"): self.response=response; self.lookup_result=lookup; self.sends=0
    def send(self,raw):
        self.sends+=1
        if self.response is TimeoutError: raise TimeoutError
        return self.response
    def lookup(self,tx_hash): return self.lookup_result

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

    def test_timeout_becomes_unknown_and_never_blindly_retries(self):
        remote=Remote(TimeoutError); service=BroadcastService(BroadcastStore(self.db),remote)
        self.assertEqual(service.submit_bitcoin("0102","proposal").state,"BROADCAST_UNKNOWN")
        self.assertEqual(service.submit_bitcoin("0102","proposal").state,"BROADCAST_UNKNOWN")
        self.assertEqual(remote.sends,1)

    def test_reconcile_and_already_known(self):
        remote=Remote(TimeoutError,lookup="known"); service=BroadcastService(BroadcastStore(self.db),remote)
        service.submit_bitcoin("0102","proposal"); self.assertEqual(service.reconcile_bitcoin("0102").state,"BROADCAST")
        other=BroadcastService(BroadcastStore(Path(self.temp.name)/"other.sqlite"),Remote({"status":"already_known"}))
        self.assertEqual(other.submit_bitcoin("0304","proposal").state,"BROADCAST")

if __name__=="__main__": unittest.main()
