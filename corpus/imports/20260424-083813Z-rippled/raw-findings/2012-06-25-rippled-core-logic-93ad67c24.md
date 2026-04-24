---
case_id: case_20120625_93ad67c24
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
impact_type:
  - state-integrity
confidence: medium
source_quality: high
date: 2012-06-25
source_refs:
  - git:93ad67c240d3d1071d2c7ec3f756825965088e26
  - "src/SHAMap.cpp:199"
  - "src/SHAMap.cpp:182"
  - "src/SHAMapNodes.cpp:318"
  - "src/SHAMap.cpp:621"
bug_class: hash-domain-separation
tags:
  - blockchain-core
  - core-logic
  - serialization-format
  - hash-prefixing
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix for SHAMap node serialization and hash-prefix handling. The commit subject explicitly says it closes a SHAMap node security hole, and the code changes move node reconstruction into `fetchNode(id, hash)`, construct fetched nodes with `STN_ARF_PREFIXED`, add explicit raw serialization formats, and retain node-hash mismatch rejection. The provided evidence supports a serialization/hash-domain hardening thesis, but not a full exploit path or concrete attack scenario.

## Observed Patch Facts

1. In `src/SHAMap.cpp`, the patch replaces `SHAMapTreeNode::pointer node;` with `SHAMapTreeNode::pointer node = fetchNode(id, hash);`.

2. In `src/SHAMap.cpp`, the patch replaces `std::vector<unsigned char> nodeData;` with `node = fetchNode(id, hash);`.

3. In `src/SHAMapNodes.cpp`, the patch replaces `bool SHAMapTreeNode::setItem(SHAMapItem::pointer& i, TNType type)` with `void SHAMapTreeNode::addRaw(Serializer& s, int format)`.

4. In `src/SHAMap.cpp`, the patch replaces `bool SHAMap::fetchNode(const uint256& hash, std::vector<unsigned char>& data)` with `SHAMapTreeNode::pointer SHAMap::fetchNode(const SHAMapNode& id, const uint256& hash)`.

## Project Context

The changed code sits primarily in `src`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/SHAMapSync.cpp`, `src/SHAMap.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/SHAMapSync.cpp`, `src/SHAMap.h`. The strongest project-level identifiers around this patch are `SHAMapTreeNode::pointer`, `hash`, `SHAMapTreeNode`, and `std::vector`.

## Before/After Behavior

Before the patch, `fetchNode` retrieved raw bytes by hash and callers constructed `SHAMapTreeNode(id, nodeData, mSeq)` before checking the resulting node hash. After the patch, `fetchNode` takes both node id and hash, returns a reconstructed node, asserts the retrieved bytes hash to the requested object hash, and constructs the node with `STN_ARF_PREFIXED`. Serialization now uses `SHAMapTreeNode::addRaw(Serializer& s, int format)`, allows only prefixed or wire formats, rejects `tnERROR`, and prefixes inner-node serialization with `sHP_InnerNode` in prefixed mode.

# Root Cause

The supported root-cause claim is that the old path did not make the node serialization format explicit when reconstructing fetched SHAMap nodes. The stronger claim that this enabled a specific replay, collision, consensus failure, or remote exploit is not established by the provided hunks.

## Walkthrough

1. A SHAMap caller requests a node using an expected `SHAMapNode id` and `uint256 hash`.

2. Before the patch, the fetch helper only returned raw object bytes for the hash.

3. The caller reconstructed a `SHAMapTreeNode` from those bytes without the shown constructor specifying a serialization format.

4. The patched helper receives both `id` and `hash` and reconstructs the node itself.

5. The patched reconstruction uses `STN_ARF_PREFIXED`, making the persisted-node interpretation explicit at that boundary.

6. Callers still reject reconstructed nodes whose computed node hash does not match the expected hash.

7. The new `addRaw` path requires either prefixed or wire format and adds an inner-node prefix in prefixed serialization.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/SHAMap.cpp | 621 | Fetches a hashed object by node hash, verifies stored bytes against the requested hash, and constructs a SHAMap node using the node id and prefixed serialization format. |
| src/SHAMap.cpp | 182 | Retrieves a SHAMap node for normal access and rejects a fetched node whose computed node hash differs from the expected hash. |
| src/SHAMap.cpp | 199 | Retrieves a fast node pointer and rejects a fetched node whose computed node hash differs from the expected hash. |
| src/SHAMapNodes.cpp | 318 | Serializes SHAMap tree nodes using explicit prefixed or wire formats and rejects invalid node types before serialization. |

## Code Snippets

## Snippet 1

Context: `src/SHAMap.cpp:199` (changes signature or replay validation logic)

Before
```cpp
return &*it->second;

	SHAMapTreeNode::pointer node;
	std::vector<unsigned char> nodeData;
	if (!fetchNode(hash, nodeData)) return NULL;

	node = boost::make_shared<SHAMapTreeNode>(id, nodeData, mSeq);
	if (node->getNodeHash() != hash) throw SHAMapException(InvalidNode);
```
After
```cpp
return &*it->second;

	SHAMapTreeNode::pointer node = fetchNode(id, hash);
	if (!node) return NULL;

	if (node->getNodeHash() != hash)
		throw std::runtime_error("invalid node fetched");
