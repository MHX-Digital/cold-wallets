"""Fail-closed Tor HTTP adapter using an injected requests-compatible session."""
from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlsplit

class TorTransportError(RuntimeError): pass
class TorConfigurationError(TorTransportError): pass
class TorTimeoutError(TorTransportError): pass
class TorTLSError(TorTransportError): pass
class TorResponseError(TorTransportError): pass

@dataclass(frozen=True)
class TorPolicy:
    proxy_url: str
    connect_timeout: float=5.0
    read_timeout: float=15.0
    max_response_bytes: int=1024*1024
    retries: int=1

class TorHttpClient:
    def __init__(self,session,policy: TorPolicy):
        if not policy.proxy_url.startswith("socks5h://"): raise TorConfigurationError("socks5h proxy required")
        if policy.retries<0 or policy.retries>3: raise TorConfigurationError("invalid retry limit")
        self._session=session; self._policy=policy
        session.trust_env=False
        session.proxies={"http":policy.proxy_url,"https":policy.proxy_url}
    def request(self,method: str,url: str,**kwargs):
        if urlsplit(url).scheme!="https": raise TorTLSError("HTTPS required")
        kwargs.update(timeout=(self._policy.connect_timeout,self._policy.read_timeout),allow_redirects=False,verify=True)
        last=None
        for _ in range(self._policy.retries+1):
            try:
                response=self._session.request(method,url,**kwargs)
                if 300<=response.status_code<400: raise TorResponseError("redirect rejected")
                content=response.content
                if len(content)>self._policy.max_response_bytes: raise TorResponseError("response too large")
                return response
            except TimeoutError as exc: last=TorTimeoutError("Tor request timed out")
        raise last or TorTransportError("Tor request failed closed")
    def get(self,url: str,**kwargs): return self.request("GET",url,**kwargs)
    def post(self,url: str,**kwargs): return self.request("POST",url,**kwargs)

def redact_url(url: str) -> str:
    parts=urlsplit(url)
    return f"{parts.scheme}://{parts.hostname or '<invalid>'}/<redacted>"
