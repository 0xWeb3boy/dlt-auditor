---
case_id: case_20150310_6bd5130f1
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2015-03-10
source_refs:
  - git:6bd5130f15beb13ee14bd8615fe79be41fe692bd
  - "src/transactions/TransactionFrame.cpp:312"
  - "src/transactions/TransactionFrame.cpp:257"
  - "src/transactions/TransactionFrame.cpp:76"
  - "src/transactions/TransactionFrame.cpp:219"
bug_class: signature-verification-amplification
impact_type:
  - denial-of-service
  - resource-exhaustion
tags:
  - blockchain-core
  - transaction-processing
  - signature-validation
  - amplification
  - resource-exhaustion
  - denial-of-service
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes a transaction authentication amplification issue. Before the change, the signature-checking loop tried envelope signatures against signer keys with PublicKey::verifySig without the shown hint prefilter. After the change, each decorated signature is indexed, its hint is compared to the candidate public key before verification, successful matches are tracked, and validation/application reject transactions with unused signatures.

## Observed Patch Facts

1. In `src/transactions/TransactionFrame.cpp`, the patch replaces `sqlTx.commit();` with `if (!checkAllSignaturesUsed())`.

2. In `src/transactions/TransactionFrame.cpp`, the patch replaces `bool TransactionFrame::checkValid(Application& app)` with `void TransactionFrame::resetState()`.

3. In `src/transactions/TransactionFrame.cpp`, the patch replaces `for(auto sig : getEnvelope().signatures)` with `for (int i = 0; i < getEnvelope().signatures.size(); i++)`.

4. In `src/transactions/TransactionFrame.cpp`, the patch adds `return checkAllSignaturesUsed();`.

## Project Context

The changed code sits primarily in `src/transactions`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/transactions/TxEnvelopeTests.cpp`, `src/transactions/TransactionFrame.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/transactions/TxEnvelopeTests.cpp`, `src/transactions/TransactionFrame.h`. The strongest project-level identifiers around this patch are `signatures`, `PublicKey::verifySig`, `auto`, and `TransactionFrame::checkValid`.

## Before/After Behavior

Before the patch, TransactionFrame::checkSignature iterated over envelope signatures and signer key weights and called PublicKey::verifySig during that nested matching process. The provided before excerpts do not show per-signature consumed tracking or rejection of unmatched extra signatures. After the patch, checkSignature compares sig.hint with the candidate signer key before calling PublicKey::verifySig on sig.signature, marks mUsedSignatures[i] on success, initializes that tracking in resetState, and calls checkAllSignaturesUsed() from checkValid and apply.

# Root Cause

The pre-fix signature validation path did not use the decorated signature hint as a cheap filter before expensive signature verification in the shown nested signer/signature loop. That allowed supplied signatures to increase verification work across candidate signer keys. The evidence supports verification-cost amplification, not replay, forgery, or threshold bypass.

## Walkthrough

1. A transaction envelope supplies decorated signatures for authorization.

2. Before the fix, TransactionFrame::checkSignature looped over supplied signatures and candidate signer keys and invoked PublicKey::verifySig in that matching process.

3. Without the shown hint check, a signature could trigger verification attempts against keys it was not plausibly intended for.

4. The patch indexes signatures, compares sig.hint to the candidate public key bytes, and only then verifies sig.signature.

5. When verification succeeds, the patch records the corresponding signature as used in mUsedSignatures.

6. resetState initializes mUsedSignatures to match the current envelope signature count.

7. checkValid and apply call checkAllSignaturesUsed(), causing unmatched or extra signatures to fail authentication instead of being ignored on a successful path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/transactions/TransactionFrame.cpp | 76 | Signature threshold/auth check now indexes decorated signatures, filters by key hint before cryptographic verification, and marks matched signatures as used. |
| src/transactions/TransactionFrame.cpp | 257 | Transaction auth state reset initializes per-envelope signature usage tracking. |
| src/transactions/TransactionFrame.cpp | 219 | checkValid rejects transactions when not all supplied signatures were consumed by signature validation. |
| src/transactions/TransactionFrame.cpp | 312 | apply adds a final guard preventing a transaction with unused signatures from committing after operation processing. |
| src/transactions/TransactionFrame.h | 32 | TransactionFrame stores mUsedSignatures state for envelope signature consumption tracking. |
| src/xdr/Stellar-transaction.x | 1 | Transaction envelope signature representation is implicated by the hint-bearing signature change, though the exact XDR lines are not provided. |
| src/transactions/TxEnvelopeTests.cpp | 53 | Transaction envelope tests cover missing/bad signature authentication outcomes around apply/check validation. |

## Code Snippets

## Snippet 1

Context: `src/transactions/TransactionFrame.cpp:312` (changes a sensitive control or state-update path)

Before
```cpp
if (!errorEncountered)
        {
            sqlTx.commit();
            thisTxDelta.commit();
```
After
```cpp
if (!errorEncountered)
        {
            if (!checkAllSignaturesUsed())
            {
                // this should never happen: malformed transaction should not be accepted by nodes
                return false;
            }
```

## Snippet 2

Context: `src/transactions/TransactionFrame.cpp:257` (changes a sensitive control or state-update path)

Before
```cpp
}

bool TransactionFrame::checkValid(Application& app)
{
    mSigningAccount.reset();
    return checkValid(app, false);
}
```
After
```cpp
}

