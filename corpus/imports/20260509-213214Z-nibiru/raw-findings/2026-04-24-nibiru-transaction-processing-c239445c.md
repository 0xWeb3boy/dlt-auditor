---
case_id: case_20260424_c239445c
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2026-04-24
source_refs:
  - git:c239445ca45c21453a9d88e96b95f9690fae8780
  - "x/evm/precompile/funtoken_test.go:878"
  - "x/evm/precompile/errors.go:82"
  - "x/evm/precompile/funtoken.go:599"
  - "x/evm/precompile/wasm.go:208"
bug_class: missing-vm-callback-guard
impact_type:
  - state-integrity
confidence: medium
tags:
  - evm
  - precompile
  - callback-guard
  - state-integrity
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded security-relevant change is the addition of a VM-sender callback guard in the EVM precompile subsystem. A new `assertNotVMCaller` helper rejects execution when `evm.IsVMSenderCtx(ctx)` is true, and the guard is applied to the mutable FunToken `sendToEvm` and Wasm `execute` paths. A separate change improves revert returndata propagation, but that is error-handling behavior rather than the main security fix.

## Observed Patch Facts

1. In `x/evm/precompile/funtoken_test.go`, the patch replaces `s.Require().Empty(resp.Ret, "Return data should be empty")` with `s.Require().NotEmpty(resp.Ret, "Return data should include revert reason")`.

2. In `x/evm/precompile/errors.go`, the patch replaces `// assertNumArgs checks if the number of provided arguments matches the expected` with `func assertNotVMCaller(`.

3. In `x/evm/precompile/funtoken.go`, the patch adds `if err := assertNotVMCaller(startResult.Ctx, startResult.Method); err != nil {`.

4. In `x/evm/precompile/wasm.go`, the patch adds `if err := assertNotVMCaller(start.Ctx, start.Method); err != nil {`.

## Project Context

The changed code sits primarily in `x/evm/precompile`, `x/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/precompile/wasm_test.go`, `x/evm/precompile/oracle_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/precompile/wasm_test.go`, `x/evm/precompile/oracle_test.go`. The strongest project-level identifiers around this patch are `Require`, `resp`, `should`, and `assertNotVMCaller`. Nearby tests or test-like files include `x/evm/precompile/test/wasteful_gas.wasm`, `x/evm/precompile/test/staking.wasm`.

## Before/After Behavior

Before the patch, the shown FunToken `sendToEvm` and Wasm `execute` paths checked readonly status and then proceeded toward mutable processing without a visible VM-sender callback guard. After the patch, both paths call `assertNotVMCaller` before parsing or processing their method arguments. Separately, a FunToken failure test changed from expecting empty returndata to expecting ABI-compatible revert data containing the missing mapping error.

# Root Cause

The mutable precompile entrypoints shown in the evidence lacked an explicit check blocking execution from an EVM-originated callback or VM-sender context. That left FunToken transfer and Wasm execution paths reachable in a context the patch now treats as disallowed.

## Walkthrough

1. A call reaches a native EVM precompile method.

2. For FunToken `sendToEvm`, the previous visible flow performed the readonly check and then continued toward argument parsing and transfer handling.

3. For Wasm `execute`, the previous visible flow performed the readonly check and then continued toward Wasm execution argument parsing.

4. The patch adds `assertNotVMCaller(ctx, method)`, which checks `evm.IsVMSenderCtx(ctx)`.

5. If the VM-sender context flag is present, the helper returns an error saying the method is disabled during an EVM-originated contract callback.

6. The FunToken and Wasm mutable paths now invoke this guard before their downstream mutable processing.

7. The patch also updates failure behavior so at least one FunToken precompile error returns decodable revert reason bytes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/precompile/errors.go | 82 | defines VM-sender guard that rejects methods during EVM-originated contract callbacks |
| x/evm/precompile/funtoken.go | 599 | applies VM-sender guard before mutable FunToken sendToEvm processing |
| x/evm/precompile/wasm.go | 208 | applies VM-sender guard before mutable Wasm execute processing |
| x/evm/precompile/funtoken_test.go | 878 | updates failure behavior expectation to return ABI revert reason data |

## Code Snippets

## Snippet 1

Context: `x/evm/precompile/funtoken_test.go:878` (changes the branch that decides whether execution stops or continues)

Before
```go
s.Require().Error(err, "CallContractWithInput failed for non-existent mapping")
		s.Require().NotEmpty(resp.VmError, "VMError should be not be empty")
		s.Require().Empty(resp.Ret, "Return data should be empty")
	})
```
After
```go
s.Require().Error(err, "CallContractWithInput failed for non-existent mapping")
		s.Require().NotEmpty(resp.VmError, "VMError should be not be empty")
		s.Require().NotEmpty(resp.Ret, "Return data should include revert reason")
		revertErr := evm.NewRevertError(resp.Ret)
		s.Require().Contains(revertErr.Error(), "no FunToken mapping found for bank denom")
	})
```

## Snippet 2

Context: `x/evm/precompile/errors.go:82` (changes the branch that decides whether execution stops or continues)

