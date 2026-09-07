import json
import ast
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from dashboard import server as dashboard
from broadcaster.store import BroadcastStore
from coordinator.api import WatchOnlyApi
from coordinator.disposable_store import DisposableStore
from coordinator.proposal_store import ProposalStore
from coordinator.service import CoordinatorService


class DashboardSecurityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.run_id = uuid.uuid4().hex
        cls.temp = tempfile.TemporaryDirectory(
            prefix=f"cold-wallets-test-{cls.run_id}-")
        cls.temp_path = Path(cls.temp.name).resolve()
        cls.manifest = [{
            "id": cls.run_id,
            "type": "temporary-directory",
            "path": str(cls.temp_path),
            "owner": "DashboardSecurityTests",
            "created_at": time.time(),
            "cleanup": "TemporaryDirectory.cleanup",
            "cleaned": False,
        }]
        dashboard._load_html()
        coordinator=CoordinatorService(ProposalStore(cls.temp_path/"proposals.sqlite"),DisposableStore(cls.temp_path/"disposable.sqlite"))
        dashboard.WORKFLOW_API=WatchOnlyApi(coordinator,BroadcastStore(cls.temp_path/"broadcast.sqlite"))
        coordinator.disposable.add("synthetic-address","bitcoin","mainnet","keyref:test")
        cls.httpd = dashboard.ThreadedHTTPServer(
            ("127.0.0.1", 0), dashboard.DashboardHandler)
        cls.port = cls.httpd.server_address[1]
        cls.manifest.append({
            "id": cls.run_id,
            "type": "http-server-thread",
            "port": cls.port,
            "owner": "DashboardSecurityTests",
            "created_at": time.time(),
            "cleanup": "shutdown/server_close/join",
            "cleaned": False,
        })
        cls.thread = threading.Thread(
            target=cls.httpd.serve_forever,
            name=f"cold-wallets-test-{cls.run_id}", daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=5)
        dashboard.WORKFLOW_API=None
        if cls.thread.is_alive():
            raise AssertionError("owned HTTP server thread did not stop")
        cls.manifest[1]["cleaned"] = True
        cls.temp.cleanup()
        cls.manifest[0]["cleaned"] = not cls.temp_path.exists()
        if not all(resource["cleaned"] for resource in cls.manifest):
            raise AssertionError(f"test resource residue: {cls.manifest!r}")
        print(
            "TEST_RESOURCE_SUMMARY "
            f"run_id={cls.run_id} port={cls.port} "
            "processes=0 containers=0 networks=0 volumes=0 residue=0"
        )

    @classmethod
    def request(cls, path, *, method="GET", body=None, headers=None):
        request = urllib.request.Request(
            f"http://127.0.0.1:{cls.port}{path}",
            data=body,
            method=method,
            headers=headers or {},
        )
        try:
            response = urllib.request.urlopen(request, timeout=3)
            return response.status, response.headers, response.read()
        except urllib.error.HTTPError as error:
            return error.code, error.headers, error.read()

    @classmethod
    def json_headers(cls, **extra):
        headers = {
            "Content-Type": "application/json",
            "X-Session-Token": dashboard.SESSION_TOKEN,
            "Origin": f"http://127.0.0.1:{cls.port}",
        }
        headers.update(extra)
        return headers

    def test_exact_routes_and_security_headers(self):
        status, headers, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertNotIn(b'id="bw"', body)
        self.assertNotIn(b'id="ep"', body)
        self.assertIn(b"not a cold wallet", body)
        status, _, _ = self.request("/unknown")
        self.assertEqual(status, 404)
        status, _, _ = self.request("/api/status")
        self.assertEqual(status, 404)

    def test_invalid_host_origin_and_token_are_rejected(self):
        body = b"{}"
        status, _, _ = self.request(
            "/api/status", method="POST", body=body,
            headers=self.json_headers(Host="attacker.invalid"))
        self.assertEqual(status, 403)
        status, _, _ = self.request(
            "/api/status", method="POST", body=body,
            headers=self.json_headers(Origin="https://attacker.invalid"))
        self.assertEqual(status, 403)
        headers = self.json_headers()
        headers.pop("X-Session-Token")
        status, _, _ = self.request(
            "/api/status", method="POST", body=body, headers=headers)
        self.assertEqual(status, 403)

    def test_content_type_and_body_limit_are_enforced(self):
        status, _, _ = self.request(
            "/api/status", method="POST", body=b"{}",
            headers={
                "Content-Type": "text/plain",
                "X-Session-Token": dashboard.SESSION_TOKEN,
            })
        self.assertEqual(status, 415)
        oversized = b" " * (dashboard.MAX_REQUEST_BODY + 1)
        status, _, _ = self.request(
            "/api/status", method="POST", body=oversized,
            headers=self.json_headers())
        self.assertEqual(status, 413)

    def test_private_key_routes_fail_closed(self):
        payload = json.dumps({"wif": "test-sentinel-not-a-key"}).encode()
        status, _, body = self.request(
            "/api/send-btc", method="POST", body=payload,
            headers=self.json_headers())
        self.assertEqual(status, 404)
        self.assertNotIn(b"test-sentinel", body)

        payload = json.dumps({"private_key": "test-sentinel"}).encode()
        status, _, body = self.request(
            "/api/status", method="POST", body=payload,
            headers=self.json_headers())
        self.assertEqual(status, 400)
        self.assertNotIn(b"test-sentinel", body)

    def test_dashboard_import_boundary(self):
        source = Path(dashboard.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        forbidden = {"signer", "cold_wallets", "requests", "socket", "subprocess"}
        self.assertFalse(imported & forbidden)
        self.assertFalse(hasattr(dashboard, "COLD_WALLETS"))
        self.assertEqual(set(dashboard.API_ROUTES), {"/api/status"})

    def test_frontend_has_no_secret_controls_or_legacy_calls(self):
        html = dashboard._HTML_CACHE.lower()
        for marker in (b"private_key", b"sign-eth", b"sign-btc",
                       b"send-eth", b"send-btc", b"generate-wallets"):
            self.assertNotIn(marker, html)

    def test_unsupported_method_is_rejected(self):
        status, _, _ = self.request(
            "/api/status", method="PUT", body=b"{}",
            headers=self.json_headers())
        self.assertEqual(status, 405)

    def test_watch_only_proposal_export_get_and_idempotency(self):
        payload={"from":"0x"+"11"*20,"to":"0x"+"22"*20,"valueWei":"3","nonce":"0","gasLimit":"21000","maxFeePerGasWei":"100","maxPriorityFeePerGasWei":"2","data":"0x","sources":[],"confirmNetwork":"ethereum-mainnet"}
        key="test-idempotency-key-0001"; headers=self.json_headers(**{"Idempotency-Key":key})
        status,_,body=self.request("/api/proposals/ethereum",method="POST",body=json.dumps(payload).encode(),headers=headers)
        self.assertEqual(status,200); proposal=json.loads(body); proposal_id=proposal["proposalId"]
        status,_,body=self.request(f"/api/proposals/{proposal_id}",headers=self.json_headers())
        self.assertEqual(status,200); self.assertEqual(json.loads(body)["state"],"PREPARED")
        status,_,body=self.request("/api/artifacts/export",method="POST",body=json.dumps({"proposalId":proposal_id}).encode(),headers=self.json_headers(**{"Idempotency-Key":"test-export-key-00001"}))
        self.assertEqual(status,200); self.assertEqual(json.loads(body)["payload"]["proposalId"],proposal_id)
        changed=dict(payload); changed["valueWei"]="4"
        status,_,_=self.request("/api/proposals/ethereum",method="POST",body=json.dumps(changed).encode(),headers=headers)
        self.assertEqual(status,400)

    def test_watch_only_api_rejects_state_txid_and_remote_broadcast(self):
        for payload in ({"state":"CONFIRMED"},{"txid":"client-value"},{"privateKey":"test-sentinel"}):
            status,_,body=self.request("/api/broadcast/register",method="POST",body=json.dumps(payload).encode(),headers=self.json_headers(**{"Idempotency-Key":"test-register-key-01"}))
            self.assertIn(status,{400}); self.assertNotIn(b"test-sentinel",body)
        status,_,body=self.request("/api/disposable/reserve",method="POST",body=b'{"requestId":"request-1"}',headers=self.json_headers(**{"Idempotency-Key":"test-reserve-key-0001"}))
        self.assertEqual(status,200); result=json.loads(body); self.assertEqual(result["state"],"RESERVED")


if __name__ == "__main__":
    unittest.main()
