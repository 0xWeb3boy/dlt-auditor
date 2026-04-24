---
case_id: case_20231013_f88557d061
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: storage
confidence: medium
source_quality: high
date: 2023-10-13
source_refs:
  - git:f88557d061d3184c68f99f9614bace3afed34d9c
  - "arbitrator/jit/src/user/mod.rs:49"
  - "arbos/programs/wasm.go:67"
  - "arbos/programs/wasm.go:111"
  - "arbitrator/jit/src/gostack.rs:244"
bug_class: gas-accounting
impact_type:
  - resource-metering
  - economic-undercharge
tags:
  - blockchain-core
  - wasm
  - stylus
  - gas-accounting
  - resource-control
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best characterized as likely security-relevant gas-accounting hardening for Stylus/Wasm activation. The evidence shows activation now receives mutable gas, returns updated remaining gas, and burns the consumed delta. The evidence does not establish a concrete exploit, consensus issue, state corruption, cryptographic bug, or quantified undercharge.

## Observed Patch Facts

1. In `arbitrator/jit/src/user/mod.rs`, the patch replaces `if out_hash_len != 32 {` with `let gas_left = &mut sp.read_u64_raw(gas);`.

2. In `arbos/programs/wasm.go`, the patch replaces `) (*wasmPricingInfo, common.Hash, error) {` with `) (common.Hash, u16, error) {`.

3. In `arbos/programs/wasm.go`, the patch replaces `func compileUserWasmRustWrapper(` with `func (vec *rustVec) intoSlice() []byte {`.

4. In `arbitrator/jit/src/gostack.rs`, the patch replaces `pub fn write_slice(&self, ptr: u64, src: &[u8]) {` with `pub fn write_slice<T: TryInto<u32>>(&self, ptr: T, src: &[u8]) {`.

## Project Context

The changed code sits primarily in `arbitrator/jit/src/user`, `arbitrator/jit/src`, `arbos/programs`, which anchors the finding in the `storage` area of the project. Historical context from `arbos/programs/wasm_api.go`, `arbos/programs/programs.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `arbos/programs/programs.go`, `arbos/programs/native.go`. The strongest project-level identifiers around this patch are `debug`, `common`, `Hash`, and `error`.

## Before/After Behavior

Before the patch, the shown Go activation path used a compile-style wrapper returning pricing/hash data, and the provided hunks do not show live caller gas being passed into Rust activation or a consumed-gas delta being burned. After the patch, activateProgram captures burner.GasLeft(), passes a gas pointer into activateWasmRustImpl, and burns the difference. The JIT bridge similarly reads gas from the Go stack, passes mutable gas into native::activate, writes remaining gas back, and sets gas to 0 on activation error.

# Root Cause

The supported root cause is incomplete gas propagation across the Go/Rust activation boundary. Stronger claims about state corruption, storage inconsistency, hash validation, or consensus divergence are not supported by the supplied evidence.

## Walkthrough

1. Activation enters the Go-side Stylus/Wasm activation path.

2. The patched Go code records the current burner gas before calling Rust activation.

3. The Rust activation interface now receives a pointer to mutable gas state.

4. After activation returns, Go burns the observed gas delta using the updated gas value.

5. The JIT activation bridge mirrors this by reading gas from Go memory, passing it into native activation, and writing back the remaining gas.

6. On JIT activation error, the bridge writes zero gas and clears the module hash output before returning the error.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| arbitrator/jit/src/user/mod.rs | 31 | JIT Go/Rust activation bridge reads gas from Go stack, passes mutable gas into native activation, writes remaining gas back, and zeroes gas on activation error. |
| arbos/programs/wasm.go | 61 | Go activation entrypoint captures burner gas, calls Rust activation with gas pointer, and burns the consumed delta after return. |
| arbos/programs/wasm.go | 85 | Wasm call path continues to pass contract gas into execution; contextual path showing activation and execution both rely on explicit gas pointers. |
| arbitrator/jit/src/gostack.rs | 244 | Interop helper for writing Rust output slices back to Go memory after activation interface changes. |

## Code Snippets

## Snippet 1

Context: `arbitrator/jit/src/user/mod.rs:49` (changes signature or replay validation logic)

Before
```rust
}

    if out_hash_len != 32 {
        error!(eyre::eyre!(
            "Go attempting to read module hash into bad buffer length: {out_hash_len}"
        ));
    }
```
After
```rust
}

    let gas_left = &mut sp.read_u64_raw(gas);
    let (_, module, pages) = match native::activate(&wasm, version, page_limit, debug, gas_left) {
        Ok(result) => result,
        Err(error) => error!(error),
    };
    sp.write_u64_raw(gas, *gas_left);
