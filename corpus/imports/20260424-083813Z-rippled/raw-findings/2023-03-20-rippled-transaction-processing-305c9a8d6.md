---
case_id: case_20230320_305c9a8d6
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: high
source_quality: high
date: 2023-03-20
source_refs:
  - git:305c9a8d61b919f8be18ff5345ccd7b050c64ddd
  - "src/ripple/app/tx/impl/NFTokenMint.cpp:161"
  - "src/ripple/app/tx/impl/DeleteAccount.cpp:215"
  - "src/ripple/protocol/impl/SField.cpp:151"
  - "src/ripple/protocol/Feature.h:75"
bug_class: identifier-collision
impact_type:
  - state-integrity
tags:
  - blockchain-core
  - transaction-processing
  - nft
  - identifier-collision
  - account-lifecycle
  - state-integrity
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

Confirmed protocol security fix for duplicate NFTokenID creation. The provided commit message and changed code show that the old mint and account deletion rules could allow an issuer to burn an NFT, delete and recreate the account, then mint another NFT with matching ID inputs and receive the same NFTokenID. The fix adds amendment-gated NFT sequence history and an account deletion restriction to prevent sequence overlap after recreation.

## Observed Patch Facts

1. In `src/ripple/app/tx/impl/NFTokenMint.cpp`, the patch replaces `std::uint32_t const tokenSeq = (*root)[~sfMintedNFTokens].value_or(0);` with `if (!ctx_.view().rules().enabled(fixNFTokenRemint))`.

2. In `src/ripple/app/tx/impl/DeleteAccount.cpp`, the patch replaces `// Verify that the account does not own any objects that would prevent` with `// When fixNFTokenRemint is enabled, we don't allow an account to be`.

3. In `src/ripple/protocol/impl/SField.cpp`, the patch adds `// Three field values of 47, 48 and 49 are reserved for`.

4. In `src/ripple/protocol/Feature.h`, the patch replaces `static constexpr std::size_t numFeatures = 57;` with `static constexpr std::size_t numFeatures = 58;`.

## Project Context

The changed code sits primarily in `src/ripple/app/tx/impl`, `src/ripple/app/tx`, `src/ripple/protocol/impl`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/ripple/protocol/impl/Serializer.cpp`, `src/ripple/protocol/impl/SecretKey.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/protocol/impl/Serializer.cpp`, `src/ripple/protocol/impl/SecretKey.cpp`. The strongest project-level identifiers around this patch are `std::uint32_t`, `std::size_t`, `tokenSeq`, and `uint32_t`. Nearby tests or test-like files include `src/ripple/beast/unit_test/detail/const_container.hpp`, `src/ripple/beast/unit_test/results.hpp`.

## Before/After Behavior

Before the change, the NFT mint path used `MintedNFTokens` as the sequence basis, which could be reset by account deletion and recreation. Account deletion only had the existing timing restriction based on account sequence and ledger sequence in the provided evidence. After the change, legacy sequence behavior is gated behind `!fixNFTokenRemint`; with the amendment, minting uses a stable `FirstNFTokenSequence + MintedNFTokens` basis, and account deletion is blocked when `FirstNFTokenSequence + MintedNFTokens + 256` is not older than the current ledger sequence.

# Root Cause

The NFTokenID construction could reuse a sequence component after the issuer account lifecycle reset. `MintedNFTokens` did not by itself preserve enough historical sequence state across account deletion and recreation, and authorized minting could create an additional overlap because it advanced issuer NFT issuance without advancing the issuer account sequence in the same way.

## Walkthrough

1. An issuer mints an NFT, creating an NFTokenID from inputs that include an issuer-related sequence value.

2. The issuer burns the NFT, removing the live token object.

3. The issuer deletes the account, removing account state used by the old sequence basis.

4. The issuer recreates the account and mints again with matching NFTokenID inputs such as taxon and flags.

5. Under the old rules, the recreated account could reuse the same NFT sequence basis and create a duplicate NFTokenID.

6. The patched mint path uses `FirstNFTokenSequence + MintedNFTokens` when `fixNFTokenRemint` is enabled.

7. The patched account deletion path adds a timing restriction based on the NFT sequence range, covering the authorized-minter collision scenario described in the commit.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/tx/impl/NFTokenMint.cpp | 161 | Mint path changes how the per-issuer NFT sequence is selected when fixNFTokenRemint is enabled, preventing reuse of the pre-deletion sequence basis. |
| src/ripple/app/tx/impl/DeleteAccount.cpp | 215 | Account deletion preclaim adds an amendment-gated restriction based on FirstNFTokenSequence plus MintedNFTokens to avoid post-recreation NFT sequence collisions. |
| src/ripple/protocol/impl/SField.cpp | 151 | Protocol serialization field registry adds sfFirstNFTokenSequence so AccountRoot can persist the stable first NFT sequence value. |
| src/ripple/protocol/Feature.h | 75 | Amendment feature count update supports registering the new fixNFTokenRemint protocol behavior. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/tx/impl/NFTokenMint.cpp:161` (updates aggregate accounting or lifecycle state)

