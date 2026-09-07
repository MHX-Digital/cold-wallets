#!/usr/bin/env python3
"""
VERIFICADOR DE CONEXAO TOR
Verifica se o Tor esta funcionando e mostra o IP de saida.
Nunca expoe o IP real — toda verificacao passa pelo proxy Tor.
"""

import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent.parent))
from transport.requests_client import build_verified_tor_client


def check_tor():
    print("\n=== VERIFICADOR DE CONEXAO TOR ===\n")

    proxies_to_try = [
        ("Tor Browser (9150)", "socks5h://127.0.0.1:9150"),
        ("Tor Daemon (9050)", "socks5h://127.0.0.1:9050"),
    ]

    for name, proxy in proxies_to_try:
        print(f"[*] Testando {name}...")

        try:
            port=int(proxy.rsplit(':',1)[1])
            session=build_verified_tor_client(ports=(port,))
            response=session.get('https://check.torproject.org/api/ip')
            data = response.json()

            if data.get('IsTor'):
                print("    [OK] Conectado ao Tor!")
                print(f"    [+] IP de saida: {data.get('IP')}")
                print(f"    [+] Proxy: {proxy}")
                return True
            else:
                print("    [!] Conectado mas NAO via Tor")

        except Exception:
            print("    [-] Tor indisponivel ou verificacao falhou")

    print("\n[!] NENHUMA CONEXAO TOR ENCONTRADA!")
    print("\n    Solucoes:")
    print("    1. Abra o Tor Browser")
    print("    2. Ou inicie o Tor daemon")
    print("    3. Verifique firewall/antivirus")

    return False


if __name__ == "__main__":
    tor_ok = check_tor()

    print("\n" + "=" * 50)
    if tor_ok:
        print("  STATUS: TOR FUNCIONANDO")
        print("  Voce pode usar os scripts com privacidade.")
    else:
        print("  STATUS: TOR NAO CONECTADO")
        print("  Inicie o Tor Browser antes de continuar!")
    print("=" * 50 + "\n")

    input("Pressione Enter para sair...")
