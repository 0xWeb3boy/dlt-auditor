---
case_id: case_20240319_b6bdd9fc5
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-03-19
source_refs:
  - git:b6bdd9fc5de200f345beb3585f4a6aee8d584ddb
  - "x/evm/types/ethtx/tx.pb.go:1694"
  - "x/evm/ante/preprocess_test.go:100"
  - "x/evm/ante/preprocess.go:137"
  - "x/evm/types/ethtx/tx.pb.go:521"
bug_class: signature-message-binding
impact_type:
  - authorization
  - signature-verification
confidence: medium
tags:
  - transaction-processing
  - evm
  - associate-tx
  - signature
  - message-binding
  - ethereum-prefix
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes AssociateTx preprocessing from recovering addresses over common.Hash{} to recovering over Keccak256(CustomMessage). Supporting changes carry CustomMessage through AssociateTx construction and protobuf serialization, and tests now sign an Ethereum Signed Message-prefixed payload. This is plausibly security relevant cryptographic binding work, but the provided evidence does not prove an exploitable vulnerability, replay issue, account takeover, or denial-of-service condition.

## Observed Patch Facts

1. In `x/evm/types/ethtx/tx.pb.go`, the patch replaces `default:` with `case 4:`.

2. In `x/evm/ante/preprocess_test.go`, the patch replaces `emptyHash := common.Hash{}` with `emptyData := make([]byte, 32)`.

3. In `x/evm/ante/preprocess.go`, the patch replaces `evmAddr, seiAddr, pubkey, err := getAddresses(V, R, S, common.Hash{}) // associate tx...` with `// Hash custom message passed in`.

4. In `x/evm/types/ethtx/tx.pb.go`, the patch replaces `if len(m.S) > 0 {` with `if len(m.CustomMessage) > 0 {`.

## Project Context

The changed code sits primarily in `x/evm/types/ethtx`, `x/evm/types`, `x/evm/ante`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/types/ethtx/blob_tx_test.go`, `x/evm/types/ethtx/blob_tx.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/types/ethtx/blob_tx_test.go`, `x/evm/types/ethtx/blob_tx.go`. The strongest project-level identifiers around this patch are `CustomMessage`, `crypto`, `wireType`, and `Hash`.

## Before/After Behavior

Before the patch, AssociateTx preprocessing read V/R/S, adjusted V by 27, and called getAddresses with common.Hash{}, while the test signed an empty hash. After the patch, AssociateTx includes CustomMessage, protobuf marshal/unmarshal handles that field, preprocessing hashes atx.CustomMessage, and the test signs an Ethereum-prefixed custom message and includes it in the transaction.

# Root Cause

The grounded issue is that AssociateTx address recovery was tied to a hard-coded empty hash rather than to bytes carried in the transaction as CustomMessage. The evidence does not establish that this was exploitable; it only shows the verification input changed to a caller-provided message hash.

## Walkthrough

1. AssociateTx is unpacked in x/evm/ante/preprocess.go during EVM transaction preprocessing.

2. For AssociateTx, preprocessing extracts raw V, R, and S signature values and adds 27 to V.

3. Before the change, getAddresses received common.Hash{}, so recovery was performed against a fixed empty hash.

4. The patch adds CustomMessage to AssociateTx construction and generated protobuf marshal/unmarshal support.

5. After the change, preprocessing computes crypto.Keccak256Hash([]byte(atx.CustomMessage)) and passes that hash to getAddresses.

6. The updated test signs an Ethereum Signed Message-prefixed custom message and stores the same string in AssociateTx.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/ante/preprocess.go | 137 | AssociateTx ante preprocessing now hashes CustomMessage and recovers addresses from that message hash instead of a fixed empty hash. |
| x/evm/types/ethtx/associate_tx.go | 10 | AssociateTx construction carries the custom association message alongside raw signature values. |
| x/evm/types/ethtx/tx.pb.go | 521 | Generated protobuf marshal path serializes the new CustomMessage field. |
| x/evm/types/ethtx/tx.pb.go | 1694 | Generated protobuf unmarshal path decodes the new CustomMessage field. |
| x/evm/ante/preprocess_test.go | 100 | Test updates expected association signature from an empty hash to an Ethereum-prefixed custom message hash. |

## Code Snippets

## Snippet 1

Context: `x/evm/types/ethtx/tx.pb.go:1694` (changes a sensitive control or state-update path)

Before
```go
}
			iNdEx = postIndex
		default:
			iNdEx = preIndex
