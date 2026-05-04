---
case_id: case_20210611_5fd30e32d5
project: avalanchego
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: medium
date: 2021-06-11
source_refs:
  - git:5fd30e32d56fc0a6eced0272d4d1cedda0b2e648
  - "vms/proposervm/block.go:215"
  - "vms/proposervm/block.go:172"
  - "vms/proposervm/vm.go:168"
  - "vms/proposervm/vm.go:89"
bug_class: signature-canonicalization-mismatch
impact_type:
  - consensus-integrity
tags:
  - consensus
  - signature-verification
  - block-authentication
  - canonicalization
  - proposervm
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix for ProposerVM proposer block authentication. The strongest grounded evidence is that signing changed from exported header fields and a stored staking key path to internal header fields and the staking certificate private key, while parent lookup also changed to the internal parent field. The evidence supports a signature/canonicalization mismatch in a consensus block path, but does not prove a concrete exploit or forged-block acceptance trace.

## Observed Patch Facts

1. In `vms/proposervm/block.go`, the patch replaces `if res, err := pb.vm.state.getProBlock(pb.header.PrntID); err == nil {` with `if res, err := pb.vm.state.getProBlock(pb.header.prntID); err == nil {`.

2. In `vms/proposervm/block.go`, the patch replaces `pb.header.Signature = nil` with `pb.header.signature = nil`.

3. In `vms/proposervm/vm.go`, the patch replaces `func (vm *VM) tryParseAsProposerBlock(b []byte) (*marshallingProposerBLock, error) {` with `func (vm *VM) ParseBlock(b []byte) (snowman.Block, error) {`.

4. In `vms/proposervm/vm.go`, the patch replaces `pKey := *ctx.StakingKey` with `vm.stakingCert = ctx.StakingCert`.

## Project Context

The changed code sits primarily in `vms/proposervm`, which anchors the finding in the `cryptography` area of the project. Historical context from `vms/proposervm/block_test.go`, `vms/proposervm/vm_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vms/proposervm/vm_test.go`, `vms/proposervm/block_test.go`. The strongest project-level identifiers around this patch are `header`, `Block`, `state`, and `crypto`.

## Before/After Behavior

Before the patch, ProposerBlock.sign cleared pb.header.Signature, hashed pb.getBytes(), and signed with vm.stakingKey. After the patch, it clears pb.header.signature, hashes pb.getBytes(), obtains a crypto.Signer from pb.vm.stakingCert.PrivateKey, and writes the signature to pb.header.signature. Before the patch, Parent used pb.header.PrntID for state lookup and missing-parent fallback. After the patch, it uses pb.header.prntID. VM initialization also changed from extracting ctx.StakingKey into vm.stakingKey to storing ctx.StakingCert for later signing. Parse/validation paths were also adjusted, including evidence of codec-version and parent validation, but the provided snippets do not fully show signature verification logic.

# Root Cause

The likely root cause was inconsistent use of proposer block header representations and signing key sources in the block authentication path. The evidence shows exported fields such as Signature and PrntID being replaced with internal fields signature and prntID, suggesting the bytes being signed, serialized, looked up, or validated could previously diverge. The exact failing verification scenario is inferred from the patch and commit subject rather than directly demonstrated.

## Walkthrough

1. BuildBlock wraps a Snowman block in a proposer block and calls NewProBlock with signing enabled before verifying, caching, and committing it.

2. NewProBlock calls sign before deriving bytes and the proposer block ID when signing is requested.

3. The old sign path cleared pb.header.Signature and used vm.stakingKey to sign the hash of pb.getBytes().

4. The new sign path clears pb.header.signature, signs the hash of pb.getBytes() with pb.vm.stakingCert.PrivateKey after a crypto.Signer type check, and writes the result back to pb.header.signature.

5. Parent lookup changed from pb.header.PrntID to pb.header.prntID, aligning parent lookup with the internal header field used by the patched path.

6. The provided changed lines also show added or moved codec-version and parent validation, but not enough detail to claim a specific rejected forged-block case.

7. The resulting behavior is a more consistent binding between proposer block bytes, signature field, parent ID, and staking certificate key.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vms/proposervm/block.go | 172 | Signs proposer blocks by clearing the header signature, hashing canonical proposer block bytes, and using the staking certificate private key. |
| vms/proposervm/block.go | 215 | Reads proposer block parent identity from the internal header field used by verification and state lookup. |
| vms/proposervm/vm.go | 138 | Builds proposer blocks around Snowman blocks, verifies them, then caches and commits them. |
| vms/proposervm/vm.go | 168 | Parses serialized proposer blocks and delegates wrapped block parsing before constructing the consensus block object. |
| vms/proposervm/vm.go | 89 | Initializes the VM staking certificate used later for proposer block signing. |

## Code Snippets

## Snippet 1

Context: `vms/proposervm/block.go:215` (changes signature or replay validation logic)

Before
```go
// snowman.Block interface implementation
func (pb *ProposerBlock) Parent() snowman.Block {
	if res, err := pb.vm.state.getProBlock(pb.header.PrntID); err == nil {
		return res
	}

	return &missing.Block{BlkID: pb.header.PrntID}
}
```
After
```go
// snowman.Block interface implementation
func (pb *ProposerBlock) Parent() snowman.Block {
	if res, err := pb.vm.state.getProBlock(pb.header.prntID); err == nil {
		return res
	}

	return &missing.Block{BlkID: pb.header.prntID}
}
```

## Snippet 2

Context: `vms/proposervm/block.go:172` (changes signature or replay validation logic)

