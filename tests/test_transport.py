import json, os, tempfile, unittest, uuid
from pathlib import Path
from transport.artifacts import ArtifactError, read, write
from transport.tor_http import TorConfigurationError, TorHttpClient, TorPolicy, TorResponseError, TorTLSError, redact_url

class Response:
    def __init__(self,status=200,content=b"{}"): self.status_code=status; self.content=content
class Session:
    def __init__(self,response=None): self.response=response or Response(); self.calls=[]; self.trust_env=True; self.proxies={}
    def request(self,*args,**kwargs): self.calls.append((args,kwargs)); return self.response

class TransportTests(unittest.TestCase):
    def setUp(self):
        self.run_id=uuid.uuid4().hex; self.temp=tempfile.TemporaryDirectory(prefix=f"cold-wallets-test-{self.run_id}-"); self.root=Path(self.temp.name)
    def tearDown(self): self.temp.cleanup()
    def payload(self): return {"schema":"cold-wallets.eth-tx","version":1,"value":"0"}
    def test_artifact_round_trip_and_overwrite(self):
        write(self.root,"proposal.cw-eth-proposal",self.payload())
        self.assertEqual(read(self.root,"proposal.cw-eth-proposal",expected_schema="cold-wallets.eth-tx"),self.payload())
        with self.assertRaises(FileExistsError): write(self.root,"proposal.cw-eth-proposal",self.payload())
    def test_artifact_rejects_traversal_symlink_and_tamper(self):
        with self.assertRaises(ArtifactError): write(self.root,"../escape.cw-eth-proposal",self.payload())
        target=self.root/"target"; target.write_text("x"); link=self.root/"link.cw-eth-proposal"; link.symlink_to(target)
        with self.assertRaises(ArtifactError): read(self.root,link.name,expected_schema="cold-wallets.eth-tx")
        path=write(self.root,"p.cw-eth-proposal",self.payload()); data=json.loads(path.read_text()); data["payload"]["value"]="1"; path.write_text(json.dumps(data))
        with self.assertRaises(ArtifactError): read(self.root,path.name,expected_schema="cold-wallets.eth-tx")
    def test_tor_policy_is_fail_closed(self):
        with self.assertRaises(TorConfigurationError): TorHttpClient(Session(),TorPolicy("http://127.0.0.1:9050"))
        session=Session(); client=TorHttpClient(session,TorPolicy("socks5h://127.0.0.1:9050"))
        with self.assertRaises(TorTLSError): client.request("GET","http://example.invalid/x")
        self.assertFalse(session.trust_env); self.assertEqual(session.proxies["https"],"socks5h://127.0.0.1:9050")
        self.assertNotIn("secret",redact_url("https://example.invalid/secret?address=abc"))
    def test_tor_rejects_redirect_and_oversize(self):
        with self.assertRaises(TorResponseError): TorHttpClient(Session(Response(302)),TorPolicy("socks5h://127.0.0.1:9050")).request("GET","https://example.invalid")
        with self.assertRaises(TorResponseError): TorHttpClient(Session(Response(content=b"xx")),TorPolicy("socks5h://127.0.0.1:9050",max_response_bytes=1)).request("GET","https://example.invalid")

if __name__=="__main__": unittest.main()
