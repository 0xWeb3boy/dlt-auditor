---
case_id: case_20260409_6eaf0bf18
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2026-04-09
source_refs:
  - git:6eaf0bf1801203e38084f8ebdfb22c6834710e78
  - "src/libxrpl/tx/transactors/delegate/DelegateSet.cpp:103"
  - "src/libxrpl/tx/transactors/delegate/DelegateSet.cpp:138"
  - "include/xrpl/protocol_autogen/ledger_entries/Delegate.h:228"
  - "include/xrpl/protocol_autogen/ledger_entries/Delegate.h:91"
bug_class: authorization-lifecycle-cleanup
impact_type:
  - stale-authorization-state
  - incomplete-account-cleanup
confidence: medium
tags:
  - blockchain-core
  - delegation
  - ledger-indexing
  - account-lifecycle
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds bidirectional owner-directory tracking for Delegate ledger entries. Creation now inserts the Delegate object into the authorized account's owner directory and stores the page in optional sfDestinationNode; deletion now removes the object from that authorized account directory when sfDestinationNode is present. This supports cleanup/discoverability, but the provided evidence does not prove an exploitable stale delegation, privilege bypass, consensus issue, or other vulnerability.

## Observed Patch Facts

1. In `src/libxrpl/tx/transactors/delegate/DelegateSet.cpp`, the patch replaces `ctx_.view().insert(sle);` with `// Add to authorized account's owner directory so the object can be found`.

2. In `src/libxrpl/tx/transactors/delegate/DelegateSet.cpp`, the patch replaces `auto const sleOwner = view.peek(keylet::account(account));` with `// Remove from authorized account's owner directory, if present`.

3. In `include/xrpl/protocol_autogen/ledger_entries/Delegate.h`, the patch replaces `* @brief Set sfPreviousTxnID (soeREQUIRED)` with `* @brief Set sfDestinationNode (soeOPTIONAL)`.

4. In `include/xrpl/protocol_autogen/ledger_entries/Delegate.h`, the patch replaces `* @brief Get sfPreviousTxnID (soeREQUIRED)` with `* @brief Get sfDestinationNode (soeOPTIONAL)`.

## Project Context

The changed code sits primarily in `src/libxrpl/tx/transactors/delegate`, `src/libxrpl/tx/transactors`, `include/xrpl/protocol_autogen/ledger_entries`, which anchors the finding in the `staking` area of the project. Historical context from `include/xrpl/protocol_autogen/ledger_entries/XChainOwnedCreateAccountClaimID.h`, `include/xrpl/protocol_autogen/ledger_entries/PayChannel.h` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `include/xrpl/protocol_autogen/ledger_entries/PayChannel.h`, `include/xrpl/protocol_autogen/ledger_entries/Escrow.h`. The strongest project-level identifiers around this patch are `keylet::ownerDir`, `SF_UINT64::type::value_type`, `account`, and `const`.

## Before/After Behavior

Before the patch, the shown DelegateSet::doApply path inserted the Delegate entry into the delegating account's owner directory and stored sfOwnerNode, with no shown insertion into the authorized account's owner directory. After the patch, it also inserts the entry into keylet::ownerDir(authAccount), returns tecDIR_FULL on failure, and stores the returned page in sfDestinationNode. Before the patch, the shown delete path removed the entry from the delegating account's owner directory. After the patch, it conditionally removes the entry from keylet::ownerDir(delegatee) when sfDestinationNode is present. The generated Delegate wrapper adds optional sfDestinationNode accessors/builders as support code.

# Root Cause

Delegate entries were only shown as indexed through the delegating account's owner directory. The patch indicates this was insufficient for finding and cleaning up the entry from the authorized account side. The evidence supports a one-sided indexing/lifecycle cleanup issue, not a missing authorization check.

## Walkthrough

1. DelegateSet::doApply creates a Delegate ledger entry for a relationship between a delegating account and an authorized account.

2. The pre-patch shown path inserted the Delegate object into the delegating account owner directory and saved that page in sfOwnerNode.

3. The patch adds a second dirInsert into the authorized account owner directory.

4. The page from that second insertion is stored in optional sfDestinationNode.

5. DelegateSet::deleteDelegate removes the object from the delegating account owner directory using sfOwnerNode.

6. The patch adds conditional removal from the authorized account owner directory when sfDestinationNode exists.

7. The generated Delegate wrapper changes expose sfDestinationNode to implementation and tests but are support code.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/libxrpl/tx/transactors/delegate/DelegateSet.cpp | 103 | Creates Delegate ledger entry and now also inserts it into the authorized account owner directory, recording sfDestinationNode. |
| src/libxrpl/tx/transactors/delegate/DelegateSet.cpp | 138 | Deletes Delegate ledger entry and now removes it from the authorized account owner directory when sfDestinationNode is present. |
| include/xrpl/protocol_autogen/ledger_entries/Delegate.h | 91 | Adds generated accessor for optional sfDestinationNode used to track the authorized account directory page. |
| include/xrpl/protocol_autogen/ledger_entries/Delegate.h | 228 | Adds generated builder setter for optional sfDestinationNode. |

## Code Snippets

## Snippet 1

Context: `src/libxrpl/tx/transactors/delegate/DelegateSet.cpp:103` (changes a sensitive control or state-update path)

Before
```cpp
(*sle)[sfOwnerNode] = *page;
    ctx_.view().insert(sle);
    adjustOwnerCount(ctx_.view(), sleOwner, 1, ctx_.journal);
```
After
```cpp
(*sle)[sfOwnerNode] = *page;

    // Add to authorized account's owner directory so the object can be found
    // and cleaned up when the authorized account is deleted.
    auto const destPage = ctx_.view().dirInsert(
        keylet::ownerDir(authAccount), delegateKey, describeOwnerDir(authAccount));
```