Before
```go
func (pb *ProposerBlock) sign() error {
	pb.header.Signature = nil
	msgHash := hashing.ComputeHash256Array(pb.getBytes())
	sig, err := pb.vm.stakingKey.Sign(cryptorand.Reader, msgHash[:], crypto.SHA256)
	if err != nil {
		return err
	}
```
After
```go
func (pb *ProposerBlock) sign() error {
	pb.header.signature = nil
	msgHash := hashing.ComputeHash256Array(pb.getBytes())
	signKey, ok := pb.vm.stakingCert.PrivateKey.(crypto.Signer)
	if !ok {
		return ErrInvalidTLSKey
	}
```

## Snippet 3

Context: `vms/proposervm/vm.go:168` (changes a sensitive control or state-update path)

Before
```go
}

func (vm *VM) tryParseAsProposerBlock(b []byte) (*marshallingProposerBLock, error) {
	var mPb marshallingProposerBLock
	cdcVer, err := cdc.Unmarshal(b, &mPb)

	if err != nil {
		return nil, fmt.Errorf("couldn't unmarshal proposerBlockHeader: %s", err)
```
After
```go
}

func (vm *VM) ParseBlock(b []byte) (snowman.Block, error) {
	var mPb marshallingProposerBLock
	if err := mPb.unmarshal(b); err == nil {
		sb, err := vm.ChainVM.ParseBlock(mPb.wrpdBytes)
		if err != nil {
			return nil, err
```

## Snippet 4

Context: `vms/proposervm/vm.go:89` (changes a sensitive control or state-update path)

Before
```go
vm.state.init(dbManager.Current().Database)

	pKey := *ctx.StakingKey
	signer, ok := pKey.(crypto.Signer)
	if !ok {
		return ErrCannotSignWithKey
	}
```
After
```go
vm.state.init(dbManager.Current().Database)

	vm.stakingCert = ctx.StakingCert

	// TODO: comparison should be with genesis timestamp, not with Now()
```

# Fix Pattern

Use one canonical proposer block header representation for signing, serialization-sensitive field clearing, parent lookup, and validation.

## How It Was Fixed

The patch clears and writes the internal signature field, signs with the staking certificate private key after checking it implements crypto.Signer, reads the parent ID from the internal header field, and stores the staking certificate during VM initialization. It also adjusts proposer block parsing and validation paths, including codec-version and parent checks as shown in the supplied changed lines.

# Why It Matters

1. Consensus block signatures must cover the same bytes validators later verify.

2. A mismatch between exported and internal header fields can undermine signature or identity checks.

3. Parent identity affects proposer block lineage and state lookup.

4. The changed code is on the proposer block build, parse, verify, cache, and commit path.

5. The evidence does not establish funds loss, chain halt, private key compromise, or remote exploitability.

# Evidence Notes

Grounded evidence: vms/proposervm/block.go changes signature clearing/signing from pb.header.Signature and vm.stakingKey to pb.header.signature and pb.vm.stakingCert.PrivateKey; vms/proposervm/block.go changes Parent from pb.header.PrntID to pb.header.prntID; vms/proposervm/vm.go changes initialization to store ctx.StakingCert; vm.go/build flow shows proposer blocks are signed, verified, cached, and committed. Unsupported or downgraded claims: the snippets do not show the full Verify implementation, a failing test, an accepted forged block, remote exploitability, double spend, funds loss, or chain halt. Protocol security invariant: ProposerVM blocks should be signed and verified over one canonical header/byte representation, with the signature field excluded consistently and parent identity read from the same representation used for serialization and validation. Verification notes: The patch does not by itself prove remote exploitability. The evidence does not show a concrete forged-block acceptance trace. The evidence does not prove double-spend, funds loss, or chain halt impact. The evidence does not show private key compromise. The precise before-state failure mode is inferred from changed signing and header-field paths, not from an included failing test body. Classified as likely rather than confirmed because the exact vulnerable verification trace is not included. Kept in the security corpus because the commit subject and code changes directly concern consensus block signature handling. Confidence is medium due to strong security relevance but incomplete exploit evidence. Subsystem narrowed to ProposerVM block authentication rather than generic cryptography or state corruption. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-canonicalization-mismatch`
Final impact type: `consensus-integrity`
Final tags: `consensus, signature-verification, block-authentication, canonicalization, proposervm`

The evidence supports retaining this as security hardening rather than a confirmed security fix. The commit subject directly names signature verification for proposer blocks, and the patch changes how proposer block signatures are cleared, signed, represented, and how parent IDs are read in a consensus block path. However, the supplied snippets do not show the actual verification failure, an accepted forged block, or a concrete exploit trace, so the original state-corruption/security-fix framing is too strong.

## Security Evidence

1. Commit subject says "Fix signature verification for proposer blocks".
2. Signing changed from exported Signature to internal signature before hashing proposer block bytes.
3. Signing key source changed to the staking certificate private key with crypto.Signer validation.
4. Parent lookup changed from exported PrntID to internal prntID in the proposer block consensus path.
5. BuildBlock signs, verifies, caches, and commits proposer blocks, placing the changed behavior on a consensus-sensitive path.

## Missing Evidence

1. No full Verify implementation is provided.
2. No failing test or before-state verification bypass is shown.
3. No evidence of forged-block acceptance, replay, funds loss, or chain halt is provided.
4. No proof that the old behavior was remotely exploitable rather than causing invalid local blocks or interoperability failure.

## Claim Boundaries

1. Classify as security hardening for consensus block authentication, not as a proven exploitable security fix.
2. Do not claim state corruption from the supplied evidence.
3. Do not claim private key compromise, double spend, funds loss, or chain halt.
4. The supported claim is a tightened or corrected proposer block signature/canonicalization path.
