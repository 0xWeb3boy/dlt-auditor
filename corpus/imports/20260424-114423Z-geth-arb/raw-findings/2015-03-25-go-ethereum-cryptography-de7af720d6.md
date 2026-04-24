---
case_id: case_20150325_de7af720d6
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
  - denial-of-service
  - traffic-amplification
tags:
  - p2p-discovery
  - udp
  - ddos
  - reflection-amplification
  - bonding
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

go-ethereum fixed a reflected UDP amplification issue in the p2p discovery protocol. Before the patch, a findnode request that passed expiration handling could proceed to table update/lookup and trigger a larger neighbors response. After the patch, findnode handling first checks for an existing bond with t.db.get(fromID) and returns errUnknownNode when none exists.

## Observed Patch Facts

1. In `p2p/discover/udp.go`, the patch replaces `return fmt.Errorf("unknown type: %d", ptype)` with `return nil, fromID, hash, fmt.Errorf("unknown type: %d", ptype)`.

2. In `p2p/discover/udp.go`, the patch replaces `func (t *udp) send(to *Node, ptype byte, req interface{}) error {` with `func (t *udp) send(toaddr *net.UDPAddr, ptype byte, req interface{}) error {`.

3. In `p2p/discover/udp.go`, the patch replaces `t.mutex.Lock()` with `if t.db.get(fromID) == nil {`.

4. In `p2p/discover/udp.go`, the patch replaces `case reply := <-t.replies:` with `case r := <-t.gotreply:`.

## Project Context

The changed code sits primarily in `p2p/discover`, which anchors the finding in the `cryptography` area of the project. Historical context from `p2p/discover/udp_test.go`, `p2p/discover/table_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `p2p/discover/udp_test.go`, `p2p/discover/table_test.go`. The strongest project-level identifiers around this patch are `ptype`, `from`, `pending`, and `send`.

## Before/After Behavior

Before the patch, findnode handling checked expiration, then bumped or added the apparent sender, selected closest nodes, and sent a neighbors packet. After the patch, findnode handling rejects senders without an existing bond before table mutation, lookup, or neighbors response generation. Supporting udp.go changes refactor packet decoding, UDP sending, and reply matching around the bonding flow, but the security-relevant behavior is the findnode bond gate.

# Root Cause

The findnode response path could emit a much larger neighbors packet based on a UDP packet's apparent source without first requiring a discovery bond. Because UDP source addresses can be spoofed, an attacker could direct amplified response traffic toward a victim.

## Walkthrough

1. An attacker sends a findnode request with a victim's IP address and UDP port as the apparent source.

2. Before the fix, the recipient checked expiration but did not require a bond before processing findnode.

3. The handler could update or add the apparent sender, compute closest nodes, and send a neighbors response.

4. The commit states that neighbors is significantly larger than findnode, creating a reflected DDoS amplification vector.

5. After the fix, the handler checks t.db.get(fromID) before continuing.

6. If no bond exists, the handler returns errUnknownNode and skips neighbors generation.

7. The commit states that a bond is created when one node replies to a ping from the other.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| p2p/discover/udp.go | 449 | findnode handler rejects unbonded senders before generating neighbors response |
| p2p/discover/udp.go | 391 | packet decoding returns packet, sender node ID, hash, and decode error for dispatch/bonding logic |
| p2p/discover/udp.go | 326 | UDP send path emits encoded discovery packets to a UDP address |
| p2p/discover/udp.go | 259 | reply matching loop tracks pending discovery replies used by bonding/request flow |
| p2p/discover/table.go | 7 | discovery table/bonding subsystem context, including bonding-related limits |
| p2p/discover/table_test.go | 15 | tests exercise table bonding and ping replacement behavior |

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

Require prior reachability/bond validation before emitting larger UDP discovery responses.

## How It Was Fixed

The patch adds a bond check at the start of findnode handling in p2p/discover/udp.go after expiration validation. If t.db.get(fromID) is nil, the request is not processed and errUnknownNode is returned. Only bonded senders proceed to bumpOrAdd, closest-node lookup, and neighbors response sending.

# Why It Matters

1. Prevents unbonded findnode requests from triggering larger neighbors responses.

2. Addresses the reflected UDP amplification vector described by the commit.

3. Keeps the fix scoped to discovery findnode/neighbors behavior.

4. Does not establish complete replay protection or full source address validation.

# Evidence Notes

The strongest evidence is p2p/discover/udp.go line 449, where findnode handling adds t.db.get(fromID) == nil and returns errUnknownNode with an inline comment describing DDoS amplification through spoofed findnode requests. The before hunk shows the handler proceeding from expiration checking into bumpOrAdd, closest lookup, and neighbors sending without that bond check. The commit message explicitly describes the attack vector and the bonding mitigation, while also noting possible replay exposure during the expiration window. Protocol security invariant: The discovery protocol should not generate large neighbors responses for unbonded findnode senders. Requiring a prior discovery bond before processing findnode reduces the ability to use spoofed-source UDP requests as a reflected amplification vector, though the commit notes replay/source-validation limitations remain. Verification notes: The patch does not prove complete prevention of all discovery replay attacks; the commit notes a remaining replay window. The evidence does not show stricter source address validation beyond requiring an existing bond. The finding is about reflected UDP amplification via findnode/neighbors, not confidentiality or cryptographic key compromise. The patch does not establish that every discovery packet type requires bonding, only that findnode processing is gated. Security verdict is confirmed by explicit commit message and inline code comment. Bug class is UDP reflection/amplification, not generic cryptography or input validation. Subsystem is p2p discovery, not cryptography. Confidence is high because the patch directly gates the vulnerable response path. Remaining replay/source-validation limitations are acknowledged and not treated as fixed. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `udp-reflection-amplification`
Final impact type: `denial-of-service, traffic-amplification`
Final tags: `p2p-discovery, udp, ddos, reflection-amplification, bonding`

The evidence strongly supports a security fix: the commit message and inline code comment explicitly describe a spoofed-source UDP findnode request causing larger neighbors responses to be reflected at a victim, and the patch adds a bond check that rejects unbonded findnode senders before generating that response. The original finding is valid, but its cryptography/input-validation framing is misleading; the core issue is UDP reflection/amplification in p2p discovery.

## Security Evidence

1. Commit body explicitly describes a DDoS amplification attack vector using spoofed findnode source addresses.
2. findnode handler now checks t.db.get(fromID) and returns errUnknownNode when no bond exists.
3. Inline comment states the bond check prevents discovery protocol amplification via larger neighbors packets.
4. Before evidence shows findnode proceeded to bumpOrAdd, closest lookup, and neighbors response sending after expiration handling.

## Missing Evidence

1. Patch does not prove complete elimination of replay attacks; commit notes a remaining replay window.
2. Patch does not show stricter source address validation beyond requiring an existing bond.
3. Evidence does not establish confidentiality, key compromise, or a cryptographic vulnerability.

## Claim Boundaries

1. Validated issue is reflected UDP amplification through p2p discovery findnode/neighbors behavior.
2. Validated fix is gating findnode processing on an existing bond.
3. Do not generalize this to all discovery packet types being protected.
4. Do not classify primarily as cryptography; cryptographic packet identity exists in the code path but is not the bug class.
