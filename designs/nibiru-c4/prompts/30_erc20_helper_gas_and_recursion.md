# Prompt: ERC20 Helper Gas And Recursion

Use this focused pass for token adapters, FunToken bridges, ERC20 precompiles, or native keepers that call attacker-controlled ERC20 contract methods internally.

## Objective

Find fixed helper-gas and chargeback bugs where internal ERC20 helper calls receive a fresh gas budget and successful read-only work is not charged to the parent transaction, precompile, or block gas accounting.

## Search Instructions

1. Map every ERC20 helper call:
   - Metadata helpers such as `name`, `symbol`, `decimals`.
   - Balance helpers such as `balanceOf`.
   - Transfer helpers and any pre/post transfer balance snapshots.
   - Mint/burn helpers.
   - FunToken creation, conversion, precompile `sendToBank`, `balance`, or equivalent paths.

2. Build a helper gas matrix:
   - Helper name.
   - Fixed gas limit or forwarded gas source.
   - `commit=false` or `commit=true`.
   - Success path chargeback target.
   - VM failure/revert chargeback target.
   - Apply error chargeback target.
   - Returned `GasUsed`.
   - Parent SDK gas delta, outer VM gas delta, transient/block gas delta, and refund/debit effect.

3. Preserve the key survivor class:
   - Successful `commit=false` read helpers returning nonzero `GasUsed` but not calling `ResetGasMeterAndConsumeGas`, `AddToBlockGasUsed`, `contract.UseGas`, or equivalent parent chargeback.
   - This is distinct from failed helpers. Do not kill it because failure paths burn the helper gas limit.

4. Analyze recursion and fresh-budget amplification:
   - Attacker-controlled ERC20 helper code can call back into FunToken/precompile/helper paths.
   - Each nested helper should derive its gas from the parent remaining gas or share a strict recursive work cap.
   - A fresh fixed helper budget per nested call can create block-level work amplification or halt production even when each helper is individually capped.
   - Check call-depth limits, precompile cache counts, state cache counts, and whether they bound every nested fresh helper invocation.

5. Analyze impact proportionally:
   - Availability, fee/quota bypass, or underpriced validator CPU is enough for Medium.
   - Do not require theft or persistent state corruption.
   - If recursion is not fully proven, keep the successful read-helper undercharge as a separate candidate rather than killing the entire helper-gas class.

## Output Format

For each candidate:
- Title:
- Entry point:
- Sensitive sink:
- Missing gas invariant:
- Helper gas matrix:
- Recursion/fresh-budget analysis:
- Key files/functions:
- Attacker preconditions:
- Compensating controls checked:
- Impact hypothesis:
- What would confirm it:
- What would kill it:

End with killed ideas if no candidate survives.
