---
case_id: case_20250218_6e39803ab8
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: medium
date: 2025-02-18
source_refs:
  - git:6e39803ab8c73093389666f57f0510bdea5c9650
  - "op-program/client/boot/boot_interop_test.go:170"
  - "op-program/client/interop/consolidate.go:62"
  - "op-program/client/interop/consolidate.go:226"
  - "op-program/client/boot/boot_interop.go:81"
bug_class: verification-config-inconsistency
impact_type:
  - state-consistency
confidence: medium
tags:
  - blockchain-core
  - proof-validation
  - config-consistency
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes interop consolidation to load a DependencySet from boot configuration and pass that object through, instead of constructing a static dependency set inside the consolidation helper. That is a real correctness and consistency change in a sensitive path, but the provided evidence does not establish a concrete vulnerability, exploit path, or even whether the old behavior caused false accepts rather than only mismatches or operational failures.

## Observed Patch Facts

1. In `op-program/client/boot/boot_interop_test.go`, the patch replaces `default:` with `case DependencySetLocalIndex.PreimageKey():`.

2. In `op-program/client/interop/consolidate.go`, the patch replaces `deps, err := newConsolidateCheckDeps(bootInfo, transitionState, superRoot.Chains, l2P...` with `// The depset is the same for all chains. So it suffices to use any chain ID`.

3. In `op-program/client/interop/consolidate.go`, the patch replaces `depset, err := depset.NewStaticConfigDependencySet(deps)` with `oracle: oracle,`.

4. In `op-program/client/boot/boot_interop.go`, the patch replaces `func (c *OracleConfigSource) loadCustomConfigs() {` with `func (c *OracleConfigSource) DependencySet(chainID eth.ChainID) (depset.DependencySet...`.

## Project Context

The changed code sits primarily in `op-program/client/boot`, `op-program/client`, `op-program/client/interop`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `op-program/client/interop/interop_test.go`, `op-program/client/boot/boot_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-program/client/interop/interop_test.go`, `op-program/client/boot/boot_test.go`. The strongest project-level identifiers around this patch are `depset`, `deps`, `PreimageKey`, and `unexpected`. Nearby tests or test-like files include `op-program/client/l2/test/stub_oracle.go`, `op-program/client/l1/test/stub_oracle.go`.

## Before/After Behavior

Before the patch, RunConsolidation called newConsolidateCheckDeps without an explicit DependencySet input, and newConsolidateCheckDeps created a static dependency set locally. The boot-side code shown did not expose a DependencySet accessor, and the interop bootstrap oracle test had no explicit DependencySet preimage case. After the patch, RunConsolidation fetches a DependencySet from bootInfo.Configs.DependencySet(superRoot.Chains[0].ChainID), passes it into newConsolidateCheckDeps, OracleConfigSource exposes DependencySet retrieval, and the bootstrap oracle test explicitly serves a serialized DependencySet for the boot path.

# Root Cause

The grounded root cause is inconsistent sourcing of dependency-set state: one path rebuilt the dependency set inside consolidation while the patched code treats it as boot-provided configuration that should be loaded and threaded through directly. The evidence supports a consistency/correctness issue, but not a demonstrated security flaw.

## Walkthrough

1. op-program/client/boot/boot_interop.go adds OracleConfigSource.DependencySet(chainID), returning c.depset if present or loading custom configs before returning it.

2. op-program/client/boot/boot_interop_test.go adds explicit handling for DependencySetLocalIndex.PreimageKey(), serializing o.depset for the bootstrap oracle path.

3. op-program/client/interop/consolidate.go changes RunConsolidation to retrieve a DependencySet from bootInfo.Configs before building consolidation dependencies.

4. The same file changes newConsolidateCheckDeps to accept a depset.DependencySet parameter directly.

5. The previous local construction step using depset.NewStaticConfigDependencySet(deps) is removed, so the helper now consumes the supplied dependency set instead of rebuilding one.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-program/client/interop/consolidate.go | 55 | loads the canonical DependencySet from boot config before running consolidation |
| op-program/client/interop/consolidate.go | 202 | threads the provided DependencySet into consolidateCheckDeps instead of reconstructing it locally |
| op-program/client/boot/boot_interop.go | 64 | OracleConfigSource exposes DependencySet retrieval from embedded/custom boot configuration |
| op-program/client/boot/boot_interop_test.go | 156 | bootstrap oracle now serves serialized DependencySet preimage for the interop boot path |

## Code Snippets

## Snippet 1

Context: `op-program/client/boot/boot_interop_test.go:170` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
case L2ChainIDLocalIndex.PreimageKey():
		panic("unexpected oracle request for l2 chain ID preimage key")
	default:
		return o.mockBoostrapOracle.Get(key)
```
After
```go
case L2ChainIDLocalIndex.PreimageKey():
		panic("unexpected oracle request for l2 chain ID preimage key")
	case DependencySetLocalIndex.PreimageKey():
		if !o.custom {
			panic(fmt.Sprintf("unexpected oracle request for preimage key %x", key.PreimageKey()))
		}
		b, _ := json.Marshal(o.depset)
		return b
