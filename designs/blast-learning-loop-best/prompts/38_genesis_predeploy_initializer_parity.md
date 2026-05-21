# Prompt Family: Genesis Predeploy Initializer Parity

## Use This For

- Direct genesis storage, predeploy state, constructor/initializer equivalence, rebasing token bootstrap values, system-contract proxies, and deployment manifests.
- Cases where a contract is marked initialized or deployed at genesis without running the initializer that normally sets nonzero economic state.

## Prompt

```text
Hunt for genesis/predeploy initializer parity bugs.

Build a table for every predeploy, genesis-installed contract, and deployment-script-installed proxy:
- normal constructor or initializer postconditions
- genesis or script storage slots actually written
- proxy implementation/admin slots
- initialized/version flags
- owner/governor/role state
- bootstrap economic state such as initial share price, total shares, principal, supply, exchange rate, and balances

Search patterns:
- direct genesis sets `_initialized` but skips nonzero share price, share count, owner, version, or role storage
- rebasing, yield, or share-accounting tokens start with zero exchange-rate state while later initialization is blocked
- scripts initialize implementation storage rather than proxy storage, or skip proxy initializer while setting some slots manually
- a contract intended to be non-upgradeable or constructor-only is installed behind a proxy or predeploy mechanism
- migration storage writes update balances but not related aggregate counters, total shares, owner indexes, or checkpoint values

Questions to answer:
1. If the initializer ran on a clean chain, which storage fields would be nonzero or linked?
2. Does genesis/script storage create the exact same postcondition?
3. If the initializer is blocked, who can ever repair omitted bootstrap state?
4. Does zero bootstrap state permanently disable rebasing, share conversion, accounting, or authorization?
5. Do tests exercise direct-genesis state rather than fresh initializer state?

Severity guidance:
- High if omitted bootstrap state permanently breaks yield, rebasing, settlement, bridge, or privileged execution.
- Medium if proxy/predeploy deployment can leave value-bearing state inconsistent or upgradeable against intent.
- Low if only local devnet metadata or no-value testing deployments differ.
```
