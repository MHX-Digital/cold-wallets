"""Checksum-bound backup and restore for authenticated synthetic vaults."""
from __future__ import annotations
import hashlib,json,secrets
from pathlib import Path
from transport.artifacts import read,write
from storage.authenticated import SCHEMA,open_sealed

BACKUP_SCHEMA="cold-wallets.backup"
class BackupError(ValueError): pass

def _digest(payload): return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _within(root: Path,authorized_root: Path):
    if root.is_symlink(): raise BackupError("symlink root rejected")
    resolved=root.resolve(); authorized=authorized_root.resolve()
    try: resolved.relative_to(authorized)
    except ValueError as exc: raise BackupError("path outside authorized root") from exc
    return resolved

def create_backup(vault_root: Path,vault_name: str,backup_root: Path,backup_name: str,*,authorized_root: Path):
    vault_root=_within(vault_root,authorized_root); backup_root=_within(backup_root,authorized_root)
    vault=read(vault_root,vault_name,expected_schema=SCHEMA)
    payload={"schema":BACKUP_SCHEMA,"version":1,"vaultSchema":SCHEMA,"vaultSha256":_digest(vault),"vaultPayload":vault}
    return write(backup_root,backup_name,payload)

def restore_backup(backup_root: Path,backup_name: str,destination_root: Path,destination_name: str,password: bytes,*,authorized_root: Path):
    backup_root=_within(backup_root,authorized_root); destination_root=_within(destination_root,authorized_root)
    backup=read(backup_root,backup_name,expected_schema=BACKUP_SCHEMA)
    if set(backup)!={"schema","version","vaultSchema","vaultSha256","vaultPayload"} or backup["version"]!=1 or backup["vaultSchema"]!=SCHEMA: raise BackupError("unsupported backup")
    vault=backup["vaultPayload"]
    if not isinstance(backup["vaultSha256"],str) or not secrets.compare_digest(_digest(vault),backup["vaultSha256"]): raise BackupError("backup checksum mismatch")
    open_sealed(vault,password)
    return write(destination_root,destination_name,vault)
