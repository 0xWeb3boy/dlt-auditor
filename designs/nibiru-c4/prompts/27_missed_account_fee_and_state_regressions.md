# Prompt: Missed Account, Fee, And State Regression Recheck

Use this focused pass after the broad cross-runtime scans. Its job is to re-open high-signal classes that are often missed because a nearby control sounds sufficient but does not protect the exact sink.

## Objective

Find concrete Medium-or-higher issues in deterministic account lifecycle, transaction fee units, shared read-only state, failed local gas accounting, nested state ownership, and failed helper-call gas.

## Search Instructions

1. Deterministic future-address account preemption:
   - Build a table of every deterministic VM deployment address formula, including factory-created children and same-sender nonce sequences.
   - Build a table of every native account class that normal users can create after launch: vesting, locked, module-like, smart-contract, named, derived, or compatibility accounts.
   - Candidate pattern: a user can pre-create a non-VM-native account at a future VM deployment address, then deployment stores code or value without writing the required VM account metadata or code hash.
   - Do not kill this with "new accounts default to VM accounts" unless the pre-existing-account path is impossible.

2. Transaction fee amount provenance:
   - Trace signed VM transaction fee helpers from gas limit, gas price, fee cap, tip cap, and base fee through local builders, RPC builders, static validation, ante admission, fee deduction, execution, and refunds.
   - For every boundary, write the unit: VM-smallest-unit, native bank base unit, display unit, decimal-scaled unit, or SDK coin amount.
   - Candidate pattern: a helper returns a VM-smallest-unit fee amount, but builder or validation constructs a native bank coin without converting to the native denominator.
   - Do not satisfy this check with unrelated value-transfer, event, display, or trace-base-fee mismatches.
   - Score the builder/static-validation/auth-info sink separately from final deduction. If a tx can be constructed, signed, compared, rejected, admitted, or propagated with the wrong native-denom fee amount, do not kill it only because final deduction later recomputes a different native debit.

3. Read-only shared-state residue:
   - Inspect query, simulation, estimate, trace, and static-call paths that borrow live keepers, module structs, global pointers, caches, warmed state objects, or gas meters.
   - Candidate pattern: read-only execution assigns a shared pointer or cache owner and does not restore it, so a later live transaction takes a different branch, consumes different gas, or syncs to a stale object.
   - Validate determinism across nodes that did or did not serve the read-only request.

4. Failed precompile or host-function local gas:
   - For every adapter method, place every `return error`, panic recovery, revert, and pre-validation failure relative to local gas chargeback.
   - Candidate pattern: native work consumes local SDK/store gas, then an error return happens before the outer VM/precompile contract is charged for that local gas.
   - Do not let "the outer tx fails" kill the local gas/resource mismatch without proving the outer gas burn covers repeated local work in the same frame.
   - Before killing the class, fill this table: ordinary error, execution-revert-like error, local SDK out-of-gas panic, pre-validation failure, post-work method error, caller-caught failure, top-level failed transaction. For each row, record forwarded gas consumed, local SDK gas consumed, caller refund/debit, and whether a loop can repeat the work.

5. Nested StateDB/helper overwrite:
   - Build a timeline with outer VM StateDB, native adapter cached context, saved/restored keeper state pointer, nested contract-call StateDB, dirty objects, and final commit owner.
   - Candidate pattern: a nested helper updates contract storage, balance, nonce, or supply through one state owner, then an older outer owner commits a dirty object that restores stale fields.
   - Require the timeline to name the account/object that is dirtied before and after the nested call.

6. Failed helper-call gas after prior work:
   - For native-to-VM helpers, build rows for success, VM revert, returned error, panic, and pre-validation failure.
   - Include previous helper work or earlier VM messages in the same outer transaction.
   - Candidate pattern: the failed branch charges only current failed helper gas or a local gas limit while skipping the cumulative value or caller accounting used by successful branches.

7. Regression-retention cross-check:
   - Re-open any strong family-scan candidate in these classes if it is at risk of being downgraded by a nearby control: native/VM mirror minting through staking or Wasm/native module paths, empty-success ERC20 return incompatibility, deterministic future-account preemption, multi-message nonce and refund accounting, direct trace replay budgets, parser-error continuation, and balance-outside-transfer token accounting.
   - For each class, either keep a candidate or write exact sink-level killer evidence. Do not leave a class only as an unpromoted "lower-ranked idea" when arbitrary user-controlled inputs reach the sink.

## Output Format

For each candidate:
- Title:
- Regression class:
- Entry point:
- Sensitive sink:
- Nearby control that might falsely kill it:
- Why that control is insufficient:
- Timeline or unit table:
- Key files/functions:
- Attacker preconditions:
- Impact hypothesis:
- What would confirm it:
- What would disprove it:

If a class is killed, record the exact file/function and exact property that kills it.
