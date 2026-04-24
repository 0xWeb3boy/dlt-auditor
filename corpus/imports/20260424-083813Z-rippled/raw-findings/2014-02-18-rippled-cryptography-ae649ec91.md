---
case_id: case_20140218_ae649ec91
project: rippled
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2014-02-18
source_refs:
  - git:ae649ec91748f2cc48ac935407590b6ffc4cd41c
  - "src/ripple_app/tx/WalletAddTransactor.cpp:40"
  - "src/ripple_app/misc/SerializedTransaction.cpp:218"
  - "src/ripple_data/protocol/RippleAddress.cpp:182"
  - "src/ripple_data/protocol/RippleAddress.cpp:948"
bug_class: signature-canonicalization-hardening
impact_type:
  - transaction-malleability-reduction
tags:
  - cryptography
  - signature
  - ecdsa
  - canonicalization
  - transaction-malleability
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is limited to ECDSA signature canonicalization hardening. The patch makes canonicality policy explicit in signature verification paths, most clearly in `SerializedTransaction::checkSign`, where `tfFullyCanonicalSig` selects `ECDSA::strict` and otherwise uses `ECDSA::not_strict`. The evidence supports a security-relevant acceptance-policy change for transaction signatures, but it does not prove unauthorized signing, account takeover, private-key compromise, or a concrete replay exploit.

## Observed Patch Facts

1. In `src/ripple_app/tx/WalletAddTransactor.cpp`, the patch replaces `if (!naMasterPubKey.accountPublicVerify (Serializer::getSHA512Half (uAuthKeyID.begin...` with `if (!naMasterPubKey.accountPublicVerify (`.

2. In `src/ripple_app/misc/SerializedTransaction.cpp`, the patch replaces `return naAccountPublic.accountPublicVerify (getSigningHash (), getFieldVL (sfTxnSigna...` with `const ECDSA fullyCanonical = (getFlags() & tfFullyCanonicalSig) ?`.

3. In `src/ripple_data/protocol/RippleAddress.cpp`, the patch replaces `bool RippleAddress::verifyNodePublic (uint256 const& hash, const std::string& strSig)...` with `bool RippleAddress::verifyNodePublic (uint256 const& hash, const std::string& strSig,...`.

4. In `src/ripple_data/protocol/RippleAddress.cpp`, the patch replaces `expect (naAccountPublic0.accountPublicVerify (uHash, vucTextSig), "Verify failed.");` with `expect (naAccountPublic0.accountPublicVerify (uHash, vucTextSig, ECDSA::strict), "Ver...`.

## Project Context

