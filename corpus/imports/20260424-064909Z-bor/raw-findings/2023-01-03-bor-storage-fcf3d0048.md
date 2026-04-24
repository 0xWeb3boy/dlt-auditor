---
case_id: case_20230103_fcf3d0048
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2023-01-03
source_refs:
  - git:fcf3d00488e471bcaf069862c6d811490d77b53e
  - "core/forkid/forkid_test.go:275"
  - "core/forkid/forkid.go:174"
  - "core/forkid/forkid.go:219"
  - "core/forkid/forkid.go:267"
bug_class: peer-validation
impact_type:
  - network-integrity
confidence: medium
tags:
  - blockchain-core
  - p2p
  - forkid
  - peer-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a fork ID validation fix in ETH/LES peer compatibility checks. It corrects how local fork state is represented and compared, but the provided diff does not establish a concrete vulnerability beyond incorrect peer accept/reject behavior, so the security thesis remains unclear.

## Observed Patch Facts

1. In `core/forkid/forkid_test.go`, the patch replaces `{88888888, ID{Hash: checksumToBytes(0xf0afd0e3), Next: 88888888}, ErrLocalIncompatibl...` with `// TODO(karalabe): This testcase will fail once mainnet gets timestamped forks, make...`.

2. In `core/forkid/forkid.go`, the patch replaces `verify := func(index int, headOrTime uint64) error {` with `block, time := headfn()`.

3. In `core/forkid/forkid.go`, the patch replaces `head, time := headfn()` with `log.Error("Impossible fork ID validation", "id", id)`.

4. In `core/forkid/forkid.go`, the patch replaces `forks = append(forks, rule.Uint64())` with `forksByBlock = append(forksByBlock, rule.Uint64())`.

## Project Context

The changed code sits primarily in `core/forkid`, which anchors the finding in the `storage` area of the project. The strongest project-level identifiers around this patch are `forks`, `fork`, `head`, and `forksByBlock`.

## Before/After Behavior

Before, fork validation used a mixed fork list plus separate later block/time verification, and the code read local progression during different phases. After, the code keeps block-based and time-based fork schedules separate, snapshots local `(block,time)` once, and chooses the matching value when validating each fork transition.

# Root Cause

Fork ID validation did not cleanly separate block-based versus time-based fork transitions and did not clearly anchor the full decision to one local snapshot, which could lead to incorrect compatibility results.

## Walkthrough

1. `gatherForks` now collects block-based fork rules into `forksByBlock` and time-based rules into `forksByTime` instead of treating them as one generic schedule.

2. The code sorts the block and time schedules independently before validation.

3. `newFilter` now reads `block, time := headfn()` once before iterating the fork schedule.

4. During validation, the loop uses `block` for entries from the block-based portion and `time` for later time-based entries.

5. The tests were updated to pass explicit config and `(head,time)` inputs and retain rejection coverage for incompatible announced forks.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/forkid/forkid.go | 135 | fork ID compatibility filter used to decide whether remote peers match local fork state |
| core/forkid/forkid.go | 243 | fork schedule extraction and ordering, now split into block-based and time-based transitions |
| core/forkid/forkid_test.go | 269 | regression coverage for incompatible or stale peer announcements across fork transitions |

## Code Snippets

## Snippet 1

Context: `core/forkid/forkid_test.go:275` (changes signature or replay validation logic)

Before
```go
//
		// This case detects non-upgraded nodes with majority hash power (typical Ropsten mess).
		{88888888, ID{Hash: checksumToBytes(0xf0afd0e3), Next: 88888888}, ErrLocalIncompatibleOrStale},

		// Local is mainnet Byzantium. Remote is also in Byzantium, but announces Gopherium (non existing
		// fork) at block 7279999, before Petersburg. Local is incompatible.
		{7279999, ID{Hash: checksumToBytes(0xa00bc324), Next: 7279999}, ErrLocalIncompatibleOrStale},
	}
```
After
```go
//
		// This case detects non-upgraded nodes with majority hash power (typical Ropsten mess).
		//
		// TODO(karalabe): This testcase will fail once mainnet gets timestamped forks, make legacy chain config
		{params.MainnetChainConfig, 88888888, 0, ID{Hash: checksumToBytes(0xf0afd0e3), Next: 88888888}, ErrLocalIncompatibleOrStale},

		// Local is mainnet Byzantium. Remote is also in Byzantium, but announces Gopherium (non existing
		// fork) at block 7279999, before Petersburg. Local is incompatible.
```

## Snippet 2

Context: `core/forkid/forkid.go:174` (changes signature or replay validation logic)

