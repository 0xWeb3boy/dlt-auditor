---
case_id: case_20181031_6bdc9e7b3
project: rippled
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
confidence: high
source_quality: high
date: 2018-10-31
source_refs:
  - git:6bdc9e7b302ab1d3e036db86dc038a562714ccb6
  - "src/ripple/app/misc/impl/ValidatorSite.cpp:384"
  - "src/ripple/app/misc/impl/ValidatorSite.cpp:405"
  - "src/ripple/app/misc/impl/ValidatorList.cpp:108"
bug_class: wrong-revocation-cache
impact_type:
  - revocation-bypass
  - trust-validation-bypass
tags:
  - validator-list
  - publisher-manifest
  - revocation-check
  - trust-validation
  - wrong-cache
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The grounded security fix is in `ValidatorList::load`: a configured validator-list publisher key was checked with `validatorManifests_.revoked(id)` before the patch and is checked with `publisherManifests_.revoked(id)` after the patch. This corrects a trust decision so publisher revocation is evaluated against the matching publisher manifest cache.

## Observed Patch Facts

1. In `src/ripple/app/misc/impl/ValidatorSite.cpp`, the patch replaces `bool shouldRetry = false;` with `auto onError = [&](std::string const& errMsg, bool retry)`.

2. In `src/ripple/app/misc/impl/ValidatorSite.cpp`, the patch replaces `shouldRetry = true;` with `onError("fetch error", true);`.

3. In `src/ripple/app/misc/impl/ValidatorList.cpp`, the patch replaces `if (validatorManifests_.revoked (id))` with `if (publisherManifests_.revoked (id))`.

## Project Context

The changed code sits primarily in `src/ripple/app/misc/impl`, `src/ripple/app/misc`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `src/ripple/app/misc/impl/Manifest.cpp`, `src/ripple/app/misc/impl/TxQ.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/misc/impl/Manifest.cpp`, `src/ripple/app/misc/ValidatorSite.h`. The strongest project-level identifiers around this patch are `std::size_t`, `std::lock_guard`, `std::mutex`, and `std::string`.

## Before/After Behavior

Before the patch, `ValidatorList::load` parsed a validator-list publisher key into `id` but checked revocation through the validator manifest cache. After the patch, the same publisher key is checked through the publisher manifest cache, and a revoked publisher key is logged and skipped. The `ValidatorSite::onSiteFetch` changes centralize fetch error status and retry handling, but the supplied evidence does not establish those changes as the security fix.

# Root Cause

The load path used the wrong manifest cache for a publisher-key revocation decision. A validator-list publisher identity was evaluated against `validatorManifests_` instead of `publisherManifests_`, so publisher revocation state could be missed at that check.

## Walkthrough

1. `ValidatorList::load` handles configured validator-list publisher keys and converts a parsed key into a `PublicKey` named `id`.

2. Before the fix, the revocation check called `validatorManifests_.revoked(id)`.

3. That cache name does not match the identity being evaluated, which is a validator-list publisher key.

4. The patch changes the check to `publisherManifests_.revoked(id)`.

5. When that check reports revocation, the code logs that the configured validator-list publisher key is revoked and continues without using that publisher entry.

6. The `ValidatorSite` edits are treated as surrounding error-handling refactor/support code, not as the root security issue.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/misc/impl/ValidatorList.cpp | 108 | Checks whether a configured validator-list publisher key has been revoked before continuing to use it. |
| src/ripple/app/misc/impl/ValidatorSite.cpp | 384 | Updates validator-site fetch failure status and retry scheduling through a shared error handler. |
| src/ripple/app/misc/impl/ValidatorSite.cpp | 405 | Handles network fetch errors for validator-list site retrieval and marks them retryable. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/misc/impl/ValidatorSite.cpp:384` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
std::size_t siteIdx)
{
    bool shouldRetry = false;
    {
        std::lock_guard <std::mutex> lock_sites{sites_mutex_};
        try
        {
            if (ec)
```
After
```cpp
std::size_t siteIdx)
{
    {
        std::lock_guard <std::mutex> lock_sites{sites_mutex_};
        auto onError = [&](std::string const& errMsg, bool retry)
        {
            sites_[siteIdx].lastRefreshStatus.emplace(
                Site::Status{clock_type::now(),
```

