---
case_id: case_20150113_82beaabf6
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: medium
date: 2015-01-13
source_refs:
  - git:82beaabf6a8b5a146a38e1d6a31a78157c79a0cf
  - "core/state_transition.go:193"
  - "vm/vm_debug.go:664"
  - "core/block_processor.go:272"
bug_class: consensus-rule-correction
impact_type:
  - consensus-integrity
tags:
  - go-ethereum
  - consensus
  - transaction-processing
  - contract-creation
  - uncle-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely consensus security fix in go-ethereum. The strongest grounded changes are in contract creation handling and uncle validation depth. The patch does not establish remote exploitability, theft, privilege escalation, or memory corruption.

## Observed Patch Facts

1. In `core/state_transition.go`, the patch replaces `if err = self.UseGas(dataGas); err == nil {` with `if err := self.UseGas(dataGas); err == nil {`.

2. In `vm/vm_debug.go`, the patch replaces `ret, err, ref := self.env.Create(context, addr, input, gas, price, value)` with `ret, suberr, ref := self.env.Create(context, addr, input, gas, price, value)`.

3. In `core/block_processor.go`, the patch replaces `for _, ancestor := range sm.bc.GetAncestors(block, 6) {` with `for _, ancestor := range sm.bc.GetAncestors(block, 7) {`.

## Project Context

Historical context from `vm/context.go`, `vm/types.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm_env.go`, `core/filter.go`. The strongest project-level identifiers around this patch are `dataGas`, `UseGas`, `ancestor`, and `SetCode`.

## Before/After Behavior

Before the patch, contract creation code-deposit gas charging assigned `self.UseGas(dataGas)` into the outer `err` return variable; after the patch, that gas-charge error is scoped locally and only controls whether `ref.SetCode(ret)` is called. Before the patch, uncle validation built its ancestor set from `GetAncestors(block, 6)`; after the patch, it uses `GetAncestors(block, 7)`. The debug VM CREATE change renames a subcall error variable to `suberr`, which is consistent with cleanup but is not enough on its own to establish security relevance.

# Root Cause

The supported root cause is consensus-sensitive edge-case handling: contract creation code-deposit gas failure was propagated through the outer transition error variable, and uncle validation used a different ancestor depth than the patched rule. The exact network split scenario is not shown by the provided evidence.

## Walkthrough

1. A contract-creation transaction reaches `StateTransition.TransitionState` and executes creation code through `vmenv.Create`.

2. If creation execution succeeds, the transition computes code-deposit gas from the returned code length.

3. Before the fix, failure to pay that code-deposit gas assigned to the outer transition `err`; after the fix, it is kept local and prevents only `ref.SetCode(ret)`.

4. Because `SetCode` persists returned creation code, this affects consensus-visible state transition behavior.

5. During block reward and uncle processing, `AccumelateRewards` constructs a set of recent ancestors.

6. The patch changes that ancestor set from 6 to 7 ancestors, altering uncle validation behavior.

7. The debug VM hunk mirrors the error-variable cleanup pattern but is treated only as supporting consistency cleanup.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/state_transition.go | 193 | contract creation code-deposit gas accounting and transition error propagation |
| core/block_processor.go | 272 | uncle ancestor set construction used during block reward/uncle validation |
| vm/vm_debug.go | 664 | debug VM CREATE subcall error handling, likely consistency cleanup rather than primary consensus path |

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

Use local error scoping for nested gas/accounting checks and correct the consensus validation boundary for uncle ancestor depth.

## How It Was Fixed

`core/state_transition.go` changed `if err = self.UseGas(dataGas)` to `if err := self.UseGas(dataGas)`, so code-deposit gas failure no longer overwrites the outer transition error. `core/block_processor.go` changed uncle ancestor collection from depth 6 to depth 7. `vm/vm_debug.go` changed the CREATE subcall error variable to `suberr`, but that debug-path change is not the main basis for classification.

# Why It Matters

1. Consensus clients must agree on transaction success, code persistence, block validity, and rewards.

2. An uncle-validation off-by-one can affect whether a block is accepted or rejected.

3. Contract creation edge cases can affect resulting state across nodes.

4. The evidence supports likely consensus security impact, but not a fully reconstructed exploit.

# Evidence Notes

Primary evidence is the commit subject `Fixed consensus issue` plus focused changes in `core/state_transition.go`, `core/block_processor.go`, and `vm/vm_debug.go`. The code shows consensus-adjacent behavior changes, especially code-deposit gas error scoping and uncle ancestor depth. Claims about remote exploitability, theft, privilege escalation, memory corruption, or the debug VM hunk being independently security-critical are unsupported. Protocol security invariant: Nodes must apply identical consensus rules for transaction execution, contract creation code-deposit gas handling, and uncle eligibility so block validity and resulting state are deterministic across the network. Verification notes: The patch does not by itself prove remote exploitability. The evidence does not show funds theft, privilege escalation, or memory corruption. The debug VM change alone is not enough to classify the issue as security-relevant. The exact consensus split scenario is not reconstructed beyond the changed state-transition and uncle-depth rules. No claim is made that all changed hunks are equally security-critical. Confirmed by provided diff snippets only; no external context used. Exact consensus split or exploit scenario is not demonstrated. Tests are mentioned in the file list, but no test content was provided for validation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-rule-correction`
Final impact type: `consensus-integrity`
Final tags: `go-ethereum, consensus, transaction-processing, contract-creation, uncle-validation`

The supplied evidence supports retaining this as security-relevant consensus hardening, but not confidently as a concrete exploitable security fix. The commit explicitly says it fixes a consensus issue and changes consensus-visible behavior in contract creation gas/code handling and uncle ancestor depth. However, the patch evidence does not reconstruct a specific fork, exploit path, attacker trigger, or demonstrated state corruption, so the original state-corruption/security-fix framing is stronger than the evidence proves.

## Security Evidence

1. Commit subject is "Fixed consensus issue".
2. State transition code changes error scoping around contract creation code-deposit gas and SetCode behavior.
3. Block processor changes uncle ancestor collection depth from 6 to 7, affecting consensus validation/reward logic.
4. Touched files are core transaction/block processing paths in go-ethereum, where divergent behavior can affect network consensus.

## Missing Evidence

1. No test content is provided showing the failing consensus case.
2. No concrete chain split, invalid block acceptance, or exploit scenario is demonstrated.
3. No evidence of theft, privilege escalation, memory corruption, or remote crash impact.
4. The debug VM variable rename appears cleanup-oriented and is not independently security-relevant from the supplied evidence.

## Claim Boundaries

1. Classify as consensus security hardening rather than proven exploitable security fix.
2. Do not claim funds theft, account compromise, memory safety impact, or privilege escalation.
3. Do not treat the debug VM hunk as a primary security fix.
4. Limit impact to consensus-visible correctness risks in contract creation and uncle validation.
