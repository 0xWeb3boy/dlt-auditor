---
case_id: case_20250930_e1b234cc5
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-09-30
source_refs:
  - git:e1b234cc515449196371633df18fdaed6166a0f8
  - "src/xrpld/app/tx/detail/Transactor.cpp:690"
  - "src/xrpld/app/tx/detail/Transactor.cpp:773"
  - "src/xrpld/app/tx/detail/Transactor.cpp:661"
  - "src/xrpld/app/tx/detail/Transactor.cpp:709"
bug_class: signature-object-confusion-hardening
impact_type:
  - authorization-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - signature-verification
  - multisig
  - object-confusion
  - least-privilege-api
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch narrows rippled transaction signature-checking helpers so they no longer receive the full PreclaimContext, and it changes multisign branch selection to inspect sigObject rather than ctx.tx. This supports an object-confusion hardening finding in a security-sensitive authorization path. However, the commit explicitly says no current code uses sigObject as anything other than the transaction, so the evidence does not establish a reachable vulnerability or production signature bypass.

## Observed Patch Facts

1. In `src/xrpld/app/tx/detail/Transactor.cpp`, the patch replaces `if (ctx.tx.isFieldPresent(sfSigners))` with `if (sigObject.isFieldPresent(sfSigners))`.

2. In `src/xrpld/app/tx/detail/Transactor.cpp`, the patch replaces `PreclaimContext const& ctx,` with `ReadView const& view,`.

3. In `src/xrpld/app/tx/detail/Transactor.cpp`, the patch replaces `PreclaimContext const& ctx,` with `ReadView const& view,`.

4. In `src/xrpld/app/tx/detail/Transactor.cpp`, the patch replaces `auto const sleAccount = ctx.view.read(keylet::account(idAccount));` with `auto const sleAccount = view.read(keylet::account(idAccount));`.

## Project Context

The changed code sits primarily in `src/xrpld/app/tx/detail`, `src/xrpld/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/xrpld/app/tx/detail/Transactor.h`, `src/xrpld/app/tx/detail/SetOracle.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/xrpld/app/tx/detail/Transactor.h`, `src/xrpld/app/tx/detail/SetOracle.cpp`. The strongest project-level identifiers around this patch are `const`, `idAccount`, `view`, and `sleAccount`.

## Before/After Behavior

Before the patch, Transactor::checkSign received PreclaimContext plus sigObject, leaving it able to consult ctx.tx while validating sigObject. The multisign path selected on ctx.tx.isFieldPresent(sfSigners). After the patch, checkSign receives only ReadView, ApplyFlags, idAccount, sigObject, and journal, and the multisign path selects on sigObject.isFieldPresent(sfSigners). Related single-sign paths were updated to use the passed ReadView and journal instead of the full context.

# Root Cause

The root cause was an overbroad signature-checking API boundary after sigObject was introduced. The helper could access both the intended signed object and the original transaction through PreclaimContext, creating a wrong-object authorization risk if a future caller supplied a sigObject different from ctx.tx. The provided evidence says that distinct-object case was not currently used.

## Walkthrough

1. PR #5594 introduced sigObject as an object whose signature could be checked separately from the transaction.

2. The pre-fix checkSign still accepted PreclaimContext, which included access to ctx.tx.

3. The pre-fix multisign branch tested ctx.tx.isFieldPresent(sfSigners) while the function also received sigObject.

4. The patch removes PreclaimContext from the signature-checking helper interface and passes only the needed view, flags, object, account, and journal data.

5. The multisign branch now tests sigObject.isFieldPresent(sfSigners), aligning branch selection with the object being checked.

6. Single-sign helper calls were adjusted to use ReadView and journal directly.

7. Because the commit states current callers do not pass a distinct sigObject, no reachable exploit path is established.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/xrpld/app/tx/detail/Transactor.cpp | 661 | checkSign now accepts ReadView, ApplyFlags, sigObject, and journal instead of full PreclaimContext, limiting access to the original transaction while validating signatures. |
| src/xrpld/app/tx/detail/Transactor.cpp | 690 | multisign branch selection now checks sfSigners on sigObject rather than ctx.tx. |
| src/xrpld/app/tx/detail/Transactor.cpp | 709 | account lookup and single-sign dispatch use the passed ReadView and forward only the needed inputs. |
| src/xrpld/app/tx/detail/Transactor.cpp | 773 | checkSingleSign now receives ReadView and journal directly, using view rules without access to ctx.tx. |
| src/xrpld/app/tx/detail/Transactor.h | 32 | context type definition shows PreclaimContext/related transaction context includes the transaction object that the patch avoids passing into signature helpers. |

## Code Snippets

## Snippet 1

Context: `src/xrpld/app/tx/detail/Transactor.cpp:690` (changes a sensitive control or state-update path)

Before
```cpp
// If the pk is empty and not simulate or simulate and signers,
    // then we must be multi-signing.
    if (ctx.tx.isFieldPresent(sfSigners))
    {
        return checkMultiSign(ctx, idAccount, sigObject);
    }
```
After
```cpp
// If the pk is empty and not simulate or simulate and signers,
    // then we must be multi-signing.
    if (sigObject.isFieldPresent(sfSigners))
    {
        return checkMultiSign(view, flags, idAccount, sigObject, j);
    }
```

## Snippet 2

Context: `src/xrpld/app/tx/detail/Transactor.cpp:773` (changes a sensitive control or state-update path)

