---
case_id: case_20150113_82beaabf6a
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2015-01-13
source_refs:
  - git:82beaabf6a8b5a146a38e1d6a31a78157c79a0cf
  - "core/state_transition.go:193"
  - "vm/vm_debug.go:664"
  - "core/block_processor.go:272"
bug_class: consensus-rule-mismatch
impact_type:
  - consensus-integrity
  - state-integrity
confidence: medium
tags:
  - infrastructure
  - consensus
  - transaction-processing
  - uncle-validation
  - gas-accounting
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The commit titled "Fixed consensus issue" changes go-ethereum consensus-relevant code in contract creation and uncle processing. The strongest supported finding is a likely consensus fix: `StateTransition` stops assigning a code-deposit gas error into the outer transaction error variable, and `BlockProcessor` changes the ancestor window used for uncle handling from 6 to 7. The debug VM change mirrors the error-variable cleanup but is only supporting evidence.

## Observed Patch Facts

1. In `core/state_transition.go`, the patch replaces `if err = self.UseGas(dataGas); err == nil {` with `if err := self.UseGas(dataGas); err == nil {`.

2. In `vm/vm_debug.go`, the patch replaces `ret, err, ref := self.env.Create(context, addr, input, gas, price, value)` with `ret, suberr, ref := self.env.Create(context, addr, input, gas, price, value)`.

3. In `core/block_processor.go`, the patch replaces `for _, ancestor := range sm.bc.GetAncestors(block, 6) {` with `for _, ancestor := range sm.bc.GetAncestors(block, 7) {`.

## Project Context

Historical context from `vm/context.go`, `vm/types.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm_env.go`, `core/filter.go`. The strongest project-level identifiers around this patch are `dataGas`, `UseGas`, `ancestor`, and `SetCode`.

## Before/After Behavior

Before the patch, contract creation code-deposit gas charging assigned `self.UseGas(dataGas)` into the outer named `err`; after the patch, that result is scoped to the conditional that decides whether to install returned code. Before the patch, uncle processing collected `GetAncestors(block, 6)`; after the patch, it collects `GetAncestors(block, 7)`. Before the patch, the debug VM CREATE path reused `err` for a subcall result; after the patch, it uses `suberr`.

# Root Cause

The evidence supports a consensus implementation mistake, not memory corruption or direct code execution. One part is error-variable reuse in contract creation gas accounting; another is an off-by-one-looking ancestor-window constant in uncle handling. The provided input does not establish which hunk was the primary root cause or show the exact failing block/transaction.

## Walkthrough

1. A contract-creation transaction reaches `StateTransition.TransitionState` and calls `vmenv.Create`.

2. If creation succeeds, the code calculates code-deposit gas from the returned code length.

3. Before the patch, failure from `UseGas(dataGas)` was assigned to the outer named return `err`.

4. After the patch, that failure is local to the `if` statement and only controls whether `ref.SetCode(ret)` runs.

5. Block reward/uncle handling builds an ancestor hash set in `AccumelateRewards`.

6. The patch changes that set from 6 ancestors to 7 ancestors, affecting consensus-relevant uncle handling.

7. The debug VM hunk uses `suberr` for CREATE failure handling, but this is secondary because the supplied evidence marks it as a debug path.

8. The evidence supports consensus-divergence risk in principle, but does not prove an exploit scenario.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state_transition.go | 193 | contract creation state transition; charges code-deposit gas and conditionally installs returned code |
| core/block_processor.go | 272 | uncle validation/reward ancestry window used during block processing |
| vm/vm_debug.go | 664 | debug VM CREATE handling; avoids clobbering outer execution error with subcall error |

## Code Snippets

## Snippet 1

Context: `core/state_transition.go:193` (changes a sensitive control or state-update path)

Before
```go
dataGas := big.NewInt(int64(len(ret)))
			dataGas.Mul(dataGas, vm.GasCreateByte)
			if err = self.UseGas(dataGas); err == nil {
				//self.state.SetCode(ref.Address(), ret)
				ref.SetCode(ret)
			}
```
After
```go
dataGas := big.NewInt(int64(len(ret)))
			dataGas.Mul(dataGas, vm.GasCreateByte)
			if err := self.UseGas(dataGas); err == nil {
				ref.SetCode(ret)
			}
```

## Snippet 2

Context: `vm/vm_debug.go:664` (changes a sensitive control or state-update path)

