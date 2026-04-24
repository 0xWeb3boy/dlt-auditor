---
case_id: case_20240626_d1ea098c1f
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-06-26
source_refs:
  - git:d1ea098c1f99c396de407a7ba69bc79d1bc578fe
  - "cannon/cmd/run.go:437"
  - "cannon/cmd/witness.go:31"
  - "op-challenger/game/fault/trace/cannon/provider.go:133"
  - "op-challenger/game/fault/trace/cannon/prestate.go:35"
bug_class: incorrect-proof-state-hash
impact_type:
  - proof-integrity
  - state-integrity
confidence: medium
tags:
  - fault-proof
  - state-commitment
  - witness-hash
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects how Cannon-related code obtains state hashes for proofs and witness consumers, especially by taking a hash from `EncodeWitness()` after execution in the shown proof path. The evidence supports a correctness fix around state-commitment derivation, but does not by itself establish an exploitable security vulnerability.

## Observed Patch Facts

1. In `cannon/cmd/run.go`, the patch replaces `preStateHash, err := state.EncodeWitness().StateHash()` with `return fmt.Errorf("failed at proof-gen step %d (PC: %08x): %w", step, state.GetPC(),...`.

2. In `cannon/cmd/witness.go`, the patch replaces `witness := state.EncodeWitness()` with `witness, h := state.EncodeWitness()`.

3. In `op-challenger/game/fault/trace/cannon/provider.go`, the patch replaces `witness := state.EncodeWitness()` with `witness, witnessHash := state.EncodeWitness()`.

4. In `op-challenger/game/fault/trace/cannon/prestate.go`, the patch replaces `state, err := p.absolutePreState()` with `_, hash, err := p.absolutePreState()`.

## Project Context

