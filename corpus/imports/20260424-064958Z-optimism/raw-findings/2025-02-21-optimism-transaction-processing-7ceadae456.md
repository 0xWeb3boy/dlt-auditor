---
case_id: case_20250221_7ceadae456
project: optimism
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-02-21
source_refs:
  - git:7ceadae45635aa5203c9a9736a3b8f41b1cfcdad
  - "op-service/signer/blockpayload_args.go:36"
  - "op-node/p2p/signer.go:41"
  - "op-service/signer/client.go:131"
  - "op-node/p2p/signer.go:77"
bug_class: input-validation
impact_type:
  - signature-integrity
confidence: medium
tags:
  - signing
  - input-validation
  - canonicalization
  - p2p
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch clearly tightens and simplifies the block-signing API and validation logic, but the provided evidence does not establish a concrete pre-patch vulnerability. What is supported is a hardening change in a security-relevant signing path: stricter payload-hash and chain-ID checks, and a move from signing based on raw payload bytes toward signing an explicit typed message.

## Observed Patch Facts

1. In `op-service/signer/blockpayload_args.go`, the patch replaces `if len(args.PayloadHash) == 0 {` with `// Check checks that the attributes are set and conform to type assumptions.`.

2. In `op-node/p2p/signer.go`, the patch replaces `func (s *LocalSigner) Sign(ctx context.Context, domain [32]byte, chainID *big.Int, en...` with `func (s *LocalSigner) Sign(ctx context.Context, domain eth.Bytes32, chainID eth.Chain...`.

3. In `op-service/signer/client.go`, the patch adds `func (s *SignerClient) SignBlockPayloadV2(ctx context.Context, args *BlockPayloadArgs...`.

4. In `op-node/p2p/signer.go`, the patch replaces `func (s *RemoteSigner) Sign(ctx context.Context, domain [32]byte, chainID *big.Int, e...` with `func (s *RemoteSigner) Sign(ctx context.Context, domain eth.Bytes32, chainID eth.Chai...`.

## Project Context

The changed code sits primarily in `op-service/signer`, `op-node/p2p`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `op-service/signer/blockpayload_args_test.go`, `op-service/signer/transaction_args.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-service/signer/blockpayload_args_test.go`, `op-node/p2p/signer_test.go`. The strongest project-level identifiers around this patch are `byte`, `args`, `domain`, and `error`.

## Before/After Behavior

Before the patch, signer entry points accepted raw encoded payload bytes and a generic big.Int chain ID, and `BlockPayloadArgs.Check()` only rejected a missing chain ID and an empty payload-hash field. After the patch, signer entry points take typed domain/chain-ID/payload-hash inputs, local signing uses an explicit `BlockSigningMessage`, and validation now rejects chain IDs wider than 256 bits and payload hashes whose length is not exactly 32 bytes.

# Root Cause

The evidence supports a utility/API design issue: the signing path relied on loosely typed inputs and incomplete shape validation, which could permit inconsistent or malformed signing arguments. The evidence does not show a demonstrated exploit, acceptance bug, or attacker-controlled reachability.

## Walkthrough

1. `op-service/signer/blockpayload_args.go` strengthens `Check()` by adding a 256-bit chain-ID bound and requiring `PayloadHash` length to be exactly 32 bytes.

2. `op-node/p2p/signer.go` changes local signing from taking raw `encodedMsg []byte` to taking a typed `payloadHash common.Hash` and building a `BlockSigningMessage` directly.

3. The remote signer in the same file makes the same interface shift, now serializing canonical fields instead of starting from raw payload bytes.

4. `op-service/signer/client.go` adds `SignBlockPayloadV2`, which is consistent with an API cleanup/versioning step around the same signing flow.

5. Tests cited in the input support serialization and message-shape expectations, such as omitting `PayloadBytes` from JSON and producing different signing hashes for different domains.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-service/signer/blockpayload_args.go | 27 | builds and validates canonical block-payload signing arguments, including payload-hash size and chain-id bounds |
| op-node/p2p/signer.go | 39 | local signer now signs a typed block-signing message from domain, chain ID, and payload hash |
| op-node/p2p/signer.go | 70 | remote signer path serializes canonical payload-hash-based arguments for RPC signing |
| op-service/signer/client.go | 118 | RPC client for block-payload signing, including added V2 typed signing call |

## Code Snippets

## Snippet 1