Before
```go
context.UseGas(context.Gas)

			ret, err, ref := self.env.Create(context, addr, input, gas, price, value)
			if err != nil {
				stack.Push(ethutil.BigFalse)
```
After
```go
context.UseGas(context.Gas)

			ret, suberr, ref := self.env.Create(context, addr, input, gas, price, value)
			if suberr != nil {
				stack.Push(ethutil.BigFalse)
```

## Snippet 3

Context: `core/block_processor.go:272` (changes a sensitive control or state-update path)

Before
```go
ancestors := set.New()
	for _, ancestor := range sm.bc.GetAncestors(block, 6) {
		ancestors.Add(string(ancestor.Hash()))
	}
```
After
```go
ancestors := set.New()
	for _, ancestor := range sm.bc.GetAncestors(block, 7) {
		ancestors.Add(string(ancestor.Hash()))
	}
```

# Fix Pattern

Scope nested operation errors locally when they should not overwrite the outer consensus result, and correct protocol-sensitive boundary constants in block-processing logic.

## How It Was Fixed

`core/state_transition.go` changed `if err = self.UseGas(dataGas); err == nil` to `if err := self.UseGas(dataGas); err == nil`. `core/block_processor.go` changed `GetAncestors(block, 6)` to `GetAncestors(block, 7)`. `vm/vm_debug.go` changed the CREATE subcall error variable from `err` to `suberr`.

# Why It Matters

1. Touches production consensus paths.

2. Consensus clients must agree on transaction results and block rewards.

3. Uncle handling depends on the exact ancestor window.

4. No evidence shows RCE, key theft, memory corruption, or a concrete exploit.

# Evidence Notes

Grounded evidence is limited to the shown hunks and commit subject. The claim that this is consensus-relevant is supported by `core/state_transition.go`, `core/block_processor.go`, and the subject "Fixed consensus issue". Claims about a demonstrated chain split, exploit transaction, attacker impact, or precise Ethereum rule are not established by the provided input. Protocol security invariant: Consensus-critical transaction execution and block processing must apply the same gas-accounting, error-result, uncle-validation, and reward rules on every node. The patch changes behavior in those paths, but the supplied evidence does not prove a concrete exploit, chain split, or attack transaction. Verification notes: The patch does not prove remote code execution, key theft, or memory corruption. The patch does not show a concrete exploit transaction or block. The debug VM hunk alone is not evidence of a production security bug. The exact intended Ethereum uncle-depth rule is inferred from the patched consensus path, not independently specified in the provided context. The diff supports consensus divergence risk, but not the scope or likelihood of real network exploitation. No concrete exploit case is provided. No independent protocol specification is provided for the ancestor depth. The debug VM change should not be treated as primary production-security evidence. Tests are mentioned in the file list, but no test diff is supplied in the evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-rule-mismatch`
Final impact type: `consensus-integrity, state-integrity`
Final confidence: `medium`
Final tags: `infrastructure, consensus, transaction-processing, uncle-validation, gas-accounting`

The supplied evidence supports retaining this as security-relevant, but the stronger `security-fix` framing is not fully proven. The commit explicitly says it fixes a consensus issue and the patch changes consensus-critical transaction execution and uncle-processing behavior. However, the evidence does not show a concrete exploit, chain split, malformed block, or failing regression, so the conservative classification is security hardening around consensus integrity rather than a confirmed exploitable security fix.

## Security Evidence

1. Commit subject is `Fixed consensus issue`.
2. `core/state_transition.go` changes contract-creation code-deposit gas handling so a code-deposit gas failure no longer overwrites the outer transaction error.
3. `core/block_processor.go` changes uncle ancestor collection from 6 to 7 ancestors in block reward/uncle processing.
4. Touched paths are production consensus paths for transaction execution and block processing.

## Missing Evidence

1. No exploit transaction or malicious block is provided.
2. No test diff or failing consensus case is shown in the supplied evidence.
3. No independent protocol rule is supplied to prove the ancestor depth or gas error behavior from specification.
4. No evidence of an observed chain split or network impact is included.

## Claim Boundaries

1. Supports consensus-integrity risk, not RCE, key theft, or memory corruption.
2. Debug VM error-variable cleanup is secondary and should not be treated as primary production-security evidence.
3. The exact primary root cause cannot be determined from the provided hunks alone.
4. Classify as security-hardening because the patch tightens consensus-sensitive behavior without proving a concrete exploit.
