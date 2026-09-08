# C8.1 Linux-to-Windows transfer manifest

## Identity

| Field | Value |
|---|---|
| Repository | `MHX-Digital/cold-wallets` |
| Branch | `audit/cold-wallet-security-architecture-20260907` |
| Base/main SHA | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` |
| Audited HEAD before this checkpoint commit | `57e35f33c8acc78801a33b7ab5bcb0609ce125c4` |
| Commit count from base to audited HEAD | 64 |
| Linux test result | 79/79 pass; zero skips/failures/errors |
| Product classification | `NO-GO` |
| Windows status | not executed; C8 remains blocked |

The publication/checkpoint commit necessarily has a SHA different from the
audited parent above. The authoritative Windows transfer SHA is the exact remote
branch tip recorded after the non-force push and in the draft PR. Verify that
value before reading or executing checkout contents.

## Critical file checksums at audited HEAD

| File | SHA-256 |
|---|---|
| `README.md` | `a66e5e0f96954e3076b83349e0b81343a46d1a1ee1bef81eeb012568d1d30861` |
| `dashboard/server.py` | `83e6a850ba635a8ea918ad217a7aa6f05c71d9fe0eaf240581770389d21d185e` |
| `dashboard/index.html` | `58df8be7b56789f9e333eb3111d091d631bb84a0523269b51825737beae37340` |
| `coordinator/api.py` | `5dbeb17801685b4b9b38ca8b8973fa697b2c01392fe22fc821af6216f6f6f485` |
| `coordinator/eth_envelope.py` | `4a7ec433fe10925de38525d6a8b6e5c311e3847467cfd92c562879970ee66026` |
| `signer/ethereum.py` | `fe1396a3c3f85791bd595deeabd49766ac713215ecf726bd285047e694bab4dd` |
| `signer/bitcoin_psbt.py` | `38ed1fd6eb1aba1e9af747263c40d282943d97b115824a8b2f437923877bd67b` |
| `broadcaster/store.py` | `669f5ab5d658efa6c4b965e23b00d20699c4ce134179dc90dbccb5de0b9aaded` |
| `broadcaster/ethereum.py` | `715ef025acb427eb8042b1811152007eeb35a098be696b3e7e6adfeffe1bf261` |
| `transport/tor_http.py` | `80de571045022ce1e1659c1a223bbff036db34a30dac83dda39470cdf7aa39a9` |
| `transport/artifacts.py` | `437c4f631c8de7b826613b861f425605e58f3e0de831033b01b01c7ef6ef13f` |
| `storage/authenticated.py` | `ec63e5299ac3a080b622805935e7952d163f5f207f565b86f8405b81915d5479` |
| `requirements/runtime-py312-linux.lock` | `c0ef4b4c2a22c4c95cafad2638dff0778d244d750d87b5311fca2ddaa6ec37d3` |
| `requirements/build-py312.lock` | `83f111e093bad00e18d8ee645a55359e4a3b9ea26a1b2d8b91776712a0db30fb` |
| `requirements/psbt-py312-linux.lock` | `edf784b4b50ec95a80e014ba7462b7d656d6b7fa594f4b8521f4d6eb6235391f` |
| `validation/windows/c8-preflight.ps1` | `1a421d74db1f77584c8071eb52aaa5add92872fbb2279b69f99a512d45ec02a2` |
| `validation/windows/c8-python-matrix.ps1` | `0b83faa62065947bdfd952f6fab9d9a13787fe219d070354070650cfbc3ea1e8` |

Expected Linux locks are exactly the three listed above. They must not be copied,
renamed or used as Windows locks.

## Commits from base to audited HEAD

```text
0f4facd06686446069ea0d2a7ad8f04a87c319fc
3710fe62579cc5841eebd7c59f38f286448c2f49
aabfbbeed6962784d7f2ae74d5fad8181fbe6b95
e43d1d980d8f183bc02586081002522a3667f138
f760ee610713579c7e1c9ddf961539fcfa2f1394
92a2993f32fd5460d4abdd201cd8519a1cb8ba90
32f6e18fa8a936b7bd65c0984be4a015e77ad3dc
042423c3b57a2acf0b4ea0ecd5eb05113c6d4cd0
023e188cd7b8bed7ab4b6c8daa3bdd4776227ef1
b5af01a36a8b0362bcf14ee6b938b2e438823ddd
8edd9730d6fe75335711962fdea0cc2d933b1b15
e71082d0a9b7bf6d01fa97d65491494cf69f4244
6806d769104ea9e66b2cf0e7aa1267a23235f951
5767af4010092d04a3f0ee0ea4a14c3f2c910cb9
ea83a5a354157c3f017405430ae89727c5ccb68b
9c1fcb4c901616043a1b255b426540f29099e4bb
aa3202e0c6b2f6ef3983bb3aa95e021219ca36f0
f62b6aacb64455228ed25e8efb04166816359526
12e42607d1eb096f1e045ee6c0d9aa73f76c559d
8c43bf0c7d616fa76c7e77d91d9737ec6fb6f9dc
597072f28abeacea5bcf567871a5f39aa35c3ee8
ef7355d7bcc4e2428fe44993b5adce324684bb08
b043805ac0a81fa48323c11703e29ec2a2b02e3a
b5da14805d82de551ba8ade2defe789228ad2d48
e4622723da6ba816ca04787b5ce9725053222f07
1fbf37a82083197108f84a9fa01faec7c3fefe1c
1c39fae6189e4281bc9c8a54d2973ed967a026e8
e285c21a853f1f0644d14a5fc7b0211709978884
a6fcf4386c870b31d28cb81df8cd44a58d4887b9
bc8ec1257bbed5c8863fa3b0efd4261d1f257106
6f7bd4dff02b7888cab266e0317de85fb839e896
dd03d6100b7d64d08f9feaeea1c8462bd7033f12
dd52bcf090b6b0515ff1ef25431d594e902d07ae
bd54619f900073e506430ed3b3998d45b9ab440f
f14db39b2b9ea0e758199f195e4e353f1a1e1b6b
9b99b38788176fdfa5ecc4486fed27701267f4bf
d07baee8be304b75736c53abb03faf842958c4c3
51dec97a9aa79925c360d72a2e2c75f93f7c6651
bfaaf12326dc53397be65296e2d14a9664e541c2
3cbb5dfcc9ca301a4d525ce739decf17260efb63
ddabbb1063c4deb986d79288ca4db7201dcf5331
883ffcdfd83c74e6fb109e85154a6d6df22366f6
2ceaf8daf50158ef17d7cc173acfbf1c86ba61a7
cdd6078a2df64613ee60054918de283de5458f81
c0b98735a3fdec3f9032d91c151e1bbe4b1d39fe
d06b9d2a4e6acdc9cb7910d3855cc39e25812d34
2ef5be3b09e759dc04b2db215ab9161c3b163ed3
dd53d6e30b5c2f964a8c1ac6274c53aa3afa1568
a2446c5a46046d62664b10178f769d485f8fd2b3
51c1fac8a96c5cd1f241141ff7a6fbed0141878f
16a0f94958a02b2655464e311df5cd9a56bf47b7
a1f3de9aab26b6e129033b62b1fdb3f81fb371fc
b0b5f052d9dad20be73160e489c3f489061cc9df
7c798af000ae88cdfbb8726360769cefe01ab2ab
88fadf972b9bdf67617bc9f9da8898fd882d2316
04d3a3a268851e3c58a40ad99e4c9e9cb636aa65
3f647bc54a4f8d1e745e09e8f071e4f4f795e1b8
5a792215e8932caac7220f9e7a0b5d5c0e37db06
d0ff76d0d1e81fa27df07661ddbd7ba5b601baa5
2bca54ef982933c8485fa468ef386580f3304753
99168af6bf864ff828ef47ab1c8b16dfec670dec
5a1cceea6d7a03dacc8a490d02466055730bac5c
59c7b545989d1f1852ab0a1b0f9eed6651111926
57e35f33c8acc78801a33b7ab5bcb0609ce125c4
```

## Windows transfer and verification

1. Use a new directory on the intended native Windows 10/11 host; do not reuse
   an older checkout.
2. Clone `https://github.com/MHX-Digital/cold-wallets` without copying any Linux
   virtualenv, wheelhouse, cache, wallet, backup or temporary file.
3. Fetch and checkout `audit/cold-wallet-security-architecture-20260907`.
4. Compare local `HEAD` with the exact remote branch SHA recorded by the C8.1
   publication result and draft PR. Require a clean worktree.
5. Run `Get-FileHash -Algorithm SHA256` for this manifest and the critical files;
   compare against `audit_output/50-c81-checksums.txt` and this table.
6. Review and run `validation/windows/c8-preflight.ps1` without elevation.
7. Stop on any Git/checksum/environment divergence. Do not use Linux locks on
   Windows and do not access an existing wallet directory.

## Limitations

This checkpoint proves Linux CPython 3.12 reproducibility and repository
integrity only. It does not prove Windows compatibility, physical air gap, Tor
routing, Bitcoin regtest interoperability, secp256k1 approval, Helios attestation
or production broadcast safety. The product remains **NO-GO for real funds**.
