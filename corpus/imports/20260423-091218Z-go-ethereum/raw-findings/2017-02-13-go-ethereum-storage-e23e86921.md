---
case_id: case_20170213_e23e86921
project: go-ethereum
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2017-02-13
source_refs:
  - git:e23e86921b55cb1ee2fca6b6fb9ed91f5532f9fd
  - "swarm/storage/dbstore.go:400"
  - "swarm/storage/dbstore.go:262"
  - "swarm/network/syncer.go:552"
  - "swarm/network/depo.go:118"
bug_class: missing-content-integrity-check
impact_type:
  - integrity
confidence: medium
tags:
  - swarm
  - storage
  - network
  - chunk-integrity
  - peer-input-validation
  - content-addressed-storage
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded security-relevant change is that Swarm store-request handling now hashes incoming chunk data and rejects it when it does not match the advertised key. Storage changes strengthen local corruption handling and repair, but the evidence does not prove RCE, privilege escalation, consensus impact, or a quantified denial-of-service.

## Observed Patch Facts

1. In `swarm/storage/dbstore.go`, the patch replaces `s.db.Delete(getDataKey(index.Idx))` with `s.delete(index.Idx, getIndexKey(key))`.

2. In `swarm/storage/dbstore.go`, the patch replaces `func (s *DbStore) Counter() uint64 {` with `func (s *DbStore) Cleanup() {`.

3. In `swarm/network/syncer.go`, the patch replaces `glog.V(logger.Detail).Infof("syncer(priority %v): request %v (synced = %v)", self.key...` with `glog.V(logger.Detail).Infof("syncer[%v]: (priority %v): request %v (synced = %v)", se...`.

4. In `swarm/network/depo.go`, the patch replaces `return` with `islocal = true`.

## Project Context

The changed code sits primarily in `swarm/storage`, `swarm/network`, which anchors the finding in the `storage` area of the project. Historical context from `swarm/network/syncdb_test.go`, `swarm/storage/netstore.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `swarm/network/syncdb_test.go`, `swarm/network/kademlia/kademlia.go`. The strongest project-level identifiers around this patch are `priority`, `glog`, `logger`, and `Infof`.

## Before/After Behavior

Before the patch, the shown incoming store-request path could assign peer-supplied SData to a chunk and derive its size without a shown hash comparison against req.Key. After the patch, the handler computes the hash of req.SData, compares it to req.Key, and ignores invalid store requests. For persisted chunks, the patch changes hash-mismatch cleanup from deleting only the data key and returning an error to using the store deletion helper for the indexed entry and stopping with a cleandb repair message.

# Root Cause

The supported root cause is incomplete enforcement of the content-addressed chunk invariant in Swarm chunk handling. Peer-supplied chunk bytes were not shown to be validated against their advertised key before use in the affected handler, and corrupt persisted records were not cleaned up consistently.

## Walkthrough

1. A peer store request supplies an advertised chunk key and SData payload.

2. The pre-patch evidence shows the handler updating chunk data and size from req.SData without a shown digest check in that path.

3. The patched handler hashes req.SData and compares the digest with req.Key.

4. If the digest does not match the advertised key, the store request is logged as invalid and ignored.

5. On database retrieval, stored bytes are also rehashed and compared with the requested key.

6. When a persisted mismatch is detected, the patch deletes through s.delete(index.Idx, getIndexKey(key)) rather than deleting only the data record.

7. The added cleanup command/path supports repair of corrupt local chunk records but is not itself the root vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| swarm/network/depo.go | 101 | incoming peer store-request handling for Swarm chunks; validates payload hash against advertised key before accepting or returning local state |
| swarm/storage/dbstore.go | 383 | persistent chunk retrieval; verifies stored data hashes to requested key and removes corrupt entries |
| swarm/storage/dbstore.go | 262 | database cleanup path; scans indexed chunks for faulty/corrupt chunk records |
| swarm/network/syncer.go | 546 | logging context only; not a security-relevant logic change in the provided evidence |

## Code Snippets

## Snippet 1

Context: `swarm/storage/dbstore.go:400` (changes signature or replay validation logic)

Before
```go
hash := hasher.Sum(nil)
		if !bytes.Equal(hash, key) {
			s.db.Delete(getDataKey(index.Idx))
			err = fmt.Errorf("invalid chunk. hash=%x, key=%v", hash, key[:])
			return
		}
```
After
```go
hash := hasher.Sum(nil)
		if !bytes.Equal(hash, key) {
			s.delete(index.Idx, getIndexKey(key))
			panic("Invalid Chunk in Database. Please repair with command: 'swarm cleandb'")
		}
```

## Snippet 2

Context: `swarm/storage/dbstore.go:262` (changes signature or replay validation logic)

Before
```go
}

func (s *DbStore) Counter() uint64 {
	s.lock.Lock()
```
After
```go
}