```

## Snippet 2

Context: `arbos/programs/wasm.go:67` (changes signature or replay validation logic)

Before
```go
debug bool,
	burner burn.Burner,
) (*wasmPricingInfo, common.Hash, error) {
	module, info, hash, err := compileUserWasmRustWrapper(db, program, wasm, pageLimit, version, debug)
	defer rustModuleDropImpl(module)
	if err != nil {
		return nil, common.Hash{}, err
	}
```
After
```go
debug bool,
	burner burn.Burner,
) (common.Hash, u16, error) {
	debugMode := arbmath.BoolToUint32(debug)
	moduleHash := common.Hash{}
	gas := burner.GasLeft()

	footprint, err := activateWasmRustImpl(wasm, pageLimit, version, debugMode, &moduleHash, &gas)
```

## Snippet 3

Context: `arbos/programs/wasm.go:111` (changes signature or replay validation logic)

Before
```go
}

func compileUserWasmRustWrapper(
	db vm.StateDB, program addr, wasm []byte, pageLimit, version u16, debug bool,
) (*rustMachine, wasmPricingInfo, common.Hash, error) {
	debugMode := arbmath.BoolToUint32(debug)
	outHash := common.Hash{}
	machine, info, err := compileUserWasmRustImpl(wasm, pageLimit, version, debugMode, outHash[:])
```
After
```go
}

func (vec *rustVec) intoSlice() []byte {
	len := readRustVecLenImpl(vec)
```

## Snippet 4

Context: `arbitrator/jit/src/gostack.rs:244` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    pub fn write_slice(&self, ptr: u64, src: &[u8]) {
        u32::try_from(ptr).expect("Go pointer not a u32");
        self.view().write(ptr, src).unwrap();
    }
```
After
```rust
}

    pub fn write_slice<T: TryInto<u32>>(&self, ptr: T, src: &[u8]) {
        let ptr: u32 = ptr.try_into().map_err(|_| "Go pointer not a u32").unwrap();
        self.view().write(ptr.into(), src).unwrap();
    }
```

# Fix Pattern

Thread live gas through the activation boundary, let lower-level activation update remaining gas, and charge the caller for the consumed delta.

## How It Was Fixed

The patch replaces the prior compile-wrapper activation shape with activateWasmRustImpl/native::activate calls that accept mutable gas. Go burns the difference between the original burner gas and the returned remaining gas. The JIT bridge writes updated gas back to Go memory, and gostack.rs adjusts write_slice to support the changed interop types.

# Why It Matters

1. Activation is a resource-control path for Stylus/Wasm programs.

2. Missing or incomplete gas charging can create economic undercharging or resource-metering gaps.

3. Both native and JIT activation paths are changed consistently.

4. The evidence supports gas-accounting hardening, not a proven exploit.

# Evidence Notes

Primary support comes from arbitrator/jit/src/user/mod.rs showing gas read/write around native::activate, arbos/programs/wasm.go showing activateWasmRustImpl called with &gas followed by burner.Burn of the delta, and the commit subject stating gas is charged during activation. The hash and write_slice changes appear ancillary to the activation interface and should not be treated as the vulnerability root cause. Protocol security invariant: Wasm activation should be charged against the caller's gas budget, and gas consumed inside Rust/native activation should be reflected back to the Go-side burner before execution continues. Verification notes: The patch does not prove a remotely triggerable exploit by itself. The patch does not prove consensus divergence or state corruption from the prior behavior. The patch does not show a cryptographic hash validation bug; hash handling is adjacent interface output. The patch does not establish whether the issue was denial of service, economic undercharging, or only accounting hardening. The provided evidence does not quantify gas undercharge magnitude or affected transaction types. No evidence proves remote exploitability. No evidence proves consensus divergence or state corruption. No evidence proves a cryptographic or hash-validation flaw. No evidence quantifies the prior undercharge or affected transaction set. Confidence is medium because the gas-accounting change is clear, but the vulnerability impact is inferred from resource-metering context. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gas-accounting`
Final impact type: `resource-metering, economic-undercharge`
Final tags: `blockchain-core, wasm, stylus, gas-accounting, resource-control`

The supplied evidence supports keeping this as security hardening, but not as state corruption or a concrete security exploit. The patch explicitly threads remaining gas through Wasm activation in both native and JIT paths and burns the consumed delta, matching the commit subject. In a blockchain execution environment, missing activation gas charging is a security-sensitive resource-accounting weakness, but the evidence does not prove exploitability, consensus divergence, storage corruption, or state-integrity impact.

## Security Evidence

1. Commit subject says gas is charged during activation for native and JIT paths.
2. JIT activation reads gas from Go stack, passes mutable gas into native activation, and writes the remaining gas back.
3. Go activation captures burner.GasLeft(), passes gas into activateWasmRustImpl, then burns the consumed delta.
4. On JIT activation error, gas is set to zero before returning the error.

## Missing Evidence

1. No evidence quantifies the previous undercharge or affected transactions.
2. No proof of remote exploitability or practical denial of service is supplied.
3. No evidence supports state corruption, storage inconsistency, or consensus divergence.
4. No evidence shows a cryptographic or hash-validation flaw.

## Claim Boundaries

1. Validate only as gas-accounting/resource-control hardening.
2. Do not classify as state-corruption or state-integrity from the supplied patch.
3. Do not claim a concrete exploitable vulnerability from this evidence alone.
4. Hash and write_slice changes appear ancillary to the activation interface, not the root issue.
