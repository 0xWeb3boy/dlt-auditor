# Temporal Bridge Mirrors And Reserve Snapshots

## Family Objective

Find bugs in bridges, cross-domain assets, reserve mirrors, supply mirrors, withdrawal limits, claimable balances, and accounting snapshots where one domain authorizes value movement from stale information about another domain.

This family is specifically about time. Per-call arithmetic can be correct and still unsafe if delayed messages overwrite mirrors, if one direction settles faster than the other, or if local admission reads a remote-balance snapshot that no longer represents the backing reserve.

## Hunt Steps

1. Identify every cross-domain or cross-runtime value system:
   - token bridges,
   - native asset wrappers,
   - escrow and mint/burn systems,
   - reserve-backed withdrawals,
   - claimable/refund paths,
   - relayer fee pots,
   - staking or validator deposits mirrored into another runtime.
2. For each system, name the real backing state and every mirror:
   - actual reserve or escrow balance,
   - local mirrored balance or limit,
   - supply on each side,
   - pending inbound and outbound messages,
   - failed withdrawals, refunds, and claims.
3. Build a two-direction time diagram. Include:
   - when a source state snapshot is read,
   - what message carries it,
   - finality or delivery delay in that direction,
   - when local mirror state is overwritten or incremented/decremented,
   - when users can initiate the opposite direction,
   - what happens if the real reserve changes before the delayed snapshot arrives.
4. Distinguish update modes:
   - overwrite with remote snapshot,
   - add/subtract delta,
   - min/max clamp,
   - monotonic checkpoint,
   - idempotent message application.
   Overwrite semantics are high signal when snapshots can arrive late or out of relation to opposite-direction settlements.
5. Search for admission checks that read a mirror before burn, mint, withdraw, unlock, claim, bridge, redeem, or transfer. Determine whether the check reserves the mirror immediately, only checks it, or updates it after remote settlement.
6. Check failure handling on the remote side. If the local side burns, locks, or decreases user balance before a remote withdrawal fails, identify whether funds become claimable, retried, refunded, or permanently stuck.
7. Search for message ordering and replay assumptions:
   - out-of-order delivery,
   - same-user overlapping transfers,
   - small snapshot updates overtaking large withdrawals,
   - retry/replay of old snapshots,
   - cross-chain reorg or finality changes,
   - paused or delayed message lanes.
8. Compare nominal amount, actual delivered amount, fees, reserve deltas, local supply deltas, and aggregate accounting. A mirror can be stale even if each individual transfer function balances locally.
9. Look for independent rate limits, caps, or safety margins. Verify they are consumed/reserved at the same time the user action is accepted, not only checked against a stale mirror.
10. If contracts or modules use an external portal, messenger, oracle, relayer, or validator set, identify whether the accounting proof binds the reserve state at a specific finalized height or merely passes a value supplied by another contract/message.

## Candidate Requirements

For every candidate, include:

- real backing state and local mirror state;
- which message or function updates the mirror;
- overwrite/delta/clamp semantics;
- two-direction timeline showing stale read or stale overwrite;
- user action authorized by the stale mirror;
- local-side effect before remote failure, such as burn, lock, debit, or supply change;
- remote-side failure or under-backed settlement consequence;
- refund, claim, retry, or recovery path if any;
- concrete test or harness with symbolic amounts and relative delays.

## False-Positive Controls

- Do not report a stale mirror if it is never used to authorize value movement or quota consumption.
- Do not report asynchronous delay by itself; show an unsafe overwrite, stale read, missing reservation, or failed remote settlement after local value movement.
- Do not report under-backing if total local supply cannot exceed real reserve under all interleavings.
- Do not assume message reordering unless the bridge/messenger permits it or the issue works even with FIFO order because the snapshot itself is stale by the time it arrives.
- Do not claim permanent loss if a durable claim/refund/retry path makes the user whole.