Before
```go
//        information.
		//   4. Reject in all other cases.

		verify := func(index int, headOrTime uint64) error {
			// Found the first unpassed fork block, check if our current state matches
			// the remote checksum (rule #1).
			if sums[index] == id.Hash {
				// Fork checksum matched, check if a remote future fork block already passed
```
After
```go
//        information.
		//   4. Reject in all other cases.
		block, time := headfn()
		for i, fork := range forks {
			// Pick the head comparison based on fork progression
			head := block
			if i >= len(forksByBlock) {
				head = time
```

## Snippet 3

Context: `core/forkid/forkid.go:219` (changes signature or replay validation logic)

Before
```go
return ErrLocalIncompatibleOrStale
		}

		head, time := headfn()
		// Verify forks by block
		for i, fork := range forks {
			// If our head is beyond this fork, continue to the next (we have a dummy
			// fork of maxuint64 as the last item to always fail this check eventually).
```
After
```go
return ErrLocalIncompatibleOrStale
		}
		log.Error("Impossible fork ID validation", "id", id)
		return nil // Something's very wrong, accept rather than reject
```

## Snippet 4

Context: `core/forkid/forkid.go:267` (changes a consensus- or validator-sensitive branch)

Before
```go
forksByTime = append(forksByTime, rule.Uint64())
			} else {
				forks = append(forks, rule.Uint64())
			}
		}
	}

	sort.Slice(forks, func(i, j int) bool { return forks[i] < forks[j] })
```
After
```go
forksByTime = append(forksByTime, rule.Uint64())
			} else {
				forksByBlock = append(forksByBlock, rule.Uint64())
			}
		}
	}
	sort.Slice(forksByBlock, func(i, j int) bool { return forksByBlock[i] < forksByBlock[j] })
	sort.Slice(forksByTime, func(i, j int) bool { return forksByTime[i] < forksByTime[j] })
```

# Fix Pattern

Separate heterogeneous transition types and validate each against the correct snapshot of local state.

## How It Was Fixed

The patch split fork schedule extraction into block and time lists, sorted them independently, and changed fork ID validation to use a single `(block,time)` snapshot with the appropriate comparison axis for each fork. Test inputs were updated accordingly.

# Why It Matters

1. Prevents incorrect peer compatibility decisions when different fork transition types exist.

2. Makes validation behavior more deterministic by avoiding mixed or stale local-state reads.

3. Improves protocol correctness in ETH/LES fork ID handling.

# Evidence Notes

The strongest evidence is in `core/forkid/forkid.go`, where fork collection is split into `forksByBlock` and `forksByTime` and `headfn()` is snapshot once for validation. `core/forkid/forkid_test.go` was updated to exercise explicit `(head,time)` inputs. The diff supports a validation-correctness or hardening interpretation, not a proven exploit. Protocol security invariant: ETH/LES fork ID checks should evaluate a remote peer against the correct local fork progression dimension and a coherent local snapshot; block-based forks must be compared to local block height, time-based forks to local time, and the decision should not mix inconsistent reads. Verification notes: The patch does not prove remote code execution, memory corruption, or key compromise. The diff shows peer compatibility validation changes, not a demonstrated consensus-break exploit. The race appears to affect validation consistency; the exact real-world impact is not quantified in the patch. Resource-exhaustion or network-partition effects are plausible but not proven by the provided evidence. The patch changes peer validation logic, not memory safety or privilege boundaries. The evidence does not prove consensus compromise, code execution, or denial-of-service impact. Regression tests were adjusted to cover the updated validation model. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `peer-validation`
Final impact type: `network-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, p2p, forkid, peer-validation`

The patch is best read as security hardening in a network-exposed protocol gate, not as a proven exploitable vulnerability. The changed code controls ETH/LES fork ID compatibility decisions for remote peers, and the fix makes that validation deterministic and type-correct by separating block-based and time-based forks and snapshotting local state once before comparison. That clearly tightens a security-sensitive peer acceptance path, but the provided evidence does not prove concrete exploitation, consensus compromise, or denial-of-service impact.

## Security Evidence

1. `newFilter` is the peer compatibility filter for remote fork IDs, so it sits on an externally influenced validation path.
2. The patch separates `forksByBlock` and `forksByTime`, removing mixed validation across different transition types.
3. The code now snapshots `block, time := headfn()` once before validation, addressing inconsistent reads during peer checks.
4. Tests were updated to cover incompatible or stale remote fork announcements under the corrected model.

## Missing Evidence

1. No commit text or test demonstrates a concrete attack or user-triggerable exploit.
2. No evidence shows actual consensus failure, state corruption, privilege gain, or remote crash.
3. The provided diff does not quantify whether the prior bug caused false accepts, false rejects, or only rare race-driven inconsistency in production.

## Claim Boundaries

1. Do not classify this as state corruption; the evidence is about peer/fork validation correctness.
2. Do not claim a concrete security bug such as DoS or consensus bypass from the patch alone.
3. The strongest supported label is security hardening of peer validation logic, not a confirmed security fix.
