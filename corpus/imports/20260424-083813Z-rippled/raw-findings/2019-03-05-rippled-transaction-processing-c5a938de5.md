---
case_id: case_20190305_c5a938de5
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2019-03-05
source_refs:
  - git:c5a938de551b24d5df505d4276120e480fb7d828
  - "src/ripple/app/tx/impl/Transactor.cpp:342"
  - "src/ripple/app/tx/impl/SetRegularKey.cpp:67"
  - "src/ripple/app/tx/impl/Transactor.cpp:351"
  - "src/ripple/app/tx/impl/Transactor.cpp:402"
bug_class: regular-key-authorization-hardening
impact_type:
  - authorization-integrity
  - key-management-integrity
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - transaction-signing
  - key-management
  - authorization
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes transaction authorization and SetRegularKey validation so that, under the fixMasterKeyAsRegularKey amendment, an account cannot set sfRegularKey to the same account ID as sfAccount and master-key disable handling is separated from regular-key authorization. The evidence supports a security-relevant authorization correctness fix, but it does not establish a concrete vulnerability such as unauthorized signing, third-party account takeover, or fund theft.

## Observed Patch Facts

1. In `src/ripple/app/tx/impl/Transactor.cpp`, the patch replaces `auto const id = ctx.tx.getAccountID(sfAccount);` with `// Check that the value in the signing key slot is a public key.`.

2. In `src/ripple/app/tx/impl/SetRegularKey.cpp`, the patch replaces `return preflight2(ctx);` with `if (ctx.rules.enabled(fixMasterKeyAsRegularKey)`.

3. In `src/ripple/app/tx/impl/Transactor.cpp`, the patch replaces `auto const pkAccount = calcAccountID (` with `// Look up the account.`.

4. In `src/ripple/app/tx/impl/Transactor.cpp`, the patch adds `// No regular key on account and signing key does not match master key.`.

## Project Context

The changed code sits primarily in `src/ripple/app/tx/impl`, `src/ripple/app/tx`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/ripple/app/tx/impl/SetAccount.cpp`, `src/ripple/app/tx/impl/SetSignerList.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/tx/impl/SetSignerList.cpp`, `src/ripple/app/tx/impl/Payment.cpp`. The strongest project-level identifiers around this patch are `const`, `auto`, `keylet::account`, and `account`.

## Before/After Behavior

Before the patch, the shown SetRegularKey::preflight path reached preflight2(ctx) without a visible check rejecting sfRegularKey equal to sfAccount. After the patch, SetRegularKey::preflight returns temBAD_REGKEY for that case when fixMasterKeyAsRegularKey is enabled. Transactor::checkSingleSign is also reworked to validate the signing public key, derive the signer account ID, load the account ledger entry, read lsfDisableMaster, and handle master-key and regular-key authorization more distinctly.

# Root Cause

The supported root cause is incomplete validation and role separation around master-key versus regular-key signing authority. The evidence does not prove exploitable key-role confusion beyond an account holder being able to configure an invalid or ambiguous regular-key value.

## Walkthrough

1. SetRegularKey::preflight handles validation for setting an account's regular key.

2. The pre-patch evidence shows no visible rejection when sfRegularKey equals sfAccount before preflight2(ctx).

3. The patch adds an amendment-gated check returning temBAD_REGKEY when sfRegularKey identifies the same account as sfAccount.

4. Transactor::checkSingleSign is part of the single-sign transaction authorization path.

5. The patched code validates the signing public key, derives idSigner, loads the account state, and reads lsfDisableMaster.

6. The authorization logic is restructured so master-disabled state is not treated as a blanket regular-key authorization failure.

7. The provided evidence does not show that an attacker could exploit the old behavior against another account.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/tx/impl/SetRegularKey.cpp | 67 | Preflight validation rejects attempts to set the account's master key as sfRegularKey when the amendment is enabled. |
| src/ripple/app/tx/impl/Transactor.cpp | 345 | Single-sign transaction authorization parses the signing public key and derives the signer account ID. |
| src/ripple/app/tx/impl/Transactor.cpp | 351 | Single-sign authorization loads account state and applies lsfDisableMaster separately from regular-key authorization. |
| src/ripple/app/tx/impl/Transactor.cpp | 396 | Authorization failure handling distinguishes invalid master/regular signing cases after the amended checks. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/tx/impl/Transactor.cpp:342` (changes a sensitive control or state-update path)

Before
```cpp
Transactor::checkSingleSign (PreclaimContext const& ctx)
{
    auto const id = ctx.tx.getAccountID(sfAccount);

    auto const sle = ctx.view.read(
        keylet::account(id));
    auto const hasAuthKey     = sle->isFieldPresent (sfRegularKey);
```
After
```cpp
Transactor::checkSingleSign (PreclaimContext const& ctx)
{
    // Check that the value in the signing key slot is a public key.
    auto const pkSigner = ctx.tx.getSigningPubKey();
    if (!publicKeyType(makeSlice(pkSigner)))
    {
        JLOG(ctx.j.trace()) <<
```

## Snippet 2

Context: `src/ripple/app/tx/impl/SetRegularKey.cpp:67` (changes a sensitive control or state-update path)

