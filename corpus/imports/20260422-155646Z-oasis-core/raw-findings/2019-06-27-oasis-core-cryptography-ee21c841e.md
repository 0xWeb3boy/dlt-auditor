---
case_id: case_20190627_ee21c841e
project: oasis-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2019-06-27
source_refs:
  - git:ee21c841e3332822a281938d0ceeab052de0f438
  - "go/beacon/tendermint/tendermint.go:75"
  - "go/tendermint/apps/beacon/beacon.go:174"
  - "go/scheduler/tendermint/tendermint.go:163"
  - "go/tendermint/apps/beacon/beacon.go:113"
bug_class: predictable-beacon-entropy
impact_type:
  - predictable-randomness
  - consensus-integrity-risk
confidence: medium
tags:
  - blockchain-core
  - beacon
  - entropy
  - debug-mode
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a security-relevant hardening interpretation around beacon entropy selection and wiring, but it does not establish a concrete pre-patch vulnerability or exploit path. The strongest grounded claim is that deterministic beacon behavior became an explicit debug mode with a production warning and that some alternate wiring paths were removed.

## Observed Patch Facts

1. In `go/beacon/tendermint/tendermint.go`, the patch replaces `// GetBeaconABCI gets the beacon for the provided epoch.` with `func (t *Backend) getCached(epoch epochtime.EpochTime) []byte {`.

2. In `go/tendermint/apps/beacon/beacon.go`, the patch replaces `func New(timeSource epochtime.Backend) abci.Application {` with `func New(timeSource epochtime.Backend, debugDeterministic bool) abci.Application {`.

3. In `go/scheduler/tendermint/tendermint.go`, the patch replaces `beacon beacon.Backend,` with `// Initialze and register the tendermint service component.`.

4. In `go/tendermint/apps/beacon/beacon.go`, the patch replaces `var entropy []byte` with `var entropyCtx, entropy []byte`.

## Project Context

The changed code sits primarily in `go/beacon/tendermint`, `go/beacon`, `go/tendermint/apps/beacon`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/tendermint/apps/epochtime_mock/epochtime_mock.go`, `go/tendermint/apps/scheduler/scheduler.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/tendermint/apps/scheduler/scheduler.go`, `go/tendermint/apps/roothash/roothash.go`. The strongest project-level identifiers around this patch are `beacon`, `timeSource`, `Backend`, and `epochtime`. Nearby tests or test-like files include `go/beacon/tests/tester.go`, `go/scheduler/tests/tester.go`.

## Before/After Behavior

Before the patch, the beacon app constructor took only `timeSource`, `onEpochChange` immediately followed the block-height-based entropy path shown in the snippet, the scheduler constructor accepted an injected `beacon.Backend` and rejected non-ABCI backends, and the Tendermint beacon backend exposed `GetBeaconABCI` that directly returned `state.GetBeacon()`. After the patch, the beacon app constructor takes `debugDeterministic`, stores it, and warns when deterministic mode is enabled; `onEpochChange` first switches on `app.debugDeterministic` and the shown production branch sets `entropyCtx = prodEntropyCtx`; the scheduler constructor no longer takes a beacon backend; and the direct ABCI getter is removed in favor of cached access.

# Root Cause

The code suggests that deterministic/debug beacon behavior and the canonical Tendermint beacon path were not previously separated as explicitly as they are after the patch. The scheduler also had a more flexible beacon-backend injection point. That supports a hardening narrative, but the provided excerpts do not prove that the older design was exploitable in production.

## Walkthrough

1. In `go/tendermint/apps/beacon/beacon.go`, the constructor changes from `New(timeSource epochtime.Backend)` to `New(timeSource epochtime.Backend, debugDeterministic bool)` and stores the new flag.

2. The same constructor logs `Determistic beacon entropy is NOT FOR PRODUCTION USE` when deterministic mode is enabled, which is direct evidence that this mode is considered unsafe for production.

3. In `go/tendermint/apps/beacon/beacon.go`, `onEpochChange` is reworked to branch on `app.debugDeterministic`; the shown non-debug branch explicitly sets `entropyCtx = prodEntropyCtx`.

4. In `go/scheduler/tendermint/tendermint.go`, the scheduler constructor drops the `beacon beacon.Backend` parameter and removes the ABCI-backend type check.

5. In `go/beacon/tendermint/tendermint.go`, the exported `GetBeaconABCI` helper that directly read beacon state is removed and replaced by a cached accessor.

6. The commit subject and file list mention `go/beacon/insecure/insecure.go`, but the supplied excerpts do not show its contents or exact removal semantics.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/beacon/insecure/insecure.go | 1 | Standalone insecure beacon backend appears to be removed from the module surface. |
| go/tendermint/apps/beacon/beacon.go | 109 | Epoch-change beacon generation now distinguishes production entropy from deterministic debug entropy. |
| go/tendermint/apps/beacon/beacon.go | 174 | Beacon application constructor now carries a `debugDeterministic` flag and logs that deterministic entropy is not for production use. |
| go/scheduler/tendermint/tendermint.go | 163 | Scheduler no longer depends on an injected ABCI beacon backend, reducing exposure to the removed insecure beacon path. |
| go/beacon/tendermint/tendermint.go | 75 | Direct ABCI beacon getter is removed in favor of cached canonical access, consistent with retiring the separate insecure beacon flow. |

## Code Snippets

## Snippet 1

Context: `go/beacon/tendermint/tendermint.go:75` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

// GetBeaconABCI gets the beacon for the provided epoch.
func (t *Backend) GetBeaconABCI(ctx *abci.Context, tree *iavl.MutableTree, epoch epochtime.EpochTime) ([]byte, error) {
	state := app.NewMutableState(tree)
	return state.GetBeacon()
}
```
After
```go
}

func (t *Backend) getCached(epoch epochtime.EpochTime) []byte {
	t.cached.RLock()
```

