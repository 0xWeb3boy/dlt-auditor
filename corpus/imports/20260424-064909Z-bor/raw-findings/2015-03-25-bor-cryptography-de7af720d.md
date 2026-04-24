---
case_id: case_20150325_de7af720d
project: bor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2015-03-25
source_refs:
  - git:de7af720d6bb10b93d716fb0c6cf3ee0e51dc71a
  - "p2p/discover/udp.go:413"
  - "p2p/discover/udp.go:332"
  - "p2p/discover/udp.go:451"
  - "p2p/discover/udp.go:293"
bug_class: network-amplification
impact_type:
  - denial-of-service
confidence: high
tags:
  - p2p
  - network-protocol
  - udp
  - reflection-amplification
  - dos
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

This patch addresses a discovery-protocol UDP reflection/amplification issue. Before the change, a `findnode` request could reach the `neighbors` reply path without a prior bond check. After the change, unbonded senders are rejected with `errUnknownNode`, preventing that reply path.

## Observed Patch Facts

1. In `p2p/discover/udp.go`, the patch replaces `return fmt.Errorf("unknown type: %d", ptype)` with `return nil, fromID, hash, fmt.Errorf("unknown type: %d", ptype)`.

2. In `p2p/discover/udp.go`, the patch replaces `func (t *udp) send(to *Node, ptype byte, req interface{}) error {` with `func (t *udp) send(toaddr *net.UDPAddr, ptype byte, req interface{}) error {`.

3. In `p2p/discover/udp.go`, the patch replaces `t.mutex.Lock()` with `if t.db.get(fromID) == nil {`.

4. In `p2p/discover/udp.go`, the patch replaces `case reply := <-t.replies:` with `case r := <-t.gotreply:`.

## Project Context

The changed code sits primarily in `p2p/discover`, which anchors the finding in the `cryptography` area of the project. Historical context from `p2p/discover/udp_test.go`, `p2p/discover/table_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `p2p/discover/udp_test.go`, `p2p/discover/table_test.go`. The strongest project-level identifiers around this patch are `ptype`, `from`, `pending`, and `send`.

## Before/After Behavior

Before the patch, `findnode.handle` rejected expired requests but otherwise proceeded into node-table update and `neighbors` response generation. After the patch, it first checks `t.db.get(fromID)` and returns `errUnknownNode` when no bond exists, so unbonded `findnode` requests no longer trigger the larger reply.

# Root Cause

The discovery handler trusted an unbonded sender enough to process `findnode` and emit a larger UDP response, enabling spoofed-source reflection/amplification.

## Walkthrough

1. `decodePacket` recovers `fromID` and decodes the incoming discovery packet into a typed request.

2. Before the fix, `findnode.handle` moved from expiration check into `bumpOrAdd`, closest-node lookup, and `neighbors` sending.

3. The commit message and new inline comment both describe the abuse case: spoofed-source `findnode` causing a larger `neighbors` packet to be sent to a victim.

4. The new code adds `if t.db.get(fromID) == nil { return errUnknownNode }` before the prior processing path.

5. With that gate in place, only already bonded peers can reach the `neighbors` reply path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| p2p/discover/udp.go | 449 | Enforces the new security gate: reject `findnode` from unbonded senders before sending `neighbors`. |
| p2p/discover/udp.go | 391 | Decodes incoming discovery packets into typed requests so the bonded/unbonded handling can be applied to `findnode` requests. |
| p2p/discover/udp.go | 326 | Outbound UDP send path used for discovery replies; relevant because the fix prevents this path from being used as an amplification reflector. |
| p2p/discover/udp.go | 259 | Reply-tracking loop that supports request/response matching for discovery traffic, part of the bonding handshake machinery around the fix. |

## Code Snippets

## Snippet 1

Context: `p2p/discover/udp.go:413` (changes signature or replay validation logic)

Before
```go
req = new(neighbors)
	default:
		return fmt.Errorf("unknown type: %d", ptype)
	}
	if err := rlp.Decode(bytes.NewReader(sigdata[1:]), req); err != nil {
		return err
	}
	log.DebugDetailf("<<< %v %T %v\n", from, req, req)
```
After
```go
req = new(neighbors)
	default:
		return nil, fromID, hash, fmt.Errorf("unknown type: %d", ptype)
	}
	err = rlp.Decode(bytes.NewReader(sigdata[1:]), req)
	return req, fromID, hash, err
}
```

## Snippet 2

Context: `p2p/discover/udp.go:332` (changes signature or replay validation logic)

Before
```go
var headSpace = make([]byte, headSize)