The changed code sits primarily in `src/ripple_app/tx`, `src/ripple_app`, `src/ripple_app/misc`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/ripple_data/protocol/RippleAddress.h`, `src/ripple_data/protocol/TER.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple_data/protocol/RippleAddress.h`, `src/ripple_app/ledger/Ledger.cpp`. The strongest project-level identifiers around this patch are `ECDSA::strict`, `accountPublicVerify`, `expect`, and `uHash`.

## Before/After Behavior

Before the patch, transaction and related signature verification call sites invoked verification without an explicit canonicality mode in the shown snippets. After the patch, `SerializedTransaction::checkSign` derives an `ECDSA` mode from `tfFullyCanonicalSig` and passes it to `accountPublicVerify`; `WalletAddTransactor` explicitly passes `ECDSA::not_strict`; and `RippleAddress` helper APIs propagate the caller-selected canonicality mode.

# Root Cause

The prior call sites did not make ECDSA canonicality requirements explicit at the signature-acceptance boundary. That left canonicality policy implicit in lower-level verification defaults rather than tied to transaction flags or path-specific protocol rules.

## Walkthrough

1. A transaction signature is checked in `SerializedTransaction::checkSign` against `getSigningHash()` and `sfTxnSignature`.

2. Previously, the shown call did not pass an explicit ECDSA canonicality requirement.

3. The patch maps `tfFullyCanonicalSig` to `ECDSA::strict` and absence of the flag to `ECDSA::not_strict`.

4. That mode is passed into `accountPublicVerify`, allowing flagged transactions to require fully canonical ECDSA signatures.

5. `RippleAddress` verification helpers are updated to carry the canonicality mode through to lower-level verification.

6. `WalletAddTransactor` explicitly opts its authorization signature check into `ECDSA::not_strict`, so the change is path-specific rather than a blanket strictness change.

7. Unit checks are adjusted to exercise strict and non-strict verification behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple_app/misc/SerializedTransaction.cpp | 218 | transaction signature verification now enforces ECDSA::strict when tfFullyCanonicalSig is set and otherwise permits ECDSA::not_strict |
| src/ripple_app/tx/WalletAddTransactor.cpp | 40 | WalletAdd authorization signature verification explicitly opts into ECDSA::not_strict canonicality policy |
| src/ripple_data/protocol/RippleAddress.cpp | 182 | RippleAddress node-public verification API propagates the requested ECDSA canonicality requirement |
| src/ripple_data/protocol/RippleAddress.cpp | 948 | unit coverage updated to exercise strict and non-strict account signature verification behavior |
| src/ripple_data/protocol/RippleAddress.h | 126 | public account signature verification interface requires an ECDSA canonicality argument |

## Code Snippets

## Snippet 1

Context: `src/ripple_app/tx/WalletAddTransactor.cpp:40` (changes signature or replay validation logic)

Before
```cpp
// FIXME: This should be moved to the transaction's signature check logic and cached
    if (!naMasterPubKey.accountPublicVerify (Serializer::getSHA512Half (uAuthKeyID.begin (), uAuthKeyID.size ()), vucSignature))
    {
        Log::out() << "WalletAdd: unauthorized: bad signature ";
```
After
```cpp
// FIXME: This should be moved to the transaction's signature check logic and cached
    if (!naMasterPubKey.accountPublicVerify (
        Serializer::getSHA512Half (uAuthKeyID.begin (), uAuthKeyID.size ()), vucSignature, ECDSA::not_strict))
    {
        Log::out() << "WalletAdd: unauthorized: bad signature ";
```

## Snippet 2

Context: `src/ripple_app/misc/SerializedTransaction.cpp:218` (changes signature or replay validation logic)

Before
```cpp
try
    {
        return naAccountPublic.accountPublicVerify (getSigningHash (), getFieldVL (sfTxnSignature));
    }
    catch (...)
```
After
```cpp
try
    {
        const ECDSA fullyCanonical = (getFlags() & tfFullyCanonicalSig) ?
                                              ECDSA::strict : ECDSA::not_strict;
        return naAccountPublic.accountPublicVerify (getSigningHash (), getFieldVL (sfTxnSignature), fullyCanonical);
    }
    catch (...)
```

## Snippet 3

Context: `src/ripple_data/protocol/RippleAddress.cpp:182` (changes signature or replay validation logic)

Before
```cpp
}

bool RippleAddress::verifyNodePublic (uint256 const& hash, const std::string& strSig) const
{
    Blob vchSig (strSig.begin (), strSig.end ());

    return verifyNodePublic (hash, vchSig);
}
```
After
```cpp
}

bool RippleAddress::verifyNodePublic (uint256 const& hash, const std::string& strSig, ECDSA fullyCanonical) const
{
    Blob vchSig (strSig.begin (), strSig.end ());

    return verifyNodePublic (hash, vchSig, fullyCanonical);
}
```

## Snippet 4

Context: `src/ripple_data/protocol/RippleAddress.cpp:948` (changes signature or replay validation logic)

Before
```cpp
// Check account signing.
        expect (naAccountPrivate0.accountPrivateSign (uHash, vucTextSig), "Signing failed.");
        expect (naAccountPublic0.accountPublicVerify (uHash, vucTextSig), "Verify failed.");
        expect (!naAccountPublic1.accountPublicVerify (uHash, vucTextSig), "Anti-verify failed.");

        expect (naAccountPrivate1.accountPrivateSign (uHash, vucTextSig), "Signing failed.");
        expect (naAccountPublic1.accountPublicVerify (uHash, vucTextSig), "Verify failed.");
        expect (!naAccountPublic0.accountPublicVerify (uHash, vucTextSig), "Anti-verify failed.");
