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
   - progress or reservation monotonicity
   - lifecycle cleanup
   - state-coordinate consistency
   - arithmetic bounds
   - read-only vs persistent-side-effect separation
   - fork/version/method-specific consensus rule coverage
   - chain-variant rule coverage
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
4. Search for compensating controls elsewhere in the codebase.
5. Decide whether the issue is:
   - confirmed
   - likely
   - unclear
   - invalid

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