## Snippet 2

Context: `go/tendermint/apps/beacon/beacon.go:174` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// New constructs a new beacon application instance.
func New(timeSource epochtime.Backend) abci.Application {
	return &beaconApplication{
		logger:     logging.GetLogger("tendermint/beacon"),
		timeSource: timeSource,
	}
}
```
After
```go
// New constructs a new beacon application instance.
func New(timeSource epochtime.Backend, debugDeterministic bool) abci.Application {
	app := &beaconApplication{
		logger:             logging.GetLogger("tendermint/beacon"),
		timeSource:         timeSource,
		debugDeterministic: debugDeterministic,
	}
```

## Snippet 3

Context: `go/scheduler/tendermint/tendermint.go:163` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
func New(ctx context.Context,
	timeSource epochtime.Backend,
	beacon beacon.Backend,
	service service.TendermintService,
) (api.Backend, error) {
	// We can only work with an ABCI beacon.
	abciBeacon, ok := beacon.(tmbeacon.Backend)
	if !ok {
```
After
```go
func New(ctx context.Context,
	timeSource epochtime.Backend,
	service service.TendermintService,
) (api.Backend, error) {
	// Initialze and register the tendermint service component.
	app := app.New(timeSource)
	if err := service.RegisterApplication(app, []string{registryapp.AppName}); err != nil {
		return nil, err
```

## Snippet 4

Context: `go/tendermint/apps/beacon/beacon.go:113` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
func (app *beaconApplication) onEpochChange(ctx *abci.Context, epoch epochtime.EpochTime, req types.RequestBeginBlock) error {
	var entropy []byte

	height := app.state.BlockHeight()
	if height <= 1 {
		// No meaningful previous commit, use the block hash.  This isn't
		// fantastic, but it's only for one epoch.
```
After
```go
func (app *beaconApplication) onEpochChange(ctx *abci.Context, epoch epochtime.EpochTime, req types.RequestBeginBlock) error {
	var entropyCtx, entropy []byte

	switch app.debugDeterministic {
	case false:
		entropyCtx = prodEntropyCtx
```

# Fix Pattern

Make deterministic behavior explicit and debug-only, add a visible warning for it, and simplify consumers to use the canonical beacon path instead of alternate backend wiring or direct raw-state access.

## How It Was Fixed

The patch introduces an explicit `debugDeterministic` flag in the beacon application, warns when that mode is used, adjusts epoch-change logic to distinguish production entropy handling from deterministic behavior, removes the scheduler's injected beacon-backend dependency, and removes a direct ABCI beacon getter in the Tendermint backend.

# Why It Matters

1. It makes non-production deterministic behavior explicit instead of implicit.

2. It reduces alternate ways to wire or fetch beacon data outside the main path.

3. It suggests tighter separation between debug behavior and production entropy handling.

# Evidence Notes

Direct evidence comes from the changed signatures and snippets in `go/tendermint/apps/beacon/beacon.go`, `go/scheduler/tendermint/tendermint.go`, and `go/beacon/tendermint/tendermint.go`, plus the commit subject `go/beacon: Remove the insecure beacon`. The strongest security signal is the newly added warning that deterministic beacon entropy is not for production use. However, the provided material does not show the contents of `go/beacon/insecure/insecure.go`, does not prove that an insecure mode was reachable in production before the patch, and does not demonstrate a concrete attacker capability or protocol break. Protocol security invariant: Production beacon generation should use the canonical Tendermint beacon path and should not silently rely on deterministic or debug entropy behavior. Verification notes: The patch does not prove the insecure beacon was enabled in production deployments. The diff does not show a concrete attacker path for biasing or predicting beacon outputs. The downstream impact on scheduler or roothash safety is inferred from subsystem wiring, not demonstrated end-to-end here. Part of the change is also architectural simplification, so severity cannot be quantified from this patch alone. No diff content for `go/beacon/insecure/insecure.go` was provided. No end-to-end test or runtime evidence shows prior production use of deterministic entropy. The scheduler and backend wiring changes are real, but their security impact is inferred rather than demonstrated. The evidence supports hardening around randomness handling more strongly than a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `predictable-beacon-entropy`
Final impact type: `predictable-randomness, consensus-integrity-risk`
Final confidence: `medium`
Final tags: `blockchain-core, beacon, entropy, debug-mode, hardening`

The patch is best treated as security hardening. The commit explicitly removes an "insecure beacon," adds a `debugDeterministic` mode with a production warning, separates production entropy handling from deterministic behavior, and removes alternate backend wiring that could expose the insecure path. That is strong evidence of tightening security-sensitive randomness and consensus behavior. However, the provided excerpts do not prove a concrete exploitable pre-patch vulnerability or show that the insecure mode was reachable in production, so this should not be upgraded to a confirmed security fix.

## Security Evidence

1. Commit subject says the insecure beacon is being removed.
2. Beacon app now takes `debugDeterministic` explicitly instead of silently using one path.
3. New warning states deterministic beacon entropy is not for production use.
4. `onEpochChange` now branches between production entropy handling and deterministic behavior.
5. Scheduler constructor no longer accepts an injected beacon backend, reducing alternate wiring to non-canonical beacon implementations.
6. Direct ABCI beacon getter was removed in favor of cached canonical access.

## Missing Evidence

1. No diff content shows what `go/beacon/insecure/insecure.go` actually did before removal.
2. No proof that deterministic or insecure beacon behavior was reachable in production deployments.
3. No concrete attacker model or exploit path is shown in the patch excerpts.
4. No test excerpt demonstrates a security regression being prevented rather than an architectural cleanup.

## Claim Boundaries

1. Supported claim: the patch hardens beacon entropy handling and removes an explicitly insecure beacon path.
2. Supported claim: deterministic beacon behavior is now treated as debug-only and unsafe for production.
3. Not supported: a confirmed exploitable vulnerability existed before the patch.
4. Not supported: specific impacts such as client divergence or state representation flaws were the root issue.
5. Not supported: measurable exploitability, severity, or real-world exposure from the provided evidence alone.