Before
```cpp
return Unexpected(tecNO_ISSUER);

        // Get the unique sequence number for this token:
        std::uint32_t const tokenSeq = (*root)[~sfMintedNFTokens].value_or(0);
        {
            std::uint32_t const nextTokenSeq = tokenSeq + 1;
            if (nextTokenSeq < tokenSeq)
                return Unexpected(tecMAX_SEQUENCE_REACHED);
```
After
```cpp
return Unexpected(tecNO_ISSUER);

        if (!ctx_.view().rules().enabled(fixNFTokenRemint))
        {
            // Get the unique sequence number for this token:
            std::uint32_t const tokenSeq =
                (*root)[~sfMintedNFTokens].value_or(0);
            {
```

## Snippet 2

Context: `src/ripple/app/tx/impl/DeleteAccount.cpp:215` (updates aggregate accounting or lifecycle state)

Before
```cpp
return tecTOO_SOON;

    // Verify that the account does not own any objects that would prevent
    // the account from being deleted.
```
After
```cpp
return tecTOO_SOON;

    // When fixNFTokenRemint is enabled, we don't allow an account to be
    // deleted if <FirstNFTokenSequence + MintedNFTokens> is within 256 of the
    // current ledger. This is to prevent having duplicate NFTokenIDs after
    // account re-creation.
    //
    // Without this restriction, duplicate NFTokenIDs can be reproduced when
```

## Snippet 3

Context: `src/ripple/protocol/impl/SField.cpp:151` (updates aggregate accounting or lifecycle state)

Before
```cpp
CONSTRUCT_TYPED_SFIELD(sfHookStateCount,        "HookStateCount",       UINT32,    45);
CONSTRUCT_TYPED_SFIELD(sfEmitGeneration,        "EmitGeneration",       UINT32,    46);

// 64-bit integers (common)
```
After
```cpp
CONSTRUCT_TYPED_SFIELD(sfHookStateCount,        "HookStateCount",       UINT32,    45);
CONSTRUCT_TYPED_SFIELD(sfEmitGeneration,        "EmitGeneration",       UINT32,    46);
// Three field values of 47, 48 and 49 are reserved for 
// LockCount(Hooks), VoteWeight(AMM), DiscountedFee(AMM)
CONSTRUCT_TYPED_SFIELD(sfFirstNFTokenSequence,  "FirstNFTokenSequence", UINT32,    50);

// 64-bit integers (common)
```

## Snippet 4

Context: `src/ripple/protocol/Feature.h:75` (updates aggregate accounting or lifecycle state)

Before
```c
// large to make the FeatureBitset, it MAY be larger. It MUST NOT be less than
// the actual number of amendments. A LogicError on startup will verify this.
static constexpr std::size_t numFeatures = 57;

/** Amendments that this server supports and the default voting behavior.
```
After
```c
// large to make the FeatureBitset, it MAY be larger. It MUST NOT be less than
// the actual number of amendments. A LogicError on startup will verify this.
static constexpr std::size_t numFeatures = 58;

/** Amendments that this server supports and the default voting behavior.
```

# Fix Pattern

