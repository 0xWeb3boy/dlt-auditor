---
case_id: case_20190124_c7664b063
project: bor
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2019-01-24
source_refs:
  - git:c7664b06361663e2027e74574804f3210542f19f
  - "params/config.go:327"
  - "core/vm/logger_json.go:35"
  - "core/vm/gas_table.go:122"
  - "cmd/puppeth/genesis.go:349"
bug_class: consensus-rule-hardening
impact_type:
  - consensus-divergence
  - unsafe-execution-semantics
confidence: medium
tags:
  - consensus
  - fork-management
  - evm-gas
  - protocol-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence shows implementation of the Petersburg/ConstantinopleFix fork across gas metering, config compatibility, and chain-spec generation. That is security-relevant protocol hardening, but the provided material does not establish a standalone exploitable vulnerability in this client.

## Observed Patch Facts

1. In `params/config.go`, the patch adds `if isForkIncompatible(c.PetersburgBlock, newcfg.PetersburgBlock, head) {`.

2. In `core/vm/logger_json.go`, the patch replaces `return &JSONLogger{json.NewEncoder(writer), cfg}` with `l := &JSONLogger{json.NewEncoder(writer), cfg}`.

3. In `core/vm/gas_table.go`, the patch replaces `if !evm.chainRules.IsConstantinople {` with `// Legacy rules should be applied if we are in Petersburg (removal of EIP-1283)`.

4. In `cmd/puppeth/genesis.go`, the patch replaces `spec.Params.MinGasLimit = (hexutil.Uint64)(params.MinGasLimit)` with `// ConstantinopleFix (remove eip-1283)`.

## Project Context

The changed code sits primarily in `core/vm`, `cmd/puppeth`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `cmd/puppeth/wizard_genesis.go`, `cmd/puppeth/module_dashboard.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cmd/puppeth/wizard_genesis.go`, `cmd/puppeth/module_dashboard.go`. The strongest project-level identifiers around this patch are `newcfg`, `PetersburgBlock`, `EWASMBlock`, and `spec`. Nearby tests or test-like files include `core/vm/runtime/fuzz.go`.

## Before/After Behavior

Before the patch, the shown code had no separate Petersburg-specific compatibility check, no separate ConstantinopleFix export in generated chain specs, and `gasSStore` only used legacy metering when Constantinople was inactive. After the patch, Petersburg/ConstantinopleFix becomes an explicit fork in config validation and chain-spec generation, and `gasSStore` also selects legacy metering when Petersburg is active.

# Root Cause

The shown code lacked first-class handling for the Petersburg/ConstantinopleFix fork. The evidence supports missing protocol-update support across consensus-critical paths, not a clearly demonstrated local implementation flaw with a proven exploit path.

## Walkthrough

1. `core/vm/gas_table.go` changes the SSTORE metering gate from `!evm.chainRules.IsConstantinople` to `evm.chainRules.IsPetersburg || !evm.chainRules.IsConstantinople`, with comments stating that Petersburg removes EIP-1283.

2. `params/config.go` adds a dedicated compatibility check for `PetersburgBlock` and returns a `ConstantinopleFix fork block` compatibility error when the configured fork height is incompatible.

3. `cmd/puppeth/genesis.go` starts emitting `spec.setConstantinopleFix(num)` from `genesis.Config.PetersburgBlock`, so generated chain specs carry the new fork transition.

4. The combined effect is explicit rollout of a new fork rule across execution, configuration validation, and network-spec generation.

5. `core/vm/logger_json.go` also changed, but the supplied evidence does not connect that nil-config guard to the fork or any security invariant.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/vm/gas_table.go | 122 | Applies the active SSTORE gas schedule; Petersburg disables the Constantinople EIP-1283 path. |
| params/config.go | 327 | Rejects incompatible Petersburg/ConstantinopleFix fork configuration after chain progress, preserving consensus compatibility. |
| cmd/puppeth/genesis.go | 349 | Emits ConstantinopleFix/Petersburg into generated chain specs so deployed nodes share the same fork activation point. |

## Code Snippets

## Snippet 1

Context: `params/config.go:327` (changes a consensus- or validator-sensitive branch)

Before
```go
return newCompatError("Constantinople fork block", c.ConstantinopleBlock, newcfg.ConstantinopleBlock)
	}
	if isForkIncompatible(c.EWASMBlock, newcfg.EWASMBlock, head) {
		return newCompatError("ewasm fork block", c.EWASMBlock, newcfg.EWASMBlock)
```
After
```go
return newCompatError("Constantinople fork block", c.ConstantinopleBlock, newcfg.ConstantinopleBlock)
	}
	if isForkIncompatible(c.PetersburgBlock, newcfg.PetersburgBlock, head) {
		return newCompatError("ConstantinopleFix fork block", c.PetersburgBlock, newcfg.PetersburgBlock)
	}
	if isForkIncompatible(c.EWASMBlock, newcfg.EWASMBlock, head) {
		return newCompatError("ewasm fork block", c.EWASMBlock, newcfg.EWASMBlock)
```

## Snippet 2

Context: `core/vm/logger_json.go:35` (changes a sensitive control or state-update path)

Before
```go
// into the provided stream.
func NewJSONLogger(cfg *LogConfig, writer io.Writer) *JSONLogger {
	return &JSONLogger{json.NewEncoder(writer), cfg}
}
```
After
```go
// into the provided stream.
func NewJSONLogger(cfg *LogConfig, writer io.Writer) *JSONLogger {
	l := &JSONLogger{json.NewEncoder(writer), cfg}
	if l.cfg == nil {
		l.cfg = &LogConfig{}
	}
	return l
}
```

