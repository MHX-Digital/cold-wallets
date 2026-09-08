"""SQLite-backed idempotency and explicit broadcast state machine."""
from __future__ import annotations
from contextlib import closing
import hashlib, sqlite3, threading, time
from pathlib import Path

STATES={"RECEIVED","VALIDATED","BROADCASTING","BROADCAST_UNKNOWN","BROADCAST","CONFIRMED","FAILED_RETRYABLE","FAILED_TERMINAL","REPLACED","DROPPED"}
TRANSITIONS={"RECEIVED":{"VALIDATED","FAILED_TERMINAL"},"VALIDATED":{"BROADCASTING","FAILED_TERMINAL"},"BROADCASTING":{"BROADCAST","BROADCAST_UNKNOWN","FAILED_RETRYABLE","FAILED_TERMINAL"},"BROADCAST_UNKNOWN":{"BROADCAST","FAILED_RETRYABLE","FAILED_TERMINAL","REPLACED","DROPPED"},"FAILED_RETRYABLE":{"BROADCASTING","FAILED_TERMINAL"},"BROADCAST":{"CONFIRMED","REPLACED","DROPPED"},"CONFIRMED":{"BROADCAST","DROPPED"},"FAILED_TERMINAL":set(),"REPLACED":set(),"DROPPED":set()}
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
            with closing(self._connect()) as db:
                db.execute("CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL)")
                if db.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0]==0: db.execute("INSERT INTO schema_version VALUES(1)")
                db.execute("CREATE TABLE IF NOT EXISTS operations(tx_hash TEXT PRIMARY KEY,network TEXT NOT NULL,state TEXT NOT NULL,retries INTEGER NOT NULL DEFAULT 0,updated_at INTEGER NOT NULL,protocol TEXT NOT NULL DEFAULT 'bitcoin',proposal_id TEXT NOT NULL DEFAULT '',last_error TEXT,result TEXT,uncertain INTEGER NOT NULL DEFAULT 0)")
                columns={row[1] for row in db.execute("PRAGMA table_info(operations)")}
                for name,definition in (("protocol","TEXT NOT NULL DEFAULT 'bitcoin'"),("proposal_id","TEXT NOT NULL DEFAULT ''"),("last_error","TEXT"),("result","TEXT"),("uncertain","INTEGER NOT NULL DEFAULT 0")):
                    if name not in columns: db.execute(f"ALTER TABLE operations ADD COLUMN {name} {definition}")
        except sqlite3.DatabaseError as exc: raise BroadcastStateError("invalid broadcast database") from exc
    def receive_bitcoin(self,raw_hex: str,network: str="bitcoin-mainnet",proposal_id: str=""):
        return self.receive(bitcoin_txid(raw_hex),network,"bitcoin",proposal_id)
    def receive(self,tx_hash: str,network: str,protocol: str,proposal_id: str):
        if not tx_hash or protocol not in {"bitcoin","ethereum"}: raise BroadcastStateError("invalid operation identity")
        now=int(time.time())
        with self._lock,closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO operations(tx_hash,network,state,updated_at,protocol,proposal_id) VALUES(?,?,?,?,?,?)",(tx_hash,network,"RECEIVED",now,protocol,proposal_id))
            row=db.execute("SELECT tx_hash,network,state,retries,protocol,proposal_id FROM operations WHERE tx_hash=?",(tx_hash,)).fetchone()
            if row[1]!=network or row[4]!=protocol or row[5]!=proposal_id: db.rollback(); raise BroadcastStateError("operation identity conflict")
            db.commit()
        return row
    def transition(self,tx_hash: str,new_state: str,max_retries: int=3,*,last_error: str|None=None,result: str|None=None,uncertain: bool|None=None):
        if new_state not in STATES: raise BroadcastStateError("unknown state")
        with self._lock,closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            row=db.execute("SELECT state,retries FROM operations WHERE tx_hash=?",(tx_hash,)).fetchone()
            if not row or new_state not in TRANSITIONS[row[0]]: db.rollback(); raise BroadcastStateError("invalid transition")
            retries=row[1]+(new_state=="BROADCASTING")
            if retries>max_retries: db.execute("UPDATE operations SET state='FAILED_TERMINAL',updated_at=? WHERE tx_hash=?",(int(time.time()),tx_hash)); db.commit(); raise BroadcastStateError("retry limit exhausted")
            uncertain_value=int(new_state=="BROADCAST_UNKNOWN") if uncertain is None else int(uncertain)
            db.execute("UPDATE operations SET state=?,retries=?,updated_at=?,last_error=?,result=?,uncertain=? WHERE tx_hash=?",(new_state,retries,int(time.time()),last_error,result,uncertain_value,tx_hash)); db.commit()
        return new_state
    def get(self,tx_hash: str):
        with closing(self._connect()) as db: return db.execute("SELECT tx_hash,network,state,retries FROM operations WHERE tx_hash=?",(tx_hash,)).fetchone()
    def details(self,tx_hash: str):
        with closing(self._connect()) as db:
            row=db.execute("SELECT tx_hash,network,state,retries,protocol,proposal_id,last_error,result,uncertain FROM operations WHERE tx_hash=?",(tx_hash,)).fetchone()
        return row
