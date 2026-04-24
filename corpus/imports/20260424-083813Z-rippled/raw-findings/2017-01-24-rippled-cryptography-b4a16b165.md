---
case_id: case_20170124_b4a16b165
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2017-01-24
source_refs:
  - git:b4a16b165b6a3200daf08d4889406661922852f6
  - "src/ripple/app/misc/impl/Manifest.cpp:403"
  - "src/ripple/app/misc/impl/Manifest.cpp:115"
  - "src/ripple/app/misc/impl/Manifest.cpp:43"
  - "src/ripple/app/misc/Manifest.h:67"
bug_class: validator-key-revocation-handling
impact_type:
  - compromised-key-containment
  - validator-trust-management
confidence: medium
tags:
  - blockchain-core
  - validator
  - key-revocation
  - manifest
  - signature-verification
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds first-class handling for validator master-key revocation manifests and a dedicated [validator_key_revocation] config input. The evidence supports a correctness or security-relevant hardening change in revocation handling, but it does not establish an exploitable vulnerability or a concrete prior security failure.

## Observed Patch Facts

1. In `src/ripple/app/misc/impl/Manifest.cpp`, the patch replaces `return true;` with `if (! configRevocation.empty())`.

2. In `src/ripple/app/misc/impl/Manifest.cpp`, the patch replaces `if (! ripple::verify (st, HashPrefix::manifest, signingKey))` with `// Signing key and signature are not required for`.

3. In `src/ripple/app/misc/impl/Manifest.cpp`, the patch replaces `auto const opt_spk = get<PublicKey>(st, sfSigningPubKey);` with `if (!opt_pk || !opt_seq || !opt_msig)`.

4. In `src/ripple/app/misc/Manifest.h`, the patch replaces `new one. Since no further manifests for this master key will be accepted` with `new one. These revocation manifests are loaded from the`.

## Project Context

The changed code sits primarily in `src/ripple/app/misc/impl`, `src/ripple/app/misc`, `src/ripple/app`, which anchors the finding in the `cryptography` area of the project. Historical context from `src/ripple/app/misc/impl/ValidatorList.cpp`, `src/ripple/app/misc/impl/ValidatorSite.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/misc/impl/ValidatorList.cpp`, `src/ripple/app/misc/impl/ValidatorSite.cpp`. The strongest project-level identifiers around this patch are `const`, `auto`, `std::string`, and `std::size_t`.

## Before/After Behavior

Before the patch, manifest parsing required sfSigningPubKey and sfSignature together with the master public key, sequence, and master signature, and Manifest::verify always used the ordinary signing-key verification path. The shown load path also had no handling for a separate revocation config field. After the patch, parsing requires only the master public key, sequence, and master signature up front, then requires signing-key fields only for non-revocation manifests; verification skips ordinary signing-key verification when revoked() is true; and ManifestCache::load processes revocation material from configRevocation.

# Root Cause

The prior code treated terminal master-key revocation manifests like ordinary validator manifests even though the documented revocation form intentionally has no replacement signing key. This made the revocation representation incompatible with parsing and verification paths that expected ordinary signing-key fields.

## Walkthrough

1. Manifest::make_Manifest now accepts the common revocation-proof fields before conditionally requiring sfSigningPubKey and sfSignature.

2. The conditional requirement appears tied to whether the sequence is the terminal revocation value.

3. Manifest::verify now preserves ordinary signing-key verification for non-revoked manifests but exempts revoked manifests from that path.

4. ManifestCache::load now processes a non-empty configRevocation input by trimming and concatenating configured lines before loading the revocation material.