The changed code sits primarily in `cannon/cmd`, `op-challenger/game/fault/trace/cannon`, `op-challenger/game/fault/trace`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-challenger/game/fault/trace/cannon/prestate_test.go`, `op-challenger/game/fault/trace/cannon/provider_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-challenger/game/fault/trace/cannon/provider_test.go`, `op-challenger/game/fault/trace/cannon/prestate_test.go`. The strongest project-level identifiers around this patch are `state`, `witness`, `Errorf`, and `hash`.

## Before/After Behavior

Before the patch, the shown `cannon/cmd/run.go` proof path computed a hash from `state.EncodeWitness().StateHash()` before calling `stepFn(true)`. After the patch, the shown path calls `stepFn(true)` first and then obtains `postStateHash` from `state.EncodeWitness()`. In `cannon/cmd/witness.go`, `provider.go`, and `prestate.go`, callers stop separately hashing serialized witness bytes and instead consume hashes returned from the canonical path.

# Root Cause

The evidence points to stage-incorrect and non-canonical state-hash derivation: some callers separately recomputed hashes from encoded witness data, and the shown proof path derived a hash before the execution step instead of taking the post-step hash afterward.

## Walkthrough

1. In `cannon/cmd/run.go`, the pre-patch code hashed `state.EncodeWitness()` before `stepFn(true)` ran.

2. In the patched `run.go` snippet, `stepFn(true)` runs first and `postStateHash` is then taken from `state.EncodeWitness()`.

3. In `cannon/cmd/witness.go`, the code changes from separate witness serialization plus `StateHash()` to `witness, h := state.EncodeWitness()`.

4. In `op-challenger/game/fault/trace/cannon/provider.go`, terminal proof extension likewise switches from rehashing witness bytes to using the hash returned with the witness.

5. In `op-challenger/game/fault/trace/cannon/prestate.go`, the absolute pre-state commitment is taken from the canonical loader/hash return path instead of a separate hash step.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| cannon/cmd/run.go | 437 | proof generation now derives the committed hash from the post-step VM state instead of a pre-step/stale witness path |
| cannon/cmd/witness.go | 31 | canonical witness generation now returns serialized witness bytes together with its commitment hash |
| op-challenger/game/fault/trace/cannon/provider.go | 133 | trace provider uses the canonical witness/hash pair when extending terminal proofs after execution ends |
| op-challenger/game/fault/trace/cannon/prestate.go | 35 | absolute pre-state commitment is sourced from the canonical prestate loader/hash path |

## Code Snippets

## Snippet 1

Context: `cannon/cmd/run.go:437` (changes signature or replay validation logic)

Before
```go
if proofAt(state) {
			preStateHash, err := state.EncodeWitness().StateHash()
			if err != nil {
				return fmt.Errorf("failed to hash prestate witness: %w", err)
			}
			witness, err := stepFn(true)
			if err != nil {
```
After
```go
if proofAt(state) {
			witness, err := stepFn(true)
			if err != nil {
				return fmt.Errorf("failed at proof-gen step %d (PC: %08x): %w", step, state.GetPC(), err)
			}
			_, postStateHash := state.EncodeWitness()
			proof := &Proof{
```

## Snippet 2

Context: `cannon/cmd/witness.go:31` (changes signature or replay validation logic)

Before
```go
return fmt.Errorf("invalid input state (%v): %w", input, err)
	}
	witness := state.EncodeWitness()
	h, err := witness.StateHash()
	if err != nil {
		return fmt.Errorf("failed to compute witness hash: %w", err)
	}
	if output != "" {
```
After
```go
return fmt.Errorf("invalid input state (%v): %w", input, err)
	}
	witness, h := state.EncodeWitness()
	if output != "" {
		if err := os.WriteFile(output, witness, 0755); err != nil {
```

## Snippet 3

Context: `op-challenger/game/fault/trace/cannon/provider.go:133` (changes signature or replay validation logic)

Before
```go
// Extend the trace out to the full length using a no-op instruction that doesn't change any state
				// No execution is done, so no proof-data or oracle values are required.
				witness := state.EncodeWitness()
				witnessHash, err := mipsevm.StateWitness(witness).StateHash()
				if err != nil {
					return nil, fmt.Errorf("cannot hash witness: %w", err)
				}
				proof := &utils.ProofData{
```
After
```go
// Extend the trace out to the full length using a no-op instruction that doesn't change any state
				// No execution is done, so no proof-data or oracle values are required.
				witness, witnessHash := state.EncodeWitness()
				proof := &utils.ProofData{
					ClaimValue:   witnessHash,
```

## Snippet 4

Context: `op-challenger/game/fault/trace/cannon/prestate.go:35` (changes signature or replay validation logic)

Before
```go
return p.prestateCommitment, nil
	}
	state, err := p.absolutePreState()
	if err != nil {
		return common.Hash{}, fmt.Errorf("cannot load absolute pre-state: %w", err)
	}
	hash, err := mipsevm.StateWitness(state).StateHash()
	if err != nil {
```
After
```go
return p.prestateCommitment, nil
	}
	_, hash, err := p.absolutePreState()
	if err != nil {
		return common.Hash{}, fmt.Errorf("cannot load absolute pre-state: %w", err)
	}
	p.prestateCommitment = hash
	return hash, nil
```

# Fix Pattern

Replace separate or timing-sensitive hash recomputation with a single canonical witness-encoding API, and obtain the hash at the correct execution stage.

## How It Was Fixed

The code was updated so `EncodeWitness()` supplies both witness bytes and hash, and callers use that result directly. In the shown proof-generation path, the state hash is now taken after the execution step, aligning the emitted hash with the post-step state.

# Why It Matters

1. Proof-related hashes are integrity-sensitive.

2. Hashing at the wrong execution point can produce the wrong commitment.

3. Using one canonical source reduces mismatch risk across callers.

4. The provided evidence does not show verifier bypass or concrete exploitability.

# Evidence Notes

The strongest evidence is the `cannon/cmd/run.go` hunk: a pre-step hash computation is removed from the shown proof path, and a post-step hash from `EncodeWitness()` appears after `stepFn(true)`. Supporting hunks in `cannon/cmd/witness.go`, `op-challenger/game/fault/trace/cannon/provider.go`, and `prestate.go` show API consolidation around returning witness bytes and hash together. The commit title references a proof post-state hash fix, but the supplied snippets do not prove attacker control, on-chain acceptance of invalid transitions, or user-impacting exploitation. Protocol security invariant: Witness-derived hashes used in Cannon proof and trace data should match the encoded VM state for the claimed execution point. Verification notes: The patch does not prove an on-chain verifier accepted invalid transitions before this change. The patch does not show a concrete attacker-controlled exploit path or funds impact. Most touched files reflect API alignment around witness encoding; the clearest invariant change is the proof hash selection in `cannon/cmd/run.go`. The evidence does not establish impact outside the Cannon fault-proof and challenger trace subsystem. Evidence supports a correctness fix in Cannon proof/trace hashing. Security relevance is plausible but not established from the provided snippets alone. Claims of exploitability or verifier bypass are not supported here. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incorrect-proof-state-hash`
Final impact type: `proof-integrity, state-integrity`
Final confidence: `medium`
Final tags: `fault-proof, state-commitment, witness-hash`

The patch is in a security-sensitive fault-proof/challenger path and directly corrects how proof-related state commitments are derived: the proof path now takes the hash after execution and multiple callers stop recomputing hashes from serialized witness bytes, instead using the canonical witness-plus-hash API. That supports retaining this as security hardening around proof integrity. The evidence does not, however, prove a concrete exploitable vulnerability, verifier bypass, or user-impacting attack, so this should not be elevated to a confirmed security fix.

## Security Evidence

1. `cannon/cmd/run.go` changes the proof path from hashing witness state before `stepFn(true)` to using a post-step hash.
2. The commit subject explicitly says `Fix post-state hash in proof`, matching the code change.
3. `witness.go`, `provider.go`, and `prestate.go` consolidate callers onto a canonical `EncodeWitness()` return value for both witness bytes and hash.
4. The touched subsystem is Cannon/fault-proof trace generation, where commitment correctness is security-sensitive.

## Missing Evidence

1. No proof that an invalid proof or claim was actually accepted before the patch.
2. No attacker-controlled input or exploit path is shown in the supplied diff.
3. No evidence of funds loss, consensus impact, or verifier bypass is provided.
4. The snippets do not show whether the bug was reachable outside internal tooling or only caused correctness failures.

## Claim Boundaries

1. Supported claim: the patch hardens proof/state-commitment correctness in a security-sensitive subsystem.
2. Supported claim: earlier code could derive a stale or non-canonical hash for proof-related data.
3. Not supported: a confirmed exploitable vulnerability existed.
4. Not supported: on-chain verification or protocol safety was demonstrably broken before this change.
