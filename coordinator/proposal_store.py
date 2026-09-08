"""Transactional coordinator store containing proposals but never keys."""
from __future__ import annotations
from contextlib import closing
import json, sqlite3, threading, time
from pathlib import Path


class ProposalStoreError(RuntimeError): pass


class ProposalStore:
    def __init__(self,path: Path): self.path=Path(path); self._lock=threading.RLock(); self._init()
    def _db(self):
        db=sqlite3.connect(self.path,timeout=1,isolation_level=None); db.execute("PRAGMA busy_timeout=1000"); return db
    def _init(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        try:
            with closing(self._db()) as db:
                db.execute("CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL CHECK(version=1))")
                if not db.execute("SELECT 1 FROM schema_version").fetchone(): db.execute("INSERT INTO schema_version VALUES(1)")
                db.execute("CREATE TABLE IF NOT EXISTS proposals(proposal_id TEXT PRIMARY KEY,protocol TEXT NOT NULL,network TEXT NOT NULL,envelope_json TEXT NOT NULL,state TEXT NOT NULL,signed_tx_hash TEXT,updated_at INTEGER NOT NULL)")
                db.execute("CREATE TABLE IF NOT EXISTS idempotency(request_key TEXT NOT NULL,operation TEXT NOT NULL,payload_hash TEXT NOT NULL,response_json TEXT NOT NULL,created_at INTEGER NOT NULL,PRIMARY KEY(request_key,operation))")
        except sqlite3.DatabaseError as exc: raise ProposalStoreError("invalid proposal database") from exc
    def create(self,envelope: dict):
        proposal_id=envelope["proposalId"]; encoded=json.dumps(envelope,sort_keys=True,separators=(",",":")); now=int(time.time())
        with self._lock,closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("INSERT OR IGNORE INTO proposals VALUES(?,?,?,?,?,NULL,?)",(proposal_id,"ethereum",envelope["network"],encoded,"PREPARED",now))
            row=db.execute("SELECT envelope_json,state,signed_tx_hash FROM proposals WHERE proposal_id=?",(proposal_id,)).fetchone()
            if row[0]!=encoded: db.rollback(); raise ProposalStoreError("proposal ID collision")
            db.commit(); return proposal_id
    def attach_signed(self,proposal_id: str,tx_hash: str):
        with self._lock,closing(self._db()) as db:
            db.execute("BEGIN IMMEDIATE"); row=db.execute("SELECT signed_tx_hash FROM proposals WHERE proposal_id=?",(proposal_id,)).fetchone()
            if not row: db.rollback(); raise ProposalStoreError("unknown proposal")
            if row[0] not in {None,tx_hash}: db.rollback(); raise ProposalStoreError("different transaction already attached")
            db.execute("UPDATE proposals SET state='SIGNED_VALIDATED',signed_tx_hash=?,updated_at=? WHERE proposal_id=?",(tx_hash,int(time.time()),proposal_id)); db.commit()
    def get(self,proposal_id: str):
        with closing(self._db()) as db: row=db.execute("SELECT envelope_json,state,signed_tx_hash FROM proposals WHERE proposal_id=?",(proposal_id,)).fetchone()
        if not row: raise ProposalStoreError("unknown proposal")
        return json.loads(row[0]),row[1],row[2]
    def get_idempotent(self,key,operation):
        with closing(self._db()) as db: row=db.execute("SELECT payload_hash,response_json FROM idempotency WHERE request_key=? AND operation=?",(key,operation)).fetchone()
        return None if row is None else (row[0],json.loads(row[1]))
    def put_idempotent(self,key,operation,payload_hash,response):
        encoded=json.dumps(response,sort_keys=True,separators=(",",":"))
        with closing(self._db()) as db: db.execute("INSERT INTO idempotency VALUES(?,?,?,?,?)",(key,operation,payload_hash,encoded,int(time.time())))
