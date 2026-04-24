---
case_id: case_20150113_82beaabf6
project: bor
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
confidence: medium
tags:
  - consensus
  - contract-creation
  - uncle-processing
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a likely consensus-fix classification, but not a fully proven exploit narrative. The patch corrects two consensus-sensitive logic points: CREATE code-deposit gas handling in state transition code and the ancestor-depth constant used in uncle/reward processing.

## Observed Patch Facts

1. In `core/state_transition.go`, the patch replaces `if err = self.UseGas(dataGas); err == nil {` with `if err := self.UseGas(dataGas); err == nil {`.

2. In `vm/vm_debug.go`, the patch replaces `ret, err, ref := self.env.Create(context, addr, input, gas, price, value)` with `ret, suberr, ref := self.env.Create(context, addr, input, gas, price, value)`.

3. In `core/block_processor.go`, the patch replaces `for _, ancestor := range sm.bc.GetAncestors(block, 6) {` with `for _, ancestor := range sm.bc.GetAncestors(block, 7) {`.

## Project Context

Historical context from `vm/context.go`, `vm/types.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm_env.go`, `core/filter.go`. The strongest project-level identifiers around this patch are `dataGas`, `UseGas`, `ancestor`, and `SetCode`.

## Before/After Behavior

Before the patch, CREATE code-deposit charging in `core/state_transition.go` assigned into the function's outer `err` variable; after the patch, that `UseGas(dataGas)` result is scoped to the conditional. Before the patch, `core/block_processor.go` built its ancestor set with `GetAncestors(block, 6)`; after the patch it uses `GetAncestors(block, 7)`. `vm/vm_debug.go` also renames the inner CREATE error from `err` to `suberr`, which supports the same local-error-separation reading but is not primary consensus evidence.

# Root Cause

Consensus-sensitive logic was encoded with brittle local control flow and an incorrect rule constant: the CREATE code-deposit check reused an enclosing error variable, and uncle processing used a different ancestor depth than the fixed code.

## Walkthrough

1. `TransitionState()` runs contract creation, computes code-deposit gas from returned bytecode, and conditionally installs code with `SetCode(ret)`.

2. The patch changes the deposit-gas check from writing to the outer `err` variable to using a scoped temporary, narrowing the effect of that sub-step.

3. `AccumelateRewards()` builds an ancestor set used during uncle handling.

4. The patch changes that ancestor lookup window from 6 to 7, altering a consensus input used in block processing.

5. `vm/vm_debug.go` mirrors the error-variable separation with `suberr`, but that file is supporting context rather than the root consensus path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state_transition.go | 193 | contract-creation state transition; gas charge for deposited code and resulting transaction error semantics |
| core/block_processor.go | 272 | block processing; ancestor set used for uncle eligibility/reward validation |
| vm/vm_debug.go | 664 | debug/execution mirror of CREATE error handling, likely consistency support rather than the authoritative consensus path |

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

Localize sub-operation error handling and correct consensus-rule constants in validation/execution paths.

## How It Was Fixed

The fix scopes the CREATE code-deposit gas result to the `if` statement in `core/state_transition.go` instead of overwriting the function's outer error state, and it updates `core/block_processor.go` to use a 7-ancestor window when building the ancestor set for uncle handling. The debug VM change renames the inner CREATE error variable for consistency.

# Why It Matters

1. Consensus code must be deterministic across nodes.

2. CREATE result handling affects post-transaction state.

3. Ancestor-depth checks affect uncle validation and rewards.

4. Small logic mismatches in these paths can cause chain disagreement.

# Evidence Notes

The strongest evidence is the direct code change in `core/state_transition.go`, the off-by-one-style constant change in `core/block_processor.go`, and the commit subject `Fixed consensus issue`. The supplied material does not prove a live fork, affected versions, or an end-to-end exploit path. `vm/vm_debug.go` should be treated as supporting evidence only. Protocol security invariant: Nodes must derive the same CREATE result state and apply the same ancestor-depth rule during uncle validation and rewards, or they can disagree on post-transaction state or block validity. Verification notes: The patch does not by itself prove a practical remote exploit path. The diff does not show whether both hunks were independently consensus-breaking on a live network. The exact protocol-intended CREATE failure semantics are inferred from the code change, not proven by an included spec. `vm/vm_debug.go` is not strong evidence on its own that the debug path participated in consensus. The patch does not quantify chain impact, affected versions, or whether any fork was observed in production. No protocol spec or incident report was provided. No test diff was provided, even though a test file is listed in the commit metadata. The exact runtime impact of the outer `err` reuse is inferred from the code change rather than demonstrated by included execution traces. The ancestor-depth change is clearly consensus-relevant code, but the intended rule is inferred from the fix rather than shown from a specification. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-rule-mismatch`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, contract-creation, uncle-processing`

The supplied patch evidence supports keeping this as a security-relevant consensus hardening case, not a fully proven security bug. The changes land in consensus-critical paths: contract-creation state transition behavior and ancestor depth used in uncle/reward processing. That is enough to infer a security-sensitive integrity risk in a blockchain client, especially with the commit subject "Fixed consensus issue." However, the patch alone does not prove a concrete exploitable vulnerability, observed fork, or attacker-driven incident, so labeling it as a confirmed security-fix or as precise "state-corruption" would overstate the evidence.

## Security Evidence

1. Commit subject explicitly says "Fixed consensus issue".
2. `core/state_transition.go` changes CREATE code-deposit gas handling in transaction state transition logic.
3. `core/block_processor.go` changes ancestor depth from 6 to 7 in uncle/reward processing, which affects consensus rules.
4. The patch alters behavior that can influence node agreement on state or block validity, not just logging or cleanup.

## Missing Evidence

1. No protocol spec, advisory, or issue text is provided to prove the intended rule.
2. No included test diff or failing regression case demonstrates the bad behavior.
3. No evidence shows an observed chain split, invalid block acceptance, or practical exploit path.
4. The debug VM rename is only supporting context and does not prove consensus impact by itself.

## Claim Boundaries

1. Supported: this is a consensus-sensitive fix in security-relevant blockchain execution/validation code.
2. Supported: retaining it as security-hardening is reasonable because consensus integrity is exposed to network inputs.
3. Not supported: a confirmed exploitable vulnerability with demonstrated attacker impact.
4. Not supported: the more specific original bug class `state-corruption` as the proven root cause from this patch alone.
