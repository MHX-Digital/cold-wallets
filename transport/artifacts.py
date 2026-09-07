"""Strict atomic artifact exchange inside an explicitly authorized root."""
from __future__ import annotations
import hashlib, json, os, secrets
from pathlib import Path

MAX_ARTIFACT_BYTES=1024*1024
EXTENSIONS={"cold-wallets.eth-tx":".cw-eth-proposal","cold-wallets.eth-signed":".cw-eth-signed","cold-wallets.btc-signed":".cw-btc-signed"}
class ArtifactError(ValueError): pass
PSBT_MAGIC=b"psbt\xff"

def _target(root: Path, name: str) -> Path:
    root=root.resolve()
    if Path(name).name!=name: raise ArtifactError("artifact name must be a basename")
    target=(root/name).resolve(strict=False)
    if target.parent!=root: raise ArtifactError("artifact path escapes authorized root")
    return target

def _encode(payload: dict) -> bytes:
    if not isinstance(payload,dict): raise ArtifactError("artifact must be an object")
    schema=payload.get("schema")
    if schema not in EXTENSIONS: raise ArtifactError("unsupported artifact schema")
    body=dict(payload); body.pop("artifactSha256",None)
    canonical=json.dumps(body,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    wrapper={"payload":body,"artifactSha256":hashlib.sha256(canonical).hexdigest()}
    encoded=json.dumps(wrapper,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    if len(encoded)>MAX_ARTIFACT_BYTES: raise ArtifactError("artifact too large")
    return encoded

def write(root: Path, name: str, payload: dict, *, overwrite: bool=False) -> Path:
    root=root.resolve(); root.mkdir(mode=0o700,parents=True,exist_ok=True)
    target=_target(root,name); expected=EXTENSIONS.get(payload.get("schema"))
    if target.suffix!=expected: raise ArtifactError("artifact extension mismatch")
    if target.is_symlink(): raise ArtifactError("symlink target rejected")
    if target.exists() and not overwrite: raise FileExistsError(target.name)
    temp=root/f".cw-write-{secrets.token_hex(12)}.tmp"
    try:
        fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"wb") as stream:
            stream.write(_encode(payload)); stream.flush(); os.fsync(stream.fileno())
        if target.is_symlink(): raise ArtifactError("symlink target rejected")
        os.replace(temp,target)
        try:
            directory_fd=os.open(root,os.O_RDONLY); os.fsync(directory_fd); os.close(directory_fd)
        except OSError: pass
        return target
    finally:
        if temp.exists(): temp.unlink()

def read(root: Path, name: str, *, expected_schema: str) -> dict:
    target=_target(root,name)
    if target.is_symlink() or not target.is_file(): raise ArtifactError("regular artifact required")
    if target.suffix!=EXTENSIONS.get(expected_schema): raise ArtifactError("artifact type mismatch")
    raw=target.read_bytes()
    if not raw or len(raw)>MAX_ARTIFACT_BYTES: raise ArtifactError("invalid artifact size")
    try: wrapper=json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise ArtifactError("invalid artifact JSON") from exc
    if not isinstance(wrapper,dict) or set(wrapper)!={"payload","artifactSha256"}: raise ArtifactError("invalid artifact wrapper")
    payload=wrapper["payload"]
    if not isinstance(payload,dict) or payload.get("schema")!=expected_schema: raise ArtifactError("artifact schema mismatch")
    canonical=json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    if not secrets.compare_digest(hashlib.sha256(canonical).hexdigest(),wrapper["artifactSha256"]): raise ArtifactError("artifact hash mismatch")
    return payload

def write_psbt(root: Path,name: str,content: bytes,*,overwrite: bool=False) -> tuple[Path,str]:
    if not isinstance(content,bytes) or not content.startswith(PSBT_MAGIC) or len(content)>MAX_ARTIFACT_BYTES: raise ArtifactError("invalid PSBT artifact")
    root=root.resolve(); root.mkdir(mode=0o700,parents=True,exist_ok=True); target=_target(root,name)
    if target.suffix!=".psbt": raise ArtifactError("artifact extension mismatch")
    if target.is_symlink(): raise ArtifactError("symlink target rejected")
    if target.exists() and not overwrite: raise FileExistsError(target.name)
    temp=root/f".cw-write-{secrets.token_hex(12)}.tmp"
    try:
        fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,"wb") as stream: stream.write(content); stream.flush(); os.fsync(stream.fileno())
        if target.is_symlink(): raise ArtifactError("symlink target rejected")
        os.replace(temp,target); return target,hashlib.sha256(content).hexdigest()
    finally:
        if temp.exists(): temp.unlink()

def read_psbt(root: Path,name: str,*,expected_sha256: str|None=None) -> bytes:
    target=_target(root,name)
    if target.suffix!=".psbt" or target.is_symlink() or not target.is_file(): raise ArtifactError("regular PSBT artifact required")
    content=target.read_bytes()
    if not content.startswith(PSBT_MAGIC) or len(content)>MAX_ARTIFACT_BYTES: raise ArtifactError("invalid PSBT artifact")
    digest=hashlib.sha256(content).hexdigest()
    if expected_sha256 is not None and not secrets.compare_digest(digest,expected_sha256): raise ArtifactError("artifact hash mismatch")
    return content
