# Prompt Family: Proxied Predeploy Constructor Initializer Matrix

## Use This For

- System/predeploy contracts installed behind proxies or proxy-like dispatch.
- Contracts that rely on constructors, immutables, or direct-genesis storage instead of proxy initializers.
- Blast/Gas/native predeploys, proxy admin scripts, genesis allocs, upgrade scripts, and implementation-storage parity.

## Prompt

```text
Hunt for constructor-only or non-upgradeable system contracts deployed behind upgradeable proxies.

Build a matrix for every predeploy/system contract:
- proxy address and implementation address
- proxy type and admin/upgrade authority
- constructor state, immutables, and initializer state
- whether proxy storage receives all constructor/initializer postconditions
- whether the implementation storage was accidentally initialized instead of proxy storage
- whether direct-genesis state matches the initializer postconditions
- whether future upgrades/reinitializers can safely preserve the state

Search patterns:
- a predeploy has meaningful constructor-only state but is used through a proxy, leaving proxy storage unset
- a system contract has no initializer, or the initializer does not reproduce constructor postconditions
- genesis alloc writes some fields but omits initialized flags, owner/governor, version, gas/yield mode, share price, or bootstrap balances
- proxy scripts install a non-upgradeable implementation but still expose upgrade semantics
- admin/owner or governor state is set on the implementation, while users interact with the proxy
- constructor immutables are assumed to protect proxy state, but the implementation can be replaced or directly initialized
- direct calls to implementation or proxy fallback can observe divergent state and affect system behavior

Questions to answer:
1. Which addresses are canonical predeploys, and are they proxies, implementations, or direct contracts?
2. What state would the constructor set if the contract were deployed normally?
3. Does the proxy storage contain equivalent state before the first user/system call?
4. Can any upgrade or reinitializer reset, skip, or duplicate initialization-sensitive state?
5. Is the issue limited to deployment hygiene, or can users/admins move value, break claims, or corrupt protocol accounting?

Severity guidance:
- Medium if constructor/proxy mismatch breaks a live predeploy invariant, claim/yield/gas accounting, or upgrade safety.
- Low if only unused implementation storage is wrong and no proxy/system sink can observe it.
- Informational if the contract is not proxied or has intentionally constructor-only immutable configuration.
```
