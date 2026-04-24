---
case_id: case_20240430_bd8fe6260
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2024-04-30
source_refs:
  - git:bd8fe626046e09a43fa9ce29d01dff749329e0ea
  - "core/vm/instructions_test.go:1102"
  - "core/blockchain_test.go:5140"
  - "core/blockchain_test.go:5125"
  - "core/vm/eips.go:418"
bug_class: operand-decoding-error
impact_type:
  - incorrect-authorized-call-execution
confidence: medium
tags:
  - authorization
  - evm
  - authcall
  - operand-decoding
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The only runtime change shown is in `core/vm/eips.go`, where `opAuthCall` stops popping one extra stack item while decoding AUTHCALL operands. That supports a real opcode-decoding bug in an authorization-related path, but the provided evidence does not establish an exploitable security vulnerability.

## Observed Patch Facts

1. In `core/vm/instructions_test.go`, the patch replaces `require.Equal(t, tt.expectedError, err, "unexpected error executing AUTH")` with `require.Equal(t, tt.expectedError, err, tt.name, "unexpected error executing AUTH")`.

2. In `core/blockchain_test.go`, the patch replaces `// copy sig to memory` with `// for 'auth', signature needs to be in memory (which will be passed via calldata)`.

3. In `core/blockchain_test.go`, the patch replaces `// The address 0xBBBB calls 0xAAAA` with `byte(vm.CALLER), // pushes the caller to stack [caller]`.

4. In `core/vm/eips.go`, the patch replaces `stack = scope.Stack` with `stack = scope.Stack`.

## Project Context

The changed code sits primarily in `core/vm`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/vm/jump_table.go`, `core/vm/interpreter.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/jump_table.go`, `core/vm/interpreter.go`. The strongest project-level identifiers around this patch are `stack`, `byte`, `scope`, and `require`. Nearby tests or test-like files include `core/state/statedb_fuzz_test.go`.

## Before/After Behavior

Before the patch, `opAuthCall` popped `temp` and then seven more stack values, including one discarded extra operand, before deriving `toAddr` and calldata offsets. After the patch, it pops only the six operands it actually uses after `temp`, so AUTHCALL operand decoding matches the implementation's expected inputs more closely. The other changes are test assertions and comments, not additional runtime fixes.

# Root Cause

`opAuthCall` consumed one more stack item than the subsequent logic used, so later operands could be shifted relative to the intended AUTHCALL layout.

## Walkthrough

1. `core/vm/eips.go` shows the substantive code change: the AUTHCALL implementation removed one discarded `stack.pop()` from its local operand binding.

2. The same function immediately uses the decoded values to build `toAddr` and read call arguments from memory, so the pop count directly affects AUTHCALL parameter interpretation.

3. `core/vm/instructions_test.go` only strengthens AUTH test assertions by including case names and checking `scope.Authorized`; it does not add new runtime logic.

4. `core/blockchain_test.go` changes are explanatory comments around EIP-3074 test setup, plus clearer inline comments for `CALLER` storage behavior.

5. Taken together, the evidence supports a correctness fix in AUTHCALL stack decoding, but not a demonstrated signature bypass, privilege escalation, theft, code execution, or consensus failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/vm/eips.go | 415 | AUTHCALL opcode implementation; decodes stack operands and executes the authorized delegated call |
| core/blockchain_test.go | 5105 | integration test for EIP-3074 AUTH/AUTHCALL flow, including downstream `CALLER` behavior under the invoker contract |
| core/vm/instructions_test.go | 1070 | unit test coverage for AUTH success and failure cases that establish the `Authorized` state consumed by AUTHCALL |

## Code Snippets

## Snippet 1

Context: `core/vm/instructions_test.go:1102` (changes an authorization or privilege gate)

Before
```go
// Call AUTH
		res, err := opAuth(&pc, evm.interpreter, scope)
		require.Equal(t, tt.expectedError, err, "unexpected error executing AUTH")
		require.Equal(t, tt.expectedResult, len(res), "unexpected return value")

		// Check the stack for response and scope for authorized
		actual := stack.pop()
		require.Equal(t, tt.expectedStack, actual.Uint64(), "unexpected value in stack")
```
After
```go
// Call AUTH
		res, err := opAuth(&pc, evm.interpreter, scope)
		require.Equal(t, tt.expectedError, err, tt.name, "unexpected error executing AUTH")
		require.Equal(t, tt.expectedResult, len(res), tt.name, "unexpected return value")

		// Check the stack for response and scope for authorized
		actual := stack.pop()
		require.Equal(t, tt.expectedStack, actual.Uint64(), tt.name, "unexpected value in stack")