Before
```go
}

// assertNumArgs checks if the number of provided arguments matches the expected
// count. If lenArgs does not equal wantArgsLen, it returns an error describing
```
After
```go
}

func assertNotVMCaller(
	ctx sdk.Context,
	method *gethabi.Method,
) error {
	if evm.IsVMSenderCtx(ctx) {
		return fmt.Errorf("method %s is disabled during EVM-originated contract callback",
```

## Snippet 3

Context: `x/evm/precompile/funtoken.go:599` (changes the branch that decides whether execution stops or continues)

Before
```go
return nil, err
	}
	// parse call: (string bankDenom, uint256 amount, string to)
	bankDenom, amount, toStr, err := parseArgsSendToEvm(args)
```
After
```go
return nil, err
	}
	if err := assertNotVMCaller(startResult.Ctx, startResult.Method); err != nil {
		return nil, err
	}
	// parse call: (string bankDenom, uint256 amount, string to)
	bankDenom, amount, toStr, err := parseArgsSendToEvm(args)
```

## Snippet 4

Context: `x/evm/precompile/wasm.go:208` (changes the branch that decides whether execution stops or continues)

Before
```go
return nil, err
	}

	wasmContract, msgArgsBz, funds, err := p.parseArgsWasmExecute(args)
```
After
```go
return nil, err
	}
	if err := assertNotVMCaller(start.Ctx, start.Method); err != nil {
		return nil, err
	}

	wasmContract, msgArgsBz, funds, err := p.parseArgsWasmExecute(args)
```

# Fix Pattern

Introduce a centralized execution-context guard and apply it at the start of mutable precompile methods, before argument parsing or native module work begins. Keep revert error propagation explicit for failed precompile calls.

## How It Was Fixed

The patch defines `assertNotVMCaller` in `x/evm/precompile/errors.go`. It rejects calls when `evm.IsVMSenderCtx(ctx)` is true. The helper is then called in `x/evm/precompile/funtoken.go` inside `sendToEvm` and in `x/evm/precompile/wasm.go` inside `execute`, immediately after readonly checks. The FunToken test expectation was also updated to require revert returndata for a failed missing-mapping call.

# Why It Matters

1. Blocks VM-originated callback contexts from reaching mutable native precompile logic.

2. Applies to the shown FunToken transfer and Wasm execution paths.

3. Reduces callback-context reachability into native state-changing code.

4. The supplied evidence supports a likely guard-bypass fix, but not a complete exploit or loss scenario.

# Evidence Notes

Primary evidence is the new `assertNotVMCaller` helper in `x/evm/precompile/errors.go:82`, its use in `x/evm/precompile/funtoken.go:599`, and its use in `x/evm/precompile/wasm.go:208`. The FunToken test at `x/evm/precompile/funtoken_test.go:878` supports a separate revert returndata behavior change. The commit subject mentions a delegate-call security patch, but the supplied code snippets do not demonstrate delegatecall mechanics or a concrete exploit path. Event truncation, upgrades, dependency changes, and broader migration work are not used as evidence for this finding. Protocol security invariant: Mutable native EVM precompile methods should not execute while the SDK context indicates an EVM-originated contract callback or VM-sender context. The patch enforces this by rejecting such calls before FunToken transfer or Wasm execution processing continues. Verification notes: The patch does not by itself prove a complete exploit path or fund theft scenario. The evidence does not show that query-only precompile methods were unsafe. The revert returndata change is error propagation behavior, not the primary security invariant. The event truncation and upgrade/dependency changes are not classified here as security fixes from the provided hunks. The exact delegatecall mechanics are inferred from commit context, not demonstrated in the shown code snippets. Verified only from the provided snippets and draft context. Exploitability, asset impact, and delegatecall mechanics are not established by the supplied evidence. The revert returndata change should be treated as supporting error-handling behavior, not the root security issue. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-vm-callback-guard`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `evm, precompile, callback-guard, state-integrity, security-hardening`

The supplied patch evidence supports retaining this as security-relevant, but more conservatively as security hardening rather than a proven security fix. The code adds a VM-sender/context guard that rejects EVM-originated contract callbacks before mutable FunToken and Wasm precompile operations proceed. That clearly tightens access to state-changing native paths, but the snippets do not prove a concrete exploit, delegatecall path, or realized state corruption impact.

## Security Evidence

1. New assertNotVMCaller helper rejects execution when evm.IsVMSenderCtx(ctx) is true.
2. Guard error explicitly says the method is disabled during an EVM-originated contract callback.
3. Mutable FunToken sendToEvm path now checks assertNotVMCaller before argument parsing and transfer processing.
4. Mutable Wasm execute path now checks assertNotVMCaller before parsing and execution processing.
5. Commit metadata explicitly describes a security patch and VM-sender guard checks for mutable methods.

## Missing Evidence

1. No concrete exploit path is shown in the supplied snippets.
2. Delegatecall mechanics are mentioned by the commit subject but not demonstrated in the provided code evidence.
3. No test demonstrates that the prior behavior enabled unauthorized state mutation, fund movement, or state corruption.
4. The revert returndata change appears to be error propagation behavior, not security impact by itself.

## Claim Boundaries

1. Validate only the VM-sender callback guard as security-relevant hardening.
2. Do not claim proven state corruption or asset loss from the supplied evidence.
3. Do not treat the revert reason propagation hunk as the primary security fix.
4. Do not generalize the guard beyond the shown FunToken sendToEvm and Wasm execute paths.