Context: `op-service/signer/blockpayload_args.go:36` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (args *BlockPayloadArgs) Check() error {
	if args.ChainID == nil {
		return errors.New("chainId not specified")
	}
	if len(args.PayloadHash) == 0 {
		return errors.New("payloadHash not specified")
```
After
```go
}

// Check checks that the attributes are set and conform to type assumptions.
func (args *BlockPayloadArgs) Check() error {
	if args.ChainID == nil {
		return errors.New("chainId not specified")
	}
	if args.ChainID.BitLen() > 256 {
```

## Snippet 2

Context: `op-node/p2p/signer.go:41` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (s *LocalSigner) Sign(ctx context.Context, domain [32]byte, chainID *big.Int, encodedMsg []byte) (sig *[65]byte, err error) {
	if s.priv == nil {
		return nil, errors.New("signer is closed")
	}

	blockPayloadArgs := opsigner.NewBlockPayloadArgs(domain, chainID, encodedMsg, nil)
```
After
```go
}

func (s *LocalSigner) Sign(ctx context.Context, domain eth.Bytes32, chainID eth.ChainID, payloadHash common.Hash) (sig *[65]byte, err error) {
	if s.priv == nil {
		return nil, errors.New("signer is closed")
	}
	msg := opsigner.BlockSigningMessage{
		Domain:      domain,
```

## Snippet 3

Context: `op-service/signer/client.go:131` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return signature, nil
}
```
After
```go
return signature, nil
}

func (s *SignerClient) SignBlockPayloadV2(ctx context.Context, args *BlockPayloadArgsV2) (eth.Bytes65, error) {
	var result eth.Bytes65
	if err := s.client.CallContext(ctx, &result, "opsigner_signBlockPayloadV2", args); err != nil {
		return [65]byte{}, fmt.Errorf("opsigner_signBlockPayloadV2 failed: %w", err)
	}
```

## Snippet 4

Context: `op-node/p2p/signer.go:77` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (s *RemoteSigner) Sign(ctx context.Context, domain [32]byte, chainID *big.Int, encodedMsg []byte) (sig *[65]byte, err error) {
	if s.client == nil {
		return nil, errors.New("signer is closed")
	}

	blockPayloadArgs := opsigner.NewBlockPayloadArgs(domain, chainID, encodedMsg, s.sender)
```
After
```go
}

func (s *RemoteSigner) Sign(ctx context.Context, domain eth.Bytes32, chainID eth.ChainID, payloadHash common.Hash) (sig *[65]byte, err error) {
	if s.client == nil {
		return nil, errors.New("signer is closed")
	}

	// We use V1 for now, since the server may not support V2 yet
```

# Fix Pattern

Tighten input validation and replace loosely typed signing inputs with a canonical typed message representation.

## How It Was Fixed

The code now validates exact payload-hash length and chain-ID width, and both local and remote signer paths operate on explicit domain/chain-ID/payload-hash fields instead of reconstructing signing material from raw payload bytes. A versioned RPC method was also added for the typed path.

# Why It Matters

1. Signing code benefits from one unambiguous message shape.

2. Exact field-size checks reduce malformed-input ambiguity.

3. Typed inputs reduce mismatches between local and RPC signing paths.

4. The evidence shows hardening of a security-relevant path, not a proven vulnerability fix.

# Evidence Notes

Supported claims come from the visible validation changes in `op-service/signer/blockpayload_args.go`, the interface and message-construction changes in `op-node/p2p/signer.go`, the added V2 RPC method in `op-service/signer/client.go`, and the cited tests about omitted `PayloadBytes` and domain-sensitive signing hashes. Unsupported stronger claims include prior signature forgery, replay, peer acceptance of invalid signatures, or proof that malformed inputs were reachable in production. Protocol security invariant: Block-signing code should derive signatures from one canonical message format with correctly sized fields, including a 32-byte payload hash and a bounded chain ID. Verification notes: The patch does not prove that invalid signatures were accepted by peers before this change. The patch does not show a demonstrated cross-chain replay or signature-forgery exploit. The diff does not establish that malformed payload hashes or oversized chain IDs were reachable from untrusted input in production. The change may fix signer/verifier consistency and API correctness, not necessarily a user-triggerable vulnerability. The diff supports canonicalization and validation hardening. The diff does not prove exploitability. The diff does not show a concrete security regression being fixed. Security relevance is plausible because the path signs block-related data, but the vulnerability thesis is not established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `input-validation`
Final impact type: `signature-integrity`
Final confidence: `medium`
Final tags: `signing, input-validation, canonicalization, p2p`

The patch is in a security-sensitive block-signing path and clearly tightens validation and canonicalization: it rejects oversized chain IDs, requires a 32-byte payload hash, and moves signer entry points from loosely typed raw payload bytes to an explicit typed signing message. That supports retaining this as security hardening. The evidence does not, however, prove a concrete exploitable pre-patch vulnerability, attacker reachability, signature forgery, or replay acceptance, so this should not be elevated to a confirmed security fix.

## Security Evidence

1. `BlockPayloadArgs.Check()` now rejects chain IDs wider than 256 bits.
2. `BlockPayloadArgs.Check()` now requires `PayloadHash` length to be exactly 32 bytes instead of merely non-empty.
3. Local signing changed from raw `encodedMsg []byte` input to typed `domain` / `chainID` / `payloadHash` fields and constructs a `BlockSigningMessage` directly.
4. Remote signing was changed to serialize explicit canonical fields rather than deriving signing input from raw payload bytes.
5. The added V2 signing RPC supports the typed signing path and is consistent with hardening/canonicalization of a cryptographic interface.
6. Related tests in the provided context emphasize omitted `PayloadBytes` serialization and domain-sensitive signing hashes, which align with message-shape hardening.

## Missing Evidence

1. No proof that malformed payload hashes or oversized chain IDs were reachable from untrusted input before the patch.
2. No evidence that peers accepted invalid signatures or that the old path enabled signature forgery.
3. No evidence of an actual replay, cross-chain confusion, or consensus-impacting incident.
4. No commit text, test, or patch fragment explicitly states a security bug or exploit was fixed.

## Claim Boundaries

1. Supported claim: the commit hardens a security-relevant signing interface through stricter validation and more canonical typed inputs.
2. Unsupported claim: the patch definitively fixes an exploitable vulnerability in production.
3. Unsupported claim: the old implementation allowed signature forgery, replay, or peer acceptance of malformed signatures.
4. The new RPC method may partly be API/versioning cleanup; only the validation and canonicalization changes should be treated as security-relevant evidence.
