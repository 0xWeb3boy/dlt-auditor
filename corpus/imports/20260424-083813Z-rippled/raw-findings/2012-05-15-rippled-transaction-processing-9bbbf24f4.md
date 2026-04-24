---
case_id: case_20120515_9bbbf24f4
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2012-05-15
source_refs:
  - git:9bbbf24f430adad3278cb870a6c5b17476a65182
  - "src/Transaction.cpp:146"
  - "src/TransactionFormats.cpp:19"
  - "src/Transaction.cpp:119"
  - "src/RPCServer.cpp:715"
bug_class: missing-claim-authority-proof
impact_type:
  - authorization-hardening
  - transaction-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - claim-transaction
  - authority-proof
  - signature
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Claim transactions from carrying GeneratorID plus Generator data to carrying Generator, PubKey, and Signature. Transaction builders now serialize the public key and signature, and the wallet Claim RPC signs the generator cipher hash before submitting the transaction. This supports a likely security fix for missing authority proof, with exploitability and enforcement details not fully established by the provided hunks.

## Observed Patch Facts

1. In `src/Transaction.cpp`, the patch replaces `return tResult->setClaim(naPrivateKey, naGeneratorID, vucGenerator);` with `return tResult->setClaim(naPrivateKey, vucGenerator, vucPubKey, vucSignature);`.

2. In `src/TransactionFormats.cpp`, the patch replaces `{ S_FIELD(GeneratorID), STI_HASH160, SOE_REQUIRED, 0 },` with `{ S_FIELD(PubKey), STI_VL, SOE_REQUIRED, 0 },`.

3. In `src/Transaction.cpp`, the patch replaces `const NewcoinAddress& naGeneratorID,` with `const std::vector<unsigned char>& vucGenerator,`.

4. In `src/RPCServer.cpp`, the patch replaces `naRegularReservedPublic, // GeneratorID` with `vucGeneratorCipher,`.

## Project Context

The changed code sits primarily in `src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/Transaction.h`, `src/uint256.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/Transaction.h`, `src/uint256.h`. The strongest project-level identifiers around this patch are `std::vector`, `const`, `vucGenerator`, and `vector`.

## Before/After Behavior

Before the patch, the Claim format required GeneratorID and Generator, and setClaim serialized sfGeneratorID from the supplied address plus sfGenerator. RPC claim construction passed the reserved public address as the GeneratorID. After the patch, the format requires Generator, PubKey, and Signature; setClaim serializes those fields; and RPC claim construction signs the generator cipher hash with the reserved private key and includes the reserved public key and signature.

# Root Cause

The pre-patch Claim transaction representation used an identifier field for the generator instead of embedding public key and signature proof material. The evidence supports a missing proof-material requirement in the transaction format and construction path, but does not independently show how validation handled the old form.

## Walkthrough

1. src/TransactionFormats.cpp removes the required GeneratorID field from Claim transactions.

2. The same Claim format adds required PubKey and Signature variable-length fields.

3. src/Transaction.cpp changes setClaim to accept generator bytes, public key bytes, and signature bytes.

4. setClaim stops writing sfGeneratorID and instead writes sfGenerator, sfPubKey, and sfSignature.

5. sharedClaim forwards the new proof fields into setClaim.

6. RPCServer::doWalletClaim signs Serializer::getSHA512Half(vucGeneratorCipher) with the reserved private key.

7. The RPC path then includes the reserved public key and generated signature in the Claim transaction.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/TransactionFormats.cpp | 19 | Defines Claim transaction required fields, replacing GeneratorID with required PubKey and Signature. |
| src/Transaction.cpp | 119 | Serializes Claim transaction generator, public key, and signature fields. |
| src/Transaction.cpp | 146 | Builds shared Claim transactions using explicit authority proof fields. |
| src/RPCServer.cpp | 715 | Wallet Claim RPC signs the generator cipher and includes public key plus signature in the transaction. |

## Code Snippets

## Snippet 1

Context: `src/Transaction.cpp:146` (changes a sensitive control or state-update path)

Before
```cpp
uSourceTag);

	return tResult->setClaim(naPrivateKey, naGeneratorID, vucGenerator);
}
```
After
```cpp
uSourceTag);

	return tResult->setClaim(naPrivateKey, vucGenerator, vucPubKey, vucSignature);
}
```

## Snippet 2

Context: `src/TransactionFormats.cpp:19` (changes signature or replay validation logic)

Before
```cpp
{ "Claim", ttCLAIM, {
		{ S_FIELD(Flags),        STI_UINT32,  SOE_FLAGS,    0 },
		{ S_FIELD(GeneratorID),  STI_HASH160, SOE_REQUIRED, 0 },
		{ S_FIELD(Generator),    STI_VL,      SOE_REQUIRED, 0 },
		{ S_FIELD(SourceTag),    STI_UINT32,  SOE_IFFLAG,   1 },
		{ S_FIELD(Extensions),   STI_TL,      SOE_IFFLAG,   0x02000000 },
```
After
```cpp
{ "Claim", ttCLAIM, {
		{ S_FIELD(Flags),        STI_UINT32,  SOE_FLAGS,    0 },
		{ S_FIELD(Generator),    STI_VL,      SOE_REQUIRED, 0 },
		{ S_FIELD(PubKey),		 STI_VL,      SOE_REQUIRED, 0 },
		{ S_FIELD(Signature),	 STI_VL,	  SOE_REQUIRED, 0 },
		{ S_FIELD(SourceTag),    STI_UINT32,  SOE_IFFLAG,   1 },
		{ S_FIELD(Extensions),   STI_TL,      SOE_IFFLAG,   0x02000000 },
```

