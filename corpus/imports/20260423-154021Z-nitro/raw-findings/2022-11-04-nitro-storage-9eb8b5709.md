---
case_id: case_20221104_9eb8b5709
project: nitro
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2022-11-04
source_refs:
  - git:9eb8b5709e3e9bdc6740d3a44a14b7c57c4d08bc
  - "arbnode/node.go:982"
  - "arbnode/node.go:971"
  - "validator/stateless_block_validator.go:504"
  - "validator/staker.go:168"
bug_class: preimage-source-mixing
impact_type:
  - validation-integrity
confidence: medium
tags:
  - validator
  - preimage
  - stateless-validation
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The diff shows a consistency hardening change in validator wiring and preimage sourcing, but the provided evidence does not establish a concrete vulnerability. The strongest grounded change is that the stateless preimage resolver stops consulting live trie state via `db.Node(hash)` and the staker path is rewired to use handles owned by `statelessBlockValidator`.

## Observed Patch Facts

1. In `arbnode/node.go`, the patch replaces `fatalErrChan,` with `} else {`.

2. In `arbnode/node.go`, the patch replaces `if !foundMachines && blockValidatorConf.Enable {` with `if foundMachines {`.

3. In `validator/stateless_block_validator.go`, the patch replaces `// Check if it's part of the state trie` with `datasource := "code"`.

4. In `validator/staker.go`, the patch replaces `val, err := NewL1Validator(client, wallet, validatorUtilsAddress, callOpts, l2Blockch...` with `val, err := NewL1Validator(client, wallet, validatorUtilsAddress, callOpts,`.

## Project Context

Historical context from `validator/block_validator.go`, `arbnode/api.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `validator/block_validator.go`, `arbnode/api.go`. The strongest project-level identifiers around this patch are `codeKey`, `statelessBlockValidator`, `hash`, and `append`.

## Before/After Behavior

Before the patch, `StatelessBlockValidator.NewMachinePreimageResolver` could fall back to `db.Node(hash)` before trying a code-hash lookup, and `NewStaker` passed separate blockchain/DA/inbox/streamer handles into `NewL1Validator`. After the patch, the resolver goes from recorded preimages directly to a code-hash lookup in `db.DiskDB()`, and `NewStaker` passes the corresponding handles from `statelessBlockValidator`. `arbnode/node.go` also separates stateless-validator construction from later enablement checks.

# Root Cause

The supplied diff supports a prior mismatch between the stateless validator's intended execution context and other available runtime state sources: missing preimages could be reconstructed from live trie state, and the staker path was not forced to use the stateless validator's own handles.

## Walkthrough

1. In `validator/stateless_block_validator.go`, the resolver previously checked `preimages[hash]`, then called `db.Node(hash)`, and only after failure tried a code-hash lookup.

2. After the patch, that `db.Node(hash)` path is removed from the shown hunk, and the resolver proceeds directly to a `rawdb.CodePrefix` lookup in `db.DiskDB()`.

3. In `validator/staker.go`, `NewStaker` previously called `NewL1Validator` with separately supplied `l2Blockchain`, `das`, `inboxTracker`, and `txStreamer` values.

4. After the patch, `NewStaker` instead passes `statelessBlockValidator.blockchain`, `.daService`, `.inboxTracker`, and `.streamer` to `NewL1Validator`.

5. In `arbnode/node.go`, creation of `statelessBlockValidator` is gated on `foundMachines`, while validator enablement checks are handled later; the removed `fatalErrChan` argument appears alongside that refactor but is not shown to affect security properties.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| validator/stateless_block_validator.go | 489 | preimage resolver for stateless validation and challenge witness generation |
| validator/staker.go | 153 | staker wiring into L1 validator using the stateless validator's execution context |
| arbnode/node.go | 965 | node setup for stateless validator construction and validator-path selection |

## Code Snippets

## Snippet 1

Context: `arbnode/node.go:982` (changes a consensus- or validator-sensitive branch)

Before
```go
daReader,
			&config.Get().BlockValidator,
			fatalErrChan,
		)
		if err != nil {
			return nil, err
		}
