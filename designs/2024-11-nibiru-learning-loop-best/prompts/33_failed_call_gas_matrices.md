# Prompt: Failed Precompile And Contract-Call Gas Matrices

Use this focused pass to separate failed precompile method gas, failed internal contract-call gas, and multi-message refund/accounting gas.

## Objective

Find candidates where a failed precompile method or failed `CallContractWithInput` branch performs native or helper work but reports, charges, accumulates, or refunds gas differently from the corresponding successful branch.

## Search Instructions

1. Build one matrix for custom precompile/host-function methods:
   - success,
   - ABI/pre-work failure,
   - post-work method error,
   - raw EVM revert,
   - non-revert returned error,
   - local SDK out-of-gas panic,
   - caller-caught failure,
   - top-level transaction failure.
2. Build a second matrix for internal `CallContractWithInput` or helper calls:
   - success,
   - revert,
   - non-revert returned error,
   - panic,
   - SDK out-of-gas,
   - failure after previous helper work in the same outer transaction,
   - failure after previous message work in a multi-message wrapper.
3. Required columns for each matrix:
   - outer EVM gas before/after,
   - helper/precompile local gas limit,
   - helper response `GasUsed` or remaining gas,
   - native SDK gas meter before/after,
   - block/transaction gas accumulator,
   - refund/debit basis,
   - whether the caller can catch, retry, or loop.
4. Do not kill a candidate with a generic "child frame burns gas" argument unless the matrix proves the repeated native SDK or helper work is fully covered and cannot be retried with fresh budgets.
5. Do not merge failed-call gas-used mismatch into ordinary multi-message refund bugs unless the same response `GasUsed`/refund sink is involved.
6. Treat compatibility/availability impacts as Medium candidates when an attacker can repeatedly force validators or public RPC nodes to do native work that is not charged to the authoritative budget.

## Output Format

For each candidate:
- Title:
- Gas class:
- Entry point:
- Sensitive sink:
- Gas matrix:
- Divergent branch:
- Key files/functions:
- Attacker preconditions:
- Impact hypothesis:
- What would confirm it:
- What would kill it:

End with a summary table splitting failed-precompile gas, failed `CallContractWithInput` gas, successful ERC20 helper undercharge, and multi-message refund/accounting bugs.
