---
case_id: case_20251021_83ee3788e
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2025-10-21
source_refs:
  - git:83ee3788e1b93c71e4365d94f028c4e950fe4ae9
  - "src/xrpld/app/tx/detail/VaultWithdraw.cpp:293"
  - "src/xrpld/app/tx/detail/VaultWithdraw.cpp:111"
  - "src/xrpld/app/tx/detail/VaultWithdraw.cpp:53"
  - "src/libxrpl/ledger/View.cpp:1243"
bug_class: missing-reserve-check
impact_type:
  - ledger-invariant-bypass
  - economic-policy-bypass
tags:
  - blockchain-core
  - transaction-processing
  - vault-withdraw
  - reserve-enforcement
  - destination-tag-policy
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes VaultWithdraw validation around implicit self-destination handling and reserve enforcement before creating a non-native holding. The supplied evidence supports a protocol validation gap, but does not establish direct theft, consensus failure, memory corruption, or unauthenticated exploitation.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, the patch replaces `auto const dstAcct = [&]() -> AccountID {` with `auto const dstAcct = ctx_.tx[~sfDestination].value_or(account_);`.

2. In `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, the patch replaces `auto const dstAcct = [&]() -> AccountID {` with `auto const dstAcct = ctx.tx[~sfDestination].value_or(account);`.

3. In `src/xrpld/app/tx/detail/VaultWithdraw.cpp`, the patch replaces `else if (ctx.tx.isFieldPresent(sfDestinationTag))` with `return tesSUCCESS;`.

4. In `src/libxrpl/ledger/View.cpp`, the patch replaces `return trustCreate(` with `// Can the account cover the trust line reserve ?`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, `src/libxrpl/ledger`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/DeleteAccount.cpp`, `src/xrpld/app/tx/detail/SetAccount.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/XChainBridge.cpp`, `src/xrpld/app/tx/detail/Payment.cpp`. The strongest project-level identifiers around this patch are `const`, `dstAcct`, `auto`, and `sfDestination`.

## Before/After Behavior

Before the patch, VaultWithdraw rejected DestinationTag when sfDestination was omitted, computed the effective destination with repeated explicit presence checks, and the shown addEmptyHolding path proceeded from duplicate checking toward trustCreate without a reserve check. After the patch, VaultWithdraw treats the destination as sfDestination or the submitting account, checks the effective destination account in preclaim, enforces lsfRequireDestTag on that account, allows DestinationTag with implicit self-destination, and addEmptyHolding rejects creation when prior balance cannot cover accountReserve(ownerCount + 1).

# Root Cause

VaultWithdraw did not consistently apply destination-account policy and owner-reserve requirements to the implicit self-destination path. In the shown holding-creation helper, a new trust line-like owner object could be created without first checking that the affected account had enough prior balance for the increased reserve.

## Walkthrough

1. A VaultWithdraw transaction may omit sfDestination, making the submitting account the effective destination.

2. The old preflight logic rejected DestinationTag solely because sfDestination was absent, which conflicted with implicit self-destination handling.

3. The patched preclaim resolves the effective destination as sfDestination or sfAccount and reads that account from the ledger.

4. The patched preclaim enforces lsfRequireDestTag on the effective destination when DestinationTag is absent.

5. The patched apply path uses the same effective destination expression for the non-native self-withdrawal case that may create a holding.

6. The patched addEmptyHolding checks ownerCount + 1 against the account reserve and returns tecNO_LINE_INSUF_RESERVE when the prior balance is insufficient.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/VaultWithdraw.cpp | 53 | preflight no longer rejects DestinationTag solely because sfDestination is omitted, allowing tag enforcement for implicit self-destination |
| src/xrpld/app/tx/detail/VaultWithdraw.cpp | 111 | preclaim computes effective destination, checks destination account existence, and enforces lsfRequireDestTag when DestinationTag is absent |
| src/xrpld/app/tx/detail/VaultWithdraw.cpp | 293 | doApply computes effective destination and calls addEmptyHolding for non-native self-withdrawal paths that may create a holding object |
| src/libxrpl/ledger/View.cpp | 1243 | addEmptyHolding rejects creation when the destination account prior balance cannot cover owner reserve for one additional object |

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

Resolve the effective destination consistently, then apply destination-account policy and reserve checks before creating ledger owner objects.

## How It Was Fixed

VaultWithdraw now uses ctx.tx[~sfDestination].value_or(account) or account_ to derive the effective destination. Preclaim validates that account and checks lsfRequireDestTag. The malformed preflight rejection for DestinationTag without explicit Destination was removed. addEmptyHolding now checks the destination account OwnerCount and prior balance against the reserve required for one additional owner object before calling trustCreate.

# Why It Matters

1. Prevents a VaultWithdraw path from bypassing the reserve check before creating a new holding.

2. Applies destination-tag requirements to the actual effective destination account.

3. Keeps VaultWithdraw behavior aligned with account-level ledger invariants.

4. Impact beyond reserve-policy bypass is not proven by the supplied evidence.

# Evidence Notes

The finding is grounded in the provided VaultWithdraw preflight, preclaim, and doApply snippets plus the View.cpp addEmptyHolding reserve check. The evidence supports reserve enforcement and lsfRequireDestTag validation. Claims about direct fund theft, consensus failure, aggregate accounting drift, or broad MPToken-specific behavior are not established by the shown code and are therefore excluded or narrowed. Protocol security invariant: VaultWithdraw must apply account-level ledger invariants to the effective destination account: if the transaction can create a new holding object for the submitter, the account must be able to satisfy the added reserve, and if the effective destination has lsfRequireDestTag set, the transaction must include DestinationTag even when Destination defaults to the submitter. Verification notes: No proof of direct fund theft is shown by the patch evidence. No consensus split, memory corruption, or crash condition is shown. No unauthenticated attack path is shown; the path is transaction submission logic. The scope appears limited to VaultWithdraw paths that create a holding for the submitter or enforce destination-tag policy. The evidence does not quantify how much ledger state could be created or the practical cost of abusing the reserve gap. Tests were reportedly updated in src/test/app/Vault_test.cpp, but test contents were not provided. The shown addEmptyHolding evidence demonstrates a trustCreate reserve check; MPToken-specific creation behavior is not independently shown. No exploitability analysis or quantitative abuse scenario is provided. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-reserve-check`
Final impact type: `ledger-invariant-bypass, economic-policy-bypass`
Final tags: `blockchain-core, transaction-processing, vault-withdraw, reserve-enforcement, destination-tag-policy`

The supplied patch evidence supports a security-hardening classification: VaultWithdraw could create a non-native holding/trust-line-like ledger object without first enforcing the account reserve, and the patch adds an explicit reserve check before creation. It also applies lsfRequireDestTag to the effective destination account, including implicit self-destination. The evidence does not prove direct theft, consensus failure, or a concrete exploit path, so the original security-fix framing is too strong.

## Security Evidence

1. Commit message explicitly says VaultWithdraw should enforce reserve before creating a new object.
2. View.cpp adds an owner reserve check before trustCreate/addEmptyHolding proceeds.
3. VaultWithdraw doApply routes non-native self-withdrawal object creation through addEmptyHolding.
4. Preclaim now resolves the effective destination and enforces lsfRequireDestTag on that account.
5. The touched code is transaction-processing logic in a blockchain ledger implementation.

## Missing Evidence

1. No exploit scenario or proof of abuse impact is provided.
2. No evidence shows direct fund theft, authorization bypass, consensus failure, or memory safety impact.
3. Test contents are not supplied, only that tests were changed.
4. MPToken-specific behavior is mentioned in the commit but not independently shown in the provided snippets.

## Claim Boundaries

1. Validate only as reserve and destination-tag policy hardening for VaultWithdraw/addEmptyHolding.
2. Do not claim direct asset theft or arbitrary ledger corruption from the supplied evidence.
3. Do not generalize beyond paths that can create a non-native holding/trust-line-like object for the submitter.
4. Do not treat the DestinationTag change alone as a proven security vulnerability.
