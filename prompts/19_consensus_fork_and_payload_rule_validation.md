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
- Header or payload fields checked in one import path but omitted in sidechain, downloaded, recovery, optimistic, reorg, replay, or Engine API paths.
- Canonical commitments such as transaction root, receipt root, uncle list, recovered sender, replay-protection flags, or terminal-total-difficulty conditions enforced in one path but omitted in replay, compatibility, recovery, signing, or side import paths.
- Early returns that process payload attributes, return VALID, or update head/safe/finalized state before forkchoice consistency checks run.
- Parent, ancestor, finalized, safe, or invalid-state decisions keyed by one coordinate while the protocol identity includes hash, number, parent hash, and validity status.
- Special cases for synthetic payloads, segmented blocks, zero hashes, legacy fixtures, or compatibility modes that skip broad validation instead of only the specific non-comparable field.
- Error paths that collapse invalid-block, invalid-header, or sender-recovery failures into generic execution or internal errors that higher layers cannot treat as invalid.
- Equal-score, equal-total-difficulty, or same-height tie-breaks that use randomness or local heuristics without an explicit protocol or policy rule.

Questions to answer:
1. Which protocol rule is authoritative for this block, payload, fork, method version, chain variant, and timestamp or height?
2. Are all fields required by that rule present and checked before any canonical state update, payload build, or success response?
3. Does every equivalent entrypoint call the same canonical validator?
4. Do special-case or compatibility branches preserve core identity checks such as block hash, parent relation, state root, transaction root, receipt root, gas semantics, and fork-specific fields?
5. Can invalid ancestry, unknown head, inconsistent safe/finalized state, or known-invalid payload state be downgraded into syncing, generic error, or success?
6. If the protocol allows equal-strength competitors, is the tie-break deterministic and policy-correct, or is security-sensitive selection hidden inside randomness or a local heuristic?

Severity guidance:
- High if malformed consensus data can be accepted as canonical, finalized, valid, or execution-ready.
- Medium for security hardening where validation is tightened in consensus-sensitive paths but exploitability or end-to-end reachability is not proven.
- Low for test-only, benchmark-only, or offline compatibility branches that cannot influence production validation.
```
