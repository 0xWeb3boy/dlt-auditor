---
case_id: case_20210803_0825857a2d
project: avalanchego
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2021-08-03
source_refs:
  - git:0825857a2d8ad9f108a198b319c6076d9973f9c2
  - "consensus/dummy/consensus.go:176"
  - "core/vm/evm.go:524"
  - "consensus/dummy/consensus.go:42"
  - "consensus/dummy/consensus.go:35"
bug_class: fork-rule-activation-mismatch
impact_type:
  - consensus-integrity
  - state-integrity
tags:
  - evm
  - contract-creation
  - fork-rules
  - eip-3541
  - consensus
  - state-transition-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded security-relevant change is in core/vm/evm.go: the contract-creation invalid-code check for returned code beginning with 0xEF moved from evm.chainRules.IsApricotPhase4 to evm.chainRules.IsApricotPhase3. This likely fixes a fork-rule activation error in a consensus-sensitive EVM path. The DummyEngine skipBlockFee changes are support/test/faker consensus plumbing based on the supplied comments and should not be treated as the root security issue.

## Observed Patch Facts

1. In `consensus/dummy/consensus.go`, the patch replaces `// TODO(aaronbuchwald) this may become necessary again for the dummy engine` with `if self.skipBlockFee {`.

2. In `core/vm/evm.go`, the patch replaces `if err == nil && len(ret) >= 1 && ret[0] == 0xEF && evm.chainRules.IsApricotPhase4 {` with `if err == nil && len(ret) >= 1 && ret[0] == 0xEF && evm.chainRules.IsApricotPhase3 {`.

3. In `consensus/dummy/consensus.go`, the patch replaces `// skipBlockFee: skipBlockFee,` with `func NewFakerSkipBlockFee() *DummyEngine {`.

4. In `consensus/dummy/consensus.go`, the patch replaces `cb *ConsensusCallbacks` with `cb *ConsensusCallbacks`.

## Project Context

The changed code sits primarily in `consensus/dummy`, `core/vm`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/vm/logger.go`, `core/vm/interface.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/vm/runtime/runtime_test.go`, `core/vm/logger.go`. The strongest project-level identifiers around this patch are `skipBlockFee`, `DummyEngine`, `types`, and `ConsensusCallbacks`.

## Before/After Behavior

Before the patch, EVM contract creation rejected 0xEF-prefixed returned contract code only when IsApricotPhase4 was true. After the patch, the same rejection occurs when IsApricotPhase3 is true. Separately, DummyEngine gained an explicit skipBlockFee field, a NewFakerSkipBlockFee constructor, and an early return from verifyBlockFee when that flag is set.

# Root Cause

The EVM create path used the wrong fork-phase predicate for the 0xEF-prefix invalid-code rule, delaying enforcement from ApricotPhase3 to ApricotPhase4. The provided evidence does not establish the dummy skipBlockFee path as a production vulnerability.

## Walkthrough

1. EVM.create executes contract initcode and obtains the returned code in ret.

2. Post-execution validation checks max code size and then checks whether returned code begins with 0xEF.

3. Before the patch, that invalid-code check was gated by IsApricotPhase4.

4. After the patch, the check is gated by IsApricotPhase3.

5. When the rule applies, ret[0] == 0xEF now sets err = ErrInvalidCode earlier than before.

6. Because contract creation validity affects state-transition acceptance, the wrong fork gate can change which blocks or transactions are considered valid under a phase.

7. The DummyEngine hunks restore skipBlockFee behavior for a dummy/faker engine, but the evidence frames this as migrated-test support.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/vm/evm.go | 524 | EVM contract creation validates returned initcode against the active fork rules and now rejects 0xEF-prefixed code at ApricotPhase3 instead of ApricotPhase4. |
| consensus/dummy/consensus.go | 35 | DummyEngine stores the skipBlockFee flag used by test/faker consensus behavior. |
| consensus/dummy/consensus.go | 41 | NewFakerSkipBlockFee constructs a dummy engine with base-fee verification disabled for migrated tests. |
| consensus/dummy/consensus.go | 176 | DummyEngine block-fee verification exits early when skipBlockFee is set, affecting dummy consensus validation only as shown. |

## Code Snippets

## Snippet 1

Context: `consensus/dummy/consensus.go:176` (changes a sensitive control or state-update path)

Before
```go
func (self *DummyEngine) verifyBlockFee(chain consensus.ChainHeaderReader, header *types.Header, txs []*types.Transaction, receipts []*types.Receipt) error {
	// TODO(aaronbuchwald) this may become necessary again for the dummy engine
	// If the engine is not charging the base fee, skip the verification.
	// Note: this is a hack to support tests migrated from geth without substantial modification.
	// if self.skipBlockFee {
	// 	return nil
	// }
```
After
```go
func (self *DummyEngine) verifyBlockFee(chain consensus.ChainHeaderReader, header *types.Header, txs []*types.Transaction, receipts []*types.Receipt) error {
	// If the engine is not charging the base fee, skip the verification.
	// Note: this is a hack to support tests migrated from geth without substantial modification.
	if self.skipBlockFee {
		return nil
	}
	bigTimestamp := new(big.Int).SetUint64(header.Time)
```

## Snippet 2

Context: `core/vm/evm.go:524` (changes a sensitive control or state-update path)

Before
```go
// Reject code starting with 0xEF if EIP-3541 is enabled.
	if err == nil && len(ret) >= 1 && ret[0] == 0xEF && evm.chainRules.IsApricotPhase4 {
		err = ErrInvalidCode
	}
```
After
```go
// Reject code starting with 0xEF if EIP-3541 is enabled.
	if err == nil && len(ret) >= 1 && ret[0] == 0xEF && evm.chainRules.IsApricotPhase3 {
		err = ErrInvalidCode
	}
```

## Snippet 3

Context: `consensus/dummy/consensus.go:42` (changes a consensus- or validator-sensitive branch)

Before
```go
return &DummyEngine{
		cb: cb,
		// skipBlockFee: skipBlockFee,
	}
}
```
After
```go
return &DummyEngine{
		cb: cb,
	}
}

