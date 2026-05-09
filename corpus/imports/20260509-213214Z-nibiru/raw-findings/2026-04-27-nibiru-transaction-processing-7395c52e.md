---
case_id: case_20260427_7395c52e
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2026-04-27
source_refs:
  - git:7395c52e408a8f2dfd27c4a5f553c4fc3c0deb20
  - "x/evm/precompile/funtoken_test.go:878"
  - "x/evm/precompile/errors.go:82"
  - "x/evm/precompile/funtoken.go:599"
  - "x/evm/precompile/wasm.go:208"
bug_class: callback-context-access-control
tags:
  - evm
  - precompile
  - access-control
  - callback-guard
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant access-control gap in Nibiru EVM precompiles by adding a VM-sender context guard to mutable FunToken and Wasm precompile methods. The evidence supports a callback-context restriction on `sendToEvm` and `execute`, but does not prove a complete delegate-call exploit, fund loss, consensus failure, or persistent state corruption.

## Observed Patch Facts

1. In `x/evm/precompile/funtoken_test.go`, the patch replaces `s.Require().Empty(resp.Ret, "Return data should be empty")` with `s.Require().NotEmpty(resp.Ret, "Return data should include revert reason")`.

2. In `x/evm/precompile/errors.go`, the patch replaces `// assertNumArgs checks if the number of provided arguments matches the expected` with `func assertNotVMCaller(`.

3. In `x/evm/precompile/funtoken.go`, the patch adds `if err := assertNotVMCaller(startResult.Ctx, startResult.Method); err != nil {`.

4. In `x/evm/precompile/wasm.go`, the patch adds `if err := assertNotVMCaller(start.Ctx, start.Method); err != nil {`.

## Project Context

The changed code sits primarily in `x/evm/precompile`, `x/evm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/precompile/wasm_test.go`, `x/evm/precompile/oracle_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/precompile/wasm_test.go`, `x/evm/precompile/oracle_test.go`. The strongest project-level identifiers around this patch are `Require`, `resp`, `should`, and `assertNotVMCaller`. Nearby tests or test-like files include `x/evm/precompile/test/wasteful_gas.wasm`, `x/evm/precompile/test/staking.wasm`.

## Before/After Behavior

Before the patch, the provided snippets show `precompileFunToken.sendToEvm` and `precompileWasm.execute` checking readonly status and then proceeding toward argument parsing and mutable execution without a visible VM-originated callback guard. After the patch, both methods call `assertNotVMCaller` before argument parsing. The patch also changes a FunToken test so failed precompile calls return ABI revert data with an error reason instead of empty return data.

# Root Cause

The visible root cause was a missing guard on selected mutable precompile entrypoints for contexts marked as VM-originated sender/callback execution. The provided evidence does not establish the broader exploit mechanics beyond that missing callback-context rejection.

## Walkthrough

1. A call enters a Nibiru EVM precompile method with SDK context and ABI method metadata.

2. The old visible FunToken `sendToEvm` path rejected readonly use, then proceeded to parse transfer arguments.

3. The old visible Wasm `execute` path rejected readonly use, then proceeded to parse Wasm execution arguments.

4. The patch adds `assertNotVMCaller`, which checks `evm.IsVMSenderCtx(ctx)` and returns an error if the call occurs during an EVM-originated contract callback.

5. `sendToEvm` and `execute` now invoke this helper immediately after the readonly guard.

6. When the VM-sender context flag is present, these mutable methods now fail before argument parsing and downstream module execution.

7. The revert-return-data test change is related failure-handling behavior, not the primary access-control evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/precompile/errors.go | 82 | Defines assertNotVMCaller, rejecting calls when evm.IsVMSenderCtx(ctx) indicates EVM-originated callback context. |
| x/evm/precompile/funtoken.go | 599 | Applies the VM-caller guard before mutable FunToken sendToEvm argument parsing and execution. |
| x/evm/precompile/wasm.go | 208 | Applies the VM-caller guard before mutable Wasm execute argument parsing and execution. |
| x/evm/precompile/funtoken_test.go | 878 | Regression coverage for precompile error propagation through revert returndata; related failure-handling evidence, not the primary access-control guard. |

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