```
After
```cpp
// Check account signing.
        expect (naAccountPrivate0.accountPrivateSign (uHash, vucTextSig), "Signing failed.");
        expect (naAccountPublic0.accountPublicVerify (uHash, vucTextSig, ECDSA::strict), "Verify failed.");
        expect (!naAccountPublic1.accountPublicVerify (uHash, vucTextSig, ECDSA::not_strict), "Anti-verify failed.");
        expect (!naAccountPublic1.accountPublicVerify (uHash, vucTextSig, ECDSA::strict), "Anti-verify failed.");

        expect (naAccountPrivate1.accountPrivateSign (uHash, vucTextSig), "Signing failed.");
        expect (naAccountPublic1.accountPublicVerify (uHash, vucTextSig, ECDSA::strict), "Verify failed.");
```

# Fix Pattern

Thread an explicit signature-canonicality parameter through verification APIs and select the required policy at each protocol boundary.

## How It Was Fixed

The patch updates verification call sites and helper APIs to accept an `ECDSA` canonicality mode. Transaction signature verification now uses `ECDSA::strict` when `tfFullyCanonicalSig` is set and `ECDSA::not_strict` otherwise, while WalletAdd explicitly keeps non-strict verification for its authorization signature.

# Why It Matters

1. Changes which ECDSA signature encodings are accepted for flagged transactions.

2. Reduces ambiguity around non-canonical signature acceptance.

3. Relevant to signature malleability and transaction mutation hardening.

4. Does not establish arbitrary forgery or key compromise from the supplied evidence.

# Evidence Notes

The strongest evidence is from `SerializedTransaction.cpp`, `WalletAddTransactor.cpp`, `RippleAddress.cpp`, and `RippleAddress.h`. The snippets show canonicality-mode plumbing and transaction-flag-based verification. The supplied evidence does not include the full transaction mutation changes named in the commit subject and does not demonstrate a concrete exploit path. Protocol security invariant: Transaction and authentication signature checks must verify signatures against the expected hash and public key, and any protocol path that requires fully canonical ECDSA signatures must pass that requirement into the verification layer before accepting the signature. Verification notes: The evidence does not prove that invalid signatures could authorize transactions before the patch. The evidence does not prove private key recovery, account takeover, or arbitrary transaction forgery. The evidence does not show whether non-canonical signatures were exploitable across consensus, mempool, or replay boundaries. The WalletAdd path is explicitly left non-strict, so the patch is not a universal rejection of non-canonical ECDSA signatures. The supplied snippets do not show the transaction mutation fixes in detail, only the signature canonicalization behavior. Supported: explicit canonicality policy is added to signature verification paths. Supported: `tfFullyCanonicalSig` selects strict verification in `SerializedTransaction::checkSign`. Supported: WalletAdd remains explicitly non-strict. Not supported: invalid signatures could authorize transactions before the patch. Not supported: account takeover, private-key recovery, or arbitrary transaction forgery. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-canonicalization-hardening`
Final impact type: `transaction-malleability-reduction`
Final tags: `cryptography, signature, ecdsa, canonicalization, transaction-malleability, security-hardening`

The supplied patch evidence supports retaining this as security hardening: transaction signature verification now passes an explicit ECDSA canonicality policy, with `tfFullyCanonicalSig` selecting strict verification. This is security-sensitive signature acceptance behavior and plausibly addresses malleability or transaction mutation risk, but the evidence does not prove an exploitable replay, request forgery, unauthorized signing, or account compromise bug.

## Security Evidence

1. `SerializedTransaction::checkSign` now derives `ECDSA::strict` from `tfFullyCanonicalSig` and passes it to `accountPublicVerify`.
2. `RippleAddress` verification APIs are changed to propagate an explicit canonicality mode.
3. Tests are updated to exercise strict and non-strict signature verification behavior.
4. The commit subject explicitly names signature canonicalization and transaction mutation fixes.

## Missing Evidence

1. No concrete exploit path is shown.
2. No evidence that invalid signatures could previously authorize transactions.
3. No proof of replay, request forgery, account takeover, or private-key compromise.
4. The WalletAdd path explicitly remains `ECDSA::not_strict`, so this is not a blanket rejection of non-canonical signatures.

## Claim Boundaries

1. Supported claim: the patch hardens or clarifies ECDSA signature canonicality enforcement.
2. Supported claim: flagged transactions can require fully canonical signatures after the patch.
3. Unsupported claim: the prior behavior allowed arbitrary signature forgery.
4. Unsupported claim: the evidence proves request forgery or replay impact.