## Snippet 2

Context: `src/ripple/app/misc/impl/ValidatorSite.cpp:405` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
":" <<
                    ec.message();
                shouldRetry = true;
                throw std::runtime_error{"fetch error"};
            }

            using namespace boost::beast::http;
            switch (res.result())
```
After
```cpp
":" <<
                    ec.message();
            onError("fetch error", true);
        }
        else
        {
            try
            {
```

## Snippet 3

Context: `src/ripple/app/misc/impl/ValidatorList.cpp:108` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
auto id = PublicKey(makeSlice(ret.first));

        if (validatorManifests_.revoked (id))
        {
            JLOG (j_.warn()) <<
```
After
```cpp
auto id = PublicKey(makeSlice(ret.first));

        if (publisherManifests_.revoked (id))
        {
            JLOG (j_.warn()) <<
```

# Fix Pattern

Use the revocation cache corresponding to the identity type being authorized.

## How It Was Fixed

The fix changed the revocation lookup in `src/ripple/app/misc/impl/ValidatorList.cpp` from `validatorManifests_.revoked(id)` to `publisherManifests_.revoked(id)`. The commit also refactored `ValidatorSite::onSiteFetch` error handling, but that refactor is not necessary to establish the security finding.

# Why It Matters

1. Prevents publisher trust decisions from consulting the wrong revocation namespace.

2. Ensures revoked validator-list publishers are rejected by the publisher manifest cache check.

3. Protects validator-list loading logic, a security-sensitive trust path.

4. Does not prove remote exploitability or observed consensus compromise.

# Evidence Notes

The primary evidence is the direct line change in `src/ripple/app/misc/impl/ValidatorList.cpp` from `validatorManifests_.revoked(id)` to `publisherManifests_.revoked(id)` near code that logs `Invalid validator list publisher key` and `Configured validator list publisher key is revoked`. The commit subject also names the same issue: using the correct manifest cache when loading `ValidatorList`. Claims about live exploitation, consensus compromise, or an independently security-relevant `ValidatorSite` bug are not supported by the supplied evidence. Protocol security invariant: Validator-list publisher keys must be checked against publisher manifest revocation state before they remain trusted in the validator-list load path. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show that a revoked publisher was accepted in a live deployment. The ValidatorSite error-handling refactor is not independently shown to fix a security issue. The evidence does not show compromise of consensus directly, only correction of validator-list publisher trust handling. Confirmed by the visible before/after diff in `ValidatorList::load`. Mapper and draft agree that the `ValidatorSite` changes are not the core security fix. No evidence was provided showing remote exploitability or production impact. Tests were changed, but their contents were not provided, so no stronger test-based claim is made. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `wrong-revocation-cache`
Final impact type: `revocation-bypass, trust-validation-bypass`
Final tags: `validator-list, publisher-manifest, revocation-check, trust-validation, wrong-cache`

The supplied patch directly changes a validator-list publisher revocation decision from checking `validatorManifests_` to checking `publisherManifests_`. Because the key being evaluated is a validator-list publisher key and the surrounding code skips revoked publishers, the evidence supports a concrete security fix in a trust-validation path. The `ValidatorSite` error-handling changes are not independently security-supported by the provided evidence.

## Security Evidence

1. `ValidatorList::load` parses a configured validator-list publisher key into `id`.
2. Before the patch, revocation was checked with `validatorManifests_.revoked(id)`.
3. After the patch, revocation is checked with `publisherManifests_.revoked(id)`.
4. The nearby code logs that a configured validator-list publisher key is revoked and skips it, showing this is an authorization/trust decision.

## Missing Evidence

1. No test contents are provided to show the exact regression scenario.
2. No evidence shows live exploitation or production impact.
3. No evidence proves consensus compromise or remote exploitability.
4. The `ValidatorSite` retry/status refactor is not shown to fix a security issue.

## Claim Boundaries

1. Keep the finding focused on publisher manifest revocation checking in `ValidatorList::load`.
2. Do not classify this as an RPC client API serialization or state representation issue.
3. Do not claim consensus compromise, client-view divergence, or exploitability from the supplied patch alone.
4. Treat the `ValidatorSite` changes as supporting/refactor context, not the validated security fix.
