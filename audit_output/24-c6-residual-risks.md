# C6 residual risks

Product verdict remains **NO-GO**.

1. Bitcoin signing is deliberately disabled: the native backend inside the
   embit sdist is hash-identified but not independently reproduced/audited.
2. Bitcoin has no completed signer-to-broadcaster end-to-end test and no Bitcoin
   Core regtest comparison. Current `bitcoin_txid` handling also needs independent
   SegWit verification before production use.
3. Legacy key/sign/send/disposable scripts and their dependency declaration
   remain physically present because their directory is read-only to this audit
   process. Several are directly invocable and import the removed legacy package.
4. Thirty-nine non-primary Batch/PowerShell scripts remain. Some contain direct
   curl/PowerShell networking, autoelevation, downloads, Docker, firewall, adapter,
   or disk operations. They are not reachable from `start.bat`, but manual use is
   not safe or supported.
5. Ethereum proposals still depend on unverified remote nonce/balance/fee inputs.
   The signer validates policy and exact intent, not consensus truth.
6. Helios was not started or attested. `HELIOS_ATTESTED` exists only as a strict
   evidence contract; runtime status must remain unverified/unattested.
7. Windows locks, ACLs, filesystem behavior, process isolation, Tor routing,
   Python 3.10/3.14 and operational air-gap behavior are untested.
8. Legacy plaintext key migration and backup/restore remain unvalidated. Python
   cannot promise complete memory zeroization or secure deletion on SSD.
