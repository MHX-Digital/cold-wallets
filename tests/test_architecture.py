import ast, unittest
from pathlib import Path

def imports(path):
    tree=ast.parse(path.read_text(encoding="utf-8")); result=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import): result.update(a.name.split('.')[0] for a in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module: result.add(node.module.split('.')[0])
    return result

class ArchitectureTests(unittest.TestCase):
    def test_trust_boundaries(self):
        self.assertFalse(imports(Path("dashboard/server.py")) & {"signer","cold_wallets","requests","socket","subprocess"})
        self.assertFalse(imports(Path("signer/ethereum.py")) & {"requests","socket","urllib","dashboard","broadcaster","transport"})
        self.assertFalse(imports(Path("broadcaster/store.py")) & {"signer","cold_wallets","eth_account","bit"})
        self.assertNotIn("signer",imports(Path("coordinator/eth_envelope.py")))
    def test_runtime_install_and_tor_download_are_blocked(self):
        launcher=Path("start.bat").read_text(encoding="utf-8").casefold()
        self.assertNotIn("-m pip install",launcher)
        tor=Path("tools/tor_manager.py").read_text(encoding="utf-8")
        self.assertNotIn("requests.get",tor); self.assertNotIn("extractall",tor)

    def test_python_http_clients_use_central_allowlist(self):
        allow={Path("transport/requests_client.py")}
        offenders=[]
        for path in Path(".").rglob("*.py"):
            if path.parts[0] in {"tests","audit_output"} or path in allow: continue
            names=imports(path)
            if names & {"requests","urllib3","httpx","aiohttp"}: offenders.append(str(path))
        self.assertEqual(offenders,[])

if __name__=="__main__": unittest.main()
