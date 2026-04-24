---
case_id: case_20190312_7504dbd6e
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2019-03-12
source_refs:
  - git:7504dbd6eb3f62371f86b06b03ffd665690951f2
  - "core/vm/interpreter.go:119"
  - "core/vm/stack_table.go:18"
  - "core/vm/interpreter.go:202"
  - "core/vm/interpreter.go:240"
bug_class: resource-accounting-overflow
impact_type:
  - resource-accounting-integrity
confidence: medium
tags:
  - security-hardening
  - evm
  - gas-accounting
  - memory-accounting
  - integer-overflow
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch clearly hardens EVM memory/gas arithmetic by moving sizing and gas-related interfaces onto `uint64` and adding explicit overflow handling, but the provided evidence does not establish a concrete vulnerability or exploit path in the pre-patch code. The stack-validation and other refactors in the same commit further weaken a strong security-fix claim.

## Observed Patch Facts

1. In `core/vm/interpreter.go`, the patch replaces `func (in *EVMInterpreter) enforceRestrictions(op OpCode, operation operation, stack *...` with `// Run loops and evaluates the contract's code with the given input data and returns`.

2. In `core/vm/stack_table.go`, the patch replaces `func makeStackFunc(pop, push int) stackValidationFunc {` with `func minSwapStack(n int) int {`.

3. In `core/vm/interpreter.go`, the patch replaces `if err = operation.validateStack(stack); err != nil {` with `// Validate stack`.

4. In `core/vm/interpreter.go`, the patch replaces `cost, err = operation.gasCost(in.gasTable, in.evm, contract, stack, mem, memorySize)` with `// Dynamic portion of gas`.

## Project Context

The changed code sits primarily in `core/vm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/vm/contracts.go`, `core/vm/stack.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/logger.go`, `core/vm/gas_table.go`. The strongest project-level identifiers around this patch are `operation`, `stack`, `cost`, and `sLen`. Nearby tests or test-like files include `core/vm/runtime/fuzz.go`.

## Before/After Behavior

Before, the run loop used a single `operation.gasCost(...)` path in the shown hunk, and the provided evidence does not show the same explicit overflow-checked memory-sizing boundary. After, the interpreter computes memory size with checked arithmetic, returns `errGasUintOverflow` on overflow, and applies dynamic gas charging through a separated path. That supports arithmetic hardening, not a proven exploitable bug fix.

# Root Cause

Arithmetic around memory sizing and gas charging was refactored to an explicit checked `uint64` path, suggesting prior correctness risk at that boundary; however, the supplied hunks do not prove that the earlier code was actually vulnerable in a security sense.

## Walkthrough

1. The commit message centers on 64-bit memory and gas calculations and a memory-calculation fix, but it also includes optimizations and refactors.

2. In `core/vm/interpreter.go`, the shown run-loop change separates dynamic gas charging from the older single gas-cost call.

3. The provided context also shows checked memory-size multiplication with overflow returning `errGasUintOverflow`.

4. `core/vm/gas_table.go` and `core/vm/jump_table.go` context point to `uint64`-based memory/gas interfaces, consistent with arithmetic hardening.

5. Other visible changes, including stack-validation inlining and error-message cleanup, look ancillary and do not strengthen a vulnerability claim.

6. Because the pre-patch failure mode is not demonstrated end-to-end, the strongest supported conclusion is unclear security relevance rather than a confirmed or likely vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/vm/interpreter.go | 234 | computes memory expansion size, checks overflow, and applies dynamic gas charging before execution continues |
| core/vm/gas_table.go | 19 | memory expansion gas-cost routine moved to overflow-safe `uint64` accounting |
| core/vm/jump_table.go | 20 | defines gas and memory-size function contracts using `uint64`, establishing the safer accounting boundary |
| core/vm/interpreter.go | 196 | opcode pre-execution validation path; stack checks were inlined here but appear ancillary to the memory/gas fix |

## Code Snippets

## Snippet 1

Context: `core/vm/interpreter.go:119` (changes a sensitive control or state-update path)

Before
```go
}

func (in *EVMInterpreter) enforceRestrictions(op OpCode, operation operation, stack *Stack) error {
	if in.evm.chainRules.IsByzantium {
		if in.readOnly {
			// If the interpreter is operating in readonly mode, make sure no
			// state-modifying operation is performed. The 3rd stack item
			// for a call operation is the value. Transferring value from one
```
After
```go
}

// Run loops and evaluates the contract's code with the given input data and returns
// the return byte-slice and an error if one occurred.
```

## Snippet 2

Context: `core/vm/stack_table.go:18` (changes bounds, limits, or capacity handling)

Before
```go
import (
	"fmt"

	"github.com/ethereum/go-ethereum/params"
)

func makeStackFunc(pop, push int) stackValidationFunc {
```
After
```go
import (
	"github.com/ethereum/go-ethereum/params"
)

func minSwapStack(n int) int {
	return minStack(n, n)
}
```

## Snippet 3

Context: `core/vm/interpreter.go:202` (changes bounds, limits, or capacity handling)

