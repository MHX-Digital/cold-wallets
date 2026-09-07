"""Versioned authenticated storage backed by reviewed AES-GCM and scrypt."""
from __future__ import annotations
import base64,binascii,hashlib,json,secrets
from pathlib import Path
from transport.artifacts import read,write

SCHEMA="cold-wallets.authenticated-store"
FIELDS={"schema","version","kdf","cipher","metadata","ciphertext","tag"}
MAX_PLAINTEXT=1024*1024
SCRYPT_N=2**14
SCRYPT_R=8
SCRYPT_P=1
SCRYPT_DKLEN=32
SALT_BYTES=16
NONCE_BYTES=12
TAG_BYTES=16
MIN_PASSWORD_BYTES=12

class StorageError(ValueError): pass
class StorageBackendUnavailable(StorageError): pass

def _aes():
    try: from Crypto.Cipher import AES
    except ImportError as exc: raise StorageBackendUnavailable("reviewed AES-GCM backend is unavailable") from exc
    return AES

def _b64(value: bytes): return base64.b64encode(value).decode("ascii")
def _unb64(value,name,max_decoded):
    if not isinstance(value,str): raise StorageError(f"invalid {name}")
    if len(value)>4*((max_decoded+2)//3): raise StorageError(f"invalid {name}")
    try: decoded=base64.b64decode(value,validate=True)
    except (ValueError,binascii.Error) as exc: raise StorageError(f"invalid {name}") from exc
    if len(decoded)>max_decoded: raise StorageError(f"invalid {name}")
    return decoded

def _password(value):
    if not isinstance(value,bytes) or len(value)<MIN_PASSWORD_BYTES: raise StorageError("invalid password material")
    return value

def _aad(envelope):
    header={key:envelope[key] for key in ("schema","version","kdf","cipher","metadata")}
    return json.dumps(header,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()

def _secret_field(value):
    if isinstance(value,dict): return any(str(key).casefold().replace("-","_") in {"password","private_key","privatekey","seed","seed_phrase","mnemonic","wif"} or _secret_field(item) for key,item in value.items())
    if isinstance(value,list): return any(_secret_field(item) for item in value)
    return False

def seal(plaintext: bytes,password: bytes,metadata: dict):
    if not isinstance(plaintext,bytes) or len(plaintext)>MAX_PLAINTEXT: raise StorageError("invalid plaintext size")
    password=_password(password)
    if not isinstance(metadata,dict) or _secret_field(metadata): raise StorageError("invalid metadata")
    salt=secrets.token_bytes(SALT_BYTES); nonce=secrets.token_bytes(NONCE_BYTES)
    key=hashlib.scrypt(password,salt=salt,n=SCRYPT_N,r=SCRYPT_R,p=SCRYPT_P,dklen=SCRYPT_DKLEN)
    envelope={"schema":SCHEMA,"version":1,"kdf":{"name":"scrypt","salt":_b64(salt),"n":SCRYPT_N,"r":SCRYPT_R,"p":SCRYPT_P,"dkLen":SCRYPT_DKLEN},"cipher":{"name":"AES-256-GCM","nonce":_b64(nonce)},"metadata":metadata,"ciphertext":"","tag":""}
    cipher=_aes().new(key,_aes().MODE_GCM,nonce=nonce,mac_len=TAG_BYTES); cipher.update(_aad(envelope)); ciphertext,tag=cipher.encrypt_and_digest(plaintext)
    envelope["ciphertext"]=_b64(ciphertext); envelope["tag"]=_b64(tag)
    return envelope

def open_sealed(envelope: dict,password: bytes):
    if not isinstance(envelope,dict) or set(envelope)!=FIELDS or envelope.get("schema")!=SCHEMA or envelope.get("version")!=1: raise StorageError("unsupported authenticated storage")
    password=_password(password)
    kdf=envelope.get("kdf"); cipher_spec=envelope.get("cipher")
    if kdf is None or set(kdf)!={"name","salt","n","r","p","dkLen"} or kdf["name"]!="scrypt" or (kdf["n"],kdf["r"],kdf["p"],kdf["dkLen"])!=(SCRYPT_N,SCRYPT_R,SCRYPT_P,SCRYPT_DKLEN): raise StorageError("KDF policy mismatch")
    if cipher_spec is None or set(cipher_spec)!={"name","nonce"} or cipher_spec["name"]!="AES-256-GCM": raise StorageError("cipher policy mismatch")
    if not isinstance(envelope.get("metadata"),dict) or _secret_field(envelope["metadata"]): raise StorageError("invalid metadata")
    salt=_unb64(kdf["salt"],"salt",SALT_BYTES); nonce=_unb64(cipher_spec["nonce"],"nonce",NONCE_BYTES); ciphertext=_unb64(envelope["ciphertext"],"ciphertext",MAX_PLAINTEXT); tag=_unb64(envelope["tag"],"tag",TAG_BYTES)
    if len(salt)!=SALT_BYTES or len(nonce)!=NONCE_BYTES or len(tag)!=TAG_BYTES: raise StorageError("storage limits violated")
    key=hashlib.scrypt(password,salt=salt,n=kdf["n"],r=kdf["r"],p=kdf["p"],dklen=kdf["dkLen"])
    try:
        aes=_aes().new(key,_aes().MODE_GCM,nonce=nonce,mac_len=TAG_BYTES); aes.update(_aad(envelope)); return aes.decrypt_and_verify(ciphertext,tag)
    except (ValueError,KeyError,TypeError) as exc: raise StorageError("authentication failed") from exc

def write_vault(root: Path,name: str,plaintext: bytes,password: bytes,metadata: dict): return write(root,name,seal(plaintext,password,metadata))
def read_vault(root: Path,name: str,password: bytes): return open_sealed(read(root,name,expected_schema=SCHEMA),password)
