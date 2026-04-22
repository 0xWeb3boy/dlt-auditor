---
case_id: case_20190506_bf949bbb0
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2019-05-06
source_refs:
  - git:bf949bbb09cdf4bd9c1a1702876abec2fd2676b9
  - "go/scheduler/trivial/trivial.go:294"
  - "go/worker/compute/worker.go:420"
  - "go/worker/compute/worker.go:173"
  - "go/scheduler/trivial/trivial.go:276"
bug_class: insufficient-input-validation
impact_type:
  - integrity-risk
confidence: medium
tags:
  - scheduler
  - tee
  - attestation
  - input-validation
  - node-selection
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a scheduler hardening change: epoch node-list construction now checks for unknown runtimes and adds a local TEE capability verification step before using TEE metadata. That is security-relevant in principle, but the record here does not establish that the pre-patch behavior was exploitable or even that equivalent validation was absent elsewhere, so this should not be treated as a confirmed vulnerability fix.

## Observed Patch Facts

1. In `go/scheduler/trivial/trivial.go`, the patch replaces `hw = caps.Hardware` with `var (`.

2. In `go/worker/compute/worker.go`, the patch replaces `// Create client gRPC server.` with `// Use existing gRPC server passed from the node.`.

3. In `go/worker/compute/worker.go`, the patch replaces `// Start client gRPC server.` with `for _, rt := range w.runtimes {`.

4. In `go/scheduler/trivial/trivial.go`, the patch replaces `// lists for the epoch. It is safe to do it this way as 'nodes' is` with `s.storageNodeLists[epoch] = []*node.Node{}`.

## Project Context

The changed code sits primarily in `go/scheduler/trivial`, `go/scheduler`, `go/worker/compute`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/worker/compute/handler.go`, `go/worker/compute/proxy.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/worker/compute/committee/group.go`, `go/worker/compute/committee/node.go`. The strongest project-level identifiers around this patch are `caps`, `runtime`, `Start`, and `epoch`. Nearby tests or test-like files include `go/worker/compute/tests/tester.go`, `go/scheduler/tests/tester.go`.

## Before/After Behavior

Before the patch, the shown scheduler path used capability-derived hardware classification via caps.Hardware without any local verification shown in that snippet. After the patch, the code defaults hardware to an invalid value, handles nil TEE capability data explicitly, verifies non-nil TEE capabilities with caps.Verify(ts), and skips unknown runtime IDs while rebuilding epoch node lists.

# Root Cause

The only grounded issue visible in the provided diff is that this scheduler path previously consumed runtime capability metadata with weaker local validation. The stronger claim that the system as a whole lacked attestation verification is not established from the provided evidence, because earlier registration-time or other validation is not shown.

## Walkthrough

1. The main substantive change is in the scheduler's updateNodeListLocked path, which rebuilds epoch node lists used for later worker or committee selection.

2. The patch adds initialization of storageNodeLists for the epoch and adds a guard that logs and skips nodes advertising an unknown runtime ID.

3. Within the per-runtime handling, the code now initializes hardware to an invalid value and reads TEE capability data through a local caps variable.

4. For non-nil TEE capability data, the scheduler now calls caps.Verify(ts) before trusting the capability object for hardware classification.

5. The evidence does not show the full post-verify control flow, so it is safer to describe this as local validation hardening rather than a proven fix for a concrete exploitable bug.

6. The separate worker gRPC server wiring change appears ancillary from the supplied record and is not supported as the root security change.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/scheduler/trivial/trivial.go | 265 | Builds per-epoch runtime node lists that feed scheduler committee/worker selection. |
| go/scheduler/trivial/trivial.go | 294 | Validates runtime TEE capabilities with `caps.Verify(ts)` before assigning a node to a TEE hardware bucket. |
| go/worker/compute/worker.go | 414 | Ancillary worker gRPC server wiring change; touched in the same commit but not the clearest security-relevant path. |

## Code Snippets

## Snippet 1

Context: `go/scheduler/trivial/trivial.go:294` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

				hw = caps.Hardware
			}

			nls[hw] = append(nls[hw], n)
		}
	}
```
After
```go
}

				var (
					hw   = node.TEEHardwareInvalid
					caps = rt.Capabilities.TEE
				)
				switch caps {
				case nil:
```

## Snippet 2

Context: `go/worker/compute/worker.go:420` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

		// Create client gRPC server.
		grpc, err := grpc.NewServerTCP("worker-client", workerCommonCfg.ClientPort, identity.TLSCertificate)
		if err != nil {
			return nil, err
		}
		w.grpc = grpc
```
After
```go
}

		// Use existing gRPC server passed from the node.
		newClientGRPCServer(grpc.Server(), w)
```

## Snippet 3

Context: `go/worker/compute/worker.go:173` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}()

	// Start client gRPC server.
	if err := w.grpc.Start(); err != nil {
		return err
	}

	// Start runtime services.
```
After
```go
}()

	// Start runtime services.
	for _, rt := range w.runtimes {
```

