---
case_id: case_20240319_d63321d8e
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2024-03-19
source_refs:
  - git:d63321d8ed8e15b94faf853fa020e08ce6ecc254
  - "x/evm/types/ethtx/tx.pb.go:1694"
  - "x/evm/ante/preprocess_test.go:100"
  - "x/evm/ante/preprocess.go:137"
  - "x/evm/types/ethtx/tx.pb.go:521"
bug_class: weak-signature-message-binding
impact_type:
  - authentication-integrity
tags:
  - transaction-processing
  - evm
  - account-association
  - signature-verification
  - message-binding
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix in the EVM account association path. The patch changes AssociateTx preprocessing from recovering addresses against common.Hash{} to recovering against Keccak256Hash([]byte(atx.CustomMessage)). It also adds CustomMessage to the AssociateTx model, protobuf serialization/deserialization, and tests. The supported issue is weak or missing signature message binding for account association, not a panic, liveness failure, theft of funds, or private-key compromise.

## Observed Patch Facts

1. In `x/evm/types/ethtx/tx.pb.go`, the patch replaces `default:` with `case 4:`.

2. In `x/evm/ante/preprocess_test.go`, the patch replaces `emptyHash := common.Hash{}` with `emptyData := make([]byte, 32)`.

3. In `x/evm/ante/preprocess.go`, the patch replaces `evmAddr, seiAddr, pubkey, err := getAddresses(V, R, S, common.Hash{}) // associate tx...` with `// Hash custom message passed in`.

4. In `x/evm/types/ethtx/tx.pb.go`, the patch replaces `if len(m.S) > 0 {` with `if len(m.CustomMessage) > 0 {`.

## Project Context

