---
case_id: case_20230320_b8d1c3a2d
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: medium
date: 2023-03-20
source_refs:
  - git:b8d1c3a2d9d8ffc96ad6a67cfaf052509458b5b4
  - "sei-tendermint/crypto/merkle/proof.go:161"
  - "sei-tendermint/crypto/merkle/proof.go:61"
  - "sei-tendermint/crypto/merkle/proof_value.go:93"
  - "sei-tendermint/crypto/merkle/tree_test.go:180"
bug_class: merkle-proof-structural-validation
impact_type:
  - integrity
  - proof-forgery-prevention
confidence: high
tags:
  - cryptography
  - merkle-proof
  - proof-validation
  - error-propagation
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Security fix in the Tendermint Merkle proof path. The patch changes malformed proof reconstruction from ambiguous nil-root behavior into explicit errors, and updates verification/output callers to stop on those errors. The commit subject identifies an empty Merkle tree forging vector, and the code evidence supports a proof-structure validation flaw, but not broader claims such as remote exploitability or consensus impact.

## Observed Patch Facts

1. In `sei-tendermint/crypto/merkle/proof.go`, the patch replaces `return nil` with `return nil, errors.New("Calling computeHashFromAunts() with total 1 but non-empty inn...`.

2. In `sei-tendermint/crypto/merkle/proof.go`, the patch replaces `computedHash := sp.ComputeRootHash()` with `computedHash, err := sp.ComputeRootHash()`.

3. In `sei-tendermint/crypto/merkle/proof_value.go`, the patch replaces `return [][]byte{` with `rootHash, err := op.Proof.ComputeRootHash()`.

4. In `sei-tendermint/crypto/merkle/tree_test.go`, the patch adds `func EncodeUvarint(w io.Writer, u uint64) (err error) {`.

## Project Context

The changed code sits primarily in `sei-tendermint/crypto/merkle`, `sei-tendermint/crypto`, which anchors the finding in the `cryptography` area of the project. Historical context from `sei-tendermint/crypto/merkle/tree.go`, `sei-tendermint/crypto/merkle/rfc6962_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-tendermint/crypto/merkle/tree.go`, `sei-tendermint/crypto/merkle/rfc6962_test.go`. The strongest project-level identifiers around this patch are `innerHashes`, `leafHash`, `computedHash`, and `ComputeRootHash`.

## Before/After Behavior

Before the patch, computeHashFromAunts returned only a hash byte slice and used nil to represent invalid proof shapes such as total == 1 with non-empty inner hashes or total > 1 with no inner hashes. Proof.Verify and ValueOp.Run called ComputeRootHash without handling a structural error path. After the patch, ComputeRootHash/computeHashFromAunts can return explicit errors for invalid proof structure, and both Verify and ValueOp.Run propagate those errors before comparing or returning a computed root.

# Root Cause

Merkle proof reconstruction represented invalid tree/proof shape as a nil hash instead of an explicit failure, and callers did not have or use an error result to distinguish malformed proof structure from normal root computation.

## Walkthrough

1. computeHashFromAunts reconstructs a Merkle root from index, total, leafHash, and innerHashes/aunts.

2. The patched code adds explicit errors when a single-leaf proof contains inner hashes and when a multi-leaf proof has no inner hashes.

3. The patched recursive calls now propagate reconstruction errors instead of only testing for nil child hashes.

4. Proof.Verify now returns ComputeRootHash errors before root comparison.

5. ValueOp.Run now returns ComputeRootHash errors before emitting the root hash output.

6. The tree_test.go additions appear to be supporting test/helper code, not the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sei-tendermint/crypto/merkle/proof.go | 154 | Reconstructs a Merkle root from a leaf hash and aunt hashes; now rejects structurally inconsistent proof shapes with errors. |
| sei-tendermint/crypto/merkle/proof.go | 52 | Verifies a proof against a root hash; now propagates ComputeRootHash errors before comparing roots. |
| sei-tendermint/crypto/merkle/proof_value.go | 77 | Runs a Merkle value proof operation; now propagates proof root computation errors instead of returning an unchecked root output. |
| sei-tendermint/crypto/merkle/tree_test.go | 180 | Test support added around Merkle encoding behavior; supporting evidence only, not the primary security path. |

## Code Snippets

## Snippet 1

Context: `sei-tendermint/crypto/merkle/proof.go:161` (changes a sensitive control or state-update path)

Before
```go
case 1:
		if len(innerHashes) != 0 {
			return nil
		}
		return leafHash
	default:
		if len(innerHashes) == 0 {
			return nil
```
After
```go
case 1:
		if len(innerHashes) != 0 {
			return nil, errors.New("Calling computeHashFromAunts() with total 1 but non-empty inner hashes")
		}
		return leafHash, nil
	default:
		if len(innerHashes) == 0 {
			return nil, errors.New("Calling computeHashFromAunts() with total > 1 but empty inner hashes")
```

## Snippet 2

Context: `sei-tendermint/crypto/merkle/proof.go:61` (changes a sensitive control or state-update path)

