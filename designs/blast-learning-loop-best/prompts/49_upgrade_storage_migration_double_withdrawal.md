# Prompt Family: Upgrade Storage Migration Double Withdrawal

## Use This For

- Bridge and messenger upgrades, proxy reinitializers, replay/finality maps, withdrawal queues, proven/finalized withdrawal state, request IDs, output roots, versioned hashes, and governance upgrade windows.

## Prompt

```text
Hunt for upgrade or reinitialization paths that can reset withdrawal replay/finality state and enable double withdrawal.

Build a before/after storage table for every bridge, portal, messenger, queue, and upgrade script:
- storage slot/key for successful messages
- storage slot/key for failed messages
- storage slot/key for finalized withdrawals
- proven withdrawal data, output-root binding, request IDs, nonces, and versioned hashes
- proxy implementation slot, initializer/reinitializer version, and migration guard
- whether old pending withdrawals remain valid after upgrade
- whether new code reads old state or starts from an empty/new domain

Search patterns:
- upgrade installs new implementation with a fresh replay/finality mapping while old withdrawals are still pending
- reinitializer clears or shadows maps used to prevent message replay
- message hash, nonce, or versioned-hash domain changes without migrating old consumed/finalized entries
- governance upgrade can be front-run or back-run with prove/finalize calls that are valid under both old and new state
- migration copies balances or config but omits successful messages, failed messages, finalized withdrawals, request IDs, or output-root bindings
- bridge finalization has separate old and new entry points that mark different replay maps
- `initialize` or `reinitialize` can be called on proxy/implementation in a way that resets replay protection

Questions to answer:
1. What pending withdrawals/messages can exist at the upgrade boundary?
2. Which exact storage keys prevent a second finalization before the upgrade, and are the same keys read after the upgrade?
3. Can the same withdrawal be represented by two hashes, request IDs, or version domains?
4. Are migration scripts atomic with pausing/finalization, or can users race the governance execution?
5. Does every new finalizer check the old finalized/replayed state before sending value?

Severity guidance:
- High if an upgrade window can enable duplicate finalization, replay consumed messages, or withdraw value twice.
- Medium if upgrade can strand or make pending withdrawals unreplayable without double spend.
- Low if only governance can repair/trigger it and all affected messages are paused/migrated atomically.
```