func (s *DbStore) Cleanup() {
	//Iterates over the database and checks that there are no faulty chunks
	it := s.db.NewIterator()
	startPosition := []byte{kpIndex}
	it.Seek(startPosition)
	var key []byte
```

## Snippet 3

Context: `swarm/network/syncer.go:552` (changes persisted or aggregate state handling)

Before
```go
if sreq, err := self.newSyncRequest(req, priority); err == nil {
			// extract key from req
			glog.V(logger.Detail).Infof("syncer(priority %v): request %v (synced = %v)", self.key.Log(), priority, req, state.Synced)
			unsynced = append(unsynced, sreq)
		} else {
			glog.V(logger.Warn).Infof("syncer(priority %v): error creating request for %v: %v)", self.key.Log(), priority, req, state.Synced, err)
		}
```
After
```go
if sreq, err := self.newSyncRequest(req, priority); err == nil {
			// extract key from req
			glog.V(logger.Detail).Infof("syncer[%v]: (priority %v): request %v (synced = %v)", self.key.Log(), priority, req, state.Synced)
			unsynced = append(unsynced, sreq)
		} else {
			glog.V(logger.Warn).Infof("syncer[%v]: (priority %v): error creating request for %v: %v)", self.key.Log(), priority, req, state.Synced, err)
		}
```

## Snippet 4

Context: `swarm/network/depo.go:118` (changes a sensitive control or state-update path)

Before
```go
// this should update access count?
		glog.V(logger.Detail).Infof("Depo.HandleStoreRequest: %v found locally. ignore.", req)
		return
	}

	// update chunk with size and data
	chunk.SData = req.SData // protocol validates that SData is minimum 9 bytes long (int64 size  + at least one byte of data)
	chunk.Size = int64(binary.LittleEndian.Uint64(req.SData[0:8]))
```
After
```go
// this should update access count?
		glog.V(logger.Detail).Infof("Depo.HandleStoreRequest: %v found locally. ignore.", req)
		islocal = true
		//return
	}
	
	hasher := self.hashfunc()
	hasher.Write(req.SData)
```

# Fix Pattern

Validate content-addressed data at ingestion and cleanup boundaries, rejecting mismatched payloads and deleting corrupt records through the store's normal deletion abstraction.

## How It Was Fixed

The patch adds a hash comparison for incoming req.SData versus req.Key in Depo.HandleStoreRequestMsg, rejects mismatches, changes DbStore.Get mismatch cleanup to remove the indexed entry consistently, and adds a cleandb cleanup path for faulty local records.

# Why It Matters

1. Prevents mismatched peer-supplied chunk bytes from being accepted as valid for an advertised content key.

2. Preserves Swarm's content-addressing integrity invariant across network ingestion and local storage.

3. Reduces risk of corrupt partial records persisting after a detected hash mismatch.

4. Does not establish RCE, privilege escalation, consensus failure, or measured DoS impact from the supplied evidence.

# Evidence Notes

The strongest evidence is the depo.go change that hashes req.SData and compares it to req.Key before accepting a store request. The dbstore.go changes support integrity enforcement for persisted chunks and repair of corrupt local entries. The syncer.go change is logging-only. The heuristic baseline's transaction-validation and panic-on-decoding claims are unsupported by the provided Swarm chunk evidence. Protocol security invariant: Swarm chunks are content-addressed: incoming or persisted chunk bytes must hash to the advertised chunk key before being accepted or treated as valid. Verification notes: The patch does not prove remote code execution or privilege escalation. The patch does not prove consensus impact; this is Swarm chunk storage/networking, not Ethereum transaction validation. The evidence supports malformed or mismatched chunk rejection, but not a quantified denial-of-service impact. The patch notes a TODO for peer penalization, so peer reputation or disconnect behavior is not shown as fixed. The database panic/cleandb behavior shows corruption detection and operator remediation, not necessarily that an attacker can always create the corrupt local state. Confirmed by supplied diff snippets only; no external code inspection was used. Impact is limited to Swarm chunk integrity based on the evidence provided. Attacker reachability is plausible because the affected path handles peer store requests, but exploitability and impact are not quantified. Database cleanup behavior supports remediation but does not prove how corrupt local state is introduced. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-content-integrity-check`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `swarm, storage, network, chunk-integrity, peer-input-validation, content-addressed-storage`

The supplied patch evidence clearly shows security-sensitive hardening of Swarm's content-addressed chunk invariant: incoming peer-supplied chunk data is now hashed and rejected if it does not match the advertised key, and persisted corrupt chunks are detected and removed more consistently. The evidence supports keeping this as security hardening, but the original liveness-focused security-fix framing is too strong because exploitability, attacker impact, and denial-of-service consequences are not proven from the patch alone.

## Security Evidence

1. Incoming store-request handling now computes a hash over req.SData and compares it with req.Key.
2. Invalid incoming chunks are logged and ignored instead of being accepted into the normal chunk update path.
3. DbStore.Get already validates stored data against the requested key and the patch changes mismatch handling to delete through the store deletion helper.
4. The commit subject and body explicitly describe fixing chunk integrity checks for incoming known chunks.

## Missing Evidence

1. No proof of a concrete exploit path beyond peer-supplied malformed chunk data.
2. No demonstrated RCE, privilege escalation, consensus impact, or quantified denial-of-service impact.
3. No evidence that the database corruption state is remotely triggerable in all cases.
4. No shown peer penalty, disconnect, or broader abuse-prevention behavior.

## Claim Boundaries

1. Validated only as Swarm chunk integrity hardening, not as a proven high-impact vulnerability fix.
2. Do not claim transaction validation, consensus safety, or Ethereum core protocol impact.
3. Do not retain the original liveness-failure impact as the primary corpus classification.
4. The syncer.go logging change is not security-relevant based on the supplied evidence.
