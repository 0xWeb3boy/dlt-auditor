---
case_id: case_20150322_838f99c3c
project: stellar-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2015-03-22
source_refs:
  - git:838f99c3ce308955a72c343d77100ddb15961142
  - "src/transactions/PaymentOpFrame.cpp:107"
  - "src/transactions/CreateOfferOpFrame.cpp:211"
  - "src/ledger/TrustFrame.cpp:71"
  - "src/transactions/CreateOfferOpFrame.cpp:227"
bug_class: trustline-invariant-enforcement
impact_type:
  - authorization-policy
  - state-integrity
confidence: medium
tags:
  - transactions
  - ledger
  - trustlines
  - authorization-check
  - balance-limit-check
  - invariant-enforcement
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant trustline invariant bypass. The evidence shows transaction paths replacing direct TrustLineEntry.balance arithmetic with TrustFrame::addBalance checks, and the payment path adding an authorization check before accepting funds into a destination trustline. The evidence supports invariant enforcement but does not prove exploitability, asset theft, or consensus impact.

## Observed Patch Facts

1. In `src/transactions/PaymentOpFrame.cpp`, the patch replaces `if (destLine.getTrustLine().limit <` with `if (!destLine.getTrustLine().authorized)`.

2. In `src/transactions/CreateOfferOpFrame.cpp`, the patch replaces `wheatLineSigningAccount.getTrustLine().balance += wheatReceived;` with `if(!wheatLineSigningAccount.addBalance(wheatReceived))`.

3. In `src/ledger/TrustFrame.cpp`, the patch replaces `TrustFrame::isValid() const` with `TrustFrame::addBalance(int64_t delta)`.

4. In `src/transactions/CreateOfferOpFrame.cpp`, the patch replaces `mSheepLineA.getTrustLine().balance -= sheepSent;` with `if(!mSheepLineA.addBalance(-sheepSent))`.

## Project Context

The changed code sits primarily in `src/transactions`, `src/ledger`, which anchors the finding in the `storage` area of the project. Historical context from `src/transactions/ChangeTrustOpFrame.cpp`, `src/ledger/TrustFrame.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/transactions/ChangeTrustOpFrame.cpp`, `src/ledger/TrustFrame.h`. The strongest project-level identifiers around this patch are `getTrustLine`, `balance`, `Payment::LINE_FULL`, and `Payment::NOT_AUTHORIZED`.

## Before/After Behavior

Before the patch, some payment and offer paths directly changed trustline balances with += or -=, with inconsistent local checks. The payment destination path also lacked the shown authorized check before proceeding. After the patch, TrustFrame::addBalance rejects resulting balances above the trustline limit or below zero, payment handling rejects unauthorized destination trustlines, and payment/offer paths use the checked helper instead of direct field mutation.

# Root Cause

Trustline balance mutations were spread across transaction code paths as direct field updates, so limit and nonnegative-balance constraints were not consistently enforced. The provided payment hunk also shows a missing destination-trustline authorization check in that path.

## Walkthrough

1. A transaction path loads a TrustFrame for a non-native asset trustline.

2. Before the patch, selected paths directly adjusted getTrustLine().balance.

3. Those direct updates could bypass the now-centralized checks that the resulting balance is not negative and does not exceed the trustline limit.

4. The payment destination path now rejects unauthorized trustlines with Payment::NOT_AUTHORIZED.

5. TrustFrame::addBalance is introduced as a checked mutation helper.

6. Payment and offer paths now call addBalance and abort when the requested balance change is invalid.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ledger/TrustFrame.cpp | 71 | Introduces TrustFrame::addBalance to enforce trustline limit and nonnegative balance before mutation. |
| src/ledger/TrustFrame.h | 23 | Exposes addBalance as the trustline balance mutation helper. |
| src/transactions/PaymentOpFrame.cpp | 101 | Loads destination trustline and rejects unauthorized trustlines during payment processing. |
| src/transactions/PaymentOpFrame.cpp | 107 | Uses checked balance mutation for received payment amount instead of unchecked direct balance update. |
| src/transactions/CreateOfferOpFrame.cpp | 205 | Credits offer proceeds to the signing account trustline through checked addBalance. |
| src/transactions/CreateOfferOpFrame.cpp | 221 | Debits offered asset from the source trustline through checked addBalance. |
| src/transactions/ChangeTrustOpFrame.cpp | 25 | Surrounding trustline limit path showing limits cannot be set below existing balances. |

## Code Snippets

## Snippet 1

Context: `src/transactions/PaymentOpFrame.cpp:107` (changes bounds, limits, or capacity handling)

Before
```cpp
return false;
            }

            if (destLine.getTrustLine().limit <
                curBReceived + destLine.getTrustLine().balance)
            {
                innerResult().code(Payment::LINE_FULL);
                return false;
```
After
```cpp
return false;
            }
            
            if (!destLine.getTrustLine().authorized)
            {
                innerResult().code(Payment::NOT_AUTHORIZED);
                return false;
            }
```