func (t *udp) send(to *Node, ptype byte, req interface{}) error {
	b := new(bytes.Buffer)
	b.Write(headSpace)
```
After
```go
var headSpace = make([]byte, headSize)

func (t *udp) send(toaddr *net.UDPAddr, ptype byte, req interface{}) error {
	packet, err := encodePacket(t.priv, ptype, req)
	if err != nil {
		return err
	}
	log.DebugDetailf(">>> %v %T %v\n", toaddr, req, req)
```

## Snippet 3

Context: `p2p/discover/udp.go:451` (changes persisted or aggregate state handling)

Before
```go
return errExpired
	}
	t.mutex.Lock()
	e := t.bumpOrAdd(fromID, from)
	closest := t.closest(req.Target, bucketSize).entries
	t.mutex.Unlock()

	t.send(e, neighborsPacket, neighbors{
```
After
```go
return errExpired
	}
	if t.db.get(fromID) == nil {
		// No bond exists, we don't process the packet. This prevents
		// an attack vector where the discovery protocol could be used
		// to amplify traffic in a DDOS attack. A malicious actor
		// would send a findnode request with the IP address and UDP
		// port of the target as the source address. The recipient of
```

## Snippet 4

Context: `p2p/discover/udp.go:293` (changes a sensitive control or state-update path)

Before
```go
rearmTimeout()

		case reply := <-t.replies:
			// run matching callbacks, remove if they return false.
			for i := 0; i < len(pending); i++ {
				p := pending[i]
				if reply.from == p.from && reply.ptype == p.ptype && p.callback(reply.data) {
					p.errc <- nil
```
After
```go
rearmTimeout()

		case r := <-t.gotreply:
			var matched bool
			for i := 0; i < len(pending); i++ {
				if p := pending[i]; p.from == r.from && p.ptype == r.ptype {
					matched = true
					if p.callback(r.data) {
```

# Fix Pattern

Require prior protocol state before honoring a request that can trigger a larger response.

## How It Was Fixed

The fix adds a bond lookup in `findnode.handle` and drops unbonded requests early. The surrounding UDP refactoring appears to support the revised flow, but the security-relevant change directly evidenced here is the new bond gate before reply generation.

# Why It Matters

1. Blocks unverified `findnode` requests from eliciting `neighbors` replies.

2. Reduces the protocol's usefulness as a UDP reflector/amplifier.

3. Moves the check ahead of both state update and outbound response generation.

4. The commit explicitly notes the fix is incomplete with respect to replay and stricter source validation.

# Evidence Notes

Strong evidence comes from the commit body, the inline comment added next to the new `t.db.get(fromID)` check, and the before/after control flow in `findnode.handle`. The broader UDP changes are present, but the provided code most directly supports a discovery-protocol resource-control fix rather than a cryptographic flaw or complete spoofing prevention. Protocol security invariant: A node must not process `findnode` requests or send the larger `neighbors` response unless the requester already has a recorded bond. Verification notes: The patch proves mitigation of a reflection/amplification path, not complete elimination of all spoofing or replay risks. The commit itself says replay during the expiration window may still be possible. The evidence does not prove confidentiality, integrity, or code-execution impact. The patch does not show strict source-address validation beyond the bonding requirement. The bug is best classified as discovery-protocol resource abuse, not a generic cryptographic flaw. Supported by explicit security language in the commit message. Supported by a direct code change that rejects unbonded `findnode` requests. The evidence does not establish full protection against replay; the commit says replay-window risk remains. The evidence supports reflection/amplification mitigation, not broader integrity or confidentiality claims. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `network-amplification`
Final impact type: `denial-of-service`
Final confidence: `high`
Final tags: `p2p, network-protocol, udp, reflection-amplification, dos`

The supplied evidence supports a real security fix, not just maintenance or reliability work. The commit message explicitly describes a UDP reflection/amplification attack, and the patch adds a concrete gate in `findnode.handle` that rejects unbonded senders before the code updates state and sends the larger `neighbors` reply. That directly mitigates an externally triggerable abuse path capable of being used for DDoS amplification. The original phase-3 metadata is too misleading in classifying this as cryptography/input-validation rather than protocol-level reflection/amplification control.

## Security Evidence

1. Commit body explicitly states this fixes an attack vector for DDoS traffic amplification.
2. `findnode.handle` now checks `t.db.get(fromID) == nil` and returns `errUnknownNode` for unbonded senders.
3. Inline comment in the new code describes the spoofed-source `findnode` to larger `neighbors` reflection scenario.
4. The new gate is placed before reply generation, preventing the protocol from sending the larger response to unverified requesters.

## Missing Evidence

1. Patch does not prove complete protection against replay within the expiration window.
2. Patch does not show stricter source-address validation beyond the bonding requirement.
3. Evidence does not quantify exploitability or real-world impact beyond reflection/amplification abuse.

## Claim Boundaries

1. Supported claim: this mitigates a UDP reflection/amplification DDoS vector in discovery traffic.
2. Not supported: a cryptographic vulnerability classification.
3. Not supported: complete spoofing or replay prevention.
4. Not supported: confidentiality, integrity, or code-execution impact.
