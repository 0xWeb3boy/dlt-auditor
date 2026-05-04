---
case_id: case_20150228_117a83b23
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
impact_type:
  - state-integrity
confidence: medium
source_quality: medium
date: 2015-02-28
source_refs:
  - git:117a83b2312d287ffdc73eecc6dd9db22d9471ee
  - "src/transactions/OfferTests.cpp:196"
  - "src/transactions/TransactionFrame.cpp:129"
  - "src/ledger/AccountFrame.cpp:189"
  - "src/transactions/OfferTests.cpp:180"
bug_class: improper-transaction-sequence-validation
tags:
  - blockchain-core
  - transaction-processing
  - sequence-validation
  - state-integrity
  - database
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The best-supported finding is a likely transaction sequencing fix. The patch adds a sequence check in `TransactionFrame::apply` after `checkValid(app)` and changes `AccountFrame::getSeq` so persisted sequence lookup is scoped by both account and sequence slot. The evidence supports a sequencing-invariant issue, but does not establish a concrete exploit such as theft, replay success, or consensus divergence.

## Observed Patch Facts

1. In `src/transactions/OfferTests.cpp`, the patch replaces `uint32_t ownA1Seq = a1_seq++;` with `uint64_t beforeID = delta.getCurrentID();`.

2. In `src/transactions/TransactionFrame.cpp`, the patch replaces `res = true;` with `// this can't be done in checkValid since we should still flood txs`.

3. In `src/ledger/AccountFrame.cpp`, the patch replaces `session << "SELECT seqNum from SeqSlots where accountID=:v1",` with `session << "SELECT seqNum from SeqSlots where accountID=:v1 and seqSlot=:v2",`.

4. In `src/transactions/OfferTests.cpp`, the patch replaces `for (auto a1Offer : a1OfferSeq)` with `for (auto a1Offer : a1OfferID)`.

## Project Context

The changed code sits primarily in `src/transactions`, `src/ledger`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/transactions/CreateOfferFrame.cpp`, `src/transactions/CancelOfferFrame.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/transactions/CreateOfferFrame.cpp`, `src/transactions/MergeFrame.cpp`. The strongest project-level identifiers around this patch are `CreateOffer::CROSS_SELF`, `OfferFrame::loadOffer`, `a1Offer`, and `retNum`.

## Before/After Behavior

Before the patch, the shown `TransactionFrame::apply` path continued after `checkValid(app)` by setting `res = true`, with no shown per-slot sequence comparison at that point. After the patch, it compares `mSigningAccount->getSeq(mEnvelope.tx.seqSlot, app.getDatabase()) + 1` to `mEnvelope.tx.seqNum`; on mismatch it sets `txBAD_SEQ` and returns before normal application. Before the patch, `AccountFrame::getSeq` queried `SeqSlots` by `accountID` only. After the patch, it queries by both `accountID` and `seqSlot`. Offer tests were adjusted to use offer IDs and ledger current ID behavior, but those test changes are supporting context rather than the root cause.

# Root Cause

The grounded root cause is incomplete or incorrectly scoped transaction sequence enforcement in the provided code path: the application path gained an explicit bad-sequence guard, and the sequence lookup helper changed from an account-only database lookup to an account-plus-slot lookup.

## Walkthrough

1. A transaction reaches `TransactionFrame::apply` and passes `checkValid(app)`.

2. In the pre-patch excerpt, execution then continued with `res = true`; the provided evidence does not show a per-slot sequence check before downstream application.

3. `AccountFrame::getSeq` previously selected `seqNum` from `SeqSlots` using only `accountID`, despite accepting a `slot` argument.

4. The patch changes `getSeq` to select by both `accountID` and `seqSlot`.

5. The patch adds an `apply` guard comparing the slot-specific stored sequence plus one against the envelope transaction sequence number.

6. If the comparison fails, the patched code sets `txBAD_SEQ` and returns `true`, with the comment indicating fee-claiming behavior is preserved.

7. Offer tests were updated around offer IDs and current ledger ID behavior; they do not independently prove the vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/transactions/TransactionFrame.cpp | 129 | Adds pre-application bad-sequence guard for the signing account and sequence slot. |
| src/ledger/AccountFrame.cpp | 189 | Reads sequence state scoped by accountID and seqSlot instead of account-only lookup. |
| src/transactions/OfferTests.cpp | 196 | Updates offer self-cross test expectation to use ledger ID behavior rather than sequence-number lookup. |
| src/transactions/OfferTests.cpp | 180 | Updates offer preservation assertions to use offer IDs rather than offer sequence values. |

## Code Snippets

## Snippet 1

Context: `src/transactions/OfferTests.cpp:196` (changes the branch that decides whether execution stops or continues)

Before
```cpp
// offer is sell 150 USD for 100 USD; sell USD @ 1.5 / buy IRD @ 0.66
            Price exactCross(usdPriceOfferA.d, usdPriceOfferA.n);
            uint32_t ownA1Seq = a1_seq++;

            applyOffer(app, a1, usdCur, idrCur, exactCross, 150 * currencyMultiplier,
                ownA1Seq, CreateOffer::CROSS_SELF);
            REQUIRE(!OfferFrame::loadOffer(a1.getPublicKey(), ownA1Seq, offer, app.getDatabase()));