func NewFakerSkipBlockFee() *DummyEngine {
	return &DummyEngine{
		cb:           new(ConsensusCallbacks),
```

## Snippet 4

Context: `consensus/dummy/consensus.go:35` (changes a consensus- or validator-sensitive branch)

Before
```go
type DummyEngine struct {
	cb *ConsensusCallbacks
	// skipBlockFee bool
}
```
After
```go
type DummyEngine struct {
	cb           *ConsensusCallbacks
	skipBlockFee bool
}
```

# Fix Pattern

Correct the fork-rule predicate at the consensus-sensitive validation point and keep dummy-engine test exceptions explicit through a flag and dedicated constructor.

## How It Was Fixed

core/vm/evm.go changed the 0xEF-prefix rejection guard from evm.chainRules.IsApricotPhase4 to evm.chainRules.IsApricotPhase3. consensus/dummy/consensus.go added a skipBlockFee bool, NewFakerSkipBlockFee, and a verifyBlockFee early return when skipBlockFee is enabled.

# Why It Matters

1. Contract creation validity is consensus-sensitive.

2. Applying a fork rule one phase late can permit state transitions that should be invalid.

3. The evidence supports a fork-rule activation fix, not claims of theft or observed network divergence.

4. The skipBlockFee changes are not shown to affect production consensus.

# Evidence Notes

Primary evidence is the core/vm/evm.go hunk changing the 0xEF invalid-code guard from IsApricotPhase4 to IsApricotPhase3 inside EVM.create. Supporting evidence shows this occurs after initcode execution and before successful code storage. DummyEngine evidence shows skipBlockFee was uncommented and exposed through NewFakerSkipBlockFee; comments describe it as a hack for tests migrated from geth. No supplied evidence shows params/config.go contents, deployed network impact, attacker exploitation, or production use of DummyEngine skipBlockFee. Protocol security invariant: EVM contract creation must enforce fork-activated code validity rules at the intended phase. If the 0xEF-prefix rejection rule is active for ApricotPhase3, newly created contract code beginning with 0xEF must be rejected during that phase so all nodes agree on valid state transitions. Verification notes: The patch does not prove remote exploitability or an attacker-controlled trigger beyond ordinary contract creation semantics. The provided evidence does not show the params/config.go changes, so the exact network activation configuration issue is inferred only from the EVM phase-gate hunk. The dummy consensus skipBlockFee changes are not shown to affect production consensus. No evidence is provided that existing deployed nodes diverged or that funds could be stolen. Verified against supplied diff excerpts only. Downgraded from confirmed/high to likely/medium because the evidence does not include the fork configuration file or external confirmation that ApricotPhase3 is the intended activation point. Kept in security corpus because the production EVM change directly affects consensus/state-transition validity. Did not treat helper/test DummyEngine changes as the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `fork-rule-activation-mismatch`
Final impact type: `consensus-integrity, state-integrity`
Final tags: `evm, contract-creation, fork-rules, eip-3541, consensus, state-transition-validation`

The supplied evidence supports retaining this as security hardening, not a proven security fix. The production EVM create path changed the 0xEF-prefixed contract-code rejection from ApricotPhase4 to ApricotPhase3, tightening a consensus-sensitive validity rule. However, the patch evidence does not include the config change, activation schedule proof, exploit scenario, or observed consensus failure, so claims of state corruption or a concrete vulnerability are too strong.

## Security Evidence

1. core/vm/evm.go changes contract creation validation in a production EVM state-transition path.
2. The changed branch rejects returned contract code beginning with 0xEF earlier, at IsApricotPhase3 instead of IsApricotPhase4.
3. Contract creation validity can affect transaction and block acceptance under fork rules.

## Missing Evidence

1. No params/config.go diff is supplied to prove ApricotPhase3 is definitely the intended EIP-3541 activation point.
2. No evidence shows deployed network divergence, exploitability, or attacker impact.
3. DummyEngine skipBlockFee changes are described as faker/test support and are not shown to affect production consensus.

## Claim Boundaries

1. Classify as fork-rule validation hardening rather than confirmed state corruption.
2. Do not treat the DummyEngine skipBlockFee hunks as the root security issue.
3. Do not claim theft, remote exploitation, or observed consensus failure from the supplied patch alone.
