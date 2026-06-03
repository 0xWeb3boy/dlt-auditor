# Prompt: Validation And Impact

Use this on any candidate produced by `01_base_hunter.md`.

## Objective

Stress-test the hypothesis, then assign impact and severity in a disciplined way.

## Prompt

```text
You are validating a candidate blockchain or DLT security issue.

You must act like a skeptic first and only conclude "confirmed" if the code supports it.

For the candidate under review:
1. Trace the exact data flow and control flow from untrusted input to the sensitive sink.
2. Identify every check that exists on the path.
3. Explain which property is missing or incomplete:
   - authentication
   - authorization
   - signer scope
   - domain separation
   - request-response correlation
   - request-response cost symmetry
   - graph or lineage binding
   - freshness
   - replay protection
   - policy/version/fork gating
   - authoritative-state revalidation
   - decision-scope alignment
   - enforcement at the actual sink
   - representation or encoding consistency
   - duplicate-representation binding
   - trusted artifact or config selection at verification time
   - content-address integrity
   - robust boundary validation
   - gas/resource/quota accounting
   - made-progress and zero-progress classification
   - progress or reservation monotonicity
   - lifecycle cleanup
   - state-coordinate consistency
   - arithmetic bounds
   - read-only vs persistent-side-effect separation
   - fork/version/method-specific consensus rule coverage
   - chain-variant rule coverage
   - block-body commitment recomputation
   - execution-side-effect journaling
   - parent/ancestor/forkchoice consistency
   - explicit absence-proof evidence
   - authenticated-state rollback atomicity
   - cache context rebinding
   - peer-quality feedback enforcement
   - listener or event policy preservation
   - deterministic external-consensus snapshot binding
   - explicit finalization error propagation
   - canonical numeric representability before narrowing
   - attestation quorum/context binding
   - exact range-continuity enforcement
   - explicit registry key-existence validation
   - ledger accounting invariant coverage
   - reserve and owner-count enforcement
   - mutable budget handoff across runtime boundaries
   - authorization error fail-closed handling
   - variant-specific authority at shared base-client sinks
   - amendment, fork, or feature-scoped authorization
   - validator-list or trust-list threshold achievability
   - generated-side-effect authorization
   - exact caller/callee buffer contract
   - lifetime-safe ownership across nested or async execution
   - destination/source length equality before copy-back
   - local progress-invariant feasibility under configured capacity
4. Search for compensating controls elsewhere in the codebase.
5. Decide whether the issue is:
   - confirmed
   - likely
   - unclear
   - invalid

When the patch clearly tightens a validator, consensus, proof, traffic-control, or authenticated-state boundary but the evidence does not prove attacker control or deployed exploitability, classify it as likely/security-hardening. Preserve the invariant and hunt lesson, but avoid impact claims such as consensus break, theft, forged state, or remote DoS unless the code path and attacker capability are demonstrated.

For security-hardening findings, distinguish direct exploit fixes from boundary tightening. Dependency upgrades, stricter config parsing, offline signing support, and added mismatch checks should be retained as hardening only when attacker control or end-to-end exploitability is not shown.

For bridge, precompile, or cross-runtime findings, distinguish the proven boundary fix from the hypothesized exploit chain. It is acceptable to keep a finding as security-hardening when the patch blocks a privileged callback, registry, gas, rollback, or mirror-state boundary, but do not claim theft, minting, consensus failure, or full exploitability unless the attacker path reaches the value or consensus sink in code.

Use three evidence levels for hardening-only findings: (1) a reachable attacker-controlled input crosses the boundary and can trigger the old behavior; (2) the patch closes a real boundary but reachability or exploit consequence is uncertain; (3) the patch is defensive cleanup, refactoring, observability, or operator-safety without a demonstrated hostile path. Preserve levels 2 and 3 as corpus lessons, but keep the impact language proportional.

For parser, recovery, and resource-hardening findings, explicitly classify which proof is missing:
- missing reachability: old behavior is bad if reached, but attacker control is unproven;
- missing consequence: attacker-controlled input reaches the boundary, but impact beyond rejection/hardening is unproven;
- duplicate-check uncertainty: patch centralizes or duplicates validation, but old equivalent checks may have existed elsewhere;
- operator-local hardening: the trust decision is real but affects CLI, monitoring, or tooling rather than protocol state.

Then assess impact:
1. What can an attacker actually cause?
2. Does it affect consensus integrity, finalized state integrity, settlement integrity, bridge safety, privileged data access, slashing/accountability, or only availability?
3. Is the trigger remote, peer-based, cross-domain, operator-only, governance-only, or debug-only?
4. Is the issue one-shot, repeatable, chain-wide, validator-local, or client-local?
5. Is the finding proven to cross a production trust boundary, or is it best classified as security hardening because it tightens a consensus, proof, peer, or resource-control path without a demonstrated exploit?
6. If the bug is in consensus validation, distinguish invalid-block acceptance, invalid-block rejection, syncing/liveness confusion, payload-building side effects, and error-classification hardening.
7. If the bug is in authenticated state or proof code, distinguish proof-generation ambiguity, verifier acceptance, local state corruption, persistence correctness, and consensus-visible state-root impact.
8. If the issue involves an external consensus client, checkpoint source, bridge oracle, or validator-set provider, distinguish stale local trust, nondeterministic data selection across honest nodes, fail-open unavailability, and direct forged-state acceptance.
9. If the issue involves finalization or generated system work, distinguish unsupported-field rejection, generated-work mismatch, receipt/accounting mismatch, and state-root divergence.
10. If the issue involves validator votes, vote extensions, side votes, or committee attestations, distinguish syntactic validity, signature validity, validator-set membership, voting-power quorum, freshness, and domain separation. Do not treat one property as proof of the others.
11. If the issue involves ranges such as checkpoints, epochs, spans, batches, or proof windows, distinguish overlap prevention, exact continuity, gap tolerance by design, and downstream enforcement by another verifier or contract.
12. If the issue involves ledger accounting, distinguish nominal amount, charged fee, delivered amount, reserve or owner-count changes, generated objects, aggregate obligations, and invariant-detector coverage. Do not call it theft unless the state transition demonstrably lets value, debt, reserve burden, or obligations move incorrectly.
13. If the issue involves amendments, forks, or feature gates, decide whether the bug is pre-activation acceptance, post-activation missing enforcement, or cross-version compatibility hardening.
14. If the issue involves delegated permissions, identify the exact transaction sub-shape, asset, issuer, destination, receiver policy, and generated side effects covered by the grant.
15. If the issue appears in a forked client or chain-variant overlay, distinguish base-client consensus impact from variant-local sequencer, validator, gas, artifact, or delayed-message impact. Do not claim base-chain consensus breakage when the evidence only proves variant-local hardening.
16. If bytes returned from an error path can enter consensus-visible results, acknowledgements, receipts, or hashes, prove they are deterministic protocol bytes rather than raw error strings, stack details, local paths, map iteration order, or environment-dependent diagnostics.
17. If the issue is in an adapter path, compare it to the canonical native path and state exactly which property differs: address association, message validation, chain or replay domain, concrete entrypoint scope, gas or accounting, return-data determinism, or final sink authorization.
18. If the issue is in peer penalty or blacklisting logic, distinguish peer abuse from ordinary invalid user transactions. A real issue should show either under-penalized invalid peer input, over-broad penalties that can harm honest peers, or lifecycle cleanup that lets stale counters affect future decisions.
19. If the issue tightens transaction admission, distinguish duplicate or replay hardening, too-new queue or resource control, and actual invalid state execution. Do not claim consensus failure, theft, or finalized-state impact unless the path proves invalid transactions can be committed, executed, or finalized.
20. If the issue involves deterministic consensus callbacks, trace every non-deterministic dependency and classify each error as deterministic invalid input, transient transport/local availability, or operator/environmental failure. A finding needs to show why the callback's return value can diverge across honest nodes or halt consensus.
21. If the issue involves Engine API, block import, or fork-versioned payloads, compare the payload body with every method side argument. Prove whether sidecars, hashes, roots, optional fields, withdrawals, commitments, or fork-gated fields are derived from the payload, checked against it, or supplied independently.
22. If the issue involves vote extensions or commit info, verify upstream guarantees for late or post-quorum data. Do not rely on the normal vote-extension verifier unless the consumed entry is proven to have passed that verifier.
23. If the issue involves aggregate validation, identify the first expensive operation and list every cheap reject condition that runs before it. A DoS finding needs an attacker-controlled aggregate large enough to force expensive work before rejection.
24. If the issue involves duplicate signatures or proofs, prove whether two valid byte encodings can represent the same semantic signer/message/proof. Then trace whether raw-byte equality can turn a duplicate into an error, persistent fork, or missed cleanup.
25. If the issue involves proposal body cardinality, test both missing required objects and many syntactically valid empty objects. Distinguish lifecycle drift from resource, disk, or decode DoS.
26. If the issue involves delayed cross-runtime events, trace past the first adapter into every downstream consensus, validator-set, accounting, upgrade, bridge, or registry consumer. Validate source event order against local sorting/grouping and check same-block dependent events.
27. If the issue involves delayed native-side uniqueness checks, model front-running and duplicate identifiers. Determine whether source-side admission reserves the identifier or whether a later native rejection can strand value, authority, or state.
28. If the issue involves bridge mirrors or cross-domain accounting, build a timed before/after ledger for both directions. A stale mirror finding should show which side has the real backing balance, which side overwrites or consumes the mirror, and how finality latency permits loss or over-withdrawal.
29. If the issue depends on upstream consensus or provider guarantees, require a guarantee ledger entry. Identify the exact provider behavior for normal entries, late entries, replay/recovery entries, and proposer-selected entries. If the local sink cannot prove the consumed entry passed the expected verifier, do not kill the candidate merely because the normal verifier exists.
30. If a consensus-critical candidate is downgraded for missing a dependency reproduction, decide whether a local mock can prove the application's unsafe behavior. A deterministic mock error, malformed-response mock, or alternate-valid-signature unit test is enough to keep the application-level bug alive while separately noting that a live dependency reproduction would strengthen impact.
31. If a validation-order candidate reaches expensive cryptography, proof verification, decompression, database scans, payload execution, or external calls before cheap rejects, estimate worst-case input size from protocol limits. Do not require a full load benchmark before classifying a consensus or proposal-path DoS as likely.
32. If a delayed adapter accepts value, authority, identity, or accounting before a remote/native sink can reject it, trace every downstream consumer. A candidate can be confirmed by a later consumer failure even when the first delivery function appears to handle or log the error.
33. If a mirrored reserve or balance is updated by snapshots, distinguish overwrite semantics from delta semantics. A stale overwrite followed by an admission check that consumes the stale mirror is stronger evidence than a simple delayed update.
34. If a signature or proof malleability candidate exists, require a canonicalization table: semantic message, valid byte encoding A, valid byte encoding B, recovered signer/prover, duplicate key, conflict check, persistence key, and finalization behavior. Kill only if the code canonicalizes before every duplicate/conflict sink or the dependency rejects alternate encodings before application code sees them.
35. If a duplicate-vote, duplicate-certificate, or duplicate-attestation candidate is downgraded because "the normal verifier rejects it", prove that the exact object being consumed necessarily passed that verifier. Otherwise keep the candidate as likely and identify the missing local revalidation.
36. If a deterministic callback depends on local helper work, prove whether the helper's error is swallowed, converted into deterministic protocol output, or returned to the consensus engine. A local availability failure returned from a replicated callback should be treated as availability or consensus risk even without a live dependency reproduction.
37. If a malformed-payload or dependency-error candidate involves retry, prove boundedness. Identify the loop exit condition, context cancellation, timeout, and consensus caller behavior. A retry loop that monopolizes proposal verification or finalization until context expiry can still be liveness-impacting.
38. If a public-key or identity candidate is partial, trace at least one downstream semantic consumer: validator-set construction, signature verification, decompression, quorum accounting, registry lookup, bridge claim, slashability, or rewards. A sink that accepts malformed identity but a later deterministic consumer rejects it is stronger than source-side self-loss.
39. If a delayed identity front-run is claimed, require two actors, one shared sink identity, source-side value or authority accepted for the victim, and sink rejection or unrecoverable downgrade for the victim. Distinguish self-duplicate mistakes from third-party griefing.
40. If a retained-state or proposal-cardinality candidate is claimed, include a numeric or symbolic bound: per-block insertions, maximum proposal size/count, retention or prune delay, repeated scan frequency, and first expensive operation. Without this, keep it as a hypothesis rather than a final finding.
41. If a detached-data or blob-like transaction candidate is claimed, require an equivalence table: user transaction fields, sidecar or commitment fields, block-body representation, proposal serialization, validator reconstruction, execution/import side arguments, and dependency error handling. Confirm whether validators can see a payload that requires side data while passing empty, nil, default, stale, or independently computed side arguments.
42. If a post-quorum metadata candidate is claimed, prove the loop: late or weakly verified entry is retained or exposed, a proposer can include or rely on it, honest validators reject or fail during proposal verification/finalization, and the same poisoned object remains available for later rounds or blocks.
43. If a malformed public-key candidate is claimed, prove both halves: source admission stores the key without semantic validation, and a later deterministic consumer performs curve decoding, decompression, signature verification, active-set export, or quorum accounting that can fail because of that stored key.
44. If a public-key front-run candidate is claimed, require two actors and one shared sink identity. Show actor A's source-side success or reservation, actor B's later source-side value or authority acceptance, the sink-side uniqueness or ownership conflict, and the absence or insufficiency of refund, retry, or recovery.
45. If a retained-root or pending-attestation candidate is claimed, identify the insertion function, persistence key, cleanup condition, retention or trim delay, approval or query iterator, and the smallest attacker-controlled sequence that maximizes retained objects at low cost.
46. If a many-empty-object proposal candidate is claimed, prove validator acceptance rather than just honest-builder behavior. Include the upper bound that permits many entries, the per-entry processing/storage performed before rejection or acceptance, and why gas, bytes, or count limits do not proportionally charge the work.
47. If a deterministic finalization candidate depends on optional helper or background work, trace whether the helper is invoked before or after the consensus state transition result is committed. Optional work that returns errors through the callback before the result is accepted should remain security-relevant.
48. When evidence is split across a final candidate and a family scan, preserve the stronger proof if it is code-grounded and uncontaminated. A final aggregation omission should not kill a concrete scanned path; instead validate it directly against this checklist.

Assign severity using this baseline:
- Critical: direct consensus break, forged finalized state acceptance, bridge or settlement compromise, unauthorized mint or burn, or broad secret compromise.
- High: missing auth on privileged interfaces, unauthorized validator or committee action, slashability bypass, privileged disclosure, or strong policy bypass.
- Medium: denial of service, fee or quota bypass, stale trust-state misuse, malformed-input panic, readiness or verification gap, or incorrect economic/accountability enforcement.
- Low: debug-only or operator-only hardening issue.
- Informational: no practical security consequence.

Output exactly in this schema:
- Verdict:
- Missing property:
- Entry point:
- Sensitive sink:
- Required attacker capabilities:
- Compensating controls:
- Impact:
- Severity:
- Why this severity is justified:
- What test or proof would strengthen confidence:
```
