---
case_id: case_20170213_e23e86921b
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
  - infrastructure
  - swarm
  - network
  - storage
  - content-integrity
  - input-validation
  - content-addressing
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch strengthens Swarm chunk integrity checks. The best-supported security-relevant change is in `swarm/network/depo.go`, where incoming store request data is hashed and compared with `req.Key` before the request can update or satisfy chunk state. Storage changes in `swarm/storage/dbstore.go` improve handling of persisted hash/key mismatches and add a cleanup path, but the provided evidence does not establish a remote crash, arbitrary execution, consensus impact, or authorization bypass.

## Observed Patch Facts

1. In `swarm/storage/dbstore.go`, the patch replaces `s.db.Delete(getDataKey(index.Idx))` with `s.delete(index.Idx, getIndexKey(key))`.

2. In `swarm/storage/dbstore.go`, the patch replaces `func (s *DbStore) Counter() uint64 {` with `func (s *DbStore) Cleanup() {`.

3. In `swarm/network/syncer.go`, the patch replaces `glog.V(logger.Detail).Infof("syncer(priority %v): request %v (synced = %v)", self.key...` with `glog.V(logger.Detail).Infof("syncer[%v]: (priority %v): request %v (synced = %v)", se...`.

4. In `swarm/network/depo.go`, the patch replaces `return` with `islocal = true`.

## Project Context

The changed code sits primarily in `swarm/storage`, `swarm/network`, which anchors the finding in the `storage` area of the project. Historical context from `swarm/network/syncdb_test.go`, `swarm/storage/netstore.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `swarm/network/syncdb_test.go`, `swarm/network/kademlia/kademlia.go`. The strongest project-level identifiers around this patch are `priority`, `glog`, `logger`, and `Infof`.

## Before/After Behavior

Before the patch, `HandleStoreRequestMsg` could proceed to update chunk data from `req.SData` without the shown hash-to-key comparison. After the patch, it computes the hash of `req.SData`, compares it with `req.Key`, and ignores mismatches. Before the patch, `DbStore.Get` detected stored data whose hash did not match the requested key, deleted only the data key, and returned an error. After the patch, it uses the store delete helper for consistent cleanup and panics with an instruction to run `swarm cleandb`. The added cleanup command supports repair of corrupt local database entries.

# Root Cause

Peer-supplied and persisted Swarm chunk data was not consistently enforced against the content-addressed key invariant at the shown boundaries. In the network path, request data could reach chunk update logic without the added hash comparison. In the storage path, corrupt persisted chunks were handled with partial direct deletion rather than the store-level deletion helper.

## Walkthrough

1. A store request reaches `Depo.HandleStoreRequestMsg` with `req.Key` and serialized chunk bytes in `req.SData`.

2. The patched code hashes `req.SData` using `self.hashfunc()`.

3. The computed digest is compared with `req.Key`.

4. If the digest does not match, the request is logged as invalid and ignored.

5. If the digest matches, normal local-return or chunk update behavior can continue.

6. When persisted data is fetched through `DbStore.Get`, the data is hashed and compared with the requested key.

7. On mismatch, the patched storage path calls `s.delete(index.Idx, getIndexKey(key))` and surfaces the corruption through a repair panic.

8. The syncer hunk changes logging format only and is not substantive evidence of a vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| swarm/network/depo.go | 118 | Validates peer-supplied chunk payload data against the requested content hash before accepting or storing it. |
| swarm/storage/dbstore.go | 400 | Checks persisted chunk data against its key on Get and removes inconsistent index/data state on mismatch. |
| swarm/storage/dbstore.go | 262 | Adds database cleanup logic to scan stored chunk index entries and repair faulty content-addressed records. |
| swarm/network/syncer.go | 552 | Logging format change only; no substantive integrity or authorization behavior shown. |

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

Validate content-addressed data at trust boundaries by hashing serialized chunk bytes and rejecting mismatches before acceptance; use centralized deletion/cleanup helpers to keep storage index and data records consistent after corruption is detected.

## How It Was Fixed

`swarm/network/depo.go` now hashes incoming `req.SData` and rejects store requests whose hash does not equal `req.Key`. `swarm/storage/dbstore.go` now removes corrupt stored records through `s.delete(index.Idx, getIndexKey(key))` and adds a cleanup path for scanning faulty database entries. The commit body also indicates a user-facing `swarm cleandb` repair command was added.

# Why It Matters

1. Prevents peer-supplied chunk bytes from being accepted under a non-matching content key.

2. Preserves Swarm's content-addressed chunk integrity invariant.

3. Reduces inconsistent local database state after detecting corrupt stored chunks.

4. Provides a repair path for faulty stored chunk records.

5. Does not prove remote code execution, consensus failure, or a reliable remote crash path.

# Evidence Notes

Strongest evidence is `swarm/network/depo.go` line 118, where `hasher.Write(req.SData)` and `bytes.Equal(hasher.Sum(nil), req.Key)` are added before accepting the request. Supporting evidence is `swarm/storage/dbstore.go` line 400, where mismatch cleanup changes from direct data-key deletion to `s.delete(index.Idx, getIndexKey(key))`, and `swarm/storage/dbstore.go` line 262, where database cleanup is added. `swarm/network/syncer.go` line 552 is logging-only. Claims about transactions, signatures, integer conversion, consensus, authentication, encryption, or arbitrary execution are unsupported by the supplied evidence. Protocol security invariant: Swarm chunks are content-addressed: the chunk key must match the hash of the serialized chunk data before peer-supplied data is accepted or persisted data is treated as valid. Verification notes: The patch does not prove arbitrary code execution or consensus impact. The patch does not prove that a remote peer can reliably crash a node. The database panic path may involve local persisted corruption; remote causation is not shown by the provided evidence. The syncer hunk is not evidence of a security fix by itself. No authentication, authorization, or encryption boundary change is shown. Classified as likely security because the patch validates peer-supplied content-addressed data. Kept in the security corpus due to direct ingress integrity validation. Confidence is high for the code-level fix pattern, but the exploit impact is bounded to chunk integrity by the evidence. No supported evidence of remote node crash beyond local database corruption handling and the new panic on detected corrupt persisted data. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-content-integrity-check`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `infrastructure, swarm, network, storage, content-integrity, input-validation, content-addressing`

