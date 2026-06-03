# Prompt Family: Upgrade Double Delivery Replay Matrix

## Use This For

- Upgrade/reinitializer paths that can deliver the same withdrawal or message value twice.
- Old/new replay maps, finalized withdrawal flags, successful message maps, versioned hashes, nonces, and migration windows.

## Prompt

```text
Hunt specifically for duplicate successful value delivery across upgrade boundaries.

Do not count zero-value underdelivery, impossible finalization, or ordinary failed-message replay as the exact double-delivery issue unless the same value can be delivered twice.

Build a double-delivery matrix:
- operation: portal withdrawal finalization, messenger relay, bridge finalizer, yield-manager queue claim
- old replay/finality key
- new replay/finality key
- old value delivery sink
- new value delivery sink
- whether both can be true/successful for the same withdrawal/message
- race window around governance upgrade, reinitializer, migration, pause, or proof/finalize calls

Search patterns:
- upgrade introduces a new hash domain without checking old successful/finalized state
- reinitializer shadows or clears a replay/finality mapping
- old implementation can finalize before upgrade and new implementation can finalize again after upgrade
- old and new bridges/messengers use different replay maps for the same underlying withdrawal
- migration copies balances/config but not successful message maps or finalized withdrawal flags
- proof/reprove state creates a second queue request or claimable request for the same withdrawal

Questions to answer:
1. What exact old key prevents duplicate delivery before upgrade?
2. What exact new key prevents duplicate delivery after upgrade?
3. Can both implementations accept the same withdrawal/message under different keys?
4. Does a user, relayer, or governance executor control ordering enough to deliver value twice?
5. If only zero underdelivery or stranded value is found, preserve it separately and keep searching for duplicate delivery.

Severity guidance:
- High if the same withdrawal/message value can be delivered twice without privileged theft assumptions.
- Medium if state migration can underdeliver, strand, or make messages unreplayable but not double deliver.
- Low if only operator tooling or paused migration hygiene is affected.
```
