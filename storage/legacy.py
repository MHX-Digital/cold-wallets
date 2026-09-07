"""Metadata-only legacy detector; never reads values or performs migration."""
from __future__ import annotations
import json
from pathlib import Path

class LegacyStorageError(ValueError): pass
FORBIDDEN_NAMES={"generated","address_pool","backups","backup","signed_transactions"}

def dry_run(root: Path,*,explicit_test_root: Path):
    root=root.resolve(); allowed=explicit_test_root.resolve()
    if root!=allowed or root.name.casefold() in FORBIDDEN_NAMES: raise LegacyStorageError("dry-run root is not an isolated test root")
    results=[]
    for path in sorted(root.glob("*.json")):
        if path.is_symlink() or path.stat().st_size>64*1024: results.append({"name":path.name,"status":"rejected"}); continue
        try: obj=json.loads(path.read_text(encoding="utf-8"))
        except Exception: results.append({"name":path.name,"status":"invalid-json"}); continue
        keys=set(obj) if isinstance(obj,dict) else set()
        results.append({"name":path.name,"status":"candidate" if keys & {"private_key","private_key_wif","mnemonic","seed"} else "non-secret","size":path.stat().st_size})
    return results