5. Manifest.h documents that revocation manifests may come from [validator_key_revocation] or gossip and that a terminal revocation leaves no signing key on record.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/misc/impl/Manifest.cpp | 43 | Parses serialized manifests and permits master-key revocation manifests without normal signing-key fields when the sequence indicates revocation. |
| src/ripple/app/misc/impl/Manifest.cpp | 115 | Verifies manifests and exempts revoked manifests from the usual signing-key signature verification requirement. |
| src/ripple/app/misc/impl/Manifest.cpp | 403 | Loads validator key revocation manifests from the dedicated config field and applies them to the manifest cache. |
| src/ripple/app/misc/Manifest.h | 67 | Documents the terminal revocation invariant and the config/gossip sources for revocation manifests. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/misc/impl/Manifest.cpp:403` (changes a consensus- or validator-sensitive branch)

Before
```cpp
}

    return true;
}
```
After
```cpp
}

    if (! configRevocation.empty())
    {
        std::string revocationStr;
        revocationStr.reserve (
            std::accumulate (configRevocation.cbegin(), configRevocation.cend(), std::size_t(0),
                [] (std::size_t init, std::string const& s)
```

## Snippet 2

Context: `src/ripple/app/misc/impl/Manifest.cpp:115` (changes signature or replay validation logic)

Before
```cpp
SerialIter sit (serialized.data (), serialized.size ());
    st.set (sit);
    if (! ripple::verify (st, HashPrefix::manifest, signingKey))
        return false;
```
After
```cpp
SerialIter sit (serialized.data (), serialized.size ());
    st.set (sit);

    // Signing key and signature are not required for
    // master key revocations
    if (! revoked () && ! ripple::verify (st, HashPrefix::manifest, signingKey))
        return false;
```

## Snippet 3

Context: `src/ripple/app/misc/impl/Manifest.cpp:43` (changes a sensitive control or state-update path)

Before
```cpp
st.set (sit);
        auto const opt_pk = get<PublicKey>(st, sfPublicKey);
        auto const opt_spk = get<PublicKey>(st, sfSigningPubKey);
        auto const opt_seq = get (st, sfSequence);
        auto const opt_sig = get (st, sfSignature);
        auto const opt_msig = get (st, sfMasterSignature);
        if (!opt_pk || !opt_spk || !opt_seq || !opt_sig || !opt_msig)
        {
```
After
```cpp
st.set (sit);
        auto const opt_pk = get<PublicKey>(st, sfPublicKey);
        auto const opt_seq = get (st, sfSequence);
        auto const opt_msig = get (st, sfMasterSignature);
        if (!opt_pk || !opt_seq || !opt_msig)
            return boost::none;

        // Signing key and signature are not required for
```

## Snippet 4

Context: `src/ripple/app/misc/Manifest.h:67` (changes a consensus- or validator-sensitive branch)

Before
```c
compromised, a manifest with sequence number 0xFFFFFFFF will supersede a
    prior manifest and discard any existing ephemeral key without storing a
    new one.  Since no further manifests for this master key will be accepted
    (since no higher sequence number is possible), and no signing key is on
    record, no validations will be accepted from the compromised validator.
```
After
```c
compromised, a manifest with sequence number 0xFFFFFFFF will supersede a
    prior manifest and discard any existing ephemeral key without storing a
    new one.  These revocation manifests are loaded from the
    [validator_key_revocation] config entry as well as received as gossip from
    peers.  Since no further manifests for this master key will be accepted
    (since no higher sequence number is possible), and no signing key is on
    record, no validations will be accepted from the compromised validator.
```

# Fix Pattern

Represent terminal key revocation as a distinct manifest state instead of forcing it through the ordinary key-rotation schema.

## How It Was Fixed

The patch relaxed signing-key field and signing-key signature requirements only for revoked manifests, retained ordinary verification for non-revoked manifests, added loading for a dedicated revocation config field, and updated documentation for the revocation invariant.

# Why It Matters

1. Allows documented validator key revocation manifests to be parsed and applied.

2. Preserves ordinary manifest signature checks for non-revoked manifests.

3. Supports local configuration of revocation material.

4. Does not prove forged revocation, signature bypass, consensus failure, or a concrete exploit.

# Evidence Notes

The evidence is strongest for behavior changes in src/ripple/app/misc/impl/Manifest.cpp and the explanatory invariant in src/ripple/app/misc/Manifest.h. The patch is security-relevant because it concerns validator key revocation, but the provided evidence does not show that attackers could exploit the old behavior or that the old behavior caused acceptance of unauthorized validations. Protocol security invariant: Validator manifest handling must preserve the distinction between ordinary key-rotation manifests and terminal master-key revocation manifests. A revocation manifest at sequence 0xFFFFFFFF is documented as superseding prior manifests, leaving no signing key on record, and causing validations from that validator master key not to be accepted. Verification notes: The patch does not prove that an attacker could forge a revocation manifest without the master signature. The patch does not prove that ordinary validator manifests bypassed signature verification. The patch does not prove consensus safety failure or ledger divergence from the prior behavior. The patch does not show network-triggered exploitability beyond accepting properly formed revocation manifests from peers. The patch appears to add or repair revocation support, not to fix a generic authorization check ordering bug. No evidence shows ordinary manifests bypassed signature verification. No evidence shows revocation manifests could be forged without a master signature. No evidence establishes network exploitability, consensus divergence, or ledger impact. Classified as unclear rather than confirmed security fix because the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validator-key-revocation-handling`
Final impact type: `compromised-key-containment, validator-trust-management`
Final confidence: `medium`
Final tags: `blockchain-core, validator, key-revocation, manifest, signature-verification, security-hardening`

The supplied evidence supports retaining this as security hardening, not as a confirmed vulnerability fix. The patch adds explicit support for terminal validator master-key revocation manifests, permits that revocation form to omit ordinary signing-key fields, and loads revocation material from a dedicated configuration field. The documentation ties this behavior directly to compromised master keys and preventing further validations from that validator. However, the evidence does not prove a concrete exploitable flaw, forged validation path, or prior consensus failure.

## Security Evidence

1. Commit and documentation describe revoking validator keys and handling compromised master keys.
2. Manifest parsing is changed so terminal revocation manifests can be accepted without ordinary signing-key fields.
3. Verification preserves ordinary signing-key checks for non-revoked manifests while treating revoked manifests as a distinct state.
4. ManifestCache::load adds handling for a dedicated validator_key_revocation config source.
5. Manifest.h states revocation leaves no signing key on record and validations from the compromised validator will not be accepted.

## Missing Evidence

1. No evidence shows an attacker could forge a revocation manifest or ordinary manifest.
2. No evidence shows prior code accepted unauthorized validations.
3. No concrete exploit scenario, CVE, advisory, or incident is provided.
4. No proof of ledger divergence or consensus safety impact from the old behavior.

## Claim Boundaries

1. Classify as security hardening rather than security-fix.
2. Do not claim signature bypass or access-control vulnerability.
3. Do not claim network exploitability beyond handling valid revocation manifests from peers.
4. The supported claim is improved validator key compromise response and revocation handling.
