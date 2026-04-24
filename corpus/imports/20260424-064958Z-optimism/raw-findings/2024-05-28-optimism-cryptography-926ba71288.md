---
case_id: case_20240528_926ba71288
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
bug_class: input-validation
source_quality: medium
date: 2024-05-28
source_refs:
  - git:926ba71288ec558b2acc6b1b6399e66e73ab0fcc
  - "op-node/rollup/types.go:348"
  - "op-plasma/damgr.go:169"
  - "op-plasma/daserver.go:142"
  - "op-node/rollup/types.go:506"
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - data-availability
  - input-validation
  - protocol-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a correctness and hardening change around handling keccak versus generic Plasma commitments, but it does not establish a concrete vulnerability. The patch adds explicit config validation, propagates commitment type into runtime config, rejects mismatched commitment types during DA input retrieval, and updates DA server behavior for generic mode. From the supplied excerpts, this is best treated as security-relevant but unproven rather than a confirmed security fix.

## Observed Patch Facts

1. In `op-node/rollup/types.go`, the patch replaces `return nil` with `if cfg.PlasmaConfig.CommitmentType != plasma.KeccakCommitmentString {`.

2. In `op-plasma/damgr.go`, the patch adds `// If it's not the right commitment type, report it as an expired commitment in order...`.

3. In `op-plasma/daserver.go`, the patch replaces `comm := GenericCommitment(crypto.Keccak256Hash(input).Bytes())` with `var comm []byte`.

4. In `op-node/rollup/types.go`, the patch replaces `ChallengeWindow: c.PlasmaConfig.DAChallengeWindow,` with `t, err := plasma.CommitmentTypeFromString(c.PlasmaConfig.CommitmentType)`.

## Project Context

The changed code sits primarily in `op-node/rollup`, which anchors the finding in the `cryptography` area of the project. Historical context from `op-plasma/commitment_test.go`, `op-plasma/commitment.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-node/rollup/derive/plasma_data_source_test.go`, `op-node/rollup/derive/engine_queue_test.go`. The strongest project-level identifiers around this patch are `PlasmaConfig`, `CommitmentType`, `comm`, and `commitment`. Nearby tests or test-like files include `op-node/rollup/derive/fuzz_parsers_test.go`, `op-node/rollup/derive/test/random.go`.

## Before/After Behavior

Before the patch, the shown config validation accepted the legacy equality checks and then returned without any visible validation of allowed commitment-type values, without visible enforcement of address requirements by commitment mode, and without visible propagation of commitment type into the runtime Plasma config. The shown DA manager path also had no visible check that an incoming commitment's encoded type matched the configured runtime mode. The shown DA server path always derived the implicit commitment from a keccak hash. After the patch, config validation only accepts keccak or generic, forbids setting a non-keccak type through the legacy path, enforces different DAChallengeAddress requirements for keccak versus generic, parses and stores commitment type in the runtime config, rejects mismatched commitment types in GetInput, and changes the DA server's implicit commitment generation when generic mode is enabled.

# Root Cause

Incomplete and inconsistent enforcement of commitment-type configuration across configuration parsing, runtime configuration construction, DA input handling, and DA server commitment generation.

## Walkthrough

1. `validatePlasmaConfig` adds explicit checks for allowed commitment-type strings instead of relying only on legacy field consistency.

2. That function now also ties `DAChallengeAddress` requirements to the selected commitment mode and rejects non-keccak commitment type in the legacy-config path.

3. `GetOPPlasmaConfig()` now parses `PlasmaConfig.CommitmentType` and includes it in the returned runtime `plasma.Config`.

4. `DA.GetInput(...)` now compares the configured runtime commitment type against the incoming commitment's type before continuing.

5. On mismatch, `GetInput(...)` returns an error wrapped with `ErrExpiredChallenge`, which the code comment says causes the commitment to be skipped.

6. `DAServer.HandlePut` changes implicit commitment generation so generic mode does not always use the prior keccak-derived path.