## Snippet 2

Context: `src/transactions/CreateOfferOpFrame.cpp:211` (changes persisted or aggregate state handling)

Before
```cpp
"have matching trust line");
                }
                wheatLineSigningAccount.getTrustLine().balance += wheatReceived;
                wheatLineSigningAccount.storeChange(delta, db);
            }
```
After
```cpp
"have matching trust line");
                }
                if(!wheatLineSigningAccount.addBalance(wheatReceived))
                {
                    innerResult().code(CreateOffer::UNDERFUNDED);
                    return false;
                }
```

## Snippet 3

Context: `src/ledger/TrustFrame.cpp:71` (changes bounds, limits, or capacity handling)

Before
```cpp
}

bool
TrustFrame::isValid() const
```
After
```cpp
}

bool
TrustFrame::addBalance(int64_t delta)
{
    if(mTrustLine.limit < delta + mTrustLine.balance)
    {
        return false;
```

## Snippet 4

Context: `src/transactions/CreateOfferOpFrame.cpp:227` (changes persisted or aggregate state handling)

Before
```cpp
else
            {
                mSheepLineA.getTrustLine().balance -= sheepSent;
                mSheepLineA.storeChange(delta, db);
            }
```
After
```cpp
else
            {
                if(!mSheepLineA.addBalance(-sheepSent))
                {
                    return false;
                }
                mSheepLineA.storeChange(delta, db);
            }
```

# Fix Pattern

Centralize trustline balance mutation behind a checked helper and replace direct transaction-path balance arithmetic with calls to that helper. Add an explicit authorization gate where payment processing loads the destination trustline.

## How It Was Fixed

The patch adds TrustFrame::addBalance(int64_t delta), which returns false if delta plus the current balance would exceed the trustline limit or fall below zero, and otherwise applies the balance update. PaymentOpFrame.cpp adds a destination trustline authorization check and uses checked mutation. CreateOfferOpFrame.cpp replaces direct trustline credits and debits with addBalance calls and aborts on failure.

# Why It Matters

1. Preserves trustline balance limits.

2. Prevents checked debit paths from producing negative trustline balances.

3. Rejects payments to unauthorized destination trustlines in the shown path.

4. Reduces duplicated accounting checks in transaction execution.

5. Does not establish broader claims such as asset theft or consensus failure.

# Evidence Notes

Grounded evidence comes from TrustFrame::addBalance in src/ledger/TrustFrame.cpp and its declaration in TrustFrame.h, plus payment and offer hunks replacing direct balance mutation or adding authorization checks. The ChangeTrustOpFrame context supports the balance-within-limit invariant but is surrounding evidence, not the root cause. The provided material does not include issue #180 details, tests, exploit steps, or full transaction-flow context. Protocol security invariant: Non-native asset trustline balances should only be mutated when the trustline is authorized and the resulting balance remains between zero and the configured trustline limit. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show whether unauthorized trustlines were exploitable in every payment mode. The patch does not prove database corruption beyond invalid trustline balance states. The patch does not establish consensus impact or asset theft without additional transaction-flow evidence. The exact behavior of all touched files is not fully reconstructable from the provided hunks alone. Behavior change is directly supported by the supplied hunks. Security classification is likely, not confirmed, because exploitability is not demonstrated. No claim is made about remote exploitability, asset theft, or consensus impact. Helper files are treated as support for enforcing the invariant, not as an independent vulnerability source. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `trustline-invariant-enforcement`
Final impact type: `authorization-policy, state-integrity`
Final confidence: `medium`
Final tags: `transactions, ledger, trustlines, authorization-check, balance-limit-check, invariant-enforcement`

The supplied patch evidence supports retaining this as security hardening: it adds an explicit authorization check before accepting payments into a destination trustline and centralizes trustline balance mutation behind checks for limit overflow and negative balances. The evidence is strong for tightening security-sensitive ledger invariants, but it does not prove a concrete exploit, asset theft, consensus failure, or database corruption, so `security-fix` and `state-corruption` are too strong.

## Security Evidence

1. Payment path now rejects destination trustlines that are not authorized with `Payment::NOT_AUTHORIZED`.
2. Direct trustline balance arithmetic is replaced with `TrustFrame::addBalance`.
3. `addBalance` rejects resulting balances above the trustline limit.
4. `addBalance` rejects resulting balances below zero.
5. Changed paths are transaction and ledger mutation code for payments and offers.

## Missing Evidence

1. No issue #180 details are provided.
2. No exploit scenario or attacker-controlled flow is shown.
3. No tests demonstrate unauthorized payment acceptance or invalid balance creation before the patch.
4. No evidence proves asset theft, consensus divergence, or persistent database corruption.

## Claim Boundaries

1. Validate only as security hardening, not a proven exploitable security fix.
2. Do not claim confirmed asset theft or consensus impact.
3. Do not classify primarily as database/storage corruption from the shown patch alone.
4. Supported claim is enforcement of trustline authorization and balance invariants in transaction processing.