The supplied patch evidence supports a security-hardening classification: peer-supplied Swarm chunk data is now hashed and compared with the requested content key before being accepted, which tightens a content-addressed integrity boundary. The storage cleanup and panic behavior mainly support local corruption handling and reliability. The evidence does not strongly prove a concrete exploitable vulnerability, remote crash, authorization bypass, or consensus impact, so the original security-fix and liveness-failure framing is too strong.

## Security Evidence

1. Incoming store requests now hash req.SData and compare the digest to req.Key before continuing.
2. Invalid incoming chunk data is logged and ignored rather than accepted into the chunk update path.
3. DbStore.Get continues to enforce hash/key consistency for persisted chunks and now deletes through the store helper on mismatch.
4. The commit subject and body explicitly describe fixing or improving chunk integrity checks.

## Missing Evidence

1. No proof that an attacker could reliably exploit the missing check beyond submitting mismatched chunk data.
2. No demonstrated remote crash path, despite the new local panic on corrupt persisted database entries.
3. No evidence of authentication, authorization, encryption, consensus, or code execution impact.
4. No test or exploit scenario showing the exact pre-patch acceptance consequences.

## Claim Boundaries

1. Valid claim: the patch hardens content-addressed chunk integrity validation for incoming Swarm data.
2. Valid claim: the patch improves handling of corrupt persisted chunk records.
3. Do not claim remote code execution, consensus compromise, or authorization bypass from this evidence.
4. Do not classify primarily as a liveness failure; integrity is the supported impact.