```

## Snippet 2

Context: `core/blockchain_test.go:5140` (changes an authorization or privilege gate)

Before
```go
invoker := []byte{
		// copy sig to memory
		byte(vm.CALLDATASIZE),
		byte(vm.PUSH0),
		byte(vm.PUSH0),
		byte(vm.CALLDATACOPY),
```
After
```go
invoker := []byte{
		// for `auth`, signature needs to be in memory (which will be passed via calldata)
		// copy the signature from calldata to memory
		byte(vm.CALLDATASIZE), // pushes calldata size to stack [len(calldata)] (size)
		byte(vm.PUSH0),        // pushes 0 to stack [len(calldata), 0] (offset)
		byte(vm.PUSH0),        // pushes 0 to stack [len(calldata), 0, 0] (destOffset)
		byte(vm.CALLDATACOPY), // copy calldata to memory (based on destOffset, offset, size above)
```

## Snippet 3

Context: `core/blockchain_test.go:5125` (changes a sensitive control or state-update path)

Before
```go
Balance: big.NewInt(0),
				},
				// The address 0xBBBB calls 0xAAAA
				bb: {
					Code: []byte{
						byte(vm.CALLER),
						byte(vm.PUSH0),
						byte(vm.SSTORE),
```
After
```go
Balance: big.NewInt(0),
				},
				bb: {
					Code: []byte{
						byte(vm.CALLER), // pushes the caller to stack [caller]
						byte(vm.PUSH0),  // pushes 0 to stack [caller, 0]
						byte(vm.SSTORE), // stores caller in slot 0 (to verify caller later)
						byte(vm.STOP),
```

## Snippet 4

Context: `core/vm/eips.go:418` (changes a sensitive control or state-update path)

Before
```go
}
	var (
		stack                                                = scope.Stack
		temp                                                 = stack.pop()
		gas                                                  = interpreter.evm.callGasTemp
		addr, value, _, inOffset, inSize, retOffset, retSize = stack.pop(), stack.pop(), stack.pop(), stack.pop(), stack.pop(), stack.pop(), stack.pop()
		toAddr                                               = common.Address(addr.Bytes20())
		args                                                 = scope.Memory.GetPtr(int64(inOffset.Uint64()), int64(inSize.Uint64()))
```
After
```go
}
	var (
		stack                                             = scope.Stack
		temp                                              = stack.pop()
		gas                                               = interpreter.evm.callGasTemp
		addr, value, inOffset, inSize, retOffset, retSize = stack.pop(), stack.pop(), stack.pop(), stack.pop(), stack.pop(), stack.pop()
		toAddr                                            = common.Address(addr.Bytes20())
		args                                              = scope.Memory.GetPtr(int64(inOffset.Uint64()), int64(inSize.Uint64()))
```

# Fix Pattern

Remove stray operand consumption in opcode stack decoding and tighten tests around the affected authorization flow.

## How It Was Fixed

The patch deleted the extra unused `stack.pop()` from `opAuthCall` so the function now decodes only the operands it actually uses. Test updates add better assertions and comments around AUTH/AUTHCALL behavior, but they are supporting evidence rather than the core fix.

# Why It Matters

1. Incorrect operand decoding can make AUTHCALL execute with unintended parameters.

2. The bug sits in an authorization-related opcode path, so semantic correctness matters.

3. This diff alone does not prove a concrete security exploit or impact.

# Evidence Notes

Evidence for the bug is strong in `core/vm/eips.go`: the function changed from popping seven post-`temp` values to six. The remaining file changes are test-side support only. The draft's stronger security framing is not established by the supplied diff, and there is no direct evidence here of AUTH signature-verification failure, exploitability, or system-wide security impact. Protocol security invariant: AUTHCALL must consume exactly its intended stack operands so an already-authorized call uses the caller-specified target, value, input offsets, and return offsets predictably. Verification notes: The patch does not show a signature-verification bypass in AUTH itself. The diff does not prove fund theft, arbitrary code execution, or a practical privilege-escalation exploit. Most non-`eips.go` changes are test clarifications and assertions, not runtime security logic. The patch alone does not establish whether this caused consensus divergence or only incorrect local opcode behavior. Runtime evidence is limited to the operand-decoding change in `core/vm/eips.go`. Test changes mostly improve diagnostics and explanation rather than demonstrating exploitability. No provided evidence shows signature bypass, fund theft, arbitrary code execution, or consensus divergence. Treat this as a plausible security-relevant correctness fix, but not a confirmed vulnerability fix from the shown material alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `operand-decoding-error`
Final impact type: `incorrect-authorized-call-execution`
Final confidence: `medium`
Final tags: `authorization, evm, authcall, operand-decoding`

The patch evidence shows a real runtime fix in `opAuthCall`: it removes an extra stack pop while decoding AUTHCALL operands in an authorization-sensitive EVM path. That is stronger than ordinary maintenance because the function only runs after authorization state is established and the decoded operands directly control the delegated call target and calldata/return regions. The diff does not prove an exploitable vulnerability, signature bypass, or concrete loss scenario, so this is best treated as security hardening rather than a confirmed security fix.

## Security Evidence

1. `core/vm/eips.go` is the substantive runtime change; AUTHCALL now consumes one fewer stack item.
2. `opAuthCall` explicitly depends on `scope.Authorized`, tying the bug to an authorization-sensitive execution path.
3. The removed extra pop changes how target address, value, input offsets, and return offsets are interpreted for the authorized call.
4. Tests around AUTH/AUTHCALL cover invalid signature, invalid authority, and expected authorized state, showing the affected behavior is security-relevant rather than incidental.

## Missing Evidence

1. No proof of a practical exploit, privilege escalation, fund loss, or consensus impact is provided.
2. No spec excerpt or advisory is included to show the exact security invariant violated.
3. Most other diff hunks are comments or test-diagnostic improvements, not additional runtime enforcement.

## Claim Boundaries

1. Do not claim a confirmed auth bypass or signature-verification flaw from this patch alone.
2. Do not claim theft, remote code execution, or consensus failure; the evidence does not establish those impacts.
3. The supported claim is limited to correcting operand decoding in an authorization-sensitive opcode, which plausibly hardens security-sensitive behavior.
