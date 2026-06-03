# Prompt: Wasm Staking Mirror Mint

Use this focused pass for EVM-compatible chains where an EVM precompile or host function can call Wasm, and Wasm can emit staking or other native bank-mutating messages.

## Objective

Find native/VM balance mirror bugs where a VM-triggered Wasm staking path mutates native `unibi` without syncing a dirty EVM balance object, then final EVM commit mints or restores the stale delta.

## Search Instructions

1. Map the exact funded Wasm precompile path:
   - EVM call to Wasm precompile `execute` or `executeMulti`.
   - The precompile installs or reuses the active `StateDB`.
   - The call includes `funds` in the VM-mirrored native denom.
   - Wasm transfers funds to the contract before contract execution.
   - The funds transfer syncs the VM-facing mirror and dirties the contract account object.

2. Map the Wasm staking/native message path:
   - Wasm encoders for `StakingMsg::Delegate`, undelegate, redelegate, rewards, or equivalent native messages.
   - SDK message handler authorization for the contract account.
   - Staking keeper method reached by the message.
   - Exact bank keeper method used by staking, especially `DelegateCoinsFromAccountToModule`, `UndelegateCoinsFromModuleToAccount`, or direct SDK `BaseKeeper` balance setters.

3. Build a state-supply ledger for the same transaction:
   - Native bank balance before funds transfer.
   - VM mirror balance before funds transfer.
   - Native bank balance after Wasm funds transfer.
   - Dirty VM mirror value after funds transfer.
   - Native bank balance after staking/delegation.
   - Dirty VM mirror value after staking/delegation.
   - Final `StateDB.Commit` / `SetAccBalance` delta.
   - Final native bank supply, module balance, account balance, and delegation shares.

4. Check compensating controls at the exact sink:
   - Ordinary bank sends syncing the mirror do not kill staking if staking bypasses those wrappers.
   - Future EVM calls overwriting a global pointer do not kill a dirty object committed by the current active `StateDB`.
   - Rollback does not kill a successful staking message path.
   - Feature gating kills only if Wasm staking messages or the Wasm precompile are unreachable in current app wiring.

5. Produce a candidate if the active EVM transaction can leave a stale dirty mirror that final commit treats as authoritative after native staking moved the same `unibi`.

## Output Format

For each candidate:
- Title:
- Entry point:
- Sensitive sink:
- Missing mirror invariant:
- State-supply ledger:
- Key files/functions:
- Attacker preconditions:
- Compensating controls checked:
- Impact hypothesis:
- What would confirm it:
- What would kill it:

End with killed ideas if no candidate survives.
