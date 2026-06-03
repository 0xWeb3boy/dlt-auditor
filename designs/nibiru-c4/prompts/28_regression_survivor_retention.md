# Prompt: Regression Survivor Retention

Use this focused pass after the broad scans. Its purpose is to prevent promising concrete candidates from being lost during canonicalization or validation because a nearby control sounds convincing at the wrong sink.

## Objective

Find and preserve concrete Medium-or-higher issues in classes that are easy to regress: native/VM mirror minting, optional-return token compatibility, deterministic account preemption, failed gas accounting, nested StateDB ownership, read-only shared-StateDB gas nondeterminism, fee builder/validation denominations, multi-message nonce/gas, direct trace replay, parser-error continuation, and balance-outside-transfer token accounting.

## Search Instructions

1. Native/VM mirror minting:
   - Build a ledger for VM-triggered native module calls that mutate the native bank denom mirrored into VM balance state.
   - Include staking, delegation, undelegation, rewards, slashing, Wasm/native messages, module sends, mints, burns, and escrow.
   - Candidate pattern: native bank state changes inside VM execution, but a stale dirty VM balance object later commits an older or larger balance delta back to native bank state.
   - Required focused path: EVM Wasm precompile `execute` or `executeMulti` with `funds=[unibi]`, Wasm contract emits `StakingMsg::Delegate` or undelegation, staking calls SDK bank delegation methods that bypass Nibiru sync wrappers, and final active `StateDB.Commit` restores the dirty mirror through `SetAccBalance`.
   - Do not merge this into generic stale global `Bank.StateDB` cleanup. The survivor question is whether the active transaction's dirty object commits after the native module mutates the same balance.

2. Optional-return token compatibility:
   - Test token helpers against empty successful return data, false returns, short returns, revert data, fee-on-transfer, rebasing/reflection, callback mutations, and metadata failures.
   - Candidate pattern: an integration accepts arbitrary third-party tokens but rejects empty successful return data before balance-delta or state checks can establish success.

3. Failed gas accounting:
   - Build separate tables for failed precompile/host-function exits and failed native-to-VM helper exits.
   - Rows must include ordinary error, VM failure/revert, local SDK out-of-gas panic, pre-validation failure, post-work method error, caller-caught failure, and top-level transaction failure.
   - Candidate pattern: a failed branch charges only current local gas or burns a coarse frame while prior cumulative work, repeated native work, or caller refund/debit diverges from the success branch.
   - Separate fixed ERC20 helper gas from failed-precompile gas. Successful `commit=false` ERC20 read helpers that return `evmResp.GasUsed` but do not charge the parent are a survivor class even when failed helpers burn their fixed limit.

4. Fee builder and validation denomination:
   - Trace fee amount construction from signed VM fee fields through local/RPC builders, static validation, auth-info, ante equality checks, final deduction, and refunds.
   - Candidate pattern: a VM-smallest-unit fee is placed into a native bank-denom SDK coin or compared as if it were native-denom amount.
   - Do not kill this solely because final deduction recomputes the native debit; builder/static-validation compatibility can be the sensitive sink.

5. Nested StateDB ownership:
   - Name the exact account/storage/supply object dirty before helper execution, the nested helper-updated value, and the final committed value.
   - Candidate pattern: an older outer owner commits stale state after a nested helper has updated the canonical object through a different owner.

6. Read-only shared-StateDB gas nondeterminism:
   - Compare a node that served read-only RPC/query/estimate/trace with a node that did not.
   - Track any singleton keeper pointer, active StateDB, cache object, dirty object, or mirror-sync branch left behind by the read-only call.
   - Candidate pattern: the next consensus transaction consumes different bank/mirror gas, takes a different branch, or warms a different object because the prior read-only path mutated process-local shared state.
   - A no-persistence argument is not a kill unless gas and branch determinism are also proven.

7. Outer ethereumTx versus nested CallContract overwrite:
   - Draw the commit order for the outer `ethereumTx` StateDB and the nested `CallContract` or helper StateDB.
   - Include old value, nested-updated value, restored outer dirty value, and final persisted value for every touched account/balance/storage object.
   - Candidate pattern: nested execution updates canonical state, then the restored outer owner commits an older dirty object over it.

8. Failed contract-call gas-used mismatch:
   - Build separate gas ledgers for failed precompile methods and failed internal `CallContractWithInput` helpers.
   - Required columns: outer EVM gas before/after, helper response `GasUsed`, native SDK gas consumed, block/transaction gas accumulator, refund/debit basis, and whether the caller can catch/retry.
   - Rows must include success, revert, non-revert returned error, post-work method error, panic, SDK out-of-gas, and pre-validation failure.

9. Survivor-retention checklist:
   - For each concrete candidate found or killed in this pass, write one of: `keep`, `duplicate`, `invalid`, or `below threshold`.
   - If invalid, name the exact file/function and exact sink property that kills it.
   - If below threshold, explain why user-controlled reachability or Medium impact is absent.
   - The checklist must include explicit rows for Wasm staking mirror minting, fixed ERC20 helper gas, shared-StateDB gas nondeterminism, nested `CallContract` overwrite, failed precompile gas, and failed `CallContractWithInput` gas. If any is absent from final survivors, write the exact sink-level killer evidence.

## Output Format

For each candidate:
- Title:
- Regression class:
- Entry point:
- Sensitive sink:
- Why nearby controls are insufficient:
- Ledger/table/timeline:
- Key files/functions:
- Attacker preconditions:
- Impact hypothesis:
- What would confirm it:
- What would kill it:

End with a survivor-retention checklist listing every candidate-like idea considered and its disposition.
