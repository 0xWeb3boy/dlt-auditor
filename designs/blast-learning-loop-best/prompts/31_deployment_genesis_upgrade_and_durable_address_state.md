# Prompt Family: Deployment Genesis Upgrade And Durable Address State

## Use This For

- Direct genesis storage, predeploy state, proxy implementation wiring, and deployment manifests.
- Non-upgradeable intent versus upgradeable mechanism.
- Deterministic deployment, selfdestruct, redeploy, address reuse, and durable per-address configuration.
- Upgrade/reinitialization that can reset replay guards, nonce state, ownership, or message-consumption state.

## Prompt

```text
Hunt for deployment, genesis, upgrade, and durable-address-state bugs in a blockchain or DLT codebase.

Focus on security-sensitive state installed outside ordinary user execution: genesis allocs, predeploy storage, deployment scripts, factory clones, deterministic deployment, proxies, upgrade scripts, migrations, and reinitializers.

Search patterns:
- genesis storage writes set only some fields that the Solidity/Rust/Go initializer would have set, such as initial price, share count, owner, version, initialized flag, role, or replay marker
- an object intended to be immutable or non-upgradeable is deployed behind a mechanism that can change implementation or storage
- implementation contracts can be initialized, reinitialized, upgraded, or destroyed in a way that affects proxy delegatecall execution, code identity, or upgrade safety
- proxy state looks safe, but the implementation code can disappear, change, or execute a provider-supplied destructive path
- deterministic deployment or address reuse lets an attacker set per-address configuration before the intended code exists
- selfdestruct or same-address redeploy preserves policy, governor, role, fee, gas, yield, or replay state that was meant to describe a previous code identity
- upgrade scripts call initializers in a different order than fresh deployment, or skip replay/nonce/message-consumption state preservation
- upgrade or reinitializer functions reset consumed-message maps, withdrawal status, failed/successful replay state, role maps, or bridge accounting
- deployment scripts transfer some admin roles to final governance but leave related provider, bridge, insurance, fee, or predeploy roles controlled by a deployer
- clones/factories initialize security state on creation but expose later reinitialization or replacement without a one-time guard

Questions to answer:
1. What postcondition should hold after fresh deployment, direct genesis, migration, upgrade, and redeploy?
2. Are direct storage writes equivalent to constructors and initializers, including nonzero bootstrap values and initialized flags?
3. Does the deployed proxy or predeploy mechanism match the contract's declared or inferred upgradeability intent?
4. Can code identity change while address-keyed config remains trusted?
5. Can address-keyed config be written before code exists, then captured by later deterministic deployment?
6. Does proxy safety depend on implementation code availability, and can delegatecall reach code that can destroy or corrupt that availability?
7. Do upgrades preserve replay guards, consumed-message maps, nonces, withdrawal status, and versioned storage layout?

Severity guidance:
- High if an untrusted actor can seize roles, brick bridge/yield/fee execution, double-withdraw, or corrupt replay/settlement state.
- Medium if a realistic deployer, governance, or migration mistake can leave value-bearing state inconsistent with intended code identity.
- Low if only devnet-only or inactive code is affected with no production-like path.
```