Before
```cpp
}

    return preflight2(ctx);
}
```
After
```cpp
}


    if (ctx.rules.enabled(fixMasterKeyAsRegularKey)
        && ctx.tx.isFieldPresent(sfRegularKey)
        && (ctx.tx.getAccountID(sfRegularKey) == ctx.tx.getAccountID(sfAccount)))
    {
        return temBAD_REGKEY;
```

## Snippet 3

Context: `src/ripple/app/tx/impl/Transactor.cpp:351` (changes a sensitive control or state-update path)

Before
```cpp
}

    auto const pkAccount = calcAccountID (
        PublicKey (makeSlice (spk)));

    if (pkAccount == id)
    {
        // Authorized to continue.
```
After
```cpp
}

    // Look up the account.
    auto const idSigner = calcAccountID(PublicKey(makeSlice(pkSigner)));
    auto const idAccount = ctx.tx.getAccountID(sfAccount);
    auto const sleAccount = ctx.view.read(keylet::account(idAccount));
    bool const isMasterDisabled = sleAccount->isFlag(lsfDisableMaster);
```

## Snippet 4

Context: `src/ripple/app/tx/impl/Transactor.cpp:402` (changes a sensitive control or state-update path)

Before
```cpp
else
    {
        JLOG(ctx.j.trace()) <<
            "checkSingleSign: Not authorized to use account.";
```
After
```cpp
else
    {
        // No regular key on account and signing key does not match master key.
        // FIXME: Why differentiate this case from tefBAD_AUTH?
        JLOG(ctx.j.trace()) <<
            "checkSingleSign: Not authorized to use account.";
```

# Fix Pattern

Add explicit preflight validation for an invalid key configuration and separate master-key disable checks from regular-key authorization in the single-sign path.

## How It Was Fixed

The fix adds a fixMasterKeyAsRegularKey-gated SetRegularKey::preflight check comparing sfRegularKey with sfAccount and returning temBAD_REGKEY on equality. It also restructures Transactor::checkSingleSign to compute the signer identity and apply master-key disabled logic separately from regular-key authorization.

# Why It Matters

1. Touches transaction signing authorization logic.

2. Prevents an ambiguous regular-key configuration when the amendment is enabled.

3. Clarifies the effect of Disable Master Key on regular-key authorization.

4. Does not establish third-party compromise or direct asset theft from the provided evidence.

# Evidence Notes

Primary evidence is the SetRegularKey.cpp preflight check at line 67 and Transactor.cpp checkSingleSign changes around lines 345, 351, and 396. The commit message explicitly describes a minor technical flaw and amendment-gated behavior. Claims of account takeover, transaction forgery, direct theft, multisignature impact, or broad protocol compromise are unsupported by the supplied evidence. Protocol security invariant: An account should not configure its own master-key account ID as its regular key, and master-key disable handling should not be conflated with regular-key authorization when the fixMasterKeyAsRegularKey amendment is enabled. Verification notes: The patch does not prove an unauthorized third party could set another account's regular key. The patch does not prove direct fund theft or transaction forgery. The patch does not show impact on multisignature authorization paths. The patch is amendment-gated, so behavior depends on fixMasterKeyAsRegularKey being enabled. The evidence supports an authorization-invariant fix, not a broader consensus or serialization vulnerability. Evidence supports an authorization correctness change, not a demonstrated exploit. Behavior depends on fixMasterKeyAsRegularKey being enabled. No proof is provided that an unauthorized party can set another account's regular key. No tests or traces in the supplied evidence prove direct loss of funds or signature forgery. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `regular-key-authorization-hardening`
Final impact type: `authorization-integrity, key-management-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, transaction-signing, key-management, authorization, security-hardening`

The supplied evidence supports retaining this as security hardening, not a demonstrated exploit fix. The patch changes transaction signing authorization and SetRegularKey validation so an account cannot configure its own master key as its regular key when the amendment is enabled, and it separates Disable Master Key handling from regular-key authorization. That is security-sensitive key-management behavior, but the evidence does not prove third-party compromise, signature forgery, or fund theft.

## Security Evidence

1. SetRegularKey::preflight adds an amendment-gated rejection when sfRegularKey equals sfAccount, returning temBAD_REGKEY.
2. Transactor::checkSingleSign is in the transaction authorization path and is reworked around signing public key validation, signer account derivation, account lookup, and lsfDisableMaster handling.
3. Commit metadata explicitly says the flaw allowed specifying the master key as the new regular key and that the amendment prevents Disable Master Key from incorrectly affecting regular keys.
4. The touched subsystem governs signing authority for ledger transactions.

## Missing Evidence

1. No evidence shows an unauthorized third party could set another account's regular key.
2. No evidence demonstrates transaction forgery, account takeover, or direct fund loss.
3. No test output or exploit scenario is provided showing concrete pre-patch abuse.
4. Behavior is amendment-gated, so deployment and activation conditions are not fully established from the patch alone.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim account takeover, theft, consensus failure, or broad protocol compromise.
3. Claims should be limited to regular-key/master-key authorization invariant enforcement and corrected master-disable interaction.
4. Impact is key-management and transaction-authorization integrity, not proven confidentiality or availability impact.