Persist the lifecycle state needed for protocol identifier uniqueness and prevent destructive lifecycle transitions until their sequence ranges cannot collide after account recreation.

## How It Was Fixed

`NFTokenMint.cpp` gates the old `MintedNFTokens`-only sequence behavior behind the disabled amendment path and uses the new first-NFT sequence model when `fixNFTokenRemint` is enabled. `DeleteAccount.cpp` adds an amendment-gated deletion restriction based on `FirstNFTokenSequence + MintedNFTokens + 256`. Protocol support files register `sfFirstNFTokenSequence` and update the amendment feature count.

# Why It Matters

1. Preserves NFTokenID uniqueness across burn, delete, recreate, and remint flows.

2. Prevents account state reset from enabling NFT identifier reuse.

3. Covers the authorized minting sequence-overlap case described in the commit.

4. Evidence supports duplicate identifier prevention, not asset theft, RCE, memory corruption, or key compromise.

# Evidence Notes

Grounded evidence comes from the commit message, `src/ripple/app/tx/impl/NFTokenMint.cpp` where legacy token sequence selection becomes amendment-gated, `src/ripple/app/tx/impl/DeleteAccount.cpp` where comments and logic describe preventing duplicate NFTokenIDs after account recreation, `src/ripple/protocol/impl/SField.cpp` where `sfFirstNFTokenSequence` is registered, and `src/ripple/protocol/Feature.h` where the feature count increases. Serializer and secret-key contexts are unrelated support context and should not be treated as root cause evidence. Protocol security invariant: NFTokenID values must remain unique across NFT burn, issuer account deletion, issuer account recreation, and authorized minting; lifecycle operations must not allow reuse of the sequence inputs used to construct an NFTokenID. Verification notes: The patch proves duplicate NFTokenID prevention, not arbitrary asset theft. No memory safety, remote code execution, or cryptographic key compromise is shown. The evidence does not prove consensus failure beyond admitting colliding NFT identities under the old rules. The impact of a duplicate NFTokenID on marketplaces or downstream applications is not established by the patch itself. Only the account deletion and NFT minting lifecycle paths are evidenced; unrelated serializer or secret-key helper contexts are not part of the bug shape. Commit message gives concrete remint and authorized-minter collision scenarios. Changed account deletion comments explicitly state the duplicate NFTokenID prevention purpose. No evidence supports broader claims such as theft, consensus failure impact, memory corruption, or cryptographic compromise. Helper/protocol registration changes support the fix but are not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `identifier-collision`
Final impact type: `state-integrity`
Final tags: `blockchain-core, transaction-processing, nft, identifier-collision, account-lifecycle, state-integrity`

The supplied commit metadata and patch evidence directly support a protocol fix for duplicate NFTokenID creation after NFT burn, account deletion, account recreation, and reminting. The mint path adds amendment-gated sequence behavior using persistent first-NFT sequence state, and the account deletion path adds a restriction explicitly documented as preventing duplicate NFTokenIDs. This is security-relevant state integrity in a blockchain protocol, but broader economic-loss claims are not proven by the supplied evidence.

## Security Evidence

1. Commit body gives concrete reproducible remint scenarios that create the same NFTokenID.
2. NFTokenMint.cpp changes the NFT sequence basis under fixNFTokenRemint instead of relying only on MintedNFTokens.
3. DeleteAccount.cpp adds an amendment-gated deletion restriction to prevent sequence overlap after account recreation.
4. Patch introduces sfFirstNFTokenSequence so account NFT issuance history can persist for ID uniqueness.

## Missing Evidence

1. No supplied evidence proves asset theft, direct monetary loss, or marketplace exploitation.
2. No supplied evidence proves consensus failure beyond duplicate NFT identity/state integrity risk.
3. Only excerpts are provided for some mint-path after behavior, not the complete implementation.

## Claim Boundaries

1. Validated issue is duplicate NFTokenID prevention across account lifecycle transitions.
2. Impact should be framed as blockchain state integrity or identifier uniqueness, not memory safety, RCE, key compromise, or arbitrary theft.
3. Authorized-minter coverage is supported by commit text and deletion-path comments, but downstream consequences are not established.
