# Prompt Family: Ledger Accounting And Invariant Coverage

## Use This For

- Reserve, owner-count, fee, supply, or balance accounting bugs.
- AMM, lending, vault, staking, escrow, or token-share accounting bugs.
- Generated ledger or state objects that must be charged, reserved, or included in invariants.
- Invariant checkers that aggregate results across multiple changed entries.
- Numeric representability or rounding bugs that affect persisted accounting state.

## Prompt

```text
Hunt for ledger-accounting and invariant-coverage bugs in a blockchain or DLT codebase.

Use this prompt when security depends on post-transaction state preserving accounting invariants across balances, reserves, owner counts, fees, shares, receipts, obligations, supply, AMM positions, vault state, lending state, escrow state, staking state, or generated protocol objects.

Search patterns:
- Rejected, aborted, failed, or partially applied transactions that still carry fees, receipts, finalize operations, refunds, or generated state effects. Recompute those effects from the VM or execution engine before accepting serialized block data.
- Fee and reward accounting split across ledger and VM layers. Ensure reward ratification, priority fees, rejected transaction context, and final state effects use one authoritative checked representation.
- Accounting circuits or state transitions that compare field-domain values but omit signed-domain, range, or non-negativity constraints.
- Transaction paths where preflight, admission, or preclaim checks reserve, fee, balance, owner count, or authorization, but execution creates, deletes, mutates, or auto-creates additional state objects.
- Generated side effects such as trust lines, holdings, directories, tickets, delegates, receipts, shares, pseudo-account balances, vault positions, lending obligations, staking positions, or AMM positions that are not included in reserve, owner-count, or accounting checks.
- Invariant detectors that visit multiple affected entries but store only the last result, reset earlier detections, short-circuit incorrectly, or treat absence or empty lists as success when explicit evidence is required.
- Checks that enforce only one side of a two-sided accounting relation: lower bound without upper bound, non-negative without conservation, or asset-local balance without issuer, vault, pool, or global aggregate consistency.
- Calculations where the estimated amount, nominal amount, charged fee, delivered amount, rounded amount, and persisted amount can differ.
- Bridge or wrapped-asset conversions where accounting depends on asset origin. For native-origin assets, returning from wrapped form should usually release escrowed backing or burn representation, not mint new native supply. For foreign-origin assets, native representation mint/burn must be tied to the nominal amount accepted by the protocol, not a token-reported delivered amount that fee-on-transfer or callback code can alter.
- AMM, lending, vault, interest, yield, fee, share, or reserve calculations where rounding direction determines who receives value, who loses value, or who becomes under-collateralized.
- Numeric wrapper types that distinguish syntactic validity, canonicality, and protocol representability. Valid-but-unrepresentable values must not reach persisted state fields.
- Delete, cleanup, revoke, close, withdraw, liquidation, or migration paths that erase an object before proving all dependent balances, obligations, directory entries, permissions, and pseudo-account holdings are empty, transferred, or accounted for.
- Issuer, asset, permission, or policy flag transitions must be checked against existing dependent state such as positive balances, trustlines, holdings, directories, and obligations. A policy change that is valid before issuance may be unsafe after dependent state exists.
- Amendment, fork, feature, or mode gates that change state-object semantics. Both pre-activation and post-activation branches must preserve the same global invariants or fail closed.
- Shared helpers and inline math that are meant to compute the same accounting relation but differ in rounding, fee selection, reserve source, owner-count behavior, or generated-object coverage.
- final accounting checks that run before gas charging, rebates, storage refunds, generated objects, dynamic fields, or temporary-store writes are known. Re-run the conservation model at the actual finalization boundary and include all generated side effects.
- alternate execution engines or fast paths that finalize state through different stores, caches, or deferred metadata. Check that finalized deltas, fee or surplus accounting, receipt data, and writes are propagated and flushed before canonical bank, end-block, or invariant code reads them
- mempool or admission bookkeeping that affects future transaction ordering, nonce eligibility, or promotion. Record it only at final admission or prove every later rejection path rolls it back
- reward or staking accounting where pending operations are summarized into aggregate fields. Check both admission-time validation and settlement-time aggregation; the aggregate must be capped by actual balances or shares and must not count more pending removal than exists.
- historical payout calculations where nominal current balances, live membership, or mutable candidate state can differ from the snapshot that earned the reward.
- Aggregate monetary or accounting counters must distinguish newly created value from redistributed, refunded, or previously escrowed value. Supply, obligation, and pool counters should be updated from the authoritative created/destroyed amount, not from payout or distribution totals.
- block-level or batch-level prepasses that summarize signers, delegated authorities, sponsor relationships, reserve eligibility, account locks, nonce usage, or generated objects before per-transaction execution. Compare whether the summary is order-sensitive or order-insensitive, and whether it gives an earlier transaction access to side effects that only occur later in the ordered batch.
- delegated, sponsored, authorized, or special-account side effects whose validity depends on chain id, nonce, signer, code state, feature activation, or execution success. The accounting/reserve/nonce summary should include only side effects that the execution layer would actually apply at that point in order.
- compare proposal-time ordered side-effect tracking against block-validation or execution-time global summaries. If the proposal path learns delegation, sponsorship, or authority only after transaction `Y`, but validation premarks it for transaction `X` before `Y`, test both orders and fee/reserve consequences.
- public RPC, debug, archive, raw, or compatibility APIs that expose transactions, receipts, logs, blocks, or proofs. Check typed envelope bytes, variant tags, length prefixes, status fields, cumulative gas, bloom/log ordering, and pre/post-fork encoding against the external standard, not only against internal root computation.
- receipt or transaction encoders where one path serializes the typed object with its envelope and another serializes only the inner payload. Roots may still be correct while raw/debug/RPC wire format is wrong.
- raw receipt APIs should be tested with at least one legacy and one typed receipt. Decode the returned bytes with a standard client/parser and verify that typed receipts include the type byte/envelope exactly where the external standard requires it.
- legacy gas-price accounting versus EIP-1559 accounting. For every transaction type, compare consensus/block-policy maximum cost, txpool affordability, and C++ execution gas charge. Legacy transactions must not be discounted by `base_fee + priority_fee` logic if execution charges full gas price.
- EIP-7702 delegated-status timing. Build a two-transaction witness where a non-7702 transaction is evaluated before a later 7702 authorization in txpool/proposal order, but block policy globally pre-marks the authority as delegated before validating the earlier transaction.

Questions to answer:
1. What exact state entries can this transaction create, delete, or mutate directly and indirectly?
2. Which reserves, owner counts, fees, aggregate balances, obligations, supply fields, shares, or receipts should change for each entry?
3. Is the invariant checked at the final state-transition boundary, after generated side effects and rounding are known?
4. Does the checker latch any violation across all visited entries, or can a later clean entry overwrite an earlier violation?
5. Are all accounting relations two-sided and exact where the protocol requires equality?
6. Are rounded, clamped, or converted values checked for canonicality and representability before persistence?
7. Do cleanup paths prove that dependent objects, permissions, holdings, and obligations are empty or transferred before deletion?
8. Do feature or fork gates change which state entries count toward the invariant, and are both sides covered?
9. If the transaction uses helper-computed accounting parts, does every caller use the same validated parts at the state write?
10. Are batch-level summaries computed with the same ordering and validity filters as the final ordered execution?
11. For every externally exposed raw or typed object, does API encoding match the protocol standard as well as the internal root/hash representation?
12. Can changing the order of two transactions switch whether a reserve/delegation/sponsor path is valid in one layer but not another?

High-signal evidence:
- A transaction can create an object while bypassing the reserve, fee, owner-count, or spam-cost requirement for that object.
- A persisted aggregate field can diverge from the sum of child balances, shares, receipts, or obligations.
- A fee, delivered amount, reserve, or supply invariant uses an estimate or requested amount instead of the actual applied amount.
- An invariant checker can observe a violation and then return success after visiting another entry.
- A valid intermediate numeric value can be serialized into an invalid, non-canonical, or non-representable persisted amount.
- A rounding direction consistently benefits the actor invoking the transaction or weakens collateralization.
- A delete or cleanup path removes the object that would have exposed unpaid obligations or unauthorized dependent state.
- A transaction earlier in an ordered batch is evaluated using authority, delegation, sponsorship, reserve, or nonce effects from a later transaction.
- An RPC or raw/debug API returns a receipt, transaction, block, log, or proof encoding that cannot be decoded by standard clients even though internal roots remain valid.
- Txpool/proposal includes an earlier high-tip transaction under emptying rules, then includes a later EIP-7702 authorization for the same authority; block policy sees the later authorization first in a global prepass and rejects the earlier transaction under reserve-only/non-emptying rules.
- Txpool admits or forwards transactions using only base fee affordability, while proposal or block policy rejects them using full gas bid, and the txpool keeps those transactions in a repeatedly selected set.

False-positive filters:
- Do not report mere rounding if the protocol explicitly assigns dust or remainder value and all aggregate fields remain consistent.
- Do not report missing reserve or owner-count checks if a shared helper proves the exact generated object set and is called on every branch before mutation.
- Do not report invariant detector differences unless they can affect acceptance, rejection, persistence, state-root computation, settlement, or externally visible accounting.
- Do not report a one-sided accounting check if another mandatory finalizer enforces the opposite side before state is committed.

Severity guidance:
- High if the bug enables unauthorized mint or burn, settlement compromise, under-collateralized obligations, systematic value extraction, or consensus-visible state corruption.
- Medium if it enables reserve, fee, owner-count, quota, or accounting bypass without proven broad value compromise.
- Low if it is local hardening, debug-only, or only improves diagnostic invariant coverage without changing acceptance or persistence.
```