Before
```go
return nil, fmt.Errorf("invalid opcode 0x%x", int(op))
		}
		if err = operation.validateStack(stack); err != nil {
			return nil, err
		}
		// If the operation is valid, enforce and write restrictions
		if err = in.enforceRestrictions(op, operation, stack); err != nil {
			return nil, err
```
After
```go
return nil, fmt.Errorf("invalid opcode 0x%x", int(op))
		}
		// Validate stack
		if sLen := stack.len(); sLen < operation.minStack {
			return nil, fmt.Errorf("stack underflow (%d <=> %d)", sLen, operation.minStack)
		} else if sLen > operation.maxStack {
			return nil, fmt.Errorf("stack limit reached %d (%d)", sLen, operation.maxStack)
		}
```

## Snippet 4

Context: `core/vm/interpreter.go:240` (changes a sensitive control or state-update path)

Before
```go
}
		}
		// consume the gas and return an error if not enough gas is available.
		// cost is explicitly set so that the capture state defer method can get the proper cost
		cost, err = operation.gasCost(in.gasTable, in.evm, contract, stack, mem, memorySize)
		if err != nil || !contract.UseGas(cost) {
			return nil, ErrOutOfGas
		}
```
After
```go
}
		}
		// Dynamic portion of gas
		// consume the gas and return an error if not enough gas is available.
		// cost is explicitly set so that the capture state defer method can get the proper cost
		if operation.dynamicGas != nil {
			cost, err = operation.dynamicGas(in.gasTable, in.evm, contract, stack, mem, memorySize)
			if err != nil || !contract.UseGas(cost) {
```

# Fix Pattern

Introduce fixed-width checked arithmetic for resource accounting and fail closed on overflow.

## How It Was Fixed

The patch makes memory-size and gas-related calculations use `uint64`-based interfaces, adds explicit overflow detection for memory sizing, and separates dynamic gas charging so execution stops on overflow or failed gas charging rather than proceeding on unchecked arithmetic.

# Why It Matters

1. Memory and gas accounting are protocol-critical execution paths.

2. Checked arithmetic reduces the chance of incorrect sizing or gas behavior.

3. The evidence supports correctness hardening even if exploitability is not shown.

# Evidence Notes

Grounded evidence supports arithmetic hardening in `core/vm/interpreter.go`, with supporting context in `core/vm/gas_table.go` and `core/vm/jump_table.go`. The record does not show a concrete pre-patch undercharge, consensus failure, or attacker-controlled exploit sequence. Commit bundling also includes non-security refactors and optimizations. Protocol security invariant: EVM memory sizing and gas accounting should use bounded arithmetic and reject overflow before charging gas or continuing execution. Verification notes: The patch does not by itself prove a practical exploit or theft scenario. The evidence does not conclusively show a consensus split occurred in production. The stack-validation refactor and generic error-message changes are not independently shown to be security fixes. The exact pre-patch failure mode is not fully reconstructed from the provided hunks alone; undercharging or incorrect OOG handling is plausible but not demonstrated end-to-end. No end-to-end vulnerable pre-patch scenario is shown in the provided material. No proof of practical exploit, consensus impact, or undercharge is included. Best-supported classification from the supplied evidence is unclear security relevance, not a confirmed security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-accounting-overflow`
Final impact type: `resource-accounting-integrity`
Final confidence: `medium`
Final tags: `security-hardening, evm, gas-accounting, memory-accounting, integer-overflow`

The supplied patch evidence supports keeping this as a security-hardening case, not a confirmed security fix. The strongest grounded change is the move to checked `uint64` memory/gas accounting with explicit overflow handling (`errGasUintOverflow`) in a protocol-critical EVM execution path. That clearly tightens security-sensitive behavior and removes a risky arithmetic condition, but the provided material does not prove a concrete exploitable pre-patch bug such as an actual undercharge, consensus split, or attacker-triggered bypass.

## Security Evidence

1. Project context shows explicit overflow checks in `core/vm/interpreter.go`, including `math.SafeMul(...)` and returns of `errGasUintOverflow`.
2. `core/vm/gas_table.go` changes memory gas accounting to `uint64`, indicating bounded arithmetic in resource accounting.
3. `core/vm/jump_table.go` introduces `memorySizeFunc` returning `(size uint64, overflow bool)` and defines `errGasUintOverflow`, which is a fail-closed hardening pattern.
4. The affected code is in `core/vm`, a security-sensitive execution path where gas and memory accounting errors can matter materially.
5. The commit subject and body explicitly mention `64 bit memory and gas calculations` and `fix error in memory calculation`, consistent with arithmetic hardening.

## Missing Evidence

1. No end-to-end proof that the old arithmetic caused exploitable gas undercharge, OOG misbehavior, or consensus divergence.
2. No reproducer, regression test, or bug report is provided showing attacker-controlled pre-patch failure.
3. The provided diff hunks mix refactors and optimizations with the arithmetic changes, so not every touched path is security-relevant.
4. The evidence does not show concrete impact beyond removal of a risky overflow condition.

## Claim Boundaries

1. This should be retained only as `security-hardening`, not as a confirmed exploitable vulnerability fix.
2. The supported claim is limited to overflow-safe gas/memory accounting hardening in the EVM interpreter and related tables.
3. Stack-validation inlining, generic error-message cleanup, and other refactors should not be treated as independent security fixes from this evidence.
4. Do not claim theft, consensus failure, gas-undercharge exploitation, or real-world incident from the supplied patch alone.
