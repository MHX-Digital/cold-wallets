"""SQLite lifecycle for public disposable addresses; stores no private keys."""
from __future__ import annotations
import sqlite3, threading, time, uuid
from pathlib import Path

STATES={"UNUSED","RESERVED","PRESENTED","DETECTED","CONFIRMED","SWEEP_PREPARED","SWEPT","EXPIRED","FAILED"}
TRANSITIONS={"UNUSED":{"RESERVED","FAILED"},"RESERVED":{"PRESENTED","EXPIRED","FAILED"},"PRESENTED":{"DETECTED","EXPIRED","FAILED"},"DETECTED":{"CONFIRMED","PRESENTED","FAILED"},"CONFIRMED":{"DETECTED","SWEEP_PREPARED","FAILED"},"SWEEP_PREPARED":{"SWEPT","CONFIRMED","FAILED"},"SWEPT":set(),"EXPIRED":set(),"FAILED":set()}
class AddressStoreError(RuntimeError): pass

class DisposableStore:
    def __init__(self,path: Path): self.path=Path(path); self._lock=threading.RLock(); self._init()
    def _db(self):
        db=sqlite3.connect(self.path,timeout=1,isolation_level=None); db.execute("PRAGMA foreign_keys=ON"); db.execute("PRAGMA busy_timeout=1000"); return db
    def _init(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        try:
            with self._db() as db:
                db.execute("CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL CHECK(version=1))")
                if not db.execute("SELECT 1 FROM schema_version").fetchone(): db.execute("INSERT INTO schema_version VALUES(1)")
                db.execute("CREATE TABLE IF NOT EXISTS addresses(id TEXT PRIMARY KEY,address TEXT UNIQUE NOT NULL,protocol TEXT NOT NULL,network TEXT NOT NULL,key_reference TEXT NOT NULL,state TEXT NOT NULL,request_id TEXT UNIQUE,reserved_until INTEGER,updated_at INTEGER NOT NULL)")
                db.execute("CREATE TABLE IF NOT EXISTS history(seq INTEGER PRIMARY KEY AUTOINCREMENT,address_id TEXT NOT NULL,from_state TEXT,to_state TEXT NOT NULL,at INTEGER NOT NULL,UNIQUE(address_id,from_state,to_state),FOREIGN KEY(address_id) REFERENCES addresses(id))")
        except sqlite3.DatabaseError as exc: raise AddressStoreError("invalid address database") from exc
    def add(self,address,protocol,network,key_reference):
        if not key_reference or "private" in key_reference.casefold(): raise AddressStoreError("opaque key reference required")
        ident=uuid.uuid4().hex; now=int(time.time())
        with self._db() as db: db.execute("INSERT INTO addresses VALUES(?,?,?,?,?,'UNUSED',NULL,NULL,?)",(ident,address,protocol,network,key_reference,now))
        return ident
    def reserve(self,request_id,ttl=300,now=None):
        now=int(time.time()) if now is None else now
        with self._lock,self._db() as db:
            db.execute("BEGIN IMMEDIATE")
            prior=db.execute("SELECT * FROM addresses WHERE request_id=?",(request_id,)).fetchone()
            if prior: db.commit(); return prior
            row=db.execute("SELECT id FROM addresses WHERE state='UNUSED' ORDER BY updated_at,id LIMIT 1").fetchone()
            if not row: db.rollback(); raise AddressStoreError("no unused address")
            db.execute("UPDATE addresses SET state='RESERVED',request_id=?,reserved_until=?,updated_at=? WHERE id=? AND state='UNUSED'",(request_id,now+ttl,now,row[0]))
            db.execute("INSERT INTO history(address_id,from_state,to_state,at) VALUES(?,'UNUSED','RESERVED',?)",(row[0],now))
            result=db.execute("SELECT * FROM addresses WHERE id=?",(row[0],)).fetchone(); db.commit(); return result
    def transition(self,ident,new_state,now=None):
        if new_state not in STATES: raise AddressStoreError("unknown state")
        now=int(time.time()) if now is None else now
        with self._lock,self._db() as db:
            db.execute("BEGIN IMMEDIATE"); row=db.execute("SELECT state FROM addresses WHERE id=?",(ident,)).fetchone()
            if not row: db.rollback(); raise AddressStoreError("unknown address")
            old=row[0]
            if new_state==old: db.commit(); return old
            if new_state not in TRANSITIONS[old]: db.rollback(); raise AddressStoreError("invalid transition")
            db.execute("UPDATE addresses SET state=?,updated_at=? WHERE id=?",(new_state,now,ident))
            db.execute("INSERT OR IGNORE INTO history(address_id,from_state,to_state,at) VALUES(?,?,?,?)",(ident,old,new_state,now)); db.commit(); return new_state
    def expire(self,now=None):
        now=int(time.time()) if now is None else now
        with self._db() as db:
            db.execute("BEGIN IMMEDIATE"); rows=db.execute("SELECT id FROM addresses WHERE state='RESERVED' AND reserved_until<=?",(now,)).fetchall()
            for (ident,) in rows:
                db.execute("UPDATE addresses SET state='EXPIRED',updated_at=? WHERE id=?",(now,ident)); db.execute("INSERT OR IGNORE INTO history(address_id,from_state,to_state,at) VALUES(?,'RESERVED','EXPIRED',?)",(ident,now))
            db.commit(); return len(rows)
    def get(self,ident):
        with self._db() as db: row=db.execute("SELECT id,address,protocol,network,state FROM addresses WHERE id=?",(ident,)).fetchone()
        if not row: raise AddressStoreError("unknown address")
        return dict(zip(("id","address","protocol","network","state"),row))