7. The broader commit text and touched files show this change also includes feature/config plumbing for generic commitments, not only a bug fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-node/rollup/types.go | 348 | validates plasma config so only supported commitment types are accepted and the challenge-address requirement matches the selected type |
| op-node/rollup/types.go | 506 | parses and carries the configured commitment type into the plasma runtime config |
| op-plasma/damgr.go | 169 | rejects DA inputs whose commitment encoding/type does not match the node's configured plasma commitment mode |
| op-plasma/daserver.go | 142 | generates/stores commitments in a way that distinguishes generic-commitment mode from keccak-derived commitments |

## Code Snippets

## Snippet 1

Context: `op-node/rollup/types.go:348` (changes a sensitive control or state-update path)

Before
```go
return fmt.Errorf("LegacyDAResolveWindow (%v) !=  PlasmaConfig.DAResolveWindow (%v)", cfg.LegacyDAResolveWindow, cfg.PlasmaConfig.DAResolveWindow)
		}
	}
	return nil
```
After
```go
return fmt.Errorf("LegacyDAResolveWindow (%v) !=  PlasmaConfig.DAResolveWindow (%v)", cfg.LegacyDAResolveWindow, cfg.PlasmaConfig.DAResolveWindow)
		}
		if cfg.PlasmaConfig.CommitmentType != plasma.KeccakCommitmentString {
			return errors.New("Cannot set CommitmentType with the legacy config")
		}
	} else if cfg.PlasmaConfig != nil {
		if !(cfg.PlasmaConfig.CommitmentType == plasma.KeccakCommitmentString || cfg.PlasmaConfig.CommitmentType == plasma.GenericCommitmentString) {
			return fmt.Errorf("invalid commitment type: %v", cfg.PlasmaConfig.CommitmentType)
```

## Snippet 2

Context: `op-plasma/damgr.go:169` (changes a sensitive control or state-update path)

Before
```go
// the challenge status in the DataAvailabilityChallenge L1 contract.
func (d *DA) GetInput(ctx context.Context, l1 L1Fetcher, comm CommitmentData, blockId eth.BlockID) (eth.Data, error) {
	// If the challenge head is ahead in the case of a pipeline reset or stall, we might have synced a
	// challenge event for this commitment. Otherwise we mark the commitment as part of the canonical
```
After
```go
// the challenge status in the DataAvailabilityChallenge L1 contract.
func (d *DA) GetInput(ctx context.Context, l1 L1Fetcher, comm CommitmentData, blockId eth.BlockID) (eth.Data, error) {
	// If it's not the right commitment type, report it as an expired commitment in order to skip it
	if d.cfg.CommitmentType != comm.CommitmentType() {
		return nil, fmt.Errorf("invalid commitment type; expected: %v, got: %v: %w", d.cfg.CommitmentType, comm.CommitmentType(), ErrExpiredChallenge)
	}
	// If the challenge head is ahead in the case of a pipeline reset or stall, we might have synced a
	// challenge event for this commitment. Otherwise we mark the commitment as part of the canonical
```

## Snippet 3

Context: `op-plasma/daserver.go:142` (changes persisted or aggregate state handling)

Before
```go
if r.URL.Path == "/put" || r.URL.Path == "/put/" { // without commitment

		comm := GenericCommitment(crypto.Keccak256Hash(input).Bytes())
		if err = d.store.Put(r.Context(), comm.Encode(), input); err != nil {
			d.log.Error("Failed to store commitment to the DA server", "err", err, "comm", comm)
			w.WriteHeader(http.StatusInternalServerError)
			return
```
After
```go
if r.URL.Path == "/put" || r.URL.Path == "/put/" { // without commitment
		var comm []byte
		if d.useGenericComm {
			n, err := rand.Int(rand.Reader, big.NewInt(99999999999999))
			if err != nil {
				d.log.Error("Failed to generate commitment", "err", err)
				w.WriteHeader(http.StatusInternalServerError)
```

## Snippet 4

Context: `op-node/rollup/types.go:506` (changes a sensitive control or state-update path)

Before
```go
return plasma.Config{}, errors.New("missing DAResolveWindow")
	}
	return plasma.Config{
		DAChallengeContractAddress: c.PlasmaConfig.DAChallengeAddress,
		ChallengeWindow:            c.PlasmaConfig.DAChallengeWindow,
		ResolveWindow:              c.PlasmaConfig.DAResolveWindow,
	}, nil
}
```
After
```go
return plasma.Config{}, errors.New("missing DAResolveWindow")
	}
	t, err := plasma.CommitmentTypeFromString(c.PlasmaConfig.CommitmentType)
	if err != nil {
		return plasma.Config{}, err
	}
	return plasma.Config{
		DAChallengeContractAddress: c.PlasmaConfig.DAChallengeAddress,
```

