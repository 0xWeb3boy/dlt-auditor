---
case_id: case_20220908_1c787aa01d
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: input-validation
impact_type:
  - correctness-or-hardening
confidence: medium
source_quality: high
date: 2022-09-08
source_refs:
  - git:1c787aa01dbbffbd68ad6874fdc0c561f85937b5
  - "op-node/p2p/gossip.go:225"
  - "op-node/p2p/gossip.go:285"
  - "op-node/p2p/gossip.go:208"
  - "op-node/p2p/gossip.go:32"
tags:
  - blockchain-core
  - p2p
  - validator
  - input-validation
  - signature
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens the `op-node/p2p/gossip.go` block-gossip validator by rejecting undersized decoded messages and moving sequencer-signature verification ahead of later payload handling. The supplied evidence supports a security-relevant trust-boundary hardening against malformed or unauthenticated P2P input, but it does not by itself prove signature bypass, consensus impact, or a guaranteed process crash.

## Observed Patch Facts

1. In `op-node/p2p/gossip.go`, the patch replaces `// [REJECT] if the block encoding is not valid` with `// [REJECT] if the signature by the sequencer is not valid`.

2. In `op-node/p2p/gossip.go`, the patch replaces `// [REJECT] if the signature by the sequencer is not valid` with `// mark it as seen. (note: with concurrent validation more than 5 blocks may be marke...`.

3. In `op-node/p2p/gossip.go`, the patch adds `if outLen < minGossipSize {`.

4. In `op-node/p2p/gossip.go`, the patch adds `// minGossipSize is used to make sure that there is at least some data`.

## Project Context

The changed code sits primarily in `op-node/p2p`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-node/p2p/signer.go`, `op-node/p2p/host_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-node/p2p/signer.go`, `op-node/p2p/host_test.go`. The strongest project-level identifiers around this patch are `signature`, `signingHash`, `const`, and `valid`.

## Before/After Behavior

Before the change, `BuildBlocksValidator` decoded gossip data, split it into `signatureBytes` and `payloadBytes`, and visible payload processing occurred before the shown sequencer-signature verification block; there was also no lower-bound decoded-size check before the later `data[:65]` / `data[65:]` split. After the change, the validator rejects `outLen < minGossipSize` with `minGossipSize = 66`, then immediately computes `BlockSigningHash(cfg, payloadBytes)`, recovers the signer with `crypto.SigToPub`, and rejects messages whose recovered address does not match `cfg.P2PSequencerAddress` before further payload handling.

# Root Cause

The validator accepted attacker-controlled decoded gossip bytes without first enforcing the minimum structure required by later slicing and without authenticating the payload at the earliest trust boundary. That left malformed or unauthenticated input reaching deeper processing than necessary.

## Walkthrough

1. `BuildBlocksValidator` is the entry point for validating untrusted block-gossip messages.

2. The patch adds `minGossipSize = 66` with a comment stating it ensures there is enough data to validate the signature against.

3. After `snappy.DecodedLen(message.Data)`, the new code rejects any decoded message smaller than `minGossipSize`.

4. The validator still splits decoded bytes into `signatureBytes` and `payloadBytes`, but now the next visible step is `BlockSigningHash(cfg, payloadBytes)` followed by `crypto.SigToPub`.

5. If signature recovery fails or the recovered address differs from `cfg.P2PSequencerAddress`, the message is rejected immediately.

6. The old later location of the signature-verification block now proceeds to seen-block bookkeeping, showing that authentication was intentionally moved earlier.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-node/p2p/gossip.go | 190 | BuildBlocksValidator entry point for sequencer block gossip validation on untrusted pubsub messages |
| op-node/p2p/gossip.go | 208 | new minimum decoded-size rejection to require signature plus non-empty payload before slicing/processing |
| op-node/p2p/gossip.go | 225 | signature verification moved before further payload unmarshaling so only authenticated payload bytes proceed |
| op-node/p2p/signer.go | 25 | computes the signing hash over raw payload bytes that the validator now checks earlier |

## Code Snippets

## Snippet 1

Context: `op-node/p2p/gossip.go:225` (changes signature or replay validation logic)

Before
```go
signatureBytes, payloadBytes := data[:65], data[65:]

		// [REJECT] if the block encoding is not valid
		var payload eth.ExecutionPayload
```
After
```go
signatureBytes, payloadBytes := data[:65], data[65:]

		// [REJECT] if the signature by the sequencer is not valid
		signingHash := BlockSigningHash(cfg, payloadBytes)

		pub, err := crypto.SigToPub(signingHash[:], signatureBytes)
		if err != nil {
			log.Warn("invalid block signature", "err", err, "peer", id)
```

## Snippet 2

Context: `op-node/p2p/gossip.go:285` (changes signature or replay validation logic)

Before
```go
}

		// [REJECT] if the signature by the sequencer is not valid
		signingHash := BlockSigningHash(cfg, payloadBytes)

		pub, err := crypto.SigToPub(signingHash[:], signatureBytes)
		if err != nil {
			log.Warn("invalid block signature", "err", err, "peer", id)
```
After
```go
}

		// mark it as seen. (note: with concurrent validation more than 5 blocks may be marked as seen still,
		// but validator concurrency is limited anyway)