## Snippet 3

Context: `src/Transaction.cpp:119` (changes a sensitive control or state-update path)

Before
```cpp
Transaction::pointer Transaction::setClaim(
	const NewcoinAddress& naPrivateKey,
	const NewcoinAddress& naGeneratorID,
	const std::vector<unsigned char>& vucGenerator)
{
	mTransaction->setITFieldH160(sfGeneratorID, naGeneratorID.getAccountID());
	mTransaction->setITFieldVL(sfGenerator, vucGenerator);
```
After
```cpp
Transaction::pointer Transaction::setClaim(
	const NewcoinAddress& naPrivateKey,
	const std::vector<unsigned char>& vucGenerator,
	const std::vector<unsigned char>& vucPubKey,
	const std::vector<unsigned char>& vucSignature)
{
	mTransaction->setITFieldVL(sfGenerator, vucGenerator);
	mTransaction->setITFieldVL(sfPubKey, vucPubKey);
```

## Snippet 4

Context: `src/RPCServer.cpp:715` (changes aggregate state or economic accounting)

Before
```cpp
naAccountPublic,
			uSourceTag,
			naRegularReservedPublic,	// GeneratorID
			vucGeneratorCipher);

		(void) theApp->getOPs().processTransaction(trns);
```
After
```cpp
naAccountPublic,
			uSourceTag,
			vucGeneratorCipher,
			naRegularReservedPublic.getAccountPublic(),
			vucGeneratorSig);

		(void) theApp->getOPs().processTransaction(trns);
```

# Fix Pattern

Replace identifier-only authority representation with required cryptographic proof fields, and update transaction construction to generate and serialize those proof fields.

## How It Was Fixed

The Claim transaction schema was changed to require PubKey and Signature instead of GeneratorID. Transaction construction APIs were updated to accept and serialize those fields. The wallet RPC path now creates a signature over the generator cipher hash and includes the matching public key and signature in the transaction.

# Why It Matters

1. Claim authority is no longer represented only by an asserted GeneratorID.

2. The serialized transaction now carries public key and signature proof material.

3. Wallet-created Claim transactions now generate proof material before submission.

4. The evidence does not show signature verification, so exact exploitability remains unproven.

# Evidence Notes

Grounded evidence comes from TransactionFormats.cpp adding required PubKey and Signature and removing GeneratorID, Transaction.cpp changing setClaim/sharedClaim to serialize those fields, and RPCServer.cpp signing the generator cipher hash before constructing the Claim. The provided evidence does not include verification logic, rejection behavior, consensus acceptance rules, or a concrete exploit scenario. Protocol security invariant: A Claim transaction should include cryptographic proof material showing authority over the generator data, not only an asserted generator identifier. The provided evidence shows proof fields being added and populated, but does not show the validation path that verifies or rejects claims. Verification notes: No signature verification or rejection path is shown in the provided patch evidence. No concrete exploit scenario is proven by the patch alone. No proof is shown that prior transactions could be accepted by consensus without authority. No evidence is provided about fund theft, key disclosure, or remote code execution. Confirmed by diff evidence that the transaction payload shape changed. Confirmed by diff evidence that wallet RPC now creates and includes a signature. Not confirmed by provided evidence whether signatures are verified during transaction validation. Not confirmed by provided evidence whether pre-patch unauthorized claims were accepted. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-claim-authority-proof`
Final impact type: `authorization-hardening, transaction-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, claim-transaction, authority-proof, signature`

The evidence supports keeping this as security hardening: the Claim transaction format was changed from an asserted GeneratorID to required PubKey and Signature fields, and the wallet RPC now signs the generator cipher before submission. That clearly tightens authority-proof material in a blockchain transaction path. However, the supplied hunks do not show transaction validation, signature verification, rejection behavior, or a demonstrated exploit, so security-fix is too strong.

## Security Evidence

1. Commit subject says Claim transactions are fixed to prove authority.
2. Claim transaction schema removes required GeneratorID and adds required PubKey and Signature fields.
3. Transaction construction now serializes sfPubKey and sfSignature with sfGenerator.
4. Wallet Claim RPC signs the generator cipher hash and includes the public key and signature.

## Missing Evidence

1. No validation path showing the signature is verified.
2. No rejection behavior for invalid or missing authority proof is shown.
3. No evidence that pre-patch unauthorized claims were accepted by consensus.
4. No concrete exploit scenario or impact such as theft, forgery, or privilege escalation is demonstrated.

## Claim Boundaries

1. Supported claim: Claim transaction construction and format were hardened to carry cryptographic authority proof material.
2. Supported claim: the patch is security-relevant because it adds required signature proof fields in a transaction-processing path.
3. Not supported: this definitively fixed an exploitable unauthorized-claim vulnerability.
4. Not supported: specific attacker impact beyond authority-proof weakening.