void TransactionFrame::resetState()
{
    mSigningAccount.reset();
    mUsedSignatures = std::vector<bool>(mEnvelope.signatures.size());
}
```

## Snippet 3

Context: `src/transactions/TransactionFrame.cpp:76` (changes signature or replay validation logic)

Before
```cpp
// calculate the weight of the signatures
    int totalWeight = 0;
    for(auto sig : getEnvelope().signatures)
    {
        for(auto it = keyWeights.begin(); it != keyWeights.end(); it++)
        {
            if(PublicKey::verifySig((*it).pubKey, sig, contentsHash))
            {
```
After
```cpp
// calculate the weight of the signatures
    int totalWeight = 0;

    for (int i = 0; i < getEnvelope().signatures.size(); i++)
    {
        auto const& sig = getEnvelope().signatures[i];

        for(auto it = keyWeights.begin(); it != keyWeights.end(); it++)
```

## Snippet 4

Context: `src/transactions/TransactionFrame.cpp:219` (changes a sensitive control or state-update path)

Before
```cpp
}
        }
    }
```
After
```cpp
}
        }
        return checkAllSignaturesUsed();
    }
```

# Fix Pattern

Use cheap signer-binding metadata before costly cryptographic verification, and enforce consumption tracking for supplied authentication material.

## How It Was Fixed

The fix adds hint-based filtering in TransactionFrame::checkSignature, verifies the decorated signature payload only after the hint matches, records successful signature use, initializes usage tracking during resetState, and adds checkAllSignaturesUsed() guards in validation and pre-commit application paths.

# Why It Matters

1. Reduces attacker-controlled public-key verification work during transaction authentication.

2. Prevents unmatched extra signatures from being silently accepted with an otherwise valid transaction.

3. Keeps the security claim scoped to amplification; the evidence does not establish forgery, replay, or threshold bypass.

# Evidence Notes

Strong evidence comes from TransactionFrame.cpp changes around checkSignature, resetState, checkValid, and apply, plus TransactionFrame.h showing mUsedSignatures. The commit subject explicitly says "Use hint in signature to avoid amplification attack". XDR details are not asserted because exact schema lines were not provided. Protocol security invariant: Transaction authentication should avoid attacker-controlled expansion of cryptographic verification work: a supplied decorated signature should be checked against signer candidates using cheap binding metadata before invoking PublicKey::verifySig, and supplied signatures should not be silently ignored after validation. Verification notes: The patch does not prove transaction forgery or threshold bypass existed. The patch does not prove replay acceptance or nonce/sequence misuse. The patch does not quantify the amplification factor or demonstrate a network-level denial-of-service exploit. The evidence does not show that all possible verification-cost amplification paths are eliminated. The XDR schema details are referenced by the changed file list but not shown in the provided excerpts. Supported by direct diff evidence for hint filtering before PublicKey::verifySig. Supported by direct diff evidence for per-signature usage tracking and checkAllSignaturesUsed() guards. No evidence provided for replay acceptance, transaction forgery, threshold bypass, or quantified network-level denial of service. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `signature-verification-amplification`
Final impact type: `denial-of-service, resource-exhaustion`
Final tags: `blockchain-core, transaction-processing, signature-validation, amplification, resource-exhaustion, denial-of-service`

The supplied evidence supports keeping this as a security fix, but the original replay/forgery framing is too strong. The commit subject explicitly identifies an amplification attack, and the patch changes transaction signature validation to use signature hints before expensive public-key verification, track consumed signatures, and reject unused signatures. The supported security claim is verification-cost/resource-amplification mitigation in transaction authentication, not replay, request forgery, or threshold bypass.

## Security Evidence

1. Commit subject says: "Use hint in signature to avoid amplification attack".
2. Signature validation changed from verifying each supplied signature against candidate signer keys to first comparing the decorated signature hint with the public key bytes.
3. Successful signature matches are tracked with mUsedSignatures, initialized per envelope signature count.
4. checkValid and apply add checkAllSignaturesUsed guards, rejecting transactions with unused or unmatched signatures.
5. The changed path is transaction authentication using PublicKey::verifySig in blockchain transaction processing.

## Missing Evidence

1. No proof of replay acceptance, request forgery, or threshold bypass is provided.
2. No exploit demonstration or quantified amplification factor is provided.
3. No evidence shows network-level denial-of-service impact beyond the inferred expensive verification amplification risk.
4. XDR schema changes are listed but not evidenced in detail.

## Claim Boundaries

1. Validate as a fix for signature verification cost amplification/resource exhaustion.
2. Do not claim transaction replay or request forgery from this evidence.
3. Do not claim authentication threshold bypass from this evidence.
4. The unused-signature rejection is supported as part of tightening signature handling, not as proof of a separate concrete exploit.
