# Prompt: Cross-Runtime Accounting And EVM Edge Cases

Use this family prompt for EVM-compatible chains embedded in a native blockchain runtime, and for any repository with precompiles, Wasm/native bridges, token adapters, or multi-message wrappers.

## Objective

Find bugs where native runtime state, VM state, token accounting, gas accounting, or account lifecycle rules diverge across equivalent paths.

## Search Instructions

1. Map every runtime boundary first:
   - EVM to native module calls.
   - Native module to EVM or token helper calls.
   - Wasm to native bank, staking, or EVM calls.
   - Precompile, host-function, RPC simulation, trace, and query entrypoints.
   - Batched SDK transactions containing multiple VM messages.

2. Build an account-class matrix:
   - EOA, VM contract account, native base account, vesting or locked account, module account, smart-contract account, precompile account, and compatibility or legacy account.
   - For each class, record whether it can be created by users after launch, by genesis/migration only, by governance/module logic, or by deterministic address derivation.
   - Compare deployment and code-hash writes against all pre-existing account classes at the derived address.
   - Include future deterministic deployment addresses from factories, salts, nonces, or child-contract counters; user-created native accounts at those future addresses do not require a hash preimage.
   - Treat account type, sequence/nonce, balance, code hash, and metadata as separate invariants.

3. Build a native balance-mutator mirror table:
   - Include send, multi-send, module send, mint, burn, escrow, staking/delegation, undelegation, rewards, slashing, vesting unlock, contract-triggered native messages, and any token factory paths.
   - For each path, record whether it updates native bank state, VM balance state, token supply, module escrow, and invariant-accounting state.
   - Search for mutators that bypass hooks or helpers used by ordinary transfers.
   - Check both direct user transactions and VM-triggered native calls.
   - For VM-triggered native module calls, add a supply-delta row: native balance before/after, VM mirror before/after, dirty StateDB object value before/after, and final committed supply. Include staking/delegation and Wasm-triggered native messages even if they are not ordinary bank sends.
   - For Wasm precompile calls, specifically trace `execute` and `executeMulti` with `funds=[unibi]` into a Wasm contract that emits `StakingMsg::Delegate` or undelegation. Check whether staking uses SDK bank methods such as `DelegateCoinsFromAccountToModule` / `UndelegateCoinsFromModuleToAccount` that bypass ordinary Nibiru bank sync wrappers.
   - If a funded Wasm execute dirties a contract's VM mirror and a later staking message in the same EVM transaction moves native `unibi`, evaluate final active `StateDB.Commit` and `SetAccBalance` before considering stale-global-pointer compensating controls.

4. Build a gas and refund ledger:
   - For precompile calls, internal contract-call helpers, RPC simulation, and trace replay, record outer VM gas, native/SDK gas, local helper gas, transient gas used, and refund base.
   - Compare success, revert, returned error, panic, pre-validation failure, and cache-context failure.
   - Do not let a full outer gas burn automatically kill a finding: first prove whether local gas, SDK gas, or refund calculation can still diverge.
   - Split failed precompile exits into ordinary returned errors, local SDK out-of-gas, revert-like errors, and post-work method errors. For each row, record whether the caller can catch/retry and whether repeated native work is fully charged.
   - Split internal helper failures into success, VM failure, returned error, panic, and pre-validation failure. Include any helper work already accumulated earlier in the same outer transaction.

5. Build a nested state-ownership timeline:
   - Active StateDB or cache owner before call.
   - Owner passed into native adapter.
   - Owner created for nested VM/helper execution.
   - Dirty object map touched by nested execution.
   - Owner restored after helper returns.
   - Owner that commits or generates return data.
   - Search for older caches, stale pointers, or shared keeper fields that can overwrite newer state or change deterministic gas/resource behavior.
   - Keep within-transaction active-owner commits separate from post-transaction stale global pointer residue. A generic "future EVM call overwrites the global pointer" does not kill a dirty object committed by the current transaction's active owner.

6. Build an ERC20/token compatibility matrix:
   - Empty successful return data.
   - ABI false return.
   - Short return data.
   - Revert with data.
   - Fee-on-transfer delta.
   - Balance change outside transfer, such as rebase.
   - Callback before and after balance snapshots.
   - Metadata lookup failure.
   - Compare requested amount, delivered amount, escrowed amount, minted amount, burned amount, native bank balance, VM balance, and invariant detector input.
   - Treat empty successful return data as reportable when arbitrary third-party ERC20s are in scope; do not merge it into false-return handling or fee-on-transfer accounting.

7. Build a fee and denomination unit matrix:
   - Local tx builders.
   - RPC tx constructors.
   - `ValidateBasic` or equivalent static validation.
   - Ante/admission checks.
   - Fee deduction.
   - Gas price conversion.
   - Execution charging.
   - Refunds.
   - Display/query fields.
   - Trace/debug paths.
   - Mark every unit boundary and search for paths that validate one denom/unit but execute another.
   - Trace transaction fee amounts separately from transfer values and debug base-fee fields. A fee helper that returns VM-smallest-unit amounts must be converted before constructing native bank-denom SDK coins.
   - Keep builder/auth-info/static-validation bugs separate from actual deduction bugs. A correct debit path does not automatically fix a wrapper fee amount that was constructed, signed, validated, compared, or propagated in the wrong denomination.

8. Build a multi-message nonce and gas timeline:
   - Include SDK sequence, VM account nonce, StateDB object nonce, transaction index, transient gas, refund base, and final account state.
   - Compare normal call, contract creation, failed call, and later messages in the same outer transaction.
   - Check whether a first message can change or reset a nonce/state object that a later message relies on.

9. Build a precompile and adapter parse-error checklist:
   - ABI unpack, address conversion, denom parsing, amount parsing, contract lookup, method selector, metadata lookup, and keeper lookup.
   - For every error, prove the method returns before keeper state access, gas/resource work, or return-data construction.
   - If execution continues, trace the empty, nil, zero, default, or stale value to a sink.

10. Output up to 5 candidate findings. Prefer candidates with:
    - A concrete entrypoint and sink.
    - A table or timeline showing the divergence.
    - A specific missing invariant.
    - A feasible attacker-controlled path.
    - A test shape that would confirm or kill it.

## Output Format

For each candidate:
- Title:
- Boundary:
- Entry point:
- Sensitive sink:
- Missing invariant:
- Table or timeline summary:
- Key files/functions:
- Attacker preconditions:
- Impact hypothesis:
- Compensating controls to check:
- Test/proof needed:

If no strong candidates exist, write a short killed-ideas section with the concrete files and compensating controls reviewed.
