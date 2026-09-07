#!/usr/bin/env python3
"""Local watch-only coordinator UI; deliberately has no key/signing/network code."""
from __future__ import annotations
import hmac, json, secrets, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

DASHBOARD_DIR=Path(__file__).resolve().parent
PORT=8888
MAX_REQUEST_BODY=64*1024
REQUEST_TIMEOUT_SECONDS=5
SESSION_TOKEN=secrets.token_urlsafe(32)
_HTML_CACHE: bytes|None=None
_SECRET_FIELDS=frozenset({"private_key","privatekey","mnemonic","seed","seed_phrase","wif"})

def _load_html():
    global _HTML_CACHE
    _HTML_CACHE=(DASHBOARD_DIR/"index.html").read_text(encoding="utf-8").replace("__SESSION_TOKEN__",SESSION_TOKEN).encode()

def _contains_secret_field(value):
    if isinstance(value,dict):
        return any(str(k).casefold().replace("-","_") in _SECRET_FIELDS or _contains_secret_field(v) for k,v in value.items())
    return isinstance(value,list) and any(_contains_secret_field(v) for v in value)

def get_system_status():
    return {"role":"online-watch-only-coordinator","signing":False,"key_storage":False,"network_status":"not-verified","rpc_status":"not-verified"}

API_ROUTES={"/api/status":lambda _data:get_system_status()}

class DashboardHandler(BaseHTTPRequestHandler):
    server_version="ColdWalletCoordinator"; sys_version=""
    def log_message(self,_format,*_args): return
    def _security_headers(self):
        for key,value in (("X-Content-Type-Options","nosniff"),("X-Frame-Options","DENY"),("Referrer-Policy","no-referrer"),("Cache-Control","no-store")):
            self.send_header(key,value)
        self.send_header("Content-Security-Policy","default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
    def _send_json(self,value,status=200):
        body=json.dumps(value,separators=(",",":")).encode(); self.send_response(status)
        self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self._security_headers(); self.end_headers(); self.wfile.write(body)
    def _valid_host(self):
        port=self.server.server_address[1]
        return self.headers.get("Host","").casefold() in {f"127.0.0.1:{port}",f"localhost:{port}"}
    def _authorized(self):
        port=self.server.server_address[1]; origin=self.headers.get("Origin")
        valid_origin=origin is None or origin.casefold() in {f"http://127.0.0.1:{port}",f"http://localhost:{port}"}
        return valid_origin and hmac.compare_digest(self.headers.get("X-Session-Token",""),SESSION_TOKEN)
    def do_GET(self):
        path=self.path.partition("?")[0]
        if not self._valid_host(): self._send_json({"error":"Invalid Host"},403)
        elif path=="/favicon.ico": self.send_response(204); self._security_headers(); self.end_headers()
        elif path in {"/","/index.html"}:
            if _HTML_CACHE is None: self._send_json({"error":"Internal server error"},500); return
            self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(_HTML_CACHE))); self._security_headers(); self.end_headers(); self.wfile.write(_HTML_CACHE)
        else: self._send_json({"error":"Not found"},404)
    def do_POST(self):
        handler=API_ROUTES.get(self.path.partition("?")[0])
        if handler is None: self._send_json({"error":"Not found"},404); return
        if not self._valid_host() or not self._authorized(): self._send_json({"error":"Request rejected"},403); return
        if self.headers.get("Transfer-Encoding"): self._send_json({"error":"Transfer-Encoding not supported"},400); return
        if self.headers.get_content_type()!="application/json": self._send_json({"error":"Content-Type must be application/json"},415); return
        try:
            raw=self.headers.get("Content-Length"); length=int(raw) if raw is not None else -1
            if length<0 or length>MAX_REQUEST_BODY: self._send_json({"error":"Request body too large"},413); return
            data=json.loads(self.rfile.read(length) if length else b"{}")
            if not isinstance(data,dict): raise ValueError
        except (ValueError,json.JSONDecodeError): self._send_json({"error":"Invalid JSON body"},400); return
        if _contains_secret_field(data): self._send_json({"error":"Secret-bearing payload rejected"},400); return
        try: self._send_json(handler(data))
        except Exception: self._send_json({"error":"Internal server error"},500)
    def _method_not_allowed(self): self._send_json({"error":"Method not allowed"},405)
    do_OPTIONS=do_PUT=do_DELETE=do_PATCH=_method_not_allowed

class ThreadedHTTPServer(HTTPServer):
    allow_reuse_address=True
    def get_request(self):
        request,address=super().get_request(); request.settimeout(REQUEST_TIMEOUT_SECONDS); return request,address
    def process_request(self,request,client_address): threading.Thread(target=self.process_request_thread,args=(request,client_address),daemon=True).start()
    def process_request_thread(self,request,client_address):
        try: self.finish_request(request,client_address)
        finally: self.shutdown_request(request)

def main():
    _load_html(); server=ThreadedHTTPServer(("127.0.0.1",PORT),DashboardHandler)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=="__main__": main()