```

## Snippet 2

Context: `src/SHAMap.cpp:182` (changes signature or replay validation logic)

Before
```cpp
}

	std::vector<unsigned char> nodeData;
	if (!fetchNode(hash, nodeData)) return SHAMapTreeNode::pointer();

	node = boost::make_shared<SHAMapTreeNode>(id, nodeData, mSeq);
	if (node->getNodeHash() != hash) throw SHAMapException(InvalidNode);
```
After
```cpp
}

	node = fetchNode(id, hash);
	if (!node) return node;

	if (node->getNodeHash() != hash)
		throw std::runtime_error("invalid node hash");
```

## Snippet 3

Context: `src/SHAMapNodes.cpp:318` (changes the branch that decides whether execution stops or continues)

Before
```cpp
}

bool SHAMapTreeNode::setItem(SHAMapItem::pointer& i, TNType type)
{
```
After
```cpp
}

void SHAMapTreeNode::addRaw(Serializer& s, int format)
{
	assert((format == STN_ARF_PREFIXED) || (format == STN_ARF_WIRE));
	if (mType == tnERROR) throw std::runtime_error("invalid I node type");

	if (mType == tnINNER)
```

## Snippet 4

Context: `src/SHAMap.cpp:621` (changes signature or replay validation logic)

Before
```cpp
}

bool SHAMap::fetchNode(const uint256& hash, std::vector<unsigned char>& data)
{
	HashedObject::pointer obj(theApp->getHashedObjectStore().retrieve(hash));
	if(!obj) return false;
	data = obj->getData();
	return true;
```
After
```cpp
}

SHAMapTreeNode::pointer SHAMap::fetchNode(const SHAMapNode& id, const uint256& hash)
{
	if (!theApp->running()) return SHAMapTreeNode::pointer();

	HashedObject::pointer obj(theApp->getHashedObjectStore().retrieve(hash));
	if(!obj) return SHAMapTreeNode::pointer();
```

# Fix Pattern

Centralize fetched-node reconstruction, require explicit serialization format selection, and reject hash or type mismatches before accepting the node.

## How It Was Fixed

`SHAMap::fetchNode` was changed from a raw-byte retrieval helper into a node-aware helper taking `id` and `hash`. It now returns an empty node when unavailable, asserts the stored bytes hash to the requested hash, and constructs the node with `STN_ARF_PREFIXED`. `getNode` and `getNodePointer` were updated to consume that helper. `SHAMapTreeNode::addRaw` was added with explicit prefixed and wire modes plus invalid-type rejection.

# Why It Matters

1. SHAMap nodes are hash-addressed state structures, so serialization ambiguity can affect integrity checks.

2. Explicit prefixes reduce the chance that bytes valid in one node format are interpreted as another format.

3. The patch changes validation and reconstruction behavior, not just cleanup.

4. Exploitability and attack reach are not proven by the supplied evidence.

# Evidence Notes

Grounded evidence comes from `src/SHAMap.cpp` changes to `getNode`, `getNodePointer`, and `fetchNode`, plus `src/SHAMapNodes.cpp` introduction of `addRaw` with explicit formats and `sHP_InnerNode`. The commit subject is strong security evidence. However, the exact old ambiguity and any practical attack path are inferred rather than demonstrated, so the finding is downgraded from confirmed/high to likely/medium. Protocol security invariant: Fetched SHAMap node bytes should be interpreted and hashed under the intended node serialization format, and a reconstructed node should not be accepted unless its computed node hash matches the expected hash. Verification notes: The patch does not show a complete remote attack path. The patch does not prove practical hash collision or preimage feasibility. The patch does not prove ledger consensus compromise by itself. The removal of `SHAMapException` appears incidental unless tied to the node validation behavior. The exact old wire-format ambiguity is inferred from the prefix-format changes, not fully demonstrated in the provided hunks. No complete exploit path is shown. No test or advisory evidence is provided. The removal of `SHAMapException` appears incidental to the security thesis. Helper changes are treated as support for the serialization and fetch-path fix, not as a separate vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `hash-domain-separation`
Final tags: `blockchain-core, core-logic, serialization-format, hash-prefixing, state-integrity`

The commit subject explicitly says it closes a SHAMap node security hole, and the patch adds explicit hash-prefix/serialization handling for hash-addressed SHAMap nodes. The code evidence supports retaining this as security hardening around node reconstruction and domain separation, but it does not prove a concrete exploit path strongly enough to validate it as a definite security-fix case.

## Security Evidence

1. Commit subject uses direct security language: "Close SHAMap node security hole".
2. Fetched nodes are reconstructed through a node-aware helper using both node id and expected hash.
3. Fetched SHAMap nodes are constructed with an explicit `STN_ARF_PREFIXED` format.
4. New raw serialization path accepts only prefixed or wire formats and adds an inner-node hash prefix.
5. Hash mismatch checks remain before accepting reconstructed nodes.

## Missing Evidence

1. No exploit scenario or attacker-controlled input path is shown.
2. No advisory, test, or vulnerability description is provided.
3. The exact pre-patch ambiguity between wire and prefixed formats is inferred, not fully demonstrated.
4. No evidence proves practical consensus compromise or ledger corruption.

## Claim Boundaries

1. Supported claim: the patch tightens SHAMap node serialization/hash-prefix handling.
2. Supported claim: the affected code is security-sensitive blockchain state infrastructure.
3. Not supported: a specific remote exploit or replay attack.
4. Not supported: confirmed state corruption from the supplied patch alone.