Before
```go
return fmt.Errorf("invalid leaf hash: wanted %X got %X", leafHash, sp.LeafHash)
	}
	computedHash := sp.ComputeRootHash()
	if !bytes.Equal(computedHash, rootHash) {
		return fmt.Errorf("invalid root hash: wanted %X got %X", rootHash, computedHash)
```
After
```go
return fmt.Errorf("invalid leaf hash: wanted %X got %X", leafHash, sp.LeafHash)
	}
	computedHash, err := sp.ComputeRootHash()
	if err != nil {
		return err
	}
	if !bytes.Equal(computedHash, rootHash) {
		return fmt.Errorf("invalid root hash: wanted %X got %X", rootHash, computedHash)
```

## Snippet 3

Context: `sei-tendermint/crypto/merkle/proof_value.go:93` (changes a sensitive control or state-update path)

Before
```go
}

	return [][]byte{
		op.Proof.ComputeRootHash(),
	}, nil
}
```
After
```go
}

	rootHash, err := op.Proof.ComputeRootHash()
	if err != nil {
		return nil, err
	}
	return [][]byte{rootHash}, nil
}
```

## Snippet 4

Context: `sei-tendermint/crypto/merkle/tree_test.go:180` (changes a sensitive control or state-update path)

Before
```go
}
}
```
After
```go
}
}

func EncodeUvarint(w io.Writer, u uint64) (err error) {
	var buf [10]byte
	n := binary.PutUvarint(buf[:], u)
	_, err = w.Write(buf[0:n])
	return
```

# Fix Pattern

Replace sentinel nil results in cryptographic proof reconstruction with explicit errors, then require all proof verification/output callers to propagate those errors before accepting or returning a root.

## How It Was Fixed

computeHashFromAunts in sei-tendermint/crypto/merkle/proof.go was changed to return ([]byte, error) and to report invalid proof-shape cases. Proof.Verify was changed to check the ComputeRootHash error before comparing roots. ValueOp.Run was changed to check the ComputeRootHash error before returning the root output.

# Why It Matters

1. Malformed Merkle proof structures are rejected explicitly.

2. Verification no longer treats reconstruction failure as an ordinary computed hash value.

3. The fix is in a cryptographic proof verification path.

4. The supplied evidence does not establish remote exploitability, arbitrary membership forgery, or consensus impact.

# Evidence Notes

Strongest evidence is in sei-tendermint/crypto/merkle/proof.go and proof_value.go. The commit subject explicitly says "Patch forging empty merkle tree attack vector," and the implementation changes align with enforcing proof-shape invariants. Supporting context from tree.go shows empty, single-leaf, and multi-leaf tree hashing are distinct. tree_test.go helper changes should be treated as support code only. Protocol security invariant: Merkle proof root reconstruction must fail when the claimed tree shape and aunt-hash structure are inconsistent, and verification callers must propagate that failure before comparing or returning a root hash. Verification notes: The patch does not by itself prove remote exploitability. The patch does not prove arbitrary non-empty Merkle membership forgery. The patch does not show consensus impact or chain-wide state compromise. The patch does not identify which higher-level callers could supply attacker-controlled malformed proofs. The test helper changes alone are not security-relevant without the proof verification changes. No higher-level attacker-controlled call path is shown in the provided evidence. No proof of consensus impact is provided. The security classification rests on the commit subject plus focused changes in Merkle proof verification behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `merkle-proof-structural-validation`
Final impact type: `integrity, proof-forgery-prevention`
Final confidence: `high`
Final tags: `cryptography, merkle-proof, proof-validation, error-propagation`

The supplied metadata and patch evidence support retaining this as a security fix. The commit subject explicitly identifies an empty Merkle tree forging attack vector, and the code changes are focused on rejecting structurally invalid Merkle proofs with explicit errors and propagating those errors through verification and value-proof execution paths. The evidence supports proof-forgery prevention in a cryptographic verification path, but not broader claims such as remote exploitability or consensus compromise.

## Security Evidence

1. Commit subject says: Patch forging empty merkle tree attack vector.
2. Merkle proof reconstruction now errors when total == 1 has non-empty inner hashes.
3. Merkle proof reconstruction now errors when total > 1 has empty inner hashes.
4. Proof.Verify now propagates ComputeRootHash errors before comparing the computed root.
5. ValueOp.Run now propagates ComputeRootHash errors before returning a root hash output.

## Missing Evidence

1. No higher-level attacker-controlled entry point is shown.
2. No exploit demonstration or failing security test is included in the supplied evidence.
3. No evidence proves consensus impact, remote exploitability, or arbitrary non-empty membership forgery.

## Claim Boundaries

1. Supported claim: malformed Merkle proof shapes are now rejected instead of producing ambiguous nil-root behavior.
2. Supported claim: this fixes a proof verification weakness relevant to empty-tree forgery prevention.
3. Unsupported claim: the patch proves chain-wide state compromise or consensus failure.
4. Unsupported claim: the patch proves all Merkle membership forgery variants were possible.
