# Prompt Family: Default Pending Resource Reuse

## Use This For

- SDK, wallet, builder, relayer, and account client bugs where normal API calls fund or build more than one transaction before prior selected resources leave the remote available-state view.
- UTXO, object, nonce, message, ticket, sequence, and account resource reuse caused by missing default reservations.
- Txpool duplicate-ID, replacement, pruning, squeezed-out, or failed-submission effects caused by client-side stale resource selection.

## Prompt

```text
Hunt specifically for default pending-resource reuse in client transaction construction.

The target pattern is not "consensus accepts a double spend." The target pattern is: a client selects scarce resources from a remote available-state query, inserts them into one transaction, then the ordinary default API can select those same resources again for another transaction before finality or explicit release.

Separate these cases:
- Default no-reservation path: ordinary users call high-level fund/build/send helpers without special options.
- Optional reservation path: a cache, exclusion list, manual reservation API, or provider option exists but is not default or is written too late.
- Cross-boundary path: connector, relayer, browser tab, process, provider instance, or service boundary cannot see the selected resources.
- Non-equivalent path: message-only, cache-cleanup-only, or connector-only issues that do not prove the default scarce-resource gap.

Search strategy:
1. Map high-level user workflows that select resources: transfer, batch transfer, deploy, contract call, withdraw, faucet, bridge, sponsored call, estimate-and-fund, manual fund/build, and retry helpers.
2. For each workflow, trace the lifecycle:
   - which remote query returns currently spendable resources,
   - which helper excludes already-used resources,
   - whether exclusions include only the current transaction's inputs,
   - when selected resources are added to the request,
   - when signing or submission happens,
   - when any local reservation is written,
   - when that reservation is released.
3. Build a two-transaction timeline. Transaction A is funded or submitted. Before a block/finality/status update removes A's resource from the remote available view, transaction B is funded through the same ordinary API.
4. Ask whether B can receive A's exact resource identity from the remote query. If yes, preserve this as a candidate even if final node validation later rejects one transaction.
5. Inspect txpool or client status semantics where available. Duplicate resource use can still matter if it causes duplicate transaction IDs, failed admission, replacement, pruning, squeezed-out status, dropped pending progress, or misleading local "funded" requests.
6. Search tests for same-request duplicate exclusion and for two separately funded pending transactions. A test that excludes duplicates inside one request does not prove cross-transaction reservation.
7. Check documentation and options. A warning or opt-in cache is not default safety. Record it as mitigation, not a kill, unless ordinary default workflows cannot hit the issue.

Candidate quality bar:
- Name the scarce resource identity and owner/account scope.
- Name the high-level default workflow that reaches selection.
- Show that selection excludes current-request inputs but not resources selected for earlier pending transactions, or show an equivalent absence of local pending state.
- Show that any reservation is optional, too late, too narrow, or absent.
- Explain user/service impact before or despite consensus rejection.
- Keep default reuse candidates separate from optional-cache cleanup, message-only reservation, and connector-boundary candidates.

False-positive filters:
- Do not claim chain-level double-spend acceptance without node evidence.
- Do not report a race that requires exotic manual misuse if ordinary high-level APIs serialize or reserve safely by default.
- Do not downgrade solely because final validation rejects the duplicate resource.
- Do not downgrade solely because users can opt into a cache or manually pass exclusions.
- Downgrade to Low only if default workflows are safe and the remaining issue is opt-in hardening with no duplicate ID, failed submission, replacement, pruning, or lost-progress risk.

Severity guidance:
- Medium when ordinary client use can create valid-looking independent transactions that fail, duplicate IDs, replace/prune earlier pending transactions, or lose pending progress.
- Low for opt-in, documented, local-only hardening gaps that do not affect default workflows and cannot displace pending transactions.
- High only for unauthorized value movement, systematic extraction, or consensus-visible state corruption.
```