# Fix Pattern

Tighten boundary validation and propagate an explicit mode value through runtime state so downstream code can reject incompatible inputs early.

## How It Was Fixed

The patch validates commitment type strings and their associated address semantics in config handling, parses commitment type into runtime Plasma config, adds a runtime type check before DA input processing, and updates DA server commitment generation to respect generic-commitment mode.

# Why It Matters

1. Prevents inconsistent Plasma configuration from being accepted silently.

2. Reduces the chance that one commitment mode is processed as another.

3. Makes runtime behavior match explicit configuration instead of implicit assumptions.

4. Improves correctness of the new generic-commitment support path.

# Evidence Notes

The strongest evidence is in `op-node/rollup/types.go` and `op-plasma/damgr.go`, which add validation and runtime rejection logic. `op-plasma/daserver.go` shows behavior changes for generic commitment generation, but that hunk is also part of adding generic-mode support rather than standalone proof of a vulnerability. The supplied material does not show attacker control, concrete exploit steps, consensus impact, or fund-loss impact. Because much of the commit is feature/config support for generic commitments, the security thesis should be downgraded to unclear. Protocol security invariant: Plasma DA must use one explicit commitment mode end to end. The configured commitment type must be a supported value, runtime config must carry that type, incoming commitments must match it, keccak mode requires a challenge-contract address, and generic mode must not use that address. Verification notes: The patch does not prove an externally reachable exploit primitive. The patch does not show confirmed consensus compromise or fund loss. It is not proven that mismatched commitment types were previously accepted all the way to unsafe state transition. Part of the change is feature/config support for generic commitments, so some diff surface may be compatibility work rather than a pure vulnerability fix. The evidence supports protocol hardening around commitment interpretation more clearly than a demonstrated exploit. Assessment is limited to the provided excerpts and commit metadata. The diff shows hardening and correctness checks, but not a demonstrated exploitable pre-patch condition. No claim of confirmed vulnerability impact is supported by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, data-availability, input-validation, protocol-hardening`

The supplied patch evidence supports retaining this as a security-hardening case, not a confirmed security bug fix. The changed code tightens validation and runtime enforcement around commitment-type handling in a security-sensitive blockchain data-availability path: only supported commitment types are accepted, challenge-address invariants are enforced by mode, the selected type is propagated into runtime config, and mismatched commitment types are rejected before further processing. That materially reduces risky ambiguity in commitment interpretation, but the excerpts do not prove a concrete exploitable pre-patch vulnerability or downstream security impact.

## Security Evidence

1. `validatePlasmaConfig` now rejects unsupported commitment types instead of accepting config and returning success.
2. The config validator enforces different `DAChallengeAddress` requirements for keccak versus generic commitments, tightening mode-specific invariants.
3. `GetOPPlasmaConfig()` now parses and carries `CommitmentType` into runtime plasma config rather than leaving it implicit.
4. `DA.GetInput(...)` now rejects commitment data whose runtime type does not match the configured commitment mode before continuing processing.
5. The affected path concerns blockchain commitment interpretation and DA challenge behavior, which is security-sensitive even without a demonstrated exploit.

## Missing Evidence

1. No evidence shows an attacker could previously exploit commitment-type confusion from an external boundary.
2. No proof that mismatched commitment types previously led to unsafe state transition, consensus failure, or acceptance of invalid data.
3. No demonstrated fund-loss, authorization bypass, or concrete integrity break tied to the pre-patch behavior.
4. Part of the commit is feature/config plumbing for generic commitments, which weakens a claim that the whole change is a pure vulnerability fix.

## Claim Boundaries

1. Supported claim: this commit hardens commitment-type validation and runtime consistency checks in a sensitive DA/commitment path.
2. Supported claim: the patch reduces ambiguity and misconfiguration risk between keccak and generic commitment modes.
3. Not supported: a confirmed exploitable vulnerability existed before this patch.
4. Not supported: the excerpts prove consensus compromise, fund loss, or attacker-driven invalid commitment acceptance.