```

## Snippet 2

Context: `op-program/client/interop/consolidate.go:62` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
tasks taskExecutor,
) (eth.Bytes32, error) {
	deps, err := newConsolidateCheckDeps(bootInfo, transitionState, superRoot.Chains, l2PreimageOracle)
	if err != nil {
		return eth.Bytes32{}, fmt.Errorf("failed to create consolidate check deps: %w", err)
```
After
```go
tasks taskExecutor,
) (eth.Bytes32, error) {
	// The depset is the same for all chains. So it suffices to use any chain ID
	depset, err := bootInfo.Configs.DependencySet(superRoot.Chains[0].ChainID)
	if err != nil {
		return eth.Bytes32{}, fmt.Errorf("failed to get dependency set: %w", err)
	}
	deps, err := newConsolidateCheckDeps(depset, bootInfo, transitionState, superRoot.Chains, l2PreimageOracle)
```

## Snippet 3

Context: `op-program/client/interop/consolidate.go:226` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	depset, err := depset.NewStaticConfigDependencySet(deps)
	if err != nil {
		return nil, fmt.Errorf("unexpected error: failed to create dependency set: %w", err)
	}

	return &consolidateCheckDeps{
```
After
```go
}

	return &consolidateCheckDeps{
		oracle:      oracle,
```

## Snippet 4

Context: `op-program/client/boot/boot_interop.go:81` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (c *OracleConfigSource) loadCustomConfigs() {
	var rollupConfigs []*rollup.Config
```
After
```go
}

func (c *OracleConfigSource) DependencySet(chainID eth.ChainID) (depset.DependencySet, error) {
	if c.depset != nil {
		return c.depset, nil
	}
	// TODO(#13887): The embedded depset must be loaded first before falling back to using custom configs
	c.loadCustomConfigs()
```

# Fix Pattern

Stop reconstructing shared configuration inside a downstream checker and instead load the canonical object from the upstream boot/config source and pass it through explicitly.

## How It Was Fixed

The fix makes DependencySet part of the boot configuration interface, teaches the bootstrap path to serve it explicitly, fetches it in RunConsolidation, and removes the local dependency-set reconstruction from newConsolidateCheckDeps.

# Why It Matters

1. It reduces the chance that different code paths use different dependency-set state.

2. It makes the consolidation path depend on the same object the boot/config layer provides.

3. It improves consistency in a proof-related subsystem, even though the evidence does not prove an exploitable bug.

# Evidence Notes

The strongest support is the direct code motion from local depset construction in op-program/client/interop/consolidate.go to boot-sourced DependencySet retrieval, plus the new DependencySet accessor in op-program/client/boot/boot_interop.go and the explicit DependencySet preimage case in op-program/client/boot/boot_interop_test.go. What is not shown is a failing scenario, attacker control, a false-accept condition, a consensus break, or any proof that the old code violated a security property rather than a correctness/configuration property. Protocol security invariant: If interop consolidation is security-relevant, all participants should evaluate it against the same DependencySet sourced from boot configuration rather than rebuilding an equivalent-looking set locally from parallel inputs. Verification notes: The patch does not prove that invalid proofs were previously accepted on mainnet or any deployed network. The diff does not show an attacker-controlled source for the DependencySet or a concrete remote exploit path. The patch does not establish a cryptographic break; it shows verifier-context consistency hardening. The evidence does not prove whether the prior bug caused false accepts, false rejects, or only configuration drift in limited cases. The patch clearly changes where DependencySet comes from. The patch does not show the removed behavior accepting invalid data. The patch does not show a concrete adversarial input or externally reachable exploit path. Security relevance is plausible because the code is in a verification-related path, but it is not established by the provided evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `verification-config-inconsistency`
Final impact type: `state-consistency`
Final confidence: `medium`
Final tags: `blockchain-core, proof-validation, config-consistency, security-hardening`

The patch moves interop consolidation onto a boot-sourced canonical `DependencySet`, removes local reconstruction of that state inside the checker, and adds explicit oracle/bootstrap handling for the dependency set. In a proof/consolidation path, that is a real hardening change because it reduces verifier-context drift and makes security-sensitive checks depend on a single authoritative configuration source. The evidence does not show a concrete exploit, invalid-proof acceptance, or attacker-controlled trigger in the old code, so this is better retained as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. `RunConsolidation` now fetches `DependencySet` from `bootInfo.Configs` before building consolidation dependencies.
2. `newConsolidateCheckDeps` no longer reconstructs a static dependency set locally; it consumes the provided canonical object.
3. The bootstrap/oracle path gained explicit `DependencySetLocalIndex.PreimageKey()` handling, indicating the dependency set became part of canonical boot input.
4. The changed code is in interop proof/consolidation logic, a security-sensitive validation path where configuration drift can matter.

## Missing Evidence

1. No shown scenario where the old code accepted an invalid proof or invalid state transition.
2. No attacker-controlled input or externally reachable exploit path is demonstrated in the patch.
3. No evidence distinguishes false-accept behavior from false-reject or reliability-only divergence.
4. No advisory, bug description, or test explicitly states a broken security property before the change.

## Claim Boundaries

1. Supported: this hardens verifier/config consistency in a proof-related path.
2. Not supported: a confirmed exploitable vulnerability in the prior implementation.
3. Not supported: a specific RPC/API serialization bug as the primary security issue.
4. Not supported: claims of consensus break, proof forgery, or validation bypass from the patch alone.
