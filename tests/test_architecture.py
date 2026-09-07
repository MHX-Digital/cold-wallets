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
    def test_legacy_paths_are_physically_absent(self):
        forbidden=(
            "cold_wallets/generate_wallets.py","cold_wallets/sign_btc.py","cold_wallets/sign_eth.py",
            "cold_wallets/enviar_btc.py","cold_wallets/enviar_eth.py","cold_wallets/network_control.py",
            "cold_wallets/requirements.txt","cold_wallets/hot_disposable/disposable_manager.py",
            "cold_wallets/hot_disposable/generate_disposable.py","cold_wallets/hot_disposable/sweep_to_cold.py",
            "cold_wallets/tools/fetch_tx_data.py","cold_wallets/tools/broadcast_tor.py",
            "tools/check_tor.py","tools/eth_rpc_proxy.py","tools/tor_manager.py",
            "security/legacy_quarantine.json",
            "rpc/docs/quickstart.md","rpc/docs/runbook.md","rpc/docs/threat-model.md",
            "rpc/helios/config.example.toml","rpc/helios/docker-compose.yml",
            "rpc/l2-templates/arbitrum/docker-compose.yml","rpc/l2-templates/optimism/docker-compose.yml",
            "rpc/reverse-proxy/docker-compose.yml","rpc/reverse-proxy/nginx.conf",
            "rpc/tor/docker-compose.yml","rpc/tor/torrc",
            "rpc/wireguard/client.conf.example","rpc/wireguard/wg0.conf.example",
        )
        self.assertEqual([name for name in forbidden if Path(name).exists()],[])

    def test_rpc_placeholders_are_disabled_and_nonexecutable(self):
        files={path for path in Path("rpc").rglob("*") if path.is_file()}
        expected={Path("rpc/README.md"),Path("rpc/helios/attestation.example.json"),Path("rpc/tor/transport-policy.example.json")}
        self.assertEqual(files,expected)
        helios=json.loads(Path("rpc/helios/attestation.example.json").read_text(encoding="utf-8"))
        self.assertEqual(helios["schema"],"cold-wallets.helios-attestation")
        self.assertEqual(helios["state"],"HELIOS_UNATTESTED")
        self.assertIs(helios["enabled"],False)
        self.assertEqual(helios["bind"],"127.0.0.1")
        self.assertIsNone(helios["imageDigest"]); self.assertIsNone(helios["binarySha256"])
        self.assertIsNone(helios["checkpoint"]); self.assertIsNone(helios["upstream"])
        self.assertEqual(len(helios["requiredEvidence"]),8)
        tor=json.loads(Path("rpc/tor/transport-policy.example.json").read_text(encoding="utf-8"))
        self.assertEqual(tor["schema"],"cold-wallets.tor-transport-policy")
        self.assertEqual(tor["state"],"TOR_UNATTESTED")
        self.assertIs(tor["enabled"],False); self.assertIs(tor["autoStart"],False)
        self.assertIs(tor["clearnetFallback"],False); self.assertIs(tor["hiddenService"],False)
        self.assertEqual(tor["proxy"],"socks5h://127.0.0.1:9050")
        self.assertEqual(tor["bind"],"127.0.0.1")
        self.assertIsNone(tor["binarySha256"]); self.assertIsNone(tor["configSha256"])

    def test_only_reviewed_windows_scripts_remain(self):
        scripts={path for suffix in ("*.bat","*.cmd","*.ps1") for path in Path(".").rglob(suffix)}
        self.assertEqual(scripts,{
            Path("start.bat"),Path("requirements/generate-windows-lock.ps1"),
            Path("validation/windows/c8-preflight.ps1"),Path("validation/windows/c8-python-matrix.ps1"),
        })
        dangerous=("curl","bitsadmin","certutil","invoke-webrequest","invoke-restmethod","start-bitstransfer","pip install","docker pull","runas","net session","netsh advfirewall","disable-netadapter","enable-netadapter")
        for path in scripts:
            text=path.read_text(encoding="utf-8",errors="replace").casefold()
            checked=dangerous if path!=Path("validation/windows/c8-python-matrix.ps1") else tuple(token for token in dangerous if token!="pip install")
            self.assertFalse(any(token in text for token in checked),str(path))

    def test_c8_windows_harness_is_native_only_and_fail_closed(self):
        preflight=Path("validation/windows/c8-preflight.ps1").read_text(encoding="utf-8").casefold()
        matrix=Path("validation/windows/c8-python-matrix.ps1").read_text(encoding="utf-8").casefold()
        for text in (preflight,matrix):
            self.assertIn("osplatform]::windows",text)
            self.assertNotIn("invoke-webrequest",text)
            self.assertNotIn("invoke-restmethod",text)
            self.assertNotIn("start-process",text)
            self.assertNotIn("stop-process",text)
            self.assertNotIn("taskkill",text)
            self.assertNotIn("netsh",text)
        self.assertIn("get-maskedidentifier",preflight)
        self.assertIn("machineidmasked = get-maskedidentifier",preflight)
        self.assertIn("useridmasked = get-maskedidentifier",preflight)
        self.assertIn("--no-index",matrix)
        self.assertIn("--require-hashes",matrix)
        self.assertIn("finally",matrix)
        self.assertIn("cold-wallets-c8-*",matrix)
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
    def test_runtime_install_and_tor_download_are_absent(self):
        launcher=Path("start.bat").read_text(encoding="utf-8").casefold()
        self.assertNotIn("-m pip install",launcher)
        explicit_offline_harness=Path("validation/windows/c8-python-matrix.ps1")
        production=[path for suffix in ("*.py","*.bat","*.cmd","*.ps1") for path in Path(".").rglob(suffix) if path.parts[0] not in {"tests","audit_output",".git"} and path!=explicit_offline_harness]
        corpus="\n".join(path.read_text(encoding="utf-8",errors="replace").casefold() for path in production)
        self.assertNotRegex(corpus,r"(?:pip\s+install|requests\.get\([^)]*(?:tor|\.zip)|urlretrieve\()")
        harness=explicit_offline_harness.read_text(encoding="utf-8").casefold()
        self.assertIn("--no-index",harness); self.assertIn("--require-hashes",harness)
        self.assertNotRegex(harness,r"(?:invoke-webrequest|invoke-restmethod|curl\s|urlretrieve\()")

    def test_python_http_clients_use_central_allowlist(self):
        allow={Path("transport/requests_client.py")}
        offenders=[]
        for path in Path(".").rglob("*.py"):
            if path.parts[0] in {"tests","audit_output"} or path in allow: continue
            names=imports(path)
            if names & {"requests","urllib3","httpx","aiohttp"}: offenders.append(str(path))
        self.assertEqual(offenders,[])

    def test_repository_never_imports_or_declares_legacy_bit_package(self):
        roots=("dashboard","coordinator","signer","broadcaster","transport","storage","cold_wallets")
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

    def test_no_parallel_broadcaster_or_secret_entrypoint(self):
        python_files={path for path in Path(".").rglob("*.py") if path.parts[0] not in {"tests","audit_output"}}
        forbidden_names={"generate_wallets.py","sign_btc.py","sign_eth.py","enviar_btc.py","enviar_eth.py","broadcast_tor.py","eth_rpc_proxy.py"}
        self.assertEqual([str(path) for path in python_files if path.name in forbidden_names],[])

if __name__=="__main__": unittest.main()
