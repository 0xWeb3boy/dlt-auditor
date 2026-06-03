# Prompt: Nested CallContract StateDB Overwrite

Use this focused pass to find outer EVM transaction state owners that can overwrite state committed by nested `CallContract` or helper execution.

## Objective

Find candidates where an outer `ethereumTx` or precompile execution owns one `StateDB`, a nested `CallContract`/helper/precompile path creates or installs another `StateDB`, the nested path updates canonical state, and the restored outer owner later commits stale dirty objects over the nested result.

## Search Instructions

1. Locate all internal contract-call helpers and precompile paths that create, save, restore, or commit a `StateDB`.
2. For each nested path, write the owner timeline:
   - active owner before nested call,
   - saved pointer/cache context,
   - nested owner during `CallContract` or helper execution,
   - object dirtied by the nested owner,
   - restored outer owner,
   - final commit owner.
3. For every touched object, build a value table:
   - old value before helper,
   - outer dirty value before helper,
   - nested-updated canonical value,
   - restored outer dirty value,
   - final persisted value after outer commit.
4. Check account balance, bank mirror balance, nonce, code hash, storage slot, and FunToken/ERC20 accounting objects separately.
5. Distinguish this from generic stale pointer cleanup:
   - a valid candidate must name the object whose old, nested-updated, and final values differ;
   - a kill must prove stale dirty objects are discarded, merged, or reloaded before final commit.
6. Include success and failure branches. A nested update followed by an outer failure may still matter for gas/refund accounting even if state rolls back.

## Output Format

For each candidate:
- Title:
- Outer entry point:
- Nested entry point:
- Sensitive sink:
- StateDB owner timeline:
- Object value table:
- Why existing rollback/restore is insufficient:
- Key files/functions:
- Attacker preconditions:
- Impact hypothesis:
- What would confirm it:
- What would kill it:

End with a checklist of every internal contract-call/precompile helper path that saves, swaps, restores, or commits a `StateDB`.
