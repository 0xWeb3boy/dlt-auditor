---
case_id: case_20150325_de7af720d
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: high
source_quality: high
date: 2015-03-25
source_refs:
  - git:de7af720d6bb10b93d716fb0c6cf3ee0e51dc71a
  - "p2p/discover/udp.go:413"
  - "p2p/discover/udp.go:332"
  - "p2p/discover/udp.go:451"
  - "p2p/discover/udp.go:293"
bug_class: udp-reflection-amplification
impact_type:
  - ddos-amplification
tags:
  - go-ethereum
  - p2p
  - discovery
  - udp
  - ddos
  - reflection-amplification
  - node-bonding
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a documented UDP discovery amplification vector in which an unbonded findnode request could cause the node to send a larger neighbors response to the packet source address, enabling spoofed-source reflection toward a victim.

## Observed Patch Facts

1. In `p2p/discover/udp.go`, the patch replaces `return fmt.Errorf("unknown type: %d", ptype)` with `return nil, fromID, hash, fmt.Errorf("unknown type: %d", ptype)`.

2. In `p2p/discover/udp.go`, the patch replaces `func (t *udp) send(to *Node, ptype byte, req interface{}) error {` with `func (t *udp) send(toaddr *net.UDPAddr, ptype byte, req interface{}) error {`.

3. In `p2p/discover/udp.go`, the patch replaces `t.mutex.Lock()` with `if t.db.get(fromID) == nil {`.

4. In `p2p/discover/udp.go`, the patch replaces `case reply := <-t.replies:` with `case r := <-t.gotreply:`.

## Project Context

The changed code sits primarily in `p2p/discover`, which anchors the finding in the `cryptography` area of the project. Historical context from `p2p/discover/udp_test.go`, `p2p/discover/table_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `p2p/discover/udp_test.go`, `p2p/discover/table_test.go`. The strongest project-level identifiers around this patch are `ptype`, `from`, `pending`, and `send`.

## Before/After Behavior

Before the patch, findnode handling rejected expired requests but then updated or added the sender, computed closest nodes, and sent a neighbors response without an observed bond check. After the patch, findnode.handle checks t.db.get(fromID) and returns errUnknownNode when no bond exists, preventing table mutation, lookup, and neighbors response generation for unbonded senders. Supporting decode, send, and reply-matching changes support the bonding flow but are not themselves the root cause.

# Root Cause

The findnode request path could generate a substantially larger neighbors response before verifying that the recovered sender NodeID had an existing bond. In a UDP protocol, the commit states this allowed spoofed-source findnode packets to reflect amplified traffic at a victim address.

## Walkthrough

1. A discovery UDP packet is decoded and the sender NodeID is recovered from the packet signature.

2. Before the fix, a non-expired findnode request proceeded to bumpOrAdd, closest-node lookup, and neighbors response generation.

3. The commit explains that an attacker could spoof the UDP source IP and port of a victim, causing the recipient to send the larger neighbors packet to that victim.

4. The fix adds an early bond check in findnode.handle using t.db.get(fromID).

5. If no bond exists, the handler returns errUnknownNode and does not process the findnode request further.

6. The surrounding ping/pong and reply-matching changes support establishing bonds, but the security-critical gate is the findnode bond requirement.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| p2p/discover/udp.go | 449 | findnode handler rejects unbonded senders before building and sending neighbors responses |
| p2p/discover/udp.go | 332 | UDP send path used to emit encoded discovery responses to a network address |
| p2p/discover/udp.go | 391 | packet decode path recovers sender NodeID and packet hash used by handlers |
| p2p/discover/udp.go | 259 | reply matching loop supports discovery ping/pong state needed for bonding |
| p2p/discover/table.go | 7 | discovery table and bonding subsystem context |

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

Require a prior lightweight peer bond before performing an asymmetric UDP response.

## How It Was Fixed

The findnode handler now checks whether the sender NodeID exists in the node database before doing table updates, closest-node selection, or sending neighbors. Unbonded senders are rejected with errUnknownNode. Related transport changes expose packet metadata and support the bonding-oriented request/reply flow.

# Why It Matters

1. Prevents unbonded findnode requests from triggering larger neighbors responses.

2. Reduces the documented UDP reflection/amplification DDoS vector.

3. Places the guard before response generation and table mutation.

4. Does not establish complete spoofed-source protection; the commit notes replay exposure and future stricter source validation.

# Evidence Notes

The strongest evidence is the commit message and the inline comment in p2p/discover/udp.go findnode.handle describing the DDoS amplification vector and the new t.db.get(fromID) == nil rejection. The before/after hunk shows the pre-fix path proceeded to bumpOrAdd, closest lookup, and neighbors send. The decode, send, loop, and table changes are supporting context for bonding and packet handling, not independent vulnerability causes. There is no evidence of confidentiality impact, key compromise, in-the-wild exploitation, or complete protection for all spoofed-source discovery traffic. Protocol security invariant: The discovery protocol should not process findnode requests or send larger neighbors responses unless the sender has an existing bond established through the discovery ping/pong flow. This is a bond requirement, not complete source-address validation. Verification notes: The patch does not prove the attack was observed in the wild. The patch does not prove complete spoofed-source prevention for all discovery packet types. The commit itself notes possible replay exposure during the expiration window. The patch does not add strict source address validation yet. No confidentiality or private-key compromise is shown by the evidence. Confirmed by explicit security language in the commit message. Confirmed by inline code comment at the new findnode bond check. Grounded in the changed findnode control flow before neighbors response generation. Residual limitation: replay risk during expiration window is acknowledged by the commit. Residual limitation: strict source-address validation was not added in this patch. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `udp-reflection-amplification`
Final impact type: `ddos-amplification`
Final tags: `go-ethereum, p2p, discovery, udp, ddos, reflection-amplification, node-bonding`

The evidence strongly supports retaining this as a security fix. The commit message explicitly describes a spoofed-source UDP discovery amplification DDoS vector, and the patch adds a bond check in the findnode handler before table mutation, closest-node lookup, and neighbors response generation. The original cryptography/input-validation framing is too broad; the validated issue is more conservatively a UDP discovery reflection/amplification flaw mitigated by node bonding.

## Security Evidence

1. Commit message explicitly identifies a DDoS amplification attack vector using spoofed findnode source addresses.
2. Inline code comment at the new findnode guard describes preventing the same amplification attack.
3. Before the patch, non-expired findnode requests proceeded to bump/add the sender, compute closest nodes, and send a larger neighbors response.
4. After the patch, unbonded senders are rejected with errUnknownNode before neighbors response generation.

## Missing Evidence

1. No evidence of in-the-wild exploitation is provided.
2. Patch does not prove complete spoofed-source validation for all discovery packet types.
3. Commit notes possible replay exposure during the expiration window.
4. No confidentiality, key compromise, or cryptographic break impact is shown.

## Claim Boundaries

1. Applies to UDP discovery findnode handling and neighbors responses.
2. Supports a DDoS reflection/amplification fix, not a general cryptography vulnerability.
3. The fix requires an existing bond before processing findnode; it is not complete source-address validation.
4. Security impact should be limited to availability/resource abuse mitigation.