## Snippet 4

Context: `go/scheduler/trivial/trivial.go:276` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
m[id] = make(map[node.TEEHardware][]*node.Node)
	}

	// Build the per-node -> per-runtime -> per-TEE implementation node
	// lists for the epoch.  It is safe to do it this way as `nodes` is
	// already sorted in the appropriate order.
	for _, n := range nodes {
		for _, rt := range n.Runtimes {
```
After
```go
m[id] = make(map[node.TEEHardware][]*node.Node)
	}
	s.storageNodeLists[epoch] = []*node.Node{}

	// Build the per-node -> per-runtime -> per-TEE implementation node
	// lists for the epoch. It is safe to do it this way as `nodes` is
	// already sorted in the appropriate order.
	for _, n := range nodes {
```

# Fix Pattern

Add local validation and default-invalid handling at the point where scheduler eligibility state is derived, instead of trusting capability metadata as-is.

## How It Was Fixed

The scheduler node-list builder was tightened so that unknown runtimes are skipped, TEE hardware classification starts from an invalid default, and TEE capability objects are locally verified with caps.Verify(ts) before their metadata is used.

# Why It Matters

1. Scheduler eligibility should not be derived from unvetted runtime capability metadata.

2. Default-invalid handling reduces the chance that malformed or missing TEE data is treated as a normal hardware classification.

3. Skipping unknown runtimes avoids populating scheduler state from unsupported runtime advertisements.

4. The evidence supports defense-in-depth around node selection, but not a demonstrated end-to-end vulnerability.

# Evidence Notes

Direct evidence exists only for local changes in go/scheduler/trivial/trivial.go: a new unknown-runtime guard, initialization to TEEHardwareInvalid, explicit handling of nil TEE capability data, and a new caps.Verify(ts) call. The provided snippets do not show whether similar validation already existed earlier in the registration pipeline, do not prove what happens after verification failure beyond logging, and do not tie the worker gRPC change to a security flaw. Protocol security invariant: When building epoch node lists, the scheduler should only derive runtime and TEE classification from known runtime entries and capability data that passes local verification at the current timestamp; unknown runtimes and invalid or absent TEE capability data should not be treated as normal eligible inputs. Verification notes: The patch does not prove that an invalid attestation could definitely be exploited on a live network. The patch does not show whether some attestation checks already happened earlier during node registration. The evidence does not establish enclave compromise, key exfiltration, or remote code execution. The worker gRPC server reuse change is not shown here to fix an authentication or authorization flaw. No full diff is available, so the exact control flow after caps.Verify(ts) failure is not proven from the provided evidence. No evidence here rules out prior attestation checks during node registration or elsewhere. The security relevance is plausible, but exploitability and impact are not established from the supplied record. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insufficient-input-validation`
Final impact type: `integrity-risk`
Final confidence: `medium`
Final tags: `scheduler, tee, attestation, input-validation, node-selection`

The supplied patch shows a security-sensitive hardening change in the scheduler path: it stops trusting runtime TEE capability data as-is, defaults hardware classification to invalid, verifies TEE capabilities with `caps.Verify(ts)`, and skips unknown runtimes when building epoch node lists. That supports retaining this as a security-hardening case because the code is tightening validation at a trust boundary used for node eligibility and classification. However, the evidence does not prove a concrete exploitable vulnerability, does not show the full failure-handling path, and does not rule out equivalent validation elsewhere, so this should not be elevated to a confirmed security-fix.

## Security Evidence

1. Scheduler code now calls `caps.Verify(ts)` before using TEE capability metadata for hardware classification.
2. The new logic initializes TEE hardware to `TEEHardwareInvalid` instead of implicitly trusting capability data.
3. Unknown runtime IDs are explicitly detected, logged, and skipped when rebuilding scheduler node lists.
4. The changed path affects per-epoch node lists used for scheduler eligibility and node selection, which is a security-sensitive control point.

## Missing Evidence

1. No full diff shows the exact control flow after `caps.Verify(ts)` fails beyond logging context.
2. No evidence proves malformed or forged capability data was exploitable before the patch.
3. No evidence shows whether TEE capabilities were already validated earlier during registration or another pipeline stage.
4. The worker gRPC server wiring changes are not tied by the provided evidence to an authentication, authorization, or exposure flaw.

## Claim Boundaries

1. Supported: the patch adds local validation and safer default handling before scheduler logic consumes TEE capability metadata.
2. Supported: the patch rejects unknown runtimes from this scheduler state-building path.
3. Not supported: the pre-patch system definitely allowed an attacker to bypass attestation checks end-to-end.
4. Not supported: this commit proves a concrete exploit, compromise, or remotely triggerable vulnerability.
5. Not supported: the worker gRPC refactor is itself a demonstrated security fix from the supplied evidence.
