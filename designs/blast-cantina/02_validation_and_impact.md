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

For gas, refund, rebate, claimable-fee, access-list, and custom-penalty findings, do not reject a concrete mechanism merely because local tests encode the current behavior or because total paid gas is conserved. Before marking invalid, perform an adversarial economic validation:
- identify who submitted the transaction, who paid, who induced the expensive work, who can later claim or receive the fee/rebate, and who would have received it under precise attribution;
- model both self-paid and victim-paid transactions, including callbacks, routers, marketplaces, signature checks, failed transactions, and aggregator flows;
- distinguish "the sender paid gas" from "the attacker paid gas"; a victim-paid failed transaction can still transfer fee value to an attacker-controlled claimable contract;
- distinguish protocol intent from security impact. A unit test that asserts proportional net-fee scaling or reverted-frame attribution proves behavior, not that the behavior is non-exploitable;
- preserve the candidate as confirmed/likely when the code proves a repeatable wrong-recipient fee flow, user/developer fee-share shift, custom gas overcharge, or access-list compatibility break, even if severity is capped by policy uncertainty.

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
20. If the issue involves fee/rebate redistribution, explicitly test the exploit story where an attacker controls a claimable/refunding contract and a different user pays for the transaction path. Reject only after ruling out adversarial transaction composition, not just after showing the fee pool is conserved.
21. If the issue involves a custom gas penalty, compare CALL, STATICCALL, DELEGATECALL, CALLCODE, precompile, no-code, access-list-warmed, first-use, and repeated-use cases separately. A candidate can be valid for one opcode/target class even when adjacent classes are intentional.
22. If the issue involves a claim-rate curve, compare the helper's chosen endpoint with split claims and interior optima. "Claim all", "claim max", and "minimum rate" are distinct sinks and one helper being safe does not kill another.
23. If the issue involves saved maturity, gas seconds, or reusable fee credits, test the resource-exhaustion story explicitly: can old maturity make new gas immediately claimable, reduce capital at risk, defeat admin clawback deterrence, or sustain victim/self-paid block stuffing?
24. If the issue involves direct non-replayable deposits, compute the actual execution budget at the finalizer sink. Include wrapper overhead, calldata/event/check costs, EIP-150 63/64 withholding, reserved gas, post-call writes, and whether the user's requested minimum is meant for the final recipient or the whole deposit transaction.
25. If the issue involves direct genesis, predeploys, or migration storage, compare every constructor/initializer postcondition against the installed storage: initialized flags, owners, roles, implementation slots, version markers, initial share price, share counts, principal, balances, and nonzero bootstrap constants.
26. If the issue involves bridging or tokenized value, compare raw token units, canonical 18-decimal units, principal accounting units, portal mint/value, burn/escrow amount, finalizer calldata amount, event amount, and provider deposit amount. A path can be correct for 18-decimal tokens and wrong for other decimals.
27. If the issue involves reverted or failed transactions, distinguish journaled EVM state from transaction-level gas trackers and fee finalization. A reverted frame can still produce exploitable fee attribution if another party submits or sponsors the failing transaction.
28. If the issue involves negative-yield, discounts, or rounded withdrawals, check protocol-owned fee vaults, base-fee recipients, L1 data-fee recipients, VOID-mode gas buckets, and governance-owned balances separately from user withdrawals.
29. If the issue involves an external yield provider, validate provider-specific emergency modes, oracle caps, delayed truth, shutdown recovery, ownership of deposits inside provider adapters, insurance eligibility snapshots, and keeper/admin sequencing.
30. If the issue involves upgrades, reinitializers, or deployment scripts, check pending message and withdrawal state before and after upgrade: successful/failed replay maps, finalized withdrawal flags, nonces, request ids, output roots, versioned hashes, and reserved-gas assumptions.
31. If a candidate is conditional, hardening-only, or below Medium but has an exact code-level root cause, keep it visible in the candidate index or rejected-candidate log with the exact mechanism. Do not drop it silently during validation.
32. If the issue involves the Blast native precompile, split valid-selector RequiredGas, invalid-selector revert gas, and high-frame precompile custom surcharge into separate candidate shapes. They have different charging predicates and different compensating controls.
33. If the issue involves Blast custom call penalties, keep precompile, no-code/EOA, delegatecall/callcode, access-list-warmed, first-use, and repeated-use cases separate unless the same predicate and same value recipient explain all of them.
34. If the issue involves gas claim helpers, keep saved-seconds carry-forward separate from claimAll split-optimum behavior. One is lifecycle/capital reuse; the other is helper/curve strategy.
35. If the issue involves a proxied predeploy or system contract, build the constructor/initializer/proxy matrix before rejecting. Compare implementation constructor state, proxy storage, direct-genesis storage, initialized flags, owner/governor, version markers, and upgrade safety.
36. If the issue involves an uninitialized implementation with provider/plugin delegatecall hooks, do not stop at "proxy storage is separate." Check whether direct implementation initialization can reach delegatecall, code-destruction, permanent bricking, or implementation-code availability impacts.
37. If the issue involves Lido or another provider with oracle caps, model a large externally knowable loss before the capped local report catches up. Check whether early withdrawals, pending exits, or claimable exits are under-discounted.
38. If the issue involves Maker/DSR or a savings adapter, check emergency shutdown/cage states, whether the normal exit path still works, who owns assets inside `DsrManager` or provider contracts, and whether recovery is possible without normal provider operation.
39. If the issue involves L1 data fees, write the equation that links the L2 fee charged to the real L1 value recovered. Discounted, rounded, or negative-yield withdrawals must be checked against L1 fee vault and protocol cost recovery, not only user balances.
40. If the issue involves custom native bookkeeping, compare resource work to charged gas: state writes, journal entries, predeploy updates, maps, loops over touched contracts, post-transaction allocation, and refunds/rebates that lower effective cost.
41. If the issue involves bridge or messenger upgrades, compare old and new storage keys for successful messages, failed messages, finalized withdrawals, proven withdrawal records, request ids, output roots, nonces, and versioned hashes. A new entrypoint or hash domain can be vulnerable even if the old map is correct.
42. If the issue involves insurance or backstops, distinguish exact loss cover, buffer residual, over-recovery, and fresh-depositor front-running before the loss is locally reported. Current-holder distribution is not equivalent to loss-time eligibility.
43. If the issue involves an uninitialized implementation, validate the implementation-address attack sequence separately from proxy storage compromise: direct initialize implementation, gain implementation-local owner/admin, configure malicious provider/plugin, invoke privileged delegatecall/arbitrary-call hook, then assess bricking/code-destruction under active fork semantics.
44. If the issue involves a constructor-only or non-upgradeable system contract behind a proxy, validate both current genesis state and future upgrade/reinitializer safety. "Genesis works today" does not kill a proxy-intent mismatch if future upgrades can bypass constructor-only invariants.
45. If the issue involves broad native bookkeeping overhead, promote at least one budget-table candidate when attacker-controlled extra native work is only partly metered. It may be Low/Medium or hardening, but do not collapse it into exact selector/surcharge findings.
46. If the issue involves invalid precompile selectors, record required gas, `Run` behavior, error type, remaining gas, gas-tracker attribution, and repeatability separately from valid selector undercharge.
47. If the issue involves Lido oracle caps, evaluate the withdrawal finalization sink explicitly: stale share price, pending/claimable provider loss, local finalization, and later loss realization.
48. If the issue involves insurance timing, include a two-cohort payoff table for old holders and fresh depositors under exact cover, no cover, partial cover, residual buffer, and over-recovery.
49. If the issue involves upgrade replay/double withdrawal, prove or kill duplicate successful value delivery. Adjacent zero-value underdelivery or stranded-value bugs should not be treated as exact double-withdrawal matches.
50. If the issue involves saved gas seconds or maturity carry-forward, validation must include a numeric capital/resource loop. Do not mark the mechanism invalid solely because comments or tests encode current claim-rate behavior; first prove whether old seconds can make later gas immediately claimable, lower capital at risk, or support victim-paid resource pressure after penalties.
51. If the issue involves an uninitialized implementation with delegatecall hooks, validate implementation-address bricking separately from proxy takeover. Proxy storage separation kills proxy takeover, but it does not by itself kill implementation code/state availability, deployment, rescue, monitoring, or accidental-balance impacts.
52. If the issue involves selfdestruct or destructive delegatecall, state the active fork semantics used by the target and whether the effect is permanent code deletion, same-transaction deletion, storage poisoning, temporary bricking, or no meaningful impact.
53. If the issue involves messenger double withdrawal during upgrades, require the nested reinitializer trace: failed value-bearing replay, external target control, upgrade/reinitializer execution inside the replay, guard reset, inner replay acceptance, and two successful value deliveries.
54. If a candidate is generic RPC, p2p, faucet, local tooling, or deployment-operator exposure, keep it out of the final report unless it crosses a production trust boundary and materially affects Blast bridge, yield, gas, predeploy, provider, fee-vault, or upgrade settlement.
55. If the issue involves broad native bookkeeping overhead, validate gas-refund finalizer overhead and native-yield balance/share-count overhead separately. A candidate that proves only `AllocateDevGas` is not enough to cover balance/share-count mutation work.
56. If the issue involves native-yield balance/share-count overhead, require a budget table for `Balance`, `SetBalance`, `SetFlags`, `GetClaimableAmount`, `SubClaimableAmount`, `adjustShareCount`, StateDB journals, predeploy storage reads/writes, automatic value transfers, gas buy/refund balance changes, and selfdestruct beneficiary changes.

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
