# Prompt Family: Upgrade Replay State And Reserved Gas

## Use This For

- Upgrade/reinitializer paths, pending bridge withdrawals, replay maps, nonce/message state, reserved gas constants, messenger relay gas, and storage writes added during upgrades.

## Prompt

```text
Hunt for upgrade replay-state and reserved-gas bugs.

Build a before/after table for every bridge, portal, messenger, withdrawal queue, and upgrade script:
- successful message maps
- failed message maps
- finalized withdrawal flags
- pending withdrawal/request ids
- nonces and versioned hashes
- output roots and proof bindings
- pause/guardian state
- reserved gas constants
- newly added storage writes on relay/finalize/failure paths

Search patterns:
- an upgrade or reinitializer can reset consumed/replayed/finalized state while old messages or withdrawals remain pending
- governance execution can be front-run by finalizing or replaying a message before state is migrated
- versioned hash or nonce domains change across upgrade without binding old and new replay maps
- new discounted-value or bookkeeping storage writes are added to a relay path without increasing reserved gas
- reserved gas is enough for the old path but not for post-call failure recording, discounted-value storage, or cleanup writes
- failed relay paths consume finalization state before the failure/replay bookkeeping can be written
- migration scripts copy balances but omit replay/finalization/failed-message state

Questions to answer:
1. What pending messages and withdrawals can exist at the upgrade boundary?
2. Does the new implementation read the same replay/finalization state, or does it start fresh?
3. Can a user front-run upgrade execution to make the same withdrawal valid under old and new state?
4. Which relay/finalize paths depend on `RELAY_RESERVED_GAS` or equivalent constants?
5. Have new post-call writes, discounts, or failure records changed the gas reserve requirement?

Severity guidance:
- High if an upgrade window can enable double withdrawals, replay consumed messages, or lose replay protection.
- High if under-reserved messenger gas can permanently lose bridge value or replay state.
- Medium if a realistic relay path can fail or become unreplayable only under bounded gas/value conditions.
- Low if only governance can trigger and pause/recovery fully compensates.
```
