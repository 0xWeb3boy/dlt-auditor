---
case_id: case_20260218_bff847a3d
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
bug_class: resource-exhaustion
confidence: low
source_quality: high
date: 2026-02-18
source_refs:
  - git:bff847a3dfc051a7679adf8dccfdfc58a972700f
  - "eth/backend.go:320"
  - "core/blockchain_test.go:4988"
  - "core/blockchain.go:4206"
  - "core/blockchain.go:4290"
impact_type:
  - denial-of-service
tags:
  - blockchain-core
  - resource-exhaustion
  - consensus
  - validator
  - availability
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a bounded-work hardening/fix in Bor's background pending-header verification path, motivated by possible OOM from large header reads. It does not establish a confirmed security vulnerability, because the visible hunks do not show a proven attacker-controlled trigger or fully show the claimed cap logic.

## Observed Patch Facts

1. In `eth/backend.go`, the patch replaces `// check if Parallel EVM is enabled` with `// Wire MilestoneFetcher so verifyPendingHeaders queries Heimdall directly.`.

2. In `core/blockchain_test.go`, the patch replaces `// Create a mock validator where finalized block equals current head` with `cfg := DefaultConfig()`.

3. In `core/blockchain.go`, the patch replaces `if bc.checker == nil {` with `if bc.milestoneFetcher == nil {`.

4. In `core/blockchain.go`, the patch replaces `// Rewind to the last valid block` with `if lastValidNumber < headNumber {`.

## Project Context

Historical context from `core/headerchain.go`, `core/headerchain_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/txindexer.go`, `core/headerchain.go`. The strongest project-level identifiers around this patch are `header`, `lastValidNumber`, `Warn`, and `chain`. Nearby tests or test-like files include `eth/tracers/internal/tracetest/supply_test.go`, `eth/tracers/internal/tracetest/prestate_test.go`.

## Before/After Behavior

Before the change, the background header-verification loop was started based on checker availability, and the backend evidence shown here did not wire a dedicated milestone fetcher into this path. After the change, `eth/backend.go` wires `MilestoneFetcher` from Heimdall, `startHeaderVerificationLoop` refuses to run without that fetcher, and `verifyPendingHeaders` fetches `milestoneEndBlock`, returns if the head is not past that milestone, and starts scanning from `milestoneEndBlock + 1`. The commit text says this path was capped to `default span length + 1`, but the actual cap enforcement is not visible in the supplied code excerpts.

# Root Cause

The background verifier built its work from the distance between a milestone boundary and the current head and materialized headers into memory before batch verification. The supplied evidence suggests that this path lacked a sufficiently explicit bounded-work control and relied on weaker configuration/startup assumptions than the patched version.

## Walkthrough

1. `eth/backend.go` now provides `options.MilestoneFetcher` by calling `borEngine.HeimdallClient.FetchMilestone(ctx)` and returning `m.EndBlock`.

2. `core/blockchain.go` changes the startup gate for the background verifier so it skips the loop if `bc.milestoneFetcher` is not set.

3. In `verifyPendingHeaders`, the code fetches `milestoneEndBlock` with a timeout and returns early when the current head is at or before that milestone.

4. The same function derives `startBlock := milestoneEndBlock + 1`, allocates a header slice for the range from `startBlock` to head, and passes those headers to `bc.engine.VerifyHeaders`.

5. `core/blockchain_test.go` is updated to set `cfg.MilestoneFetcher`, showing regression coverage for the new configuration path.

6. The commit subject/body describe the intended fix as capping this verification work, but the provided hunks do not include the explicit numeric cap logic.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/blockchain.go | 4236 | Background Bor pending-header verification path that computes the range from milestone end block to current head and batches headers for `VerifyHeaders`; this is the OOM-prone read/allocation path being constrained. |
| core/blockchain.go | 4206 | Startup gate for the header verification loop; now depends on a milestone fetcher so the verifier only runs when it has the correct milestone source. |
| eth/backend.go | 320 | Wires `MilestoneFetcher` to Heimdall and returns the milestone `EndBlock`, defining the verifier's trusted lower bound for header scanning. |
| core/blockchain_test.go | 4988 | Regression coverage for milestone-at-head and related verifier behavior after the cap/refactor. |

## Code Snippets

## Snippet 1

Context: `eth/backend.go:320` (changes a sensitive control or state-update path)

Before
```go
options.Checker = checker

	// check if Parallel EVM is enabled
	// if enabled, use parallel state processor
```
After
```go
options.Checker = checker

	// Wire MilestoneFetcher so verifyPendingHeaders queries Heimdall directly.
	if borEngine, ok := eth.engine.(*bor.Bor); ok && borEngine.HeimdallClient != nil {
		options.MilestoneFetcher = func(ctx context.Context) (uint64, error) {
			m, err := borEngine.HeimdallClient.FetchMilestone(ctx)
			if err != nil {
				return 0, err
```

## Snippet 2

Context: `core/blockchain_test.go:4988` (changes signature or replay validation logic)

Before
```go
_, blocks, _ := GenerateChainWithGenesis(genesis, engine, 5, nil)

		// Create a mock validator where finalized block equals current head
		mockValidator := &mockChainValidator{
			hasMilestone:    true,
			milestoneNumber: 5, // Same as head
			milestoneHash:   blocks[4].Hash(),
		}
```
After
```go
_, blocks, _ := GenerateChainWithGenesis(genesis, engine, 5, nil)

		cfg := DefaultConfig()
		cfg.MilestoneFetcher = func(ctx context.Context) (uint64, error) {
			return 5, nil // milestone at head
		}
		chain, err := NewBlockChain(rawdb.NewMemoryDatabase(), genesis, engine, cfg)
		if err != nil {
```

