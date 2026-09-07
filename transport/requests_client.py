"""The sole production import boundary for requests."""
from __future__ import annotations
import requests
from transport.tor_http import TorHttpClient, TorPolicy, TorTransportError

TOR_CHECK="https://check.torproject.org/api/ip"

def build_verified_tor_client(ports=(9150,9050)):
    errors=[]
    for port in ports:
        client=TorHttpClient(requests.Session(),TorPolicy(f"socks5h://127.0.0.1:{port}"))
        try:
            response=client.get(TOR_CHECK)
            if response.status_code==200 and response.json().get("IsTor") is True: return client
        except Exception as exc: errors.append(type(exc).__name__)
    raise TorTransportError("Tor verification failed closed")
