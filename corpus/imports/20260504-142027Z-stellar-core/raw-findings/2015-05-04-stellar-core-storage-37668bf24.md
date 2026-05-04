---
case_id: case_20150504_37668bf24
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2015-05-04
source_refs:
  - git:37668bf242b50fea0e46b6482649425326985491
  - "src/transactions/AllowTrustOpFrame.cpp:32"
  - "src/transactions/SetOptionsOpFrame.cpp:51"
  - "src/overlay/TCPPeer.cpp:288"
  - "src/ledger/TrustFrame.cpp:268"
bug_class: authorization-state-invariant
impact_type:
  - authorization-integrity
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - transactions
  - authorization
  - trustlines
  - issuer-controls
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported security-relevant change is in trustline authorization handling. The patch adds checks that block revocation by non-revocable issuers and block setting AUTH_REQUIRED_FLAG or AUTH_REVOCABLE_FLAG after the account has already issued credit with positive-balance trustlines. The TCPPeer logging change is diagnostic only and is not evidence of a vulnerability fix.

## Observed Patch Facts

1. In `src/transactions/AllowTrustOpFrame.cpp`, the patch replaces `Currency ci;` with `if(!(mSourceAccount->getAccount().flags & AUTH_REVOCABLE_FLAG) &&`.

2. In `src/transactions/SetOptionsOpFrame.cpp`, the patch replaces `account.flags = account.flags | *mSetOptions.setFlags;` with `if((*mSetOptions.setFlags & AUTH_REQUIRED_FLAG) ||`.

3. In `src/overlay/TCPPeer.cpp`, the patch replaces `<< "readHeaderHandler error: " << error.message();` with `<< "readHeaderHandler error: " << error.message()`.

4. In `src/ledger/TrustFrame.cpp`, the patch replaces `void` with `bool`.

## Project Context

The changed code sits primarily in `src/transactions`, `src/overlay`, `src/ledger`, which anchors the finding in the `storage` area of the project. Historical context from `src/ledger/OfferFrame.cpp`, `src/transactions/TxTests.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ledger/OfferFrame.cpp`, `src/transactions/TxTests.h`. The strongest project-level identifiers around this patch are `TrustFrame::hasIssued`, `error`, `mSetOptions`, and `setFlags`.

## Before/After Behavior

Before the patch, AllowTrustOpFrame::doApply proceeded after checking AUTH_REQUIRED_FLAG without the shown guard preventing deauthorization by an issuer lacking AUTH_REVOCABLE_FLAG. After the patch, such an operation fails with ALLOW_TRUST_CANT_REVOKE. Before the patch, SetOptionsOpFrame::doApply directly ORed setFlags into account.flags. After the patch, attempts to set AUTH_REQUIRED_FLAG or AUTH_REVOCABLE_FLAG first call TrustFrame::hasIssued and fail with SET_OPTIONS_AUTH_SET if positive-balance issued trustlines already exist.

# Root Cause

The pre-fix transaction application paths did not fully enforce authorization-state preconditions before changing or applying issuer authorization semantics for trustlines.

## Walkthrough

1. AllowTrustOpFrame::doApply already checks whether the source account requires authorization before processing allow-trust behavior.

2. The patch adds a second AllowTrust guard for revocation attempts.

3. If mAllowTrust.authorize is false and the source account lacks AUTH_REVOCABLE_FLAG, the operation is rejected with ALLOW_TRUST_CANT_REVOKE.

4. SetOptionsOpFrame::doApply previously applied mSetOptions.setFlags directly to account.flags when setFlags was present.

5. The patch detects attempts to set AUTH_REQUIRED_FLAG or AUTH_REVOCABLE_FLAG.

6. For those flag changes, SetOptions calls TrustFrame::hasIssued(account.accountID, db).

7. TrustFrame::hasIssued queries TrustLines for a row with the issuer account ID and balance greater than zero.

8. If such issued credit exists, SetOptions rejects the flag change with SET_OPTIONS_AUTH_SET.

9. The overlay TCPPeer hunk only adds peer context to a log message and does not support the security classification.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/transactions/AllowTrustOpFrame.cpp | 32 | Rejects trust authorization revocation when issuer lacks AUTH_REVOCABLE_FLAG. |
| src/transactions/SetOptionsOpFrame.cpp | 51 | Rejects enabling authorization-required or revocable flags after the issuer already has issued credit in circulation. |
| src/ledger/TrustFrame.cpp | 268 | Adds hasIssued ledger query used to detect existing positive-balance issued trustlines. |
| src/overlay/TCPPeer.cpp | 288 | Logging context change only; no demonstrated security invariant change. |

## Code Snippets

## Snippet 1

Context: `src/transactions/AllowTrustOpFrame.cpp:32` (changes an authorization or privilege gate)

Before
```cpp
}

    Currency ci;
    ci.type(ISO4217);
```
After
```cpp
}

    if(!(mSourceAccount->getAccount().flags & AUTH_REVOCABLE_FLAG) &&
        !mAllowTrust.authorize)
    {
        innerResult().code(ALLOW_TRUST_CANT_REVOKE);
        return false;
    }
```

## Snippet 2

Context: `src/transactions/SetOptionsOpFrame.cpp:51` (changes persisted or aggregate state handling)