Before
```cpp
NotTEC
Transactor::checkSingleSign(
    PreclaimContext const& ctx,
    AccountID const& idSigner,
    AccountID const& idAccount,
    std::shared_ptr<SLE const> sleAccount)
{
    bool const isMasterDisabled = sleAccount->isFlag(lsfDisableMaster);
```
After
```cpp
NotTEC
Transactor::checkSingleSign(
    ReadView const& view,
    AccountID const& idSigner,
    AccountID const& idAccount,
    std::shared_ptr<SLE const> sleAccount,
    beast::Journal const j)
{
```

## Snippet 3

Context: `src/xrpld/app/tx/detail/Transactor.cpp:661` (changes a sensitive control or state-update path)

Before
```cpp
NotTEC
Transactor::checkSign(
    PreclaimContext const& ctx,
    AccountID const& idAccount,
    STObject const& sigObject)
{
    auto const pkSigner = sigObject.getFieldVL(sfSigningPubKey);
    // Ignore signature check on batch inner transactions
```
After
```cpp
NotTEC
Transactor::checkSign(
    ReadView const& view,
    ApplyFlags flags,
    AccountID const& idAccount,
    STObject const& sigObject,
    beast::Journal const j)
{
```

## Snippet 4

Context: `src/xrpld/app/tx/detail/Transactor.cpp:709` (changes a sensitive control or state-update path)

Before
```cpp
? idAccount
        : calcAccountID(PublicKey(makeSlice(pkSigner)));
    auto const sleAccount = ctx.view.read(keylet::account(idAccount));
    if (!sleAccount)
        return terNO_ACCOUNT;

    return checkSingleSign(ctx, idSigner, idAccount, sleAccount);
}
```
After
```cpp
? idAccount
        : calcAccountID(PublicKey(makeSlice(pkSigner)));
    auto const sleAccount = view.read(keylet::account(idAccount));
    if (!sleAccount)
        return terNO_ACCOUNT;

    return checkSingleSign(view, idSigner, idAccount, sleAccount, j);
}
```

# Fix Pattern

Apply least-privilege parameter passing at a security-sensitive helper boundary, and ensure authorization branch decisions are derived from the object being validated rather than from a broader context object.

## How It Was Fixed

The patch replaced PreclaimContext parameters in transaction signature-checking helpers with explicit parameters such as ReadView, ApplyFlags, STObject const& sigObject, and beast::Journal. It changed multisign detection from ctx.tx.isFieldPresent(sfSigners) to sigObject.isFieldPresent(sfSigners), and updated account lookup and rule checks to use the passed ReadView.

# Why It Matters

1. Signature authorization should not mix fields from different transaction-like objects.

2. The old API shape could become dangerous if future callers passed a distinct sigObject.

3. The patch reduces the chance of wrong-object authorization decisions.

4. No current unauthorized transaction acceptance is shown.

# Evidence Notes

Strongest evidence is the Transactor.cpp change from ctx.tx.isFieldPresent(sfSigners) to sigObject.isFieldPresent(sfSigners), plus helper signatures changing from PreclaimContext to explicit view/flags/journal parameters. The commit message is also limiting evidence: it says the bug is harmless for now because no code currently uses sigObject as anything other than the transactor. Claims of state corruption, consensus divergence, ledger mutation, or an exploitable signature bypass are unsupported. Protocol security invariant: Signature-checking code should make authorization decisions from the same STObject whose signature is being validated. Ledger view, flags, account state, and logging can be passed separately, but helpers should not retain access to a broader transaction context that contains another candidate object. Verification notes: No current exploitable path is proven because the commit says sigObject is not yet used as anything other than the transaction. No unauthorized transaction acceptance is demonstrated by the provided evidence. No consensus divergence, state corruption, or ledger mutation bug is shown directly. The patch is not evidence that existing production callers could bypass signature checks. Related files such as SetOracle.cpp, DeleteAccount.cpp, and DID.cpp do not establish a vulnerable business-logic path from the provided excerpts. No tests are provided in the input. No current caller using sigObject differently from ctx.tx is shown. Related context snippets do not establish a reachable vulnerable workflow. Classified as security-relevant hardening, not a confirmed security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-object-confusion-hardening`
Final impact type: `authorization-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, signature-verification, multisig, object-confusion, least-privilege-api`

The evidence supports retaining this as security hardening, not as a confirmed security fix. The patch changes signature-checking code so branch decisions are made from the supplied sigObject rather than the broader transaction context, and it removes full PreclaimContext access from helpers in an authorization-sensitive path. However, the commit message explicitly says no current code uses sigObject differently from the transaction, so the evidence does not prove a reachable signature bypass, state corruption, or exploitable production bug.

## Security Evidence

1. Signature-checking helper previously accepted both PreclaimContext and sigObject, allowing access to ctx.tx while validating sigObject.
2. Multisign detection changed from ctx.tx.isFieldPresent(sfSigners) to sigObject.isFieldPresent(sfSigners).
3. The helper API was narrowed from full PreclaimContext to explicit ReadView, flags, sigObject, account, and journal parameters.
4. The changed code is in transaction signature validation, a security-sensitive authorization path.

## Missing Evidence

1. No current caller is shown passing a sigObject different from ctx.tx.
2. The commit states the bug is harmless for now.
3. No test, exploit scenario, or reachable workflow demonstrates unauthorized transaction acceptance.
4. No direct evidence shows state corruption, consensus divergence, or ledger mutation from the old behavior.

## Claim Boundaries

1. Classify as security hardening only, not a confirmed vulnerability fix.
2. Do not claim an exploitable signature bypass from the provided evidence.
3. Do not retain the original state-corruption framing; it is too strong.
4. The supported claim is least-privilege and wrong-object authorization hardening in signature validation.