## Snippet 3

Context: `core/blockchain.go:4206` (changes a consensus- or validator-sensitive branch)

Before
```go
// invalid headers are detected.
func (bc *BlockChain) startHeaderVerificationLoop() {
	if bc.checker == nil {
		log.Warn("chain validator service is not set, skipping header verification loop")
		return // No checker available
	}
```
After
```go
// invalid headers are detected.
func (bc *BlockChain) startHeaderVerificationLoop() {
	if bc.milestoneFetcher == nil {
		log.Warn("milestone fetcher is not set, skipping header verification loop")
		return
	}
```

## Snippet 4

Context: `core/blockchain.go:4290` (changes a sensitive control or state-update path)

Before
```go
log.Warn("Invalid header detected during background verification",
					"number", header.Number.Uint64(), "hash", header.Hash(), "err", err)
				// Rewind to the last valid block
				if lastValidNumber < currentHead.Number.Uint64() {
					log.Warn("Rewinding chain due to invalid header",
						"from", currentHead.Number.Uint64(), "to", lastValidNumber)
					if err := bc.SetHead(lastValidNumber); err != nil {
						log.Error("Failed to rewind chain", "err", err)
```
After
```go
log.Warn("Invalid header detected during background verification",
					"number", header.Number.Uint64(), "hash", header.Hash(), "err", err)

				if lastValidNumber < headNumber {
					dropCount := int64(headNumber - lastValidNumber)

					log.Warn("Rewinding chain due to an invalid header",
						"from", headNumber, "to", lastValidNumber, "drop", dropCount)
```

# Fix Pattern

Constrain a background validation loop with an explicit checkpoint source and add tests for the new bounded-start behavior.

## How It Was Fixed

The patch wires a dedicated `MilestoneFetcher` from Heimdall into blockchain setup, requires that fetcher before starting the background header-verification loop, and derives verification from the fetched milestone end block. Tests were updated to configure the new fetcher path. The commit metadata also claims an added cap for `verifyPendingHeaders`, but that specific cap is not shown in the supplied excerpts.

# Why It Matters

1. Reduces the chance that background header verification scales with an excessively large pending range.

2. Makes the verifier depend on a direct milestone source instead of looser startup conditions.

3. Improves robustness of a consensus-adjacent maintenance path.

4. The evidence supports availability hardening, but not a proven exploitable security bug.

# Evidence Notes

Strongest support comes from the commit subject `fix(core): cap verifyPendingHeaders to prevent OOM from unbounded header reads (#2057)` and body entries about capping verification and using milestone end block as the start block. The visible code supports milestone-fetcher plumbing, loop gating on `bc.milestoneFetcher`, fetching `milestoneEndBlock`, and deriving `startBlock := milestoneEndBlock + 1`. However, the excerpts do not show the actual `default span length + 1` cap logic, and they do not demonstrate remote triggerability, a validation bypass, or state corruption. The safer classification is resource-exhaustion-related hardening/fix with unproven security exploitability. Protocol security invariant: Background pending-header verification should run over a bounded post-milestone range derived from a trustworthy milestone boundary, so routine verification does not expand into unbounded memory or CPU work as the head advances. Verification notes: The patch does not prove that an external peer can directly force stale Heimdall milestone data or trigger the OOM remotely. The diff does not show any header-authentication, signature, or hash-validation bypass. The patch evidence supports an availability failure mode, not consensus/state corruption. The exact pre-patch memory growth and reliability of OOM are not quantified by the provided hunks alone. Visible hunks support the milestone-fetcher refactor and verifier startup gating. Visible hunks support that verification now begins from fetched milestone end block plus one. The claimed explicit cap is only stated in commit metadata, not shown in the provided code excerpts. No provided evidence proves external attacker control, consensus bypass, or state-corruption impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `denial-of-service`
Final tags: `blockchain-core, resource-exhaustion, consensus, validator, availability`

The supplied patch and commit metadata support keeping this as a security-hardening case focused on availability. The commit explicitly says it prevents OOM from unbounded header reads, and the code evidence shows the pending-header verification path is tightened to use a milestone-derived starting point and is disabled when that fetcher is unavailable. That materially reduces risk in a consensus-sensitive verification loop, but the provided hunks do not show the claimed explicit cap or prove attacker-controlled remote triggerability, so this should not be elevated to a confirmed security fix.

## Security Evidence

1. Commit subject states prevention of OOM from unbounded header reads.
2. `verifyPendingHeaders` now derives `startBlock` from `milestoneEndBlock + 1` instead of an implicitly broader range.
3. The background verifier now requires `milestoneFetcher`, tightening when the verification loop can run.
4. The changed path is consensus/validator-adjacent and processes batches of headers in memory.
5. Tests were updated to exercise the milestone-fetcher-based behavior.

## Missing Evidence

1. No visible hunk shows the claimed numeric cap at `default span length + 1`.
2. No proof that an external peer can force the unbounded read condition remotely.
3. No quantitative evidence of pre-patch memory growth or reproducible OOM in the supplied excerpts.
4. No evidence of integrity, authentication, or consensus-bypass impact beyond availability risk.

## Claim Boundaries

1. Supported claim: the patch hardens a header-verification path against excessive work and memory use.
2. Supported claim: the change is availability-oriented in a security-sensitive subsystem.
3. Not supported: a confirmed exploitable vulnerability with demonstrated attacker control.
4. Not supported: the original `remote-dos` specificity from patch evidence alone.