The changed code sits primarily in `x/evm/types/ethtx`, `x/evm/types`, `x/evm/ante`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/types/ethtx/blob_tx_test.go`, `x/evm/types/ethtx/blob_tx.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/types/ethtx/blob_tx_test.go`, `x/evm/types/ethtx/blob_tx.go`. The strongest project-level identifiers around this patch are `CustomMessage`, `crypto`, `wireType`, and `Hash`.

## Before/After Behavior

Before the patch, AssociateTx preprocessing extracted V, R, and S, adjusted V, and called getAddresses with common.Hash{}, so signature recovery used a fixed empty hash. After the patch, preprocessing hashes atx.CustomMessage and passes that hash to getAddresses. The patch also adds CustomMessage to AssociateTx construction and protobuf encoding, and updates the test to sign an Ethereum-prefixed message and include that same message in the transaction data.

# Root Cause

AssociateTx verification was not bound to transaction-carried signed message bytes. The ante preprocessing path recovered the EVM signer from a signature over a fixed empty hash rather than from the intended association message. The provided evidence supports a signature binding/domain issue, but does not establish a concrete exploit scenario or impact beyond the association verification weakness.

## Walkthrough

1. AssociateTx data is unpacked in EVM preprocessing.

2. For AssociateTx, preprocessing reads raw signature values V, R, and S and adjusts V by adding 27.

3. Before the fix, getAddresses was called with common.Hash{}, so signer recovery used a fixed hash.

4. The patch adds CustomMessage to the AssociateTx data model and generated protobuf marshal/unmarshal code.

5. After the fix, preprocessing computes Keccak256Hash over atx.CustomMessage and uses that for address recovery.

6. The updated test signs an Ethereum-prefixed custom message and constructs AssociateTx with the same CustomMessage.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/ante/preprocess.go | 137 | Verifies AssociateTx signatures during EVM transaction preprocessing and now recovers addresses from the custom message hash instead of an empty hash. |
| x/evm/types/ethtx/associate_tx.go | 10 | Carries the custom signed message in the AssociateTx data model so verification can bind the signature to the intended message. |
| x/evm/types/ethtx/tx.pb.go | 521 | Serializes the new AssociateTx CustomMessage field into transaction data. |
| x/evm/types/ethtx/tx.pb.go | 1694 | Deserializes the new AssociateTx CustomMessage field from transaction data. |
| x/evm/ante/preprocess_test.go | 100 | Updates association preprocessing test to sign and verify an Ethereum-prefixed custom message instead of a zero hash. |

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

Carry the signed message in the transaction data and bind signature recovery to the hash of those bytes instead of using a constant placeholder hash.

## How It Was Fixed

The fix added CustomMessage to AssociateTx, populated it in NewAssociateTx, serialized/deserialized it as protobuf field 4, and changed preprocessing to hash atx.CustomMessage before recovering addresses. Tests were updated to sign and verify an Ethereum-prefixed custom message rather than an empty hash.

# Why It Matters

1. Keeps account association proofs tied to the message being verified.

2. Avoids accepting signatures against a fixed empty hash for association recovery.

3. Improves signature domain/message binding in a sensitive EVM account-linking path.

4. Impact details are not proven by the provided evidence.

# Evidence Notes

Strongest evidence is x/evm/ante/preprocess.go changing getAddresses from common.Hash{} to Keccak256Hash([]byte(atx.CustomMessage)). Supporting evidence is x/evm/types/ethtx/associate_tx.go carrying CustomMessage, x/evm/types/ethtx/tx.pb.go serializing and deserializing field 4, and x/evm/ante/preprocess_test.go signing an Ethereum-prefixed custom message. The evidence does not support the mapper baseline's panic/liveness claim and does not prove theft, private-key compromise, consensus failure, or node crash. Protocol security invariant: An AssociateTx account association proof should recover the EVM signer from the hash of the exact association message carried with the transaction, not from a fixed empty hash unrelated to the message the user signed. Verification notes: The patch does not prove that an attacker could obtain a victim signature over the previous empty hash. The patch does not prove consensus failure, node crash, or panic-based denial of service. The patch does not show whether old empty-hash AssociateTx signatures were accepted from mempool, block replay, or only local construction paths. The patch does not establish theft of funds or direct private-key compromise. The exact user-facing association message semantics are not fully shown beyond the custom Ethereum-prefixed test message. No command execution or file inspection was performed, per instruction. Classification is based only on the supplied diff excerpts and mapper/draft text. Confidence is medium because the cryptographic binding change is clear, but exploitability and exact user-facing association semantics are not fully shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `weak-signature-message-binding`
Final impact type: `authentication-integrity`
Final tags: `transaction-processing, evm, account-association, signature-verification, message-binding, security-hardening`

The supplied patch evidence supports retaining this as security hardening, not a fully proven security fix. The key behavioral change moves AssociateTx address recovery from a constant empty hash to a hash of a transaction-carried custom message, with protobuf/model/test updates to carry and sign that message. That clearly tightens signature-message binding in a sensitive account association path, but the evidence does not prove a concrete exploit, accepted attacker flow, liveness impact, or funds impact.

## Security Evidence

1. AssociateTx preprocessing previously called getAddresses with common.Hash{} for signature recovery.
2. The patch hashes atx.CustomMessage and uses that hash for getAddresses.
3. AssociateTx is extended to carry CustomMessage through construction and protobuf serialization/deserialization.
4. Tests now sign an Ethereum-prefixed custom message and include that message in the AssociateTx data.

## Missing Evidence

1. No concrete exploit scenario is shown.
2. No proof that an attacker could obtain or replay a useful empty-hash signature is shown.
3. No evidence establishes theft, private-key compromise, node crash, consensus failure, or liveness failure.
4. No full user-facing account association semantics are provided beyond the test message.

## Claim Boundaries

1. Valid claim: the patch strengthens signature recovery by binding it to transaction-carried message bytes.
2. Valid claim: the affected path is security-sensitive account association/signature verification logic.
3. Do not claim proven liveness impact from the supplied evidence.
4. Do not claim a confirmed exploitable vulnerability or direct asset loss from the supplied evidence.