```
After
```cpp
// offer is sell 150 USD for 100 USD; sell USD @ 1.5 / buy IRD @ 0.66
            Price exactCross(usdPriceOfferA.d, usdPriceOfferA.n);
            
            uint64_t beforeID = delta.getCurrentID();
            applyOffer(app, delta, a1, usdCur, idrCur, exactCross, 150 * currencyMultiplier,
                a1_seq++, CreateOffer::CROSS_SELF);
            REQUIRE(beforeID== delta.getCurrentID());
```

## Snippet 2

Context: `src/transactions/TransactionFrame.cpp:129` (changes a sensitive control or state-update path)

Before
```cpp
if(checkValid(app))
    {
        res = true;
```
After
```cpp
if(checkValid(app))
    {
        // this can't be done in checkValid since we should still flood txs 
        // where seq != envelope.seq
        if(mSigningAccount->getSeq(mEnvelope.tx.seqSlot, app.getDatabase())+1 != mEnvelope.tx.seqNum)
        {
            mResult.body.code(txBAD_SEQ);
            return true;  // needs to return true since it will still claim a fee
```

## Snippet 3

Context: `src/ledger/AccountFrame.cpp:189` (changes a sensitive control or state-update path)

Before
```cpp
uint32_t retNum = 0;

        session << "SELECT seqNum from SeqSlots where accountID=:v1",
            into(retNum);

        return retNum;
    }return mUpdatedSeqNums[slot];
```
After
```cpp
uint32_t retNum = 0;

        session << "SELECT seqNum from SeqSlots where accountID=:v1 and seqSlot=:v2",
            into(retNum),use(base58ID),use(slot);

        return retNum;
    }
```

## Snippet 4

Context: `src/transactions/OfferTests.cpp:180` (changes a sensitive control or state-update path)

Before
```cpp
// and that a1 offers were not touched
            for (auto a1Offer : a1OfferSeq)
            {
                REQUIRE(OfferFrame::loadOffer(a1.getPublicKey(), a1Offer, offer, app.getDatabase()));
```
After
```cpp
// and that a1 offers were not touched
            for (auto a1Offer : a1OfferID)
            {
                REQUIRE(OfferFrame::loadOffer(a1.getPublicKey(), a1Offer, offer, app.getDatabase()));
```

# Fix Pattern

Add an explicit pre-application invariant check and make the supporting state read use the same key dimensions required by that invariant.

## How It Was Fixed

`TransactionFrame::apply` now checks the signing account sequence for `mEnvelope.tx.seqSlot` against `mEnvelope.tx.seqNum` before proceeding. `AccountFrame::getSeq` now queries `SeqSlots` with both `accountID` and `seqSlot`. Related offer tests were updated to avoid sequence-number-derived offer lookup assumptions.

# Why It Matters

1. Bad-sequence transactions are blocked before normal application in the shown path.

2. Sequence validation now uses slot-specific stored state.

3. The patch preserves distinct handling for bad sequence transactions that may still claim a fee.

4. The evidence does not prove a specific exploit or consensus failure.

# Evidence Notes

Strongest evidence is the runtime guard in `src/transactions/TransactionFrame.cpp` and the scoped query change in `src/ledger/AccountFrame.cpp`. The offer test changes are not enough to establish a security issue by themselves. The commit subject `fix tests` weakens confidence, and the provided evidence does not show a concrete attack path. Protocol security invariant: A transaction should not proceed into normal ledger application unless the signing account's stored sequence value for the envelope's declared sequence slot is exactly one less than the transaction sequence number. Verification notes: The patch does not prove a practical replay attack or fund theft path. The patch does not show whether consensus divergence was possible before the change. The offer test updates alone do not establish a security bug. The commit subject is test-oriented, so classification relies on the runtime sequence-check and seqSlot query changes. Classified as likely, not confirmed, because impact is inferred from transaction sequencing semantics. No claim is made that replay, fund theft, or consensus divergence was demonstrated. Helper or test changes are treated as support code, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-transaction-sequence-validation`
Final tags: `blockchain-core, transaction-processing, sequence-validation, state-integrity, database`

The evidence supports retaining this as security-hardening, not a confirmed security-fix. The patch adds an explicit transaction apply-time sequence guard and fixes sequence lookup to include seqSlot, which tightens a security-sensitive blockchain transaction invariant. However, the supplied evidence does not prove a concrete exploit, replay success, fund loss, or consensus divergence, and the commit subject is test-oriented.

## Security Evidence

1. TransactionFrame::apply now rejects transactions whose stored slot sequence plus one does not match the envelope sequence number.
2. AccountFrame::getSeq now scopes persisted sequence lookup by both accountID and seqSlot instead of accountID alone.
3. The changed code is in transaction-processing and ledger state paths where sequence enforcement protects transaction ordering and replay resistance.

## Missing Evidence

1. No commit message or patch comment identifies a security vulnerability.
2. No exploit scenario is demonstrated from the supplied evidence.
3. No evidence shows fund theft, unauthorized transaction acceptance, or consensus divergence before the patch.
4. Offer test changes mostly adjust expectations and do not independently establish security impact.

## Claim Boundaries

1. Classify as hardening of transaction sequence validation, not a proven exploitable security bug.
2. Do not claim confirmed replay, theft, or consensus failure from this evidence alone.
3. Do not rely on the offer test edits as primary vulnerability evidence.
4. The strongest supported impact is preservation of transaction state integrity.
