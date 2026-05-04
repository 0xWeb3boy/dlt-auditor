# Prompt Family: Consensus, Fork, And Payload Rule Validation

## Use This For

- Engine API, consensus API, block import, and payload validation paths.
- Forkchoice head, safe, finalized, invalid, syncing, and payload-attribute handling.
- Fork, hardfork, network-upgrade, L2 variant, method-version, or payload-version gates.
- Header, receipt, blob gas, base fee, difficulty, nonce, timestamp, parent, and state-root semantics.
- Special-case replay, synthetic block, legacy, benchmark, migration, or compatibility branches that may weaken normal validation.

## Prompt

```text
Hunt for consensus-rule validation bugs in a blockchain or DLT codebase.

Focus on externally supplied or consensus-layer supplied blocks, headers, payloads, forkchoice states, receipts, sidecars, and payload attributes before they affect canonical state, payload building, execution, or success responses.

Search patterns:
- A fork or feature predicate called with fewer inputs than the protocol rule requires, such as height without timestamp, parent total difficulty without current difficulty, method version without message kind, or activation state without chain variant.
- A generic mainnet or base-chain validator reused for a chain variant that has different field presence, value, or timing rules.
- In rollup or multi-domain derivation pipelines, compare the trusted origin context with payload-carried timestamps, origins, fork markers, and batch metadata. Fork or feature gates should use the trusted origin when the protocol defines the gate there, not a value decoded from untrusted batch contents.
- Header or payload fields checked in one import path but omitted in sidechain, downloaded, recovery, optimistic, reorg, replay, or Engine API paths.
- Canonical commitments such as transaction root, receipt root, withdrawal root, blob commitment, state root, generated-system-work root, recovered sender, replay-protection flags, or terminal-total-difficulty conditions enforced in one path but omitted in replay, compatibility, recovery, signing, or side import paths. Recompute body and payload commitments before execution or success, not only in the happy-path import flow.
- Execution-state side effects that influence consensus roots, such as account touches, empty-account deletion, gas accounting, generated transactions, receipts, logs, refunds, or storage journaling, where one edge-case path updates the committed state but not the journal or rollback state.
- Check conversions between aggregate batch formats and per-block or per-transaction formats. A span, segment, or aggregate batch must not produce child payloads whose origin, parent, timestamp, fork activation, or safe-head relation is older or weaker than the boundary being processed.
- Check fallback payload construction paths such as deposits-only, system-transaction-only, invalid-payload recovery, or post-execution metadata paths. The fallback must filter exactly the allowed transaction classes and must clear or rebuild cached attributes that came from the invalid path.
- Early returns that process payload attributes, return VALID, or update head/safe/finalized state before forkchoice consistency checks run.
- For rollups, distinguish unsafe, local-safe, cross-safe, finalized, and disputed target states. Code must not relabel unsafe data as safe/finalized during startup, sync completion, rewind, or recovery without re-deriving that label from authoritative protocol context.
- Parent, ancestor, finalized, safe, or invalid-state decisions keyed by one coordinate while the protocol identity includes hash, number, parent hash, and validity status.
- Special cases for synthetic payloads, segmented blocks, zero hashes, legacy fixtures, or compatibility modes that skip broad validation instead of only the specific non-comparable field.
- Error paths that collapse invalid-block, invalid-header, or sender-recovery failures into generic execution or internal errors that higher layers cannot treat as invalid.
- Equal-score, equal-work, equal-total-difficulty, same-height, or same-round tie-breaks that use randomness or local heuristics without an explicit protocol or policy rule.
- Finalization, post-execution, state-sync, deposit, withdrawal, or system-transaction paths that derive extra receipts, generated transactions, or state changes. Check that the block body, locally derived system work, receipts, and state root are cross-checked before success and that unsupported fields fail closed.
- Fork-aware hashing, signing, opcode decoding, and header sanity paths where the canonical object shape changes by fork. Check that every verifier, signer, replay path, and helper includes exactly the fields active for that fork and rejects fields forbidden before or after the fork.
- Consensus validation that depends on an external chain or consensus client. Check that time-based or latest queries are first pinned to a deterministic height/hash/finality boundary, and that all validators would query the same snapshot for the same local block.
- ABCI, consensus API, proposal-building, or proposal-processing paths that embed or consume validator vote extensions, side votes, committee votes, or aggregate approvals. Check that every path validates signer identity, signature, duplicate votes, voting power, quorum, height, round, proposer, and block/domain context before proposal acceptance or tallying.
- proposal/validation consensus systems where agreement is over transaction sets, close times, trusted validator or committee validations, and prior-ledger identity rather than only block payloads. Check that proposal duplicate suppression, transaction-set ordering, wrong-ledger mode, and switch-ledger or catch-up mode bind proposal hash, prior state, sequence, signer, and active rules
- amendment, fork, or feature activation votes where quorum or majority thresholds are computed by integer or rounded arithmetic. Test boundary values just below and above the policy threshold and ensure small validator sets cannot produce impossible or unsafe quorum requirements
- consensus observability or misbehavior detectors that only watch trusted participants or only the happy path. Hardening should cover untrusted reports, laggards, censorship suspicion, invalid proposals, and desync or catch-up transitions without changing consensus rules
- consensus-visible error, acknowledgement, receipt, precompile return, or result data built from raw errors or local diagnostics. These bytes must be deterministic protocol outputs if they can affect app hashes, results hashes, or replicated state
- view, round, timeout, or commit transitions where a certificate carries a lock, proposal identity, part-set header, or latest quorum state into the next step. Verify that state clearing, reconstruction, timeout vote emission, and commit handling preserve the certified identity rather than falling back to empty or stale local state
- verification predicates such as "needed", "current", "fresh", or "verified" must gate every later mutation derived from that object. Do not let stale or unnecessary certificates update ranges, headers, block matching, or emitted votes
- externally anchored chains, L2s, or hybrid consensus systems where local consensus depends on a base-chain sortition, checkpoint, epoch, reward set, or committee snapshot. Check that every block, signer-set, equivocation, and fork-choice lookup is bound to the canonical anchored context, not only a height or local hash.
- canonical-tip, safe-tip, or accepted-block caches that can be updated by lower-height, different-history, or stale validation results. Tip advancement should be monotonic within the same canonical history and should reject cross-history shortcuts.
- equivocation or misbehavior evidence predicates that require too many fields to match. Evidence should match the protocol's definition of conflict, such as same parent, same sequence, same height or round, or mutually exclusive vote target, not just exact duplicate structure.

Questions to answer:
1. Which protocol rule is authoritative for this block, payload, fork, method version, chain variant, and timestamp or height?
2. Are all fields required by that rule present and checked before any canonical state update, payload build, or success response?
3. Does every equivalent entrypoint call the same canonical validator?
4. Do special-case or compatibility branches preserve core identity checks such as block hash, parent relation, state root, transaction root, receipt root, gas semantics, and fork-specific fields?
5. Can invalid ancestry, unknown head, inconsistent safe/finalized state, or known-invalid payload state be downgraded into syncing, generic error, or success?
6. If the protocol allows equal-strength competitors, is the tie-break deterministic and policy-correct, or is security-sensitive selection hidden inside randomness or a local heuristic?
7. For proposal/validation consensus, are proposal identity, prior state, transaction-set identity, signer identity, sequence, round, and active rules bound together at every acceptance and duplicate-suppression point?
8. Are quorum, threshold, and amendment or feature activation calculations safe at exact boundary fractions and small validator or committee sets?
9. Does every execution path that can affect the state root, receipt root, generated work, or fork-choice result journal and validate the same side effects as the canonical path?

Severity guidance:
- High if malformed consensus data can be accepted as canonical, finalized, valid, or execution-ready.
- Medium for security hardening where validation is tightened in consensus-sensitive paths but exploitability or end-to-end reachability is not proven.
- Low for test-only, benchmark-only, or offline compatibility branches that cannot influence production validation.
```
