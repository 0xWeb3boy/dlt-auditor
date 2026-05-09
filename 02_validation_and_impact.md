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