Add an early shared context guard to sensitive mutable precompile methods and fail before argument parsing or state-changing execution when the call originates from VM callback context.

## How It Was Fixed

The patch introduced `assertNotVMCaller(ctx sdk.Context, method *gethabi.Method)` in `x/evm/precompile/errors.go`. It rejects calls when `evm.IsVMSenderCtx(ctx)` is true. The helper was inserted into `x/evm/precompile/funtoken.go` for `sendToEvm` and `x/evm/precompile/wasm.go` for `execute`, immediately after the existing readonly checks.

# Why It Matters

1. Protects mutable precompile paths that can affect module state.

2. Prevents VM-originated callback context from reaching FunToken send and Wasm execute logic.

3. Centralizes the callback-context check for reuse across affected precompiles.

4. Exploitability and concrete impact are not proven by the supplied snippets.

# Evidence Notes

Grounded evidence consists of the new `assertNotVMCaller` helper, its use in `precompileFunToken.sendToEvm`, and its use in `precompileWasm.execute`. The helper error text explicitly disables methods during EVM-originated contract callbacks. The commit subject mentions a security patch for delegate call, but the provided hunks do not show the complete delegate-call attack path or demonstrate successful pre-patch exploitation. Protocol security invariant: Mutable EVM precompile methods that bridge into module state should reject execution when the SDK context indicates an EVM-originated contract callback. Verification notes: The patch does not by itself prove successful exploitation before the fix. The evidence does not establish fund theft, consensus failure, or persistent state corruption. The revert-reason returndata change is failure-handling/API behavior unless tied to the VM-caller guard. The exact delegate-call attack path is not fully shown in the provided hunks. Other changed files in the commit may be migrations, tests, dependency updates, or cleanup and are not independently classified as security fixes here. Verified from supplied snippets only; no repository inspection was performed. Do not classify the revert-reason returndata change as the root vulnerability mechanism on its own. Downgraded from confirmed/high to likely/medium because the concrete exploit path and impact are not established in the provided evidence. Kept in security corpus because the patch adds an access-control guard to mutable EVM precompile paths and the commit explicitly frames the change as a security patch. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `callback-context-access-control`
Final tags: `evm, precompile, access-control, callback-guard, state-integrity`

The supplied evidence supports retaining this as a security-relevant hardening case: the patch adds an explicit VM-sender/callback-context guard to mutable FunToken and Wasm precompile methods, and the commit subject frames it as a security patch for delegate call. However, the provided hunks do not prove a concrete exploitable delegate-call path, fund loss, consensus failure, or actual state corruption, so classifying it as a full security-fix with state-corruption as the bug class is too strong from the evidence alone.

## Security Evidence

1. New assertNotVMCaller rejects execution when evm.IsVMSenderCtx(ctx) is true.
2. The guard error explicitly disables methods during EVM-originated contract callback context.
3. precompileFunToken.sendToEvm now checks assertNotVMCaller before parsing transfer arguments or executing mutable logic.
4. precompileWasm.execute now checks assertNotVMCaller before parsing Wasm execution arguments or executing mutable logic.
5. The commit subject says Security patch for delegate call, aligning with the added callback-context restriction.

## Missing Evidence

1. No supplied pre-patch exploit test showing delegatecall or callback abuse succeeds.
2. No demonstrated unauthorized transfer, fund loss, consensus failure, or persistent state corruption.
3. No full call-chain evidence explaining how VM-sender context becomes attacker-controlled or dangerous.
4. The revert-return-data change is failure-handling behavior and is not independently security evidence.

## Claim Boundaries

1. Keep the finding as security hardening around mutable EVM precompile callback restrictions.
2. Do not claim confirmed state corruption from the supplied snippets.
3. Do not claim concrete fund theft or consensus impact.
4. Do not treat revert reason propagation as the root vulnerability mechanism.
