import ast,json,unittest
from pathlib import Path

def imports(path):
    tree=ast.parse(path.read_text(encoding="utf-8")); result=set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Import): result.update(a.name.split('.')[0] for a in node.names)
        elif isinstance(node,ast.ImportFrom) and node.module: result.add(node.module.split('.')[0])
    return result

def local_dependencies(path):
    tree=ast.parse(path.read_text(encoding="utf-8")); result=set()
    for node in ast.walk(tree):
        module=None
        if isinstance(node,ast.ImportFrom): module=node.module
        elif isinstance(node,ast.Import):
            for alias in node.names:
                candidate=Path(*alias.name.split(".")); file=candidate.with_suffix(".py")
                if file.exists(): result.add(file)
        if module:
            candidate=Path(*module.split(".")); file=candidate.with_suffix(".py")
            if file.exists(): result.add(file)
    return result

def reachable(start):
    pending=[Path(start)]; seen=set()
    while pending:
        path=pending.pop()
        if path in seen: continue
        seen.add(path); pending.extend(local_dependencies(path)-seen)
    return seen

class ArchitectureTests(unittest.TestCase):
    def test_legacy_quarantine_is_complete_and_unreachable(self):
        manifest=json.loads(Path("security/legacy_quarantine.json").read_text(encoding="utf-8")); quarantined={Path(item) for item in manifest["scripts"]}
        scripts={path for suffix in ("*.bat","*.cmd","*.ps1") for path in Path(".").rglob(suffix)}
        allowed={Path("start.bat"),Path("requirements/generate-windows-lock.ps1")}
        self.assertEqual(scripts-allowed,quarantined)
        reachable_text=(Path("start.bat").read_text(encoding="utf-8")+Path("dashboard/index.html").read_text(encoding="utf-8")+Path("dashboard/server.py").read_text(encoding="utf-8")).casefold()
        self.assertFalse(any(str(path).casefold() in reachable_text for path in quarantined))
        dangerous=("curl","bitsadmin","invoke-webrequest","invoke-restmethod","start-bitstransfer","pip install","docker pull","runas","net session","netsh advfirewall","disable-netadapter","start-process")
        for path in scripts:
            text=path.read_text(encoding="utf-8",errors="replace").casefold()
            if any(token in text for token in dangerous): self.assertIn(path,quarantined)
    def test_trust_boundaries(self):
        self.assertFalse(imports(Path("dashboard/server.py")) & {"signer","cold_wallets","requests","socket","subprocess"})
        self.assertFalse(imports(Path("signer/ethereum.py")) & {"requests","socket","urllib","dashboard","broadcaster","transport"})
        self.assertFalse(imports(Path("broadcaster/store.py")) & {"signer","cold_wallets","eth_account","bit"})
        self.assertNotIn("signer",imports(Path("coordinator/eth_envelope.py")))
        dashboard_tree=reachable("dashboard/server.py")
        self.assertFalse(any(path.parts[0] in {"signer","cold_wallets"} for path in dashboard_tree))
        for path in Path("signer").glob("*.py"):
            self.assertFalse(imports(path) & {"requests","socket","urllib","dashboard","broadcaster","transport"},str(path))
        for path in Path("broadcaster").glob("*.py"):
            self.assertFalse(imports(path) & {"signer","cold_wallets"},str(path))
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

    def test_new_architecture_never_imports_or_declares_legacy_bit_package(self):
        roots=("dashboard","coordinator","signer","broadcaster","transport")
        offenders=[]
        for root in roots:
            for path in Path(root).rglob("*.py"):
                if "bit" in imports(path): offenders.append(str(path))
        declarations="\n".join(path.read_text(encoding="utf-8") for path in Path("requirements").glob("*.in"))
        self.assertEqual(offenders,[])
        self.assertNotRegex(declarations,r"(?m)^bit(?:==|$)")

    def test_primary_launcher_is_unprivileged_and_foreground_only(self):
        launcher=Path("start.bat").read_text(encoding="utf-8").casefold()
        for forbidden in ("runas","net session","curl ","start \"cold wallets server\"","tor_manager","sign_btc","sign_eth","generate_wallets"):
            self.assertNotIn(forbidden,launcher)
        self.assertIn("dashboard\\server.py",launcher)

    def test_replaced_network_entrypoints_fail_before_legacy_imports(self):
        for name in ("cold_wallets/tools/fetch_tx_data.py","cold_wallets/tools/broadcast_tor.py","tools/eth_rpc_proxy.py"):
            tree=ast.parse(Path(name).read_text(encoding="utf-8")); statements=tree.body
            if statements and isinstance(statements[0],ast.Expr) and isinstance(statements[0].value,ast.Constant): statements=statements[1:]
            self.assertIsInstance(statements[0],ast.Raise,name)

if __name__=="__main__": unittest.main()