Before
```cpp
if (mSetOptions.setFlags)
    {
        account.flags = account.flags | *mSetOptions.setFlags;
    }
```
After
```cpp
if (mSetOptions.setFlags)
    {
        if((*mSetOptions.setFlags & AUTH_REQUIRED_FLAG) ||
            (*mSetOptions.setFlags & AUTH_REVOCABLE_FLAG))
        {
            // must ensure no one is holding your credit
            if(TrustFrame::hasIssued(account.accountID, db))
            {
```

## Snippet 3

Context: `src/overlay/TCPPeer.cpp:288` (changes a sensitive control or state-update path)

Before
```cpp
mErrorRead.Mark();
            CLOG(DEBUG, "Overlay")
                << "readHeaderHandler error: " << error.message();
        }
        drop();
```
After
```cpp
mErrorRead.Mark();
            CLOG(DEBUG, "Overlay")
                << "readHeaderHandler error: " << error.message() 
                << " :" << toString();
        }
        drop();
```

## Snippet 4

Context: `src/ledger/TrustFrame.cpp:268` (changes bounds, limits, or capacity handling)

Before
```cpp
}

void
TrustFrame::loadLines(details::prepare_temp_type& prep,
```
After
```cpp
}

bool 
TrustFrame::hasIssued(AccountID const& issuerID, Database& db)
{
    std::string accStr;
    accStr = toBase58Check(VER_ACCOUNT_ID, issuerID);
```

# Fix Pattern

Add explicit transaction-level authorization-state precondition checks before mutating account flags or trust authorization state.

## How It Was Fixed

The fix adds a revocation guard in AllowTrustOpFrame::doApply, adds a SetOptions precondition for authorization-related flags, and introduces TrustFrame::hasIssued as the ledger predicate for detecting existing positive-balance issued trustlines.

# Why It Matters

1. Prevents issuers without revocation authority from revoking trust authorization.

2. Prevents authorization semantics from being introduced retroactively after credit is already issued.

3. Keeps account authorization flags consistent with existing trustline balances.

4. Does not establish direct theft, remote exploitability, consensus divergence, or ledger corruption from the supplied evidence.

# Evidence Notes

Primary evidence is the added AllowTrustOpFrame::doApply check for AUTH_REVOCABLE_FLAG, the added SetOptionsOpFrame::doApply check around AUTH_REQUIRED_FLAG and AUTH_REVOCABLE_FLAG, and the new TrustFrame::hasIssued query for positive-balance TrustLines by issuer. XDR files are listed as changed, but no XDR hunks are provided. The TCPPeer change is logging only. Protocol security invariant: Issuer authorization controls for holding credit must be consistent with current trustline state: an issuer without AUTH_REVOCABLE_FLAG must not revoke holder authorization, and authorization-related flags must not be enabled after the issuer already has positive-balance issued trustlines. Verification notes: Patch evidence does not prove remote exploitability. Patch evidence does not prove direct fund theft. Patch evidence does not prove consensus divergence or ledger corruption. Overlay logging change is not shown to fix a security issue. Exact behavior of XDR changes is not shown in the provided hunks. Economic impact on existing trustline holders is inferred from authorization-state rules, not demonstrated by tests. Supported by provided hunks in AllowTrustOpFrame.cpp, SetOptionsOpFrame.cpp, and TrustFrame.cpp. No supplied evidence proves exploitability beyond invalid authorization-state transitions. No supplied tests or advisory confirm impact, so verdict remains likely rather than confirmed. Helper query TrustFrame::hasIssued is support code, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-state-invariant`
Final impact type: `authorization-integrity, state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, transactions, authorization, trustlines, issuer-controls`

The supplied patch evidence supports a security-relevant authorization hardening case, but not a confirmed exploit or state-corruption security fix. The strongest evidence is that transaction application now rejects trust revocation by issuers without AUTH_REVOCABLE_FLAG and rejects enabling authorization-related issuer flags after positive-balance trustlines already exist. That tightens security-sensitive issuer authorization semantics in ledger state, while the TCPPeer hunk is only diagnostic logging.

## Security Evidence

1. AllowTrustOpFrame now rejects deauthorization when the source account lacks AUTH_REVOCABLE_FLAG.
2. SetOptionsOpFrame now checks AUTH_REQUIRED_FLAG and AUTH_REVOCABLE_FLAG changes before applying account flags.
3. SetOptionsOpFrame rejects those flag changes when TrustFrame::hasIssued finds positive-balance issued trustlines.
4. TrustFrame::hasIssued adds a ledger query for existing positive-balance trustlines by issuer, supporting the new authorization precondition.

## Missing Evidence

1. No advisory, test, or commit body proves a concrete vulnerability or exploit scenario.
2. No supplied evidence shows theft, remote exploitability, consensus divergence, or ledger corruption.
3. The XDR file changes are listed but not shown, so their security relevance cannot be assessed.
4. The TCPPeer change only adds logging context and does not support the security classification.

## Claim Boundaries

1. Keep the corpus entry as authorization hardening, not as a confirmed security fix.
2. Do not claim direct fund loss, state corruption, or consensus failure from the supplied patch alone.
3. Do not treat the overlay logging hunk as security evidence.
4. The supported claim is limited to stricter trustline issuer authorization-state preconditions.
