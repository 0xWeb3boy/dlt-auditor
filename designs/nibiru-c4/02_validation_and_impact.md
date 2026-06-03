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
   - failed-exit gas/resource chargeback
   - authorization error fail-closed handling
   - variant-specific authority at shared base-client sinks
   - amendment, fork, or feature-scoped authorization
   - validator-list or trust-list threshold achievability
   - generated-side-effect authorization
   - exact caller/callee buffer contract
   - lifetime-safe ownership across nested or async execution
   - destination/source length equality before copy-back
   - local progress-invariant feasibility under configured capacity
   - deterministic account creation compatibility
   - account-type compatibility before code or metadata writes
   - nested runtime state ownership
   - token return-value compatibility
   - balance-outside-transfer escrow accounting
   - denomination and unit consistency
   - multi-message nonce or sequence lifecycle consistency
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
17a. If the issue is in a precompile, host function, or VM-to-native adapter, compare success and every failure exit after native work has started. Validate whether cache-context gas, SDK gas, storage writes, and callback resource use are charged or rolled back symmetrically.
17b. If a native adapter calls back into arbitrary VM or token code, prove whether callback gas is bounded by the caller's remaining gas or by a safe protocol cap. For fixed callback gas, analyze recursive reachability and whether the runtime's normal recursion or EIP-150-style constraints are bypassed.
17c. If a finding involves nested execution state, identify which state cache or database instance owns each account/object before the nested call, during the nested call, after restore, and at final commit. A valid finding should show that a stale owner can overwrite a newer authoritative change.
18. If the issue is in peer penalty or blacklisting logic, distinguish peer abuse from ordinary invalid user transactions. A real issue should show either under-penalized invalid peer input, over-broad penalties that can harm honest peers, or lifecycle cleanup that lets stale counters affect future decisions.
19. If the issue tightens transaction admission, distinguish duplicate or replay hardening, too-new queue or resource control, and actual invalid state execution. Do not claim consensus failure, theft, or finalized-state impact unless the path proves invalid transactions can be committed, executed, or finalized.
20. If the issue involves deterministic contract or VM-account creation, compare the pre-existing native account types that can occupy the derived address with the deployment path's required account interface. Prove whether code, code hash, metadata, balance, or nonce can become inconsistent.
21. If the issue involves token integration, distinguish requested amount, transfer return value, actual balance delta, escrow balance, minted or burned representation, and supply invariant. Empty successful return data, false returns, fee-on-transfer, rebasing, and callback behavior should each be checked separately.
22. If the issue involves fees or denominations, name the unit at each boundary and prove where the wrong unit is accepted, compared, charged, refunded, displayed, or persisted.
23. If the issue involves multi-message wrappers, compare admission nonce/sequence changes to execution-time writes for every message in the same wrapper. Include contract creation and failure paths before deciding whether replay, skipped execution, or state/sequence divergence is possible.
24. If the issue involves native balance mutation and VM balance mirrors, enumerate every mutator that can affect the same asset and prove the path under review updates both the native ledger and the VM-facing representation, or prove that only one representation is authoritative at every later sink.
25. If the issue involves staking, delegation, rewards, or slashing from a VM-triggered path, compare it against ordinary native transfers. A path that bypasses transfer hooks may still need mirror synchronization or invariant accounting.
26. If the issue involves a failed internal contract call, validate success and failure gas separately from failed precompile gas. Confirm exactly which gas meter is read for refunding or charging the caller after an error.
27. If the issue involves an outer rollback or full-gas burn as a compensating control, still validate the local invariant. Decide whether the alleged bug is invalid globally, or whether it remains a local accounting, refund, determinism, or availability issue.
28. If the issue involves native account preemption, identify whether the incumbent account can be created after chain launch by normal users, by privileged modules, or only by genesis/migration. Do not mark it below threshold until post-launch account-creation paths have been checked.
29. If the issue involves a parse, decode, or conversion error in an adapter method, trace whether execution continues with an empty address, zero amount, default denom, nil contract, or stale input. Confirm whether that value reaches a keeper, state mutation, gas operation, or consensus-visible return.
30. If the issue involves rebasing or balance-outside-transfer tokens, do not merge it into fee-on-transfer unless the same invariant and trigger are proven. Analyze external balance changes and callbacks independently from transfer-fee deltas.
31. If the issue involves nested StateDB ownership, accept the finding only if the timeline shows a stale owner can influence final commit, gas, or return data. Reject it only after proving every stale object is either discarded before commit or cannot affect later deterministic gas/resource behavior.
32. If the issue involves failed internal contract calls, distinguish the helper's returned error from the caller's gas accounting. A valid finding can be about the caller deducting or refunding the wrong gas value even when state rollback is correct.
33. If the issue involves an ERC20 empty return, do not classify "ABI unpack fails" as a compensating control unless the protocol explicitly rejects optional-return ERC20s. For integrations that accept arbitrary ERC20s, empty success return incompatibility can be a Medium availability/accounting issue.
34. If the issue involves fixed callback gas, validate recursive reachability and block-level work amplification. Do not require theft or persisted state corruption for an availability finding.
35. If the issue involves transaction denomination or fee units, require a path through transaction construction or admission before downgrading as debug-only. Builders and RPC constructors that produce accepted transactions are part of the transaction validity boundary.
36. If the issue involves execution-time nonce writes, ante sequence checks are not sufficient kill evidence by themselves. Compare the actual StateDB nonce at each message boundary and after commit.
37. If the issue involves precompile or adapter parse errors, validate the specific method body. Shared ABI decode success does not prove method-specific parsing, address conversion, denom parsing, or return-value parsing errors are consumed.
38. If the issue involves TraceTx or replay APIs, validate total request cost, not just per-traced-transaction timeout. Predecessor count and predecessor gas should have independent caps or a shared total budget.
39. If the issue involves nested StateDB overwrite after an internal contract call, require evidence about the outer transaction's restored StateDB and final dirty-object commit order. Do not merge it into generic shared-pointer races unless the same overwrite sink is proven.
40. If a candidate was previously rejected as "fail closed", "rollback handles it", "ante handles it", or "only debug", rerun validation against the missing property. A failing tx can still be a compatibility DoS, a rollback can still skip local gas accounting, ante can still miss execution-time state restoration, and debug/query paths can still be public RPC DoS.
41. If the issue involves deterministic account preemption, validate the future-address path separately from random collision or preimage arguments. A factory, deployer nonce, salt, or equivalent deterministic address can give the attacker the address without breaking hashes.
42. If the issue involves a pre-existing native account at a VM deployment address, do not kill it with "missing accounts default to VM accounts." Kill it only if user-created non-VM account classes cannot occupy the address or deployment forcibly converts them before code/metadata writes.
43. If the issue involves transaction fees, require a table from signed fee fields to the SDK coin actually validated or charged. Do not downgrade as debug-only because an unrelated trace, event, value-transfer, or display unit mismatch was found instead.
44. If the issue involves read-only shared mutable state, compare post-query process state against a fresh process and then evaluate a normal live transaction. Deterministic state, gas, and branch behavior must be identical.
45. If the issue involves failed precompile local gas, prove the local gas chargeback executes on every error path after native work starts. A revert or outer failure is not enough unless it charges the same repeated native work budget.
46. If the issue involves nested StateDB overwrite, require the validation to name the old object value, nested helper-updated value, and final committed value. If that table cannot be built, keep the candidate partial rather than merging into a generic mirror-sync issue.
47. If the issue involves failed internal helper calls, include previous helper work or previous wrapped messages in the same outer transaction. A failure branch can be wrong even if single-helper failure appears locally bounded.
48. When validating unit mismatches, state whether the wrong unit affects admission, execution, persistence, refund, event/RPC output, or debug-only output. Admission/execution mismatches carry more weight than display-only mismatches.
49. Before aggregation, check whether any family scan produced a high-confidence candidate in these regression-sensitive classes: native/VM mirror minting, optional ERC20 empty-return incompatibility, deterministic account preemption, multi-message nonce/gas, trace replay budgets, parser-error continuation, and balance-outside-transfer accounting. If a class is absent from the final report, require explicit killer evidence in `rejected-candidates.md`.
50. If validation kills a failed-precompile gas candidate because the VM burns forwarded gas on error, require an error-class matrix. The kill is sufficient only for rows where the same repeated local native/SDK work is fully covered by the consumed gas budget and cannot be retried/caught inside the same frame.
51. If validation kills a fee-denomination candidate because actual deduction recomputes the fee, first decide whether the candidate's claimed sink is builder/static validation/auth-info/mempool compatibility rather than final debit. Keep the candidate if the mismatched SDK coin amount is accepted, signed, compared, or propagated in a way that can reject valid txs, admit invalid txs, or create interoperability failure.
52. If validation kills an optional-return ERC20 candidate, require an explicit in-repo invariant that arbitrary ERC20s with empty successful returns are out of scope. Balance-delta checks do not by themselves prove compatibility if ABI unpacking rejects before the delta can be used.
53. If validation kills native/VM mirror minting, require a full state-supply ledger showing native bank balance, VM mirror balance, dirty StateDB object value, and final committed bank supply for the native module path under review.
54. If validation downgrades a shared StateDB pointer candidate to memory-only, still check whether read-only RPC/query calls can make a later consensus transaction consume different gas on nodes that did not serve the query. That branch-difference property is separate from final-state corruption.
55. If validation kills a Wasm-staking mirror mint candidate, it must address the exact funded precompile timeline: EVM Wasm `execute` installs active `StateDB`, funds transfer dirties the Wasm contract mirror, Wasm staking calls `DelegateCoinsFromAccountToModule` or `UndelegateCoinsFromModuleToAccount`, that SDK bank method bypasses Nibiru sync wrappers, and final active `StateDB.Commit` calls `SetAccBalance`. Generic stale-pointer cleanup analysis is not a kill.
56. If validation kills fixed ERC20 helper gas, separate these rows: successful `commit=false` read helper, failed helper, successful `commit=true` mutation helper, and recursive nested helper. A full charge on failed helpers or charged mutation helpers does not kill successful read-helper undercharging.
57. If validation kills hardcoded helper gas recursion, require evidence that recursive helper calls derive gas from the parent frame's remaining gas or hit a strict shared call-count/depth/work cap before fresh fixed budgets can amplify block work.
58. If validation finds a concrete regression survivor but judges severity below threshold, keep the root-cause dossier and write a sink-level rejected row. Do not silently omit concrete paths for Wasm staking mirror minting, fixed ERC20 helper gas, optional-return ERC20s, fee denomination, deterministic account preemption, multi-message nonce/gas, trace replay, parser-error continuation, or balance-outside-transfer accounting.
59. If validation kills shared `Bank.StateDB` gas nondeterminism, it must compare a node that served the read-only call with a node that did not and prove the next consensus transaction takes identical bank-sync/cache branches and consumes identical gas. Proving no state persistence is not enough.
60. If validation kills an outer `ethereumTx` / nested `CallContract` overwrite candidate, it must identify both StateDB instances, their dirty object maps, the nested commit result, the restored outer owner, and the final persisted value. Kill only if the outer owner cannot commit stale values over nested writes.
61. If validation kills failed precompile native gas chargeback, it must include rows for post-work method error, caller-caught failure, top-level failure, pre-work ABI failure, raw revert, and SDK out-of-gas. For each row, name outer EVM gas, native SDK gas, local helper gas, block gas, and refund/debit.
62. If validation kills failed `CallContractWithInput` gas-used mismatch, it must compare response `GasUsed`, parent gas deducted, block gas added, and refund base for success, revert, non-revert error, panic, and SDK out-of-gas branches.
63. If a candidate is adjacent to a known survivor but not exact, preserve it as partial/support in `rejected-candidates.md` instead of silently merging it. Aggregation should be able to see whether H-02, H-04, H-05, and M-03 were checked exactly.
64. If a candidate claims "failed call gas" generically, split it into failed precompile method gas, failed internal contract-call gas, and multi-message refund/accounting gas before deciding severity or duplication.

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
