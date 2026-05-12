# Prompt Family: Pending Resource Reservation And Client Lifecycle

## Use This For

- SDK, wallet, relayer, builder, account-abstraction, or client-side transaction construction bugs.
- UTXO, object, nonce, message, ticket, sequence, account resource, fee, or reservation reuse before finality.
- Pending transaction lifecycle bugs where local state disagrees with node or txpool state.
- Txpool replacement, duplicate transaction IDs, squeezed-out transactions, dropped pending transactions, or failed inclusion caused by client-side construction.

## Prompt

```text
Hunt for pending-resource reservation and client lifecycle bugs.

Focus on code that selects scarce resources from an authoritative remote state view, adds them to a transaction, signs or submits that transaction, and then later builds another transaction before the first one is finalized.

Search patterns:
- Resource selection helpers: get coins, get objects, get messages, get spendable resources, get account nonce, get sequence, get tickets, get inputs, select funding, estimate funding, build request, fund request, add resources, add inputs, add change, submit, wait, retry.
- Exclusion helpers that exclude only resources already inside the current request, while ignoring resources selected for earlier in-flight requests from the same owner.
- Reservation state that is optional, disabled by default, process-local only, provider-local only, tab-local only, not shared with wallet connectors, not shared with relayers, or scoped to the wrong owner/resource key.
- Reservation state that is written too late, such as after submit instead of after funding/signing, or after txpool acceptance instead of before another funding call can run.
- Reservation state that is released only by TTL, never released on failure, or not updated on rejected, replaced, squeezed-out, dropped, reverted, expired, or finalized transactions.
- Remote available-state queries that are stale until a new block or finality point. Ask what happens if two local transactions are built within the same block interval.
- Txpool or mempool rules where a later transaction using the same resource can duplicate a transaction ID, replace an earlier transaction, prune it, squeeze it out, or cause one submit path to fail.
- High-level convenience APIs that look independent to a user but share hidden funding state: transfer, batch transfer, deploy, contract call, withdraw, faucet, bridge, relayer, sponsored transaction, simulation, or estimate-and-fund helpers.
- Simulation/dry-run/estimate paths that select resources but do not reserve them, then live submit selects again or races with another call.
- Retry paths that refetch resources after a failure without excluding resources already used by a still-pending retry or sibling transaction.
- Multi-process or connector boundaries where the SDK assumes a reservation exists but another process, wallet extension, relayer, or provider instance can select the same resource.
- Default-path resource selection where the SDK offers an optional cache or mitigation but does not reserve selected resources unless callers opt in.
- Funding-time gaps where two independent high-level calls each build, fund, sign, or submit a transaction, and the second call cannot see resources selected by the first call because no owner/account-level pending set exists.
- Cache-only or connector-only variants. Keep them separate from the default no-reservation case; do not let an optional-cache message/connector issue subsume a default coin/UTXO/object reuse issue.

Questions to answer:
1. What resource is scarce: UTXO, object, nonce, sequence, message, ticket, coin, account slot, fee reserve, or signer authorization?
2. When is the resource selected, when is it added to a request, when is it signed, and when is it submitted?
3. What local state records that the resource is reserved before finality?
4. Is reservation default-on, or must callers opt in?
5. Is the reservation visible to every API path that can fund another transaction from the same owner?
6. Is the reservation keyed by the exact resource identity, owner, asset, network, chain, provider, and account scope needed by the protocol?
7. What releases the reservation on success, failure, rejection, replacement, squeezed-out status, timeout, or finalization?
8. Can a later transaction reuse the resource before a block, finality point, or txpool status change removes it from the remote available-state query?
9. If the node rejects the duplicate spend, what user-facing or service-facing damage already occurred: duplicate transaction ID, failed submission, replaced pending transaction, pruned earlier transaction, lost progress, or stuck retry loop?
10. Are test cases covering two independent transaction builds in the same finality window, not only one transaction that already contains duplicate inputs?
11. Does the default configuration reserve resources selected for pending transactions, or is protection opt-in, advisory, local-only, or written too late?
12. If documentation warns about the race or describes an opt-in mitigation, does the default API still make ordinary valid transactions fail, replace, prune, or lose pending progress?

High-signal evidence:
- A funding function queries remote spendable resources without subtracting local in-flight reservations.
- Excluded IDs are derived only from the current transaction inputs.
- Pending-resource cache exists but is off by default, TTL-only, or written after submit rather than after selection.
- Tests prove duplicate inputs inside one request are excluded, but do not test two separately funded pending requests.
- A txpool replacement or duplicate-hash rule can turn local duplicate resource selection into failed or silently displaced transactions.
- A scan finds both an optional mitigation and an unsafe default. Preserve the unsafe default as its own candidate if ordinary high-level SDK calls can hit it.

False-positive filters:
- Do not claim the protocol accepts double spends unless node-side evidence proves it.
- Do not kill the issue solely because consensus rejects duplicate resources. This family is about SDK/client safety, transaction inclusion reliability, and pending-state lifecycle.
- Do not kill the default unsafe path solely because an opt-in cache or manual exclusion parameter exists. First decide whether ordinary users are protected by default.
- Do not collapse default coin/UTXO/object reuse into a narrower message-only, cache-only, or connector-only candidate.
- Do not report a purely theoretical multi-process race unless there is a realistic same-account workflow or API contract where users/services build more than one transaction before finality.
- If the target is only a consensus node with no client-side resource selection API, mark this family out of scope.

Severity guidance:
- Medium when ordinary SDK/wallet/relayer use can make valid independent transactions fail, duplicate IDs, replace/prune earlier pending transactions, or produce misleading funded/signed requests.
- High only if the lifecycle bug can cause unauthorized value movement, systematic value extraction, or consensus-visible state corruption.
- Low if the issue is only a documented opt-in concurrency limitation with no default-path failed submission, duplicate ID, replacement, pruning, or lost-progress risk.
```
