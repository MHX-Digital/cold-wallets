# Security policy

## Supported versions

No Cold Wallets version is approved for production or real funds. Only the
most recent experimental pre-release is eligible for security fixes. Audit
checkpoints and older pre-releases are unsupported experimental evidence, not
production releases.

## Reporting a vulnerability

Use GitHub Private Vulnerability Reporting for this repository. Do not open a
public issue for a suspected vulnerability. Never submit private keys, seeds,
mnemonics, WIFs, tokens, credentials, wallet files, or signed/raw transactions.

Include only the minimum safe evidence:

- affected component and version or commit;
- impact and realistic threat scenario;
- minimal reproduction using public vectors or synthetic fixtures;
- environmental assumptions;
- suggested mitigation, if known.

If Private Vulnerability Reporting is unavailable, contact the verified
repository owner through the private contact method published on the
`MHX-Digital` GitHub organization profile. Do not move sensitive details to a
public channel.

## Response policy

Maintainers will acknowledge receipt when the reporting channel permits,
triage the report, coordinate a correction, and disclose it after a patch or
safe mitigation is available. Timelines depend on severity and reproducibility.
This project does not promise a financial bug bounty or reward.

## In scope

- watch-only coordinator and Dashboard;
- offline signer boundaries and transaction validation;
- artifact transport, authenticated storage, and backup/restore;
- persistent broadcaster and idempotency;
- Tor transport adapter and RPC trust classification;
- dependency and build supply chain;
- GitHub workflows and release controls;
- documentation that could induce unsafe operation.

## Out of scope and prohibited testing

- loss caused by using the software contrary to its explicit NO-GO warnings;
- third-party forks, deployments, domains, or services;
- social engineering, phishing, harassment, or physical intrusion;
- destructive testing or denial of service;
- mainnet or public-testnet transactions, broadcasts, or funded wallets.

Testing must use public vectors, synthetic fixtures, local mocks, or explicitly
authorized isolated environments. A report does not authorize access to other
people's systems or assets.