## Snippet 3

Context: `core/vm/gas_table.go:122` (changes a sensitive control or state-update path)

Before
```go
)
	// The legacy gas metering only takes into consideration the current state
	if !evm.chainRules.IsConstantinople {
		// This checks for 3 scenario's and calculates gas accordingly:
		//
```
After
```go
)
	// The legacy gas metering only takes into consideration the current state
	// Legacy rules should be applied if we are in Petersburg (removal of EIP-1283)
	// OR Constantinople is not active
	if evm.chainRules.IsPetersburg || !evm.chainRules.IsConstantinople {
		// This checks for 3 scenario's and calculates gas accordingly:
		//
```

## Snippet 4

Context: `cmd/puppeth/genesis.go:349` (changes a sensitive control or state-update path)

Before
```go
spec.setConstantinople(num)
	}
	spec.Params.MaximumExtraDataSize = (hexutil.Uint64)(params.MaximumExtraDataSize)
	spec.Params.MinGasLimit = (hexutil.Uint64)(params.MinGasLimit)
```
After
```go
spec.setConstantinople(num)
	}
	// ConstantinopleFix (remove eip-1283)
	if num := genesis.Config.PetersburgBlock; num != nil {
		spec.setConstantinopleFix(num)
	}

	spec.Params.MaximumExtraDataSize = (hexutil.Uint64)(params.MaximumExtraDataSize)
```

# Fix Pattern

Implement a new fork boundary consistently across execution rules, compatibility checks, and chain-spec tooling.

## How It Was Fixed

The patch adds Petersburg-aware SSTORE metering, rejects incompatible Petersburg fork heights in chain configuration, and emits ConstantinopleFix/Petersburg in generated Parity chain specs. This aligns runtime behavior and generated network configuration with the rollback of EIP-1283.

# Why It Matters

1. Consensus clients need the same fork schedule to avoid rule divergence.

2. SSTORE gas accounting is consensus-critical, so fork-specific gating must be explicit.

3. Chain-spec tooling must carry the same fork settings as runtime validation.

4. The commit message shows operational breakage risk for misconfigured private networks, even if direct exploitability is not proven here.

# Evidence Notes

Direct evidence is limited to consensus-rule and tooling changes in `core/vm/gas_table.go`, `params/config.go`, and `cmd/puppeth/genesis.go`. The commit message says the PR adds a fork that disables EIP-1283 and warns that private networks can break unless ConstantinopleFix is set. That supports a protocol-update or hardening reading. It does not, by itself, prove attacker-triggered compromise, asset theft, or privilege bypass in this client. The JSON logger change is unsupported as part of the security thesis. Protocol security invariant: Nodes on the same chain must activate the same fork rules at the same block and apply the same SSTORE gas schedule. If Petersburg/ConstantinopleFix is active, execution and configuration must stop treating Constantinople EIP-1283 behavior as the active rule set. Verification notes: The patch does not by itself prove a remotely exploitable bug in this client. It does not show asset theft or privilege bypass; the clearest risk is protocol-rule divergence or unsafe gas semantics. Much of the change is adoption of the Petersburg fork, so the underlying issue may originate in protocol design rather than a local implementation defect. The JSON logger nil-config change is not shown here to affect any security invariant. The commit message's private-network breakage warning describes operational compatibility risk, not direct attacker compromise. No provided snippet shows an exploit, failing transaction, or attacker-controlled trigger. The supplied evidence does not prove asset loss, privilege escalation, or a direct remote compromise path. No test excerpt is included here that demonstrates the exact regression or attack scenario. The strongest supported classification is security-relevant protocol hardening, but the vulnerability thesis remains unproven from the provided evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-rule-hardening`
Final impact type: `consensus-divergence, unsafe-execution-semantics`
Final confidence: `medium`
Final tags: `consensus, fork-management, evm-gas, protocol-hardening`

The patch clearly changes security-sensitive protocol behavior by disabling EIP-1283 semantics under the Petersburg/ConstantinopleFix fork, enforcing fork-height compatibility, and propagating the new fork setting into generated chain specs. That is enough to treat the change as security hardening for consensus and execution safety. However, the supplied evidence does not prove a concrete exploitable vulnerability in this client, so it should not be elevated to a confirmed security-fix case.

## Security Evidence

1. `core/vm/gas_table.go` switches SSTORE metering away from Constantinople behavior when `IsPetersburg` is active, explicitly noting removal of EIP-1283.
2. `params/config.go` adds compatibility enforcement for `PetersburgBlock`, reducing risk of nodes running divergent fork rules.
3. `cmd/puppeth/genesis.go` emits `ConstantinopleFix` into generated chain specs so deployed nodes share the same fork transition.
4. The commit subject/body explicitly describe a fix fork that disables EIP-1283, which is a security-sensitive execution-rule rollback.

## Missing Evidence

1. No provided test excerpt demonstrates an attacker-triggerable exploit or failing security regression.
2. No snippet shows concrete impact such as theft, privilege bypass, or remote compromise in this client.
3. The evidence does not prove whether the underlying issue was a local implementation bug versus adoption of an external protocol fix.
4. `core/vm/logger_json.go` is included in the diff but is not tied to the security claim by the provided material.

## Claim Boundaries

1. Supported claim: the commit hardens consensus/execution behavior by removing EIP-1283 semantics under a new fork boundary.
2. Supported claim: the change reduces risk of fork-rule mismatch across runtime config and generated chain specs.
3. Not supported: a specific exploitable vulnerability in this codebase was conclusively fixed by the shown patch.
4. Not supported: the JSON logger nil-config guard is security-relevant based on the supplied evidence.