```

## Snippet 3

Context: `op-node/p2p/gossip.go:208` (changes a sensitive control or state-update path)

Before
```go
return pubsub.ValidationReject
		}

		res := msgBufPool.Get().(*[]byte)
```
After
```go
return pubsub.ValidationReject
		}
		if outLen < minGossipSize {
			log.Warn("rejecting undersized gossip payload")
			return pubsub.ValidationReject
		}

		res := msgBufPool.Get().(*[]byte)
```

## Snippet 4

Context: `op-node/p2p/gossip.go:32` (changes a sensitive control or state-update path)

Before
```go
const maxGossipSize = 1 << 20
const maxOutboundQueue = 256
const maxValidateQueue = 256
```
After
```go
const maxGossipSize = 1 << 20

// minGossipSize is used to make sure that there is at least some data
// to validate the signature against.
const minGossipSize = 66
const maxOutboundQueue = 256
const maxValidateQueue = 256
```

# Fix Pattern

Add explicit structural bounds checks and perform authentication before deeper parsing of network input.

## How It Was Fixed

The fix introduced a decoded-size floor check (`outLen < minGossipSize`) and moved sequencer-signature verification to immediately follow the `signatureBytes` / `payloadBytes` split. The validator now authenticates the raw payload bytes first and rejects invalid or undersized messages before later unmarshaling and bookkeeping.

# Why It Matters

1. Too-short gossip messages are rejected before unsafe downstream handling.

2. Unauthenticated payload bytes no longer reach deeper parsing first.

3. The change narrows attack surface at a public P2P validation boundary.

# Evidence Notes

The commit message explicitly describes a security fix and says signature verification was moved before further unmarshaling to guard against malformed payloads, plus a minimum-size check was added so a signature and payload are always present. The diff directly shows both changes in `op-node/p2p/gossip.go`, and `op-node/p2p/signer.go` confirms that `BlockSigningHash` authenticates the raw `payloadBytes`. What the supplied evidence does not establish is signature forgery, consensus corruption, or the exact runtime consequence of the old path beyond missing bounds validation and later authentication. Protocol security invariant: Untrusted block-gossip messages must be large enough to contain a 65-byte signature and a non-empty payload, and the payload bytes should be authenticated as coming from the configured sequencer before deeper decoding or bookkeeping. Verification notes: The patch does not prove a complete node crash path; it shows a panic-prone or unsafe malformed-input path unless surrounding code recovers. The evidence does not show signature forgery, key compromise, or acceptance of blocks without a valid sequencer signature. The patch does not demonstrate consensus-state corruption; the visible effect is at the P2P validation boundary. The exact downstream unmarshaling failure mode before the change is not fully shown, only that unauthenticated malformed payloads reached it. The evidence directly shows a new lower-bound check on decoded gossip length. The evidence directly shows signature verification moved earlier in the validator flow. The provided material does not prove a full pre-patch crash path or other exact exploit outcome. The provided material does not show acceptance of invalid sequencer signatures or consensus-state corruption. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final tags: `blockchain-core, p2p, validator, input-validation, signature`

The patch is on a security-sensitive P2P validation boundary and clearly hardens handling of untrusted gossip input by adding a minimum decoded-size check and moving sequencer-signature verification ahead of further payload processing. That supports retaining it as a security-hardening case. However, the supplied patch does not by itself prove a fully demonstrated exploit, signature bypass, or consensus compromise, so treating it as a concrete security-fix would be too strong from patch evidence alone.

## Security Evidence

1. `BuildBlocksValidator` validates untrusted pubsub/gossip messages on the P2P path.
2. A new `minGossipSize = 66` check rejects undersized decoded messages before the code splits `data[:65]` and `data[65:]`.
3. Signature recovery and sequencer-address validation were moved before further unmarshaling/handling of the payload.
4. The validator now rejects invalid signatures immediately with `pubsub.ValidationReject`.
5. The commit message explicitly says the change guards against malformed payloads and adds a security issue fix.

## Missing Evidence

1. No reproducer or test is shown demonstrating the exact pre-patch runtime failure or exploitability.
2. The evidence does not prove forged signatures were previously accepted.
3. The patch does not show concrete consensus impact, privilege gain, or a confirmed remote crash path.

## Claim Boundaries

1. Supported: the commit hardens a cryptographic/message-validation boundary against malformed or unauthenticated gossip input.
2. Supported: pre-patch code exposed a risky condition by processing deeper before early authentication and minimum-size rejection.
3. Not supported: a proven signature-bypass vulnerability, key compromise, or consensus corruption.
4. Not supported: a specific confirmed impact beyond security-relevant hardening and malformed-input risk reduction.
