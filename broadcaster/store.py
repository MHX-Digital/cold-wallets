"""SQLite-backed idempotency and explicit broadcast state machine."""
from __future__ import annotations
import hashlib, sqlite3, threading, time
from pathlib import Path

STATES={"RECEIVED","VALIDATED","BROADCASTING","BROADCAST_UNKNOWN","BROADCAST","CONFIRMED","FAILED_RETRYABLE","FAILED_TERMINAL"}
TRANSITIONS={"RECEIVED":{"VALIDATED","FAILED_TERMINAL"},"VALIDATED":{"BROADCASTING","FAILED_TERMINAL"},"BROADCASTING":{"BROADCAST","BROADCAST_UNKNOWN","FAILED_RETRYABLE","FAILED_TERMINAL"},"BROADCAST_UNKNOWN":{"BROADCAST","FAILED_RETRYABLE","FAILED_TERMINAL"},"FAILED_RETRYABLE":{"BROADCASTING","FAILED_TERMINAL"},"BROADCAST":{"CONFIRMED"},"CONFIRMED":set(),"FAILED_TERMINAL":set()}
class BroadcastStateError(RuntimeError): pass

def bitcoin_txid(raw_hex: str) -> str:
    try: raw=bytes.fromhex(raw_hex)
    except ValueError as exc: raise BroadcastStateError("invalid transaction encoding") from exc
    if not raw: raise BroadcastStateError("empty transaction")
    return hashlib.sha256(hashlib.sha256(raw).digest()).digest()[::-1].hex()

class BroadcastStore:
    def __init__(self,path: Path):
        self.path=Path(path); self._lock=threading.RLock(); self._initialize()
    def _connect(self):
        connection=sqlite3.connect(self.path,timeout=1,isolation_level=None)
        connection.execute("PRAGMA busy_timeout=1000")
        return connection
    def _initialize(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        try:
            with self._connect() as db:
                db.execute("CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL)")
                if db.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]==0: db.execute("INSERT INTO schema_version VALUES(1)")
                db.execute("CREATE TABLE IF NOT EXISTS operations(tx_hash TEXT PRIMARY KEY,network TEXT NOT NULL,state TEXT NOT NULL,retries INTEGER NOT NULL DEFAULT 0,updated_at INTEGER NOT NULL,protocol TEXT NOT NULL DEFAULT 'bitcoin',proposal_id TEXT NOT NULL DEFAULT '',last_error TEXT,result TEXT,uncertain INTEGER NOT NULL DEFAULT 0)")
                columns={row[1] for row in db.execute("PRAGMA table_info(operations)")}
                for name,definition in (("protocol","TEXT NOT NULL DEFAULT 'bitcoin'"),("proposal_id","TEXT NOT NULL DEFAULT ''"),("last_error","TEXT"),("result","TEXT"),("uncertain","INTEGER NOT NULL DEFAULT 0")):
                    if name not in columns: db.execute(f"ALTER TABLE operations ADD COLUMN {name} {definition}")
        except sqlite3.DatabaseError as exc: raise BroadcastStateError("invalid broadcast database") from exc
    def receive_bitcoin(self,raw_hex: str,network: str="bitcoin-mainnet",proposal_id: str=""):
        tx_hash=bitcoin_txid(raw_hex); now=int(time.time())
        with self._lock,self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO operations(tx_hash,network,state,updated_at,protocol,proposal_id) VALUES(?,?,?,?,?,?)",(tx_hash,network,"RECEIVED",now,"bitcoin",proposal_id))
            row=db.execute("SELECT tx_hash,network,state,retries FROM operations WHERE tx_hash=?",(tx_hash,)).fetchone(); db.commit()
        return row
    def transition(self,tx_hash: str,new_state: str,max_retries: int=3):
        if new_state not in STATES: raise BroadcastStateError("unknown state")
        with self._lock,self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT state,retries FROM operations WHERE tx_hash=?",(tx_hash,)).fetchone()
            if not row or new_state not in TRANSITIONS[row[0]]: db.rollback(); raise BroadcastStateError("invalid transition")
            retries=row[1]+(new_state=="BROADCASTING")
            if retries>max_retries: db.execute("UPDATE operations SET state='FAILED_TERMINAL',updated_at=? WHERE tx_hash=?",(int(time.time()),tx_hash)); db.commit(); raise BroadcastStateError("retry limit exhausted")
            db.execute("UPDATE operations SET state=?,retries=?,updated_at=? WHERE tx_hash=?",(new_state,retries,int(time.time()),tx_hash)); db.commit()
        return new_state
    def get(self,tx_hash: str):
        with self._connect() as db: return db.execute("SELECT tx_hash,network,state,retries FROM operations WHERE tx_hash=?",(tx_hash,)).fetchone()
