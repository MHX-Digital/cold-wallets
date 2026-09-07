"""Versioned authenticated storage backed by reviewed AES-GCM and scrypt."""
from __future__ import annotations
import base64,hashlib,json,secrets
from pathlib import Path
from transport.artifacts import read,write

SCHEMA="cold-wallets.authenticated-store"
FIELDS={"schema","version","kdf","cipher","metadata","ciphertext","tag"}
MAX_PLAINTEXT=1024*1024

class StorageError(ValueError): pass
class StorageBackendUnavailable(StorageError): pass

def _aes():
    try: from Crypto.Cipher import AES
    except ImportError as exc: raise StorageBackendUnavailable("reviewed AES-GCM backend is unavailable") from exc
    return AES

def _b64(value: bytes): return base64.b64encode(value).decode("ascii")
def _unb64(value,name):
    if not isinstance(value,str): raise StorageError(f"invalid {name}")
    try: return base64.b64decode(value,validate=True)
    except Exception as exc: raise StorageError(f"invalid {name}") from exc

def _aad(envelope):
    header={key:envelope[key] for key in ("schema","version","kdf","cipher","metadata")}
    return json.dumps(header,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def _secret_field(value):
    if isinstance(value,dict): return any(str(key).casefold().replace("-","_") in {"password","private_key","privatekey","seed","seed_phrase","mnemonic","wif"} or _secret_field(item) for key,item in value.items())
    if isinstance(value,list): return any(_secret_field(item) for item in value)
    return False

def seal(plaintext: bytes,password: bytes,metadata: dict):
    if not isinstance(plaintext,bytes) or len(plaintext)>MAX_PLAINTEXT: raise StorageError("invalid plaintext size")
    if not isinstance(password,bytes) or len(password)<12: raise StorageError("password must be bytes with at least 12 bytes")
    if not isinstance(metadata,dict) or _secret_field(metadata): raise StorageError("invalid metadata")
    salt=secrets.token_bytes(16); nonce=secrets.token_bytes(12); n=2**14; r=8; p=1
    key=hashlib.scrypt(password,salt=salt,n=n,r=r,p=p,dklen=32)
    envelope={"schema":SCHEMA,"version":1,"kdf":{"name":"scrypt","salt":_b64(salt),"n":n,"r":r,"p":p,"dkLen":32},"cipher":{"name":"AES-256-GCM","nonce":_b64(nonce)},"metadata":metadata,"ciphertext":"","tag":""}
    cipher=_aes().new(key,_aes().MODE_GCM,nonce=nonce,mac_len=16); cipher.update(_aad(envelope)); ciphertext,tag=cipher.encrypt_and_digest(plaintext)
    envelope["ciphertext"]=_b64(ciphertext); envelope["tag"]=_b64(tag)
    return envelope

def open_sealed(envelope: dict,password: bytes):
    if not isinstance(envelope,dict) or set(envelope)!=FIELDS or envelope.get("schema")!=SCHEMA or envelope.get("version")!=1: raise StorageError("unsupported authenticated storage")
    kdf=envelope.get("kdf"); cipher_spec=envelope.get("cipher")
    if kdf is None or set(kdf)!={"name","salt","n","r","p","dkLen"} or kdf["name"]!="scrypt" or (kdf["n"],kdf["r"],kdf["p"],kdf["dkLen"])!=(2**14,8,1,32): raise StorageError("KDF policy mismatch")
    if cipher_spec is None or set(cipher_spec)!={"name","nonce"} or cipher_spec["name"]!="AES-256-GCM": raise StorageError("cipher policy mismatch")
    salt=_unb64(kdf["salt"],"salt"); nonce=_unb64(cipher_spec["nonce"],"nonce"); ciphertext=_unb64(envelope["ciphertext"],"ciphertext"); tag=_unb64(envelope["tag"],"tag")
    if len(salt)!=16 or len(nonce)!=12 or len(tag)!=16 or len(ciphertext)>MAX_PLAINTEXT: raise StorageError("storage limits violated")
    key=hashlib.scrypt(password,salt=salt,n=kdf["n"],r=kdf["r"],p=kdf["p"],dklen=kdf["dkLen"])
    try:
        aes=_aes().new(key,_aes().MODE_GCM,nonce=nonce,mac_len=16); aes.update(_aad(envelope)); return aes.decrypt_and_verify(ciphertext,tag)
    except (ValueError,KeyError,TypeError) as exc: raise StorageError("authentication failed") from exc

def write_vault(root: Path,name: str,plaintext: bytes,password: bytes,metadata: dict): return write(root,name,seal(plaintext,password,metadata))
def read_vault(root: Path,name: str,password: bytes): return open_sealed(read(root,name,expected_schema=SCHEMA),password)
