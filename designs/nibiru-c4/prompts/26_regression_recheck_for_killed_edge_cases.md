# Prompt: Regression Recheck For Killed Edge Cases

Use this family prompt after broad family scans have mapped the repository. Its purpose is to re-open edge classes that are commonly killed too early during validation.

## Objective

Find concrete Medium-or-higher issues in edge cases that look "safe" only because a nearby generic control exists: fail-closed behavior, ante checks, rollback, outer gas burn, broad timeouts, or query-only wrappers.

## Search Instructions

1. Internal contract-call gas:
   - Enumerate helpers that call contracts from native code, precompiles, token integrations, or module logic.
   - For each helper, build success, revert, returned error, panic, and pre-validation failure rows.
   - Track callee gas used, caller gas deducted, caller refund, SDK/native gas, and persisted gas fields.
   - Candidate pattern: state rollback is correct but caller gas accounting uses the success value, zero value, stale value, or total wrapper gas after a failed call.

2. Fee denomination and unit validation:
   - Compare CLI/local builders, RPC builders, transaction JSON/API constructors, `ValidateBasic`, ante decorators, fee deduction, execution gas price conversion, refunds, events, and queries.
   - Candidate pattern: one path builds or accepts a transaction in display/native units while validation or execution interprets it in another unit.
   - Do not downgrade builder/admission mismatches as debug-only if the built transaction can be signed and accepted.
   - Keep a separate row for transaction fee amounts; do not satisfy this row with value-transfer truncation or trace/debug base-fee mismatches.

3. Precompile and adapter method parse errors:
   - Inspect each method body after shared ABI decode.
   - List every parser/converter: address, denom, amount, selector, metadata, bank balance, contract address, query path, and return value.
   - Candidate pattern: an error is ignored, shadowed, overwritten, or checked after a zero/default value reaches keeper state, gas accounting, or return construction.

4. ERC20 optional-return compatibility:
   - Separate empty successful return, ABI `false`, short return, revert, fee-on-transfer, rebasing, and callback behavior.
   - Candidate pattern: the integration claims arbitrary ERC20 support but rejects empty successful returns that widely used ERC20s treat as success.
   - Do not call the rejection a compensating control unless unsupported tokens are explicitly excluded at registration.

5. Fixed callback/helper gas:
   - Search for hardcoded gas budgets in token queries, token transfers, metadata calls, callbacks, or native-to-VM helper calls.
   - Candidate pattern: every nested helper invocation receives a fresh fixed gas budget instead of a budget derived from the current caller frame, enabling recursive or repeated block-level work amplification.
   - Availability impact is enough; do not require theft.

6. Multi-message contract-creation nonce:
   - Build a timeline for SDK sequence, EVM tx nonce, StateDB account nonce, contract-creation nonce reset, failure path, and later messages in the same outer transaction.
   - Candidate pattern: a contract-creation message restores or resets StateDB nonce so a later message passes with a nonce that should have been consumed.
   - Ante sequence checks are not a kill condition unless the execution-time StateDB nonce is proven equal at every boundary.

7. Nested StateDB overwrite:
   - Trace outer Ethereum tx StateDB, saved precompile StateDB, nested contract-call StateDB, restored pointer, dirty-object maps, and final commit.
   - Candidate pattern: an older restored StateDB commits after a nested helper changed the authoritative account, overwriting nested writes or balances.
   - Require the exact object timeline: dirty before nested call, value written by nested helper, restored owner, and final committed value.

8. Trace/replay resource budgets:
   - For TraceTx, TraceCall, TraceBlock, and debug/RPC variants, list predecessor count, predecessor gas, traced tx gas, total timeout, output size, memory capture, return-data capture, and malformed nested tx checks.
   - Candidate pattern: a per-transaction timeout exists but the caller controls an unbounded predecessor list or output dimension.

9. Rebasing or balance-outside-transfer tokens:
   - Build snapshots before transfer, after transfer, after callback, after external balance mutation, during burn/return, and after final invariant checks.
   - Candidate pattern: requested amount, delivered amount, escrow delta, bank amount, EVM balance, and burn/mint amount reconcile for fee-on-transfer but fail after balance changes outside the transfer call.

10. Deterministic account preemption:
   - Re-open account-preemption candidates that were killed as random collision or preimage attacks.
   - Candidate pattern: a deterministic future deployment address is knowable from factory/deployer state, and a normal user can create a non-VM native account at the corresponding address before deployment.
   - New-account default type is not killer evidence for the pre-existing-account path.

11. Read-only shared-state residue:
   - Re-open query/simulation candidates that were killed as "read-only."
   - Candidate pattern: the read-only path writes a shared keeper pointer, cache owner, warmed object, or gas branch flag that survives and changes a later live transaction.

## Output Format

For each candidate:
- Title:
- Edge class:
- Entry point:
- Sensitive sink:
- Generic control that might falsely kill it:
- Why that control is insufficient:
- Exact table/timeline:
- Key files/functions:
- Attacker preconditions:
- Impact hypothesis:
- What would confirm it:
- What would disprove it:

If a class is truly killed, record the exact file/function evidence that kills the exact property, not just a nearby property.