## Snippet 2

Context: `src/libxrpl/tx/transactors/delegate/DelegateSet.cpp:138` (changes a sensitive control or state-update path)

Before
```cpp
}

    auto const sleOwner = view.peek(keylet::account(account));
    if (!sleOwner)
        return tecINTERNAL;  // LCOV_EXCL_LINE
```
After
```cpp
}

    // Remove from authorized account's owner directory, if present
    if (auto const optPage = (*sle)[~sfDestinationNode])
    {
        if (!view.dirRemove(keylet::ownerDir(delegatee), *optPage, sle->key(), false))
        {
            // LCOV_EXCL_START
```

## Snippet 3

Context: `include/xrpl/protocol_autogen/ledger_entries/Delegate.h:228` (changes a sensitive control or state-update path)

Before
```c
}

    /**
     * @brief Set sfPreviousTxnID (soeREQUIRED)
```
After
```c
}

    /**
     * @brief Set sfDestinationNode (soeOPTIONAL)
     * @return Reference to this builder for method chaining.
     */
    DelegateBuilder&
    setDestinationNode(std::decay_t<typename SF_UINT64::type::value_type> const& value)
```

## Snippet 4

Context: `include/xrpl/protocol_autogen/ledger_entries/Delegate.h:91` (changes a sensitive control or state-update path)

Before
```c
}

    /**
     * @brief Get sfPreviousTxnID (soeREQUIRED)
```
After
```c
}

    /**
     * @brief Get sfDestinationNode (soeOPTIONAL)
     * @return The field value, or std::nullopt if not present.
     */
    [[nodiscard]]
    protocol_autogen::Optional<SF_UINT64::type::value_type>
```

# Fix Pattern

Maintain directory indexes for both accounts involved in a two-account ledger relationship, and persist the secondary directory page so deletion can remove the object from every directory where it was inserted.

## How It Was Fixed

DelegateSet::doApply now inserts the Delegate object into keylet::ownerDir(authAccount) and stores the resulting page in sfDestinationNode. DelegateSet::deleteDelegate now checks optional sfDestinationNode and removes the Delegate object from keylet::ownerDir(delegatee). The autogenerated Delegate ledger-entry API was updated to get and set sfDestinationNode.

# Why It Matters

1. Delegate entries represent account-to-account authorization state.

2. One-sided indexing can make lifecycle cleanup miss related objects.

3. The patch improves discoverability and cleanup consistency.

4. The provided evidence does not establish a vulnerability.

# Evidence Notes

The strongest evidence is the DelegateSet.cpp creation and deletion hunks adding authorized-account owner-directory insertion/removal and the optional sfDestinationNode field. Claims about access-control bypass, moved permission checks, staking, consensus corruption, or proven stale-delegation exploit are unsupported by the supplied hunks. AccountDelete.cpp and tests are listed as changed, but no relevant hunks are provided, so cleanup impact during account deletion remains inferred rather than demonstrated. Protocol security invariant: Delegate ledger entries that relate a delegating account and an authorized account appear intended to be discoverable from both relevant owner directories so lifecycle cleanup can remove the entry from each side. The provided evidence does not establish a concrete security violation if that invariant is broken. Verification notes: The patch does not show a missing transaction authorization check. The patch does not prove that an attacker can create or use a stale Delegate entry after account deletion. The patch does not show consensus divergence or ledger corruption by itself. The provided hunks do not show the AccountDelete cleanup path, only the indexing needed for cleanup. The autogen changes are support code, not independently security-relevant. No provided hunk shows an authorization check being added or fixed. No provided hunk shows AccountDelete discovering Delegate entries through the new directory link. No provided test output or test hunk demonstrates an exploitable stale Delegate scenario. Autogenerated accessor changes are support code, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `authorization-lifecycle-cleanup`
Final impact type: `stale-authorization-state, incomplete-account-cleanup`
Final confidence: `medium`
Final tags: `blockchain-core, delegation, ledger-indexing, account-lifecycle, security-hardening`

The supplied patch evidence supports a security-hardening classification, not a concrete security-fix. Delegate entries represent authorization state between accounts, and the patch adds bidirectional owner-directory indexing so the authorized account side can find and clean up Delegate objects during account deletion. That tightens lifecycle handling for security-sensitive authorization data, but the evidence does not prove an exploitable stale delegation, privilege bypass, or consensus failure.

## Security Evidence

1. Delegate creation now inserts the object into the authorized account's owner directory.
2. The new code comment explicitly ties the secondary index to finding and cleanup when the authorized account is deleted.
3. Delegate deletion now removes the object from the authorized account owner directory when sfDestinationNode is present.
4. sfDestinationNode is added to persist the secondary directory page needed for later cleanup.
5. The subsystem concerns delegation, which is account-to-account authorization state.

## Missing Evidence

1. No AccountDelete.cpp hunk is provided to show the exact cleanup path using the new index.
2. No test hunk or output demonstrates an exploitable stale Delegate scenario.
3. No evidence shows a missing authorization check or privilege bypass being fixed.
4. No evidence shows consensus divergence, ledger corruption, or fund loss.
5. The Attackathon subject suggests security relevance but does not by itself prove a vulnerability.

## Claim Boundaries

1. Classify as security-hardening rather than security-fix.
2. Do not claim a proven access-control bypass.
3. Do not claim RPC involvement from the supplied hunks.
4. Do not classify this as staking-specific based on the provided code paths.
5. Limit the finding to bidirectional indexing and lifecycle cleanup for Delegate ledger entries.