```
After
```go
}
			iNdEx = postIndex
		case 4:
			if wireType != 2 {
				return fmt.Errorf("proto: wrong wireType = %d for field CustomMessage", wireType)
			}
			var stringLen uint64
			for shift := uint(0); ; shift += 7 {
```

## Snippet 2

Context: `x/evm/ante/preprocess_test.go:100` (changes signature or replay validation logic)

Before
```go
testPrivHex := hex.EncodeToString(privKey.Bytes())
	key, _ := crypto.HexToECDSA(testPrivHex)
	emptyHash := common.Hash{}
	sig, err := crypto.Sign(emptyHash[:], key)
	require.Nil(t, err)
	R, S, _, _ := ethtx.DecodeSignature(sig)
	V := big.NewInt(int64(sig[64]))
	txData := ethtx.AssociateTx{V: V.Bytes(), R: R.Bytes(), S: S.Bytes()}
```
After
```go
testPrivHex := hex.EncodeToString(privKey.Bytes())
	key, _ := crypto.HexToECDSA(testPrivHex)

	emptyData := make([]byte, 32)
	prefixedMessage := fmt.Sprintf("\x19Ethereum Signed Message:\n%d", len(emptyData)) + string(emptyData)
	hash := crypto.Keccak256Hash([]byte(prefixedMessage))
	sig, err := crypto.Sign(hash.Bytes(), key)
	require.Nil(t, err)
```

## Snippet 3

Context: `x/evm/ante/preprocess.go:137` (changes signature or replay validation logic)

Before
```go
V, R, S := atx.GetRawSignatureValues()
		V = new(big.Int).Add(V, big.NewInt(27))
		evmAddr, seiAddr, pubkey, err := getAddresses(V, R, S, common.Hash{}) // associate tx should sign over an empty hash
		if err != nil {
			return err
```
After
```go
V, R, S := atx.GetRawSignatureValues()
		V = new(big.Int).Add(V, big.NewInt(27))
		// Hash custom message passed in
		customMessageHash := crypto.Keccak256Hash([]byte(atx.CustomMessage))
		evmAddr, seiAddr, pubkey, err := getAddresses(V, R, S, customMessageHash)
		if err != nil {
			return err
```

## Snippet 4

Context: `x/evm/types/ethtx/tx.pb.go:521` (changes a sensitive control or state-update path)

Before
```go
var l int
	_ = l
	if len(m.S) > 0 {
		i -= len(m.S)
```
After
```go
var l int
	_ = l
	if len(m.CustomMessage) > 0 {
		i -= len(m.CustomMessage)
		copy(dAtA[i:], m.CustomMessage)
		i = encodeVarintTx(dAtA, i, uint64(len(m.CustomMessage)))
		i--
		dAtA[i] = 0x22
```

# Fix Pattern

Carry the message used for signature recovery through transaction encoding and hash that message during preprocessing instead of using a constant placeholder hash.

## How It Was Fixed

The patch added CustomMessage to AssociateTx, serialized and deserialized it as protobuf field 4, populated it in NewAssociateTx, and changed Preprocess to pass Keccak256(CustomMessage) into getAddresses. Tests were updated to sign and verify an Ethereum-prefixed custom message.

# Why It Matters

1. Avoids recovering AssociateTx addresses over a hard-coded empty hash.

2. Aligns the tested recovery path with an Ethereum-prefixed signed message.

3. May improve signature-message binding for EVM association.

4. Impact is not established from the provided evidence alone.

# Evidence Notes

Strong evidence exists for the code behavior change in x/evm/ante/preprocess.go, x/evm/types/ethtx/associate_tx.go, x/evm/types/ethtx/tx.pb.go, and x/evm/ante/preprocess_test.go. The evidence does not support the heuristic baseline claim of panic, malformed-input crash, or liveness failure. It also does not prove account takeover, replay protection failure, required CustomMessage format enforcement, or an independently exploitable vulnerability. Protocol security invariant: If EVM association is intended to prove control over a specific association message, address recovery should use the hash of that signed message rather than a fixed placeholder hash. The provided evidence shows this binding was added, but does not establish the security impact of the prior behavior. Verification notes: The patch does not prove that attackers could associate someone else's EVM address without that key's signature. The patch does not show validation that CustomMessage has a required format beyond being hashed as bytes. The protobuf changes are serialization support, not independently a vulnerability fix. The evidence does not support the heuristic baseline claim of a panic or liveness failure. The patch does not prove replay protection across chains, accounts, or sessions unless enforced elsewhere. Confirmed only from provided snippets; no external code inspection was used. Treat protobuf changes as support code for the new field, not as the root cause. Classified as unclear because security relevance is plausible but exploitability and protocol impact are not demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-message-binding`
Final impact type: `authorization, signature-verification`
Final confidence: `medium`
Final tags: `transaction-processing, evm, associate-tx, signature, message-binding, ethereum-prefix`

The supplied patch evidence supports retaining this as security hardening, not as a proven exploitable security fix. AssociateTx address recovery changed from a hard-coded empty hash to Keccak256(CustomMessage), with protobuf and constructor changes carrying that message and tests updated to sign an Ethereum-prefixed message. That clearly tightens a security-sensitive signature binding path, but the evidence does not prove account takeover, replay, denial of service, or another concrete exploit. The original liveness-failure metadata is misleading and should be narrowed to signature-message binding hardening.

## Security Evidence

1. AssociateTx preprocessing previously recovered addresses using common.Hash{} as the signed message input.
2. The patch now hashes atx.CustomMessage and passes that hash into getAddresses for signature recovery.
3. AssociateTx serialization and construction were extended to carry CustomMessage through the transaction path.
4. The updated test signs an Ethereum Signed Message-prefixed payload and includes that same message in AssociateTx.

## Missing Evidence

1. No proof that an attacker could associate another user's EVM address without a valid signature.
2. No demonstrated replay scenario across accounts, chains, sessions, or messages.
3. No evidence of liveness failure, panic, malformed-input crash, or denial of service.
4. No explicit invariant or validation showing the required CustomMessage format beyond hashing its bytes.

## Claim Boundaries

1. Classify as security hardening because the patch strengthens signature-message binding in transaction preprocessing.
2. Do not claim confirmed exploitability or account takeover from the provided evidence alone.
3. Do not retain the original liveness-failure framing.
4. Treat protobuf changes as support for the hardened signature path, not as an independent vulnerability fix.
