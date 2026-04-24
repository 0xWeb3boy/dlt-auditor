---
case_id: case_20251021_5ebc29c48
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-10-21
source_refs:
  - git:5ebc29c481364a894a16150e5d84b7971c3c1755
  - "src/xrpld/app/tx/detail/VaultWithdraw.cpp:293"
  - "src/xrpld/app/tx/detail/VaultWithdraw.cpp:111"
  - "src/xrpld/app/tx/detail/VaultWithdraw.cpp:53"
  - "src/libxrpl/ledger/View.cpp:1243"
bug_class: reserve-enforcement-bypass
impact_type:
  - state-accounting
  - resource-consumption
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - reserve-enforcement
  - destination-tag-policy
  - ledger-invariant
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes VaultWithdraw handling for non-native self-withdrawals that can create a new holding object. It resolves the effective destination consistently, allows a DestinationTag to be supplied when the destination defaults to the submitter, enforces lsfRequireDestTag on that effective account, and adds a reserve check before addEmptyHolding creates the ledger object.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, the patch replaces `auto const dstAcct = [&]() -> AccountID {` with `auto const dstAcct = ctx_.tx[~sfDestination].value_or(account_);`.

2. In `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, the patch replaces `auto const dstAcct = [&]() -> AccountID {` with `auto const dstAcct = ctx.tx[~sfDestination].value_or(account);`.

3. In `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, the patch replaces `else if (ctx.tx.isFieldPresent(sfDestinationTag))` with `return tesSUCCESS;`.

4. In `src/libxrpl/ledger/View.cpp`, the patch replaces `return trustCreate(` with `// Can the account cover the trust line reserve ?`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, `src/libxrpl/ledger`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/DeleteAccount.cpp`, `src/xrpld/app/tx/detail/SetAccount.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/XChainBridge.cpp`, `src/xrpld/app/tx/detail/Payment.cpp`. The strongest project-level identifiers around this patch are `const`, `dstAcct`, `auto`, and `sfDestination`.

## Before/After Behavior

Before the patch, VaultWithdraw could reach the addEmptyHolding/trustCreate path without an observed reserve check for the additional owner object. It also rejected sfDestinationTag when sfDestination was omitted, even though later logic treated the submitter as the effective destination, which prevented satisfying lsfRequireDestTag for that self-destination case. After the patch, preclaim derives the effective destination with sfDestination or sfAccount, checks the destination account, enforces lsfRequireDestTag there, and addEmptyHolding rejects creation with tecNO_LINE_INSUF_RESERVE if priorBalance cannot cover accountReserve(ownerCount + 1).

# Root Cause

VaultWithdraw and the shared holding-creation helper did not apply the same reserve and effective-destination policy checks expected for a transaction path that can create a new owner object for the submitter.

## Walkthrough

1. A VaultWithdraw transaction may omit sfDestination, making the submitter the effective destination.

2. For non-native vault assets, the apply path can create an empty holding for the submitter when the effective destination is the submitter and is not the asset issuer.

3. Before the fix, the supplied View::addEmptyHolding evidence shows duplicate detection followed by trustCreate, with no reserve check in between.

4. That allowed the observed creation path to lack a priorBalance versus accountReserve(ownerCount + 1) gate before adding an owner object.

5. Before the fix, preflight rejected sfDestinationTag when sfDestination was absent, despite the effective destination defaulting to the submitter.

6. The patch removes that malformed rejection, resolves the effective destination in preclaim, reads the destination account, and enforces lsfRequireDestTag on it.

7. The patch adds an addEmptyHolding reserve check using sfOwnerCount and priorBalance before the holding can be created.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/VaultWithdraw.cpp | 53 | Allows DestinationTag without explicit Destination so the tag can satisfy the submitter's lsfRequireDestTag requirement when the destination defaults to the account. |
| src/xrpld/app/tx/detail/VaultWithdraw.cpp | 111 | Computes the effective destination, verifies the destination account exists, and enforces lsfRequireDestTag on that effective account. |
| src/xrpld/app/tx/detail/VaultWithdraw.cpp | 293 | Calls addEmptyHolding for non-native self-withdrawals where VaultWithdraw may create a holding object for the submitter. |
| src/libxrpl/ledger/View.cpp | 1243 | Checks whether the destination account's prior balance covers the reserve for one additional owner object before creating an empty holding. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/VaultWithdraw.cpp:293` (updates aggregate accounting or lifecycle state)

Before
```cpp
}

    auto const dstAcct = [&]() -> AccountID {
        if (ctx_.tx.isFieldPresent(sfDestination))
            return ctx_.tx.getAccountID(sfDestination);
        return account_;
    }();
```
After
```cpp
}

    auto const dstAcct = ctx_.tx[~sfDestination].value_or(account_);
    if (!vaultAsset.native() &&               //
        dstAcct != vaultAsset.getIssuer() &&  //
        dstAcct == account_)
    {
        if (auto const ter = addEmptyHolding(
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/VaultWithdraw.cpp:111` (updates aggregate accounting or lifecycle state)

Before
```cpp
auto const account = ctx.tx[sfAccount];
    auto const dstAcct = [&]() -> AccountID {
        if (ctx.tx.isFieldPresent(sfDestination))
            return ctx.tx.getAccountID(sfDestination);
        return account;
    }();
```
After
```cpp
auto const account = ctx.tx[sfAccount];
    auto const dstAcct = ctx.tx[~sfDestination].value_or(account);
    auto const sleDst = ctx.view.read(keylet::account(dstAcct));
    if (sleDst == nullptr)
        return account == dstAcct ? tecINTERNAL : tecNO_DST;

    if (sleDst->isFlag(lsfRequireDestTag) &&
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/VaultWithdraw.cpp:53` (updates aggregate accounting or lifecycle state)

Before
```cpp
}
    }
    else if (ctx.tx.isFieldPresent(sfDestinationTag))
    {
        JLOG(ctx.j.debug()) << "VaultWithdraw: sfDestinationTag is set but "
                               "sfDestination is not";
        return temMALFORMED;
    }
```
After
```cpp
}
    }

    return tesSUCCESS;
```

## Snippet 4

Context: `src/libxrpl/ledger/View.cpp:1243` (updates aggregate accounting or lifecycle state)

Before
```cpp
if (view.read(index))
        return tecDUPLICATE;
    return trustCreate(
        view,
```
After
```cpp
if (view.read(index))
        return tecDUPLICATE;

    // Can the account cover the trust line reserve ?
    std::uint32_t const ownerCount = sleDst->at(sfOwnerCount);
    if (priorBalance < view.fees().accountReserve(ownerCount + 1))
        return tecNO_LINE_INSUF_RESERVE;
```

# Fix Pattern

Resolve the effective transaction destination before policy checks, then enforce account existence, destination-tag policy, and reserve requirements at the object-creation boundary.

## How It Was Fixed

VaultWithdraw now derives dstAcct from optional sfDestination or the submitting account, validates the effective destination account, and requires sfDestinationTag when that account has lsfRequireDestTag. The preflight restriction that rejected DestinationTag without an explicit Destination was removed. View::addEmptyHolding now checks whether the account can cover the reserve for one more owner object before calling trustCreate.

# Why It Matters

1. Preserves the reserve invariant for new owner objects created through VaultWithdraw.

2. Keeps destination-tag policy consistent when Destination is omitted but defaults to the submitter.

3. Prevents this path from creating a holding when the account cannot cover the added reserve.

4. Evidence supports reserve and account-policy enforcement, not theft or consensus-divergence claims.

# Evidence Notes

Grounded evidence comes from VaultWithdraw.cpp changes around preflight, preclaim, and doApply, plus View.cpp addEmptyHolding. The commit message explicitly states that VaultWithdraw should enforce reserve before creating a new trust line or MPToken-like object and should enforce lsfRequireDestTag for the transaction submitter. The supplied snippets do not establish direct asset theft, unauthorized withdrawal, consensus divergence, or behavior for paths outside the shown effective self-destination/addEmptyHolding flow. Protocol security invariant: A VaultWithdraw transaction that creates a new non-native holding object for the submitting account must enforce the account reserve for the additional owner object, and destination-tag requirements must be evaluated against the transaction's effective destination even when sfDestination is omitted and defaults to sfAccount. Verification notes: The patch does not prove direct fund theft or unauthorized withdrawal. The evidence does not show consensus divergence by itself. The evidence does not prove the issue applies to explicit third-party destinations after the patch conditions. The evidence does not show whether MPToken and trust-line creation share identical downstream behavior beyond the addEmptyHolding path. The destination-tag change is an account-policy enforcement fix, not proof of asset loss. No independent file inspection or test execution was performed; this review uses only the provided input. The changed test file is listed, but no test contents were provided. The security classification is likely rather than confirmed because exploitability and chain impact are inferred from protocol invariant enforcement, not demonstrated by a provided reproducer. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `reserve-enforcement-bypass`
Final impact type: `state-accounting, resource-consumption`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, reserve-enforcement, destination-tag-policy, ledger-invariant`

The supplied patch evidence supports a security-hardening classification: VaultWithdraw could create a non-native holding object through addEmptyHolding without the newly added reserve check, and the patch also enforces destination-tag policy on the effective destination account. This tightens ledger/account policy invariants in a security-sensitive transaction path, but the evidence does not demonstrate a concrete exploit, asset theft, consensus failure, or proven economic impact, so security-fix/high-confidence claims are too strong.

## Security Evidence

1. Adds an account reserve check before addEmptyHolding proceeds to trustCreate for a new holding object.
2. Patch is in VaultWithdraw transaction processing and shared ledger object creation code.
3. Commit message explicitly says VaultWithdraw should enforce reserve before creating a new object.
4. Preclaim now reads the effective destination account and enforces lsfRequireDestTag when Destination defaults to the submitter.

## Missing Evidence

1. No reproducer or test contents showing an exploitable reserve bypass are provided.
2. No evidence proves direct theft, unauthorized withdrawal, consensus divergence, or node compromise.
3. No quantitative impact is shown for resource exhaustion or economic distortion.
4. No full surrounding code proves all affected MPToken/trust-line paths or third-party destination behavior.

## Claim Boundaries

1. Keep the claim to reserve and destination-tag policy enforcement in VaultWithdraw/addEmptyHolding.
2. Do not claim asset theft or unauthorized withdrawal from the supplied evidence.
3. Do not claim consensus divergence from the supplied evidence alone.
4. Treat this as security hardening of ledger invariants, not a confirmed exploitable vulnerability.
