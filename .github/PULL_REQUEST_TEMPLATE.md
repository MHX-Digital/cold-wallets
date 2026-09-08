## Context

<!-- What problem is addressed and why? Link the prior issue/discussion. -->

## Security boundary

- [ ] No real wallet, key, seed, mnemonic, WIF, credential, or fund was used.
- [ ] No mainnet/public broadcast, deploy, or privileged network change occurred.
- [ ] Trust-boundary and residual-risk changes are documented.
- [ ] New dependencies are exact, hash-locked, and justified.

## Evidence

<!-- List tests, public vectors, negative cases, and cleanup evidence. -->

- [ ] Complete deterministic suite passes with zero relevant skips.
- [ ] `git diff --check` passes.
- [ ] Tests leave zero owned process, listener, file, cache, database, or bytecode residue.
- [ ] Logs and diff were reviewed for secrets.

## Rollback

<!-- Describe a non-destructive rollback or revert strategy. -->

## Classification

- [ ] Documentation continues to state **EXPERIMENTAL — NO-GO FOR REAL FUNDS**.
- [ ] Commits contain a DCO `Signed-off-by:` line.