```
After
```go
daReader,
			&config.Get().BlockValidator,
		)
		if err != nil {
			return nil, err
		}
	} else {
		if blockValidatorConf.Enable || config.Validator.Enable {
```

## Snippet 2

Context: `arbnode/node.go:971` (changes a sensitive control or state-update path)

Before
```go
var statelessBlockValidator *validator.StatelessBlockValidator

	if !foundMachines && blockValidatorConf.Enable {
		return nil, fmt.Errorf("failed to find machines %v", machinesPath)
	} else if !foundMachines {
		log.Warn("Failed to find machines", "path", machinesPath)
	} else {
		statelessBlockValidator, err = validator.NewStatelessBlockValidator(
```
After
```go
var statelessBlockValidator *validator.StatelessBlockValidator

	if foundMachines {
		statelessBlockValidator, err = validator.NewStatelessBlockValidator(
			nitroMachineLoader,
```

## Snippet 3

Context: `validator/stateless_block_validator.go:504` (changes signature or replay validation logic)

Before
```go
return preimage, nil
		}
		// Check if it's part of the state trie
		preimage, err := db.Node(hash)
		if err != nil {
			// Check if it's a code hash
			codeKey := append([]byte{}, rawdb.CodePrefix...)
			codeKey = append(codeKey, hash.Bytes()...)
```
After
```go
return preimage, nil
		}
		// Check if it's a code hash
		codeKey := append([]byte{}, rawdb.CodePrefix...)
		codeKey = append(codeKey, hash.Bytes()...)
		datasource := "code"
		preimage, err := db.DiskDB().Get(codeKey)
		if err != nil {
```

## Snippet 4

Context: `validator/staker.go:168` (changes a consensus- or validator-sensitive branch)

Before
```go
}
	client := l1Reader.Client()
	val, err := NewL1Validator(client, wallet, validatorUtilsAddress, callOpts, l2Blockchain, das, inboxTracker, txStreamer, blockValidator)
	if err != nil {
		return nil, err
	}
	return &Staker{
		L1Validator:         val,
```
After
```go
}
	client := l1Reader.Client()
	val, err := NewL1Validator(client, wallet, validatorUtilsAddress, callOpts,
		statelessBlockValidator.blockchain, statelessBlockValidator.daService, statelessBlockValidator.inboxTracker, statelessBlockValidator.streamer, blockValidator)
	if err != nil {
		return nil, err
	}
	return &Staker{
```

# Fix Pattern

Remove fallback reads from alternate live state in a supposedly self-contained validation path, and route dependent components through a single owning validator context.

## How It Was Fixed

The patch removes the shown trie-node fallback from the stateless preimage resolver, keeps explicit code-hash lookup, rewires staker construction to use the `statelessBlockValidator`'s own context objects, and adjusts node setup so stateless-validator construction is decoupled from later mode checks.

# Why It Matters

1. It reduces mixing between recorded stateless-validation inputs and live runtime state.

2. It makes the staker path use the same validator-owned context instead of separately passed handles.

3. It may prevent inconsistency in witness reconstruction, but the supplied evidence does not prove exploitability or a past failure mode.

# Evidence Notes

Primary evidence is limited to `validator/stateless_block_validator.go`, `validator/staker.go`, and `arbnode/node.go`. Those hunks support a consistency/hardening interpretation. They do not, by themselves, prove invalid-block acceptance, challenge bypass, consensus failure, or attacker reachability. The `fatalErrChan` removal is not supported as a security change by the provided snippets. Protocol security invariant: Stateless validation should use the preimages and service handles associated with the stateless validator itself, rather than mixing in other runtime state sources. Verification notes: The patch does not prove an attacker could force acceptance of an invalid block or win an on-chain challenge. The diff does not demonstrate a confirmed consensus split; it shows a consistency fix in validator/challenge data sourcing. Removal of `fatalErrChan` from stateless block-validator construction appears operational from the provided evidence, not independently security-relevant. The evidence does not show whether the prior live-DB trie lookup was adversarially reachable or mainly caused honest-validator correctness failures. The removal of `db.Node(hash)` from the shown resolver path is directly supported by the diff. The rewiring of `NewStaker` to use `statelessBlockValidator` fields is directly supported by the diff. The downstream behavior when a required non-code preimage is missing is not fully shown in the provided excerpt. No supplied evidence demonstrates an exploitable vulnerability rather than correctness or hardening work. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `preimage-source-mixing`
Final impact type: `validation-integrity`
Final confidence: `medium`
Final tags: `validator, preimage, stateless-validation, hardening`

The patch is in a security-sensitive validator/challenge path and clearly tightens how stateless validation sources preimages and dependent state handles. The strongest evidence is the removal of the fallback from recorded preimages to live trie-node lookup, plus rewiring the staker to use the stateless validator's own blockchain/DA/inbox/streamer context. That supports a security-hardening interpretation around validation integrity and witness consistency. However, the diff alone does not prove a concrete exploitable vulnerability, attacker control, invalid-block acceptance, or a demonstrated consensus break, so this should not be labeled a confirmed security fix.

## Security Evidence

1. The stateless preimage resolver stops consulting live trie state via `db.Node(hash)` and instead goes from recorded preimages directly to code-hash lookup.
2. The commit message explicitly says the preimage resolver now assumes everything was recorded, indicating an intentional tightening of the stateless model.
3. `NewStaker` is rewired to pass `statelessBlockValidator`'s own blockchain/DA/inbox/streamer handles into `NewL1Validator`, reducing context mixing in validator logic.
4. The touched code is validator/challenge infrastructure where input-source consistency is security-sensitive.

## Missing Evidence

1. No proof that an attacker could influence the missing-preimage path or exploit the old live-state fallback.
2. No evidence that the old behavior caused invalid block acceptance, challenge bypass, fund loss, or consensus divergence.
3. No test evidence here showing a prior security failure mode versus an internal correctness mismatch.
4. The `fatalErrChan` change appears operational, not independently security-relevant from the shown patch.

## Claim Boundaries

1. Treat this as hardening of stateless validation integrity, not a confirmed exploitable bug fix.
2. Do not claim state corruption, consensus split, or challenge compromise from this diff alone.
3. Do not attribute security significance to the `fatalErrChan` removal based on the provided evidence.
4. The supported claim is limited to removing live-state fallback and aligning validator consumers to the stateless validator's owned context.
