---
case_id: case_20181008_7fe1d4b9c
project: rippled
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2018-10-08
source_refs:
  - git:7fe1d4b9c20acce1fa00e423b5da4ad766dac197
  - "src/ripple/app/misc/impl/ValidatorSite.cpp:32"
  - "src/ripple/app/misc/impl/ValidatorSite.cpp:97"
  - "src/ripple/app/misc/impl/ValidatorSite.cpp:225"
  - "src/ripple/app/misc/impl/ValidatorSite.cpp:170"
bug_class: validator-site-redirect-retry-hardening
impact_type:
  - availability-hardening
  - bounded-network-fetch
confidence: medium
tags:
  - validator-ops
  - validator-site-fetch
  - redirect-handling
  - retry-limit
  - url-validation
  - availability-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes rippled's ValidatorSite fetch path to represent fetch targets as Resource objects, centralize URL parsing and http/https validation, honor redirect-oriented resource state, use per-site refresh intervals, reset redirect counts per cycle, and add explicit retry/redirect limits. This is plausibly security-adjacent availability hardening for validator-list fetching, but the supplied evidence does not prove an exploitable vulnerability or security fix.

## Observed Patch Facts

1. In `src/ripple/app/misc/impl/ValidatorSite.cpp`, the patch replaces `ValidatorSite::ValidatorSite (` with `auto constexpr ERROR_RETRY_INTERVAL = std::chrono::seconds{30};`.

2. In `src/ripple/app/misc/impl/ValidatorSite.cpp`, the patch replaces `for (auto uri : siteURIs)` with `for (auto const& uri : siteURIs)`.

3. In `src/ripple/app/misc/impl/ValidatorSite.cpp`, the patch replaces `clock_type::now() + DEFAULT_REFRESH_INTERVAL;` with `clock_type::now() + sites_[siteIdx].refreshInterval;`.

4. In `src/ripple/app/misc/impl/ValidatorSite.cpp`, the patch replaces `ValidatorSite::onTimer (` with `ValidatorSite::makeRequest (`.

## Project Context

The changed code sits primarily in `src/ripple/app/misc/impl`, `src/ripple/app/misc`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `src/ripple/app/misc/impl/TxQ.cpp`, `src/ripple/app/misc/impl/Manifest.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/app/misc/ValidatorSite.h`, `src/ripple/app/misc/impl/TxQ.cpp`. The strongest project-level identifiers around this patch are `std::lock_guard`, `std::mutex`, `clock_type::now`, and `std::shared_ptr`.

## Before/After Behavior

Before the patch, configured validator-site URLs were parsed and scheme-checked in ValidatorSite::load, fetch scheduling used DEFAULT_REFRESH_INTERVAL directly, and the visible evidence does not show redirect-aware Resource state or bounded redirect counting in the request path. After the patch, URL validation is performed when constructing Site::Resource, Site tracks loadedResource, startingResource, and activeResource, onTimer uses sites_[siteIdx].refreshInterval, redirCount is reset for each timer cycle, makeRequest starts fetches for a specific Resource, and constants define a 30-second error retry interval and a maximum of 3 redirects.

# Root Cause

The supported root cause is incomplete or less explicit handling of validator-site redirects and retry timing in the fetch scheduler/resource layer. The evidence does not support stronger claims such as signature-verification bypass, consensus failure, ledger divergence, memory corruption, or attacker-controlled redirect exploitation in normal deployments.

## Walkthrough

1. ValidatorSite loads configured validator-list site URIs into sites_.

2. The patch moves URL parsing and http/https scheme validation into Site::Resource construction.

3. Invalid configured URLs are handled by catching Resource/Site construction exceptions during load.

4. Site now models loadedResource, startingResource, and activeResource, separating configured, cycle-start, and currently fetched resources.

5. onTimer schedules the next fetch from the site's refreshInterval instead of always using DEFAULT_REFRESH_INTERVAL.

6. onTimer resets redirCount to 0 before starting a timer-driven fetch cycle.

7. makeRequest records the active resource and starts the Work fetch path for that resource.

8. The added ERROR_RETRY_INTERVAL and MAX_REDIRECTS constants indicate bounded error retry and redirect behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/app/misc/impl/ValidatorSite.cpp | 32 | Defines retry/redirect constants and Resource construction with http/https URL validation. |
| src/ripple/app/misc/impl/ValidatorSite.cpp | 91 | Loads configured validator site URIs through Site/Resource construction and handles invalid configured URLs. |
| src/ripple/app/misc/impl/ValidatorSite.cpp | 164 | Introduces makeRequest for active resource fetches, enabling redirected resources to be requested through the same path. |
| src/ripple/app/misc/impl/ValidatorSite.cpp | 219 | Schedules refresh using per-site refreshInterval, resets redirect count per timer cycle, and routes request failures through fetch handling. |
| src/ripple/app/misc/ValidatorSite.h | 63 | Models loaded, starting, and active validator-site resources used for redirect-aware fetching. |

## Code Snippets

## Snippet 1

Context: `src/ripple/app/misc/impl/ValidatorSite.cpp:32` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
// default site query frequency - 5 minutes
auto constexpr DEFAULT_REFRESH_INTERVAL = std::chrono::minutes{5};

ValidatorSite::ValidatorSite (
```
After
```cpp
// default site query frequency - 5 minutes
auto constexpr DEFAULT_REFRESH_INTERVAL = std::chrono::minutes{5};
auto constexpr ERROR_RETRY_INTERVAL = std::chrono::seconds{30};
unsigned short constexpr MAX_REDIRECTS = 3;

ValidatorSite::Site::Resource::Resource (std::string uri_)
    : uri {std::move(uri_)}
{
```

## Snippet 2

Context: `src/ripple/app/misc/impl/ValidatorSite.cpp:97` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
std::lock_guard <std::mutex> lock{sites_mutex_};

    for (auto uri : siteURIs)
    {
        parsedURL pUrl;
        if (! parseUrl (pUrl, uri) ||
            (pUrl.scheme != "http" && pUrl.scheme != "https"))
        {
```
After
```cpp
std::lock_guard <std::mutex> lock{sites_mutex_};

    for (auto const& uri : siteURIs)
    {
        try
        {
            sites_.emplace_back (uri);
        }
```

## Snippet 3

Context: `src/ripple/app/misc/impl/ValidatorSite.cpp:225` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
std::lock_guard <std::mutex> lock{sites_mutex_};
    sites_[siteIdx].nextRefresh =
        clock_type::now() + DEFAULT_REFRESH_INTERVAL;

    assert(! fetching_);
    fetching_ = true;

    std::shared_ptr<detail::Work> sp;
```
After
```cpp
std::lock_guard <std::mutex> lock{sites_mutex_};
    sites_[siteIdx].nextRefresh =
        clock_type::now() + sites_[siteIdx].refreshInterval;

    assert(! fetching_);
    sites_[siteIdx].redirCount = 0;
    try
    {
```

## Snippet 4

Context: `src/ripple/app/misc/impl/ValidatorSite.cpp:170` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
}

void
ValidatorSite::onTimer (
```
After
```cpp
}

void
ValidatorSite::makeRequest (
    std::shared_ptr<Site::Resource> resource,
    std::size_t siteIdx,
    std::lock_guard<std::mutex>& lock)
{
```

# Fix Pattern

Model validator-site fetch targets as validated Resource objects and keep redirect/retry state explicit and bounded in the scheduler.

## How It Was Fixed

The implementation adds ERROR_RETRY_INTERVAL and MAX_REDIRECTS, introduces Resource construction with URL parsing and http/https validation, changes load to construct Site/Resource objects under exception handling, adds makeRequest for resource-specific fetches, tracks active/start resources, uses per-site refreshInterval scheduling, and resets redirect count per refresh cycle.

# Why It Matters

1. Validator-list fetching is part of validator trust-data distribution.

2. Redirect handling should not bypass URL validation applied to configured sites.

3. Retry and redirect behavior should be bounded to avoid uncontrolled repeated network fetches.

4. The evidence supports hardening or correctness improvement, not a confirmed vulnerability.

# Evidence Notes

Grounded evidence comes from ValidatorSite.cpp and ValidatorSite.h excerpts showing Resource URL validation, loaded/start/active resource fields, makeRequest, per-site refreshInterval use, redirCount reset, ERROR_RETRY_INTERVAL, and MAX_REDIRECTS. The draft's RPC, serialization, cryptographic, and consensus implications are unsupported. The evidence also does not show who controls redirects, whether redirects were followed unsafely before, or whether any validator-list authenticity checks were affected. Protocol security invariant: Validator list fetching should request only validated http/https resources and keep redirect/retry behavior bounded. The provided evidence shows changes in that area, but does not establish a concrete vulnerability, attacker capability, or bypass of validator-list trust validation. Verification notes: The patch does not prove a validator list signature-verification bypass. The patch does not prove consensus safety failure or ledger divergence. The patch does not prove remote code execution or memory corruption. The patch does not show whether redirects are attacker-controlled in normal deployments. The patch supports bounded retry/redirect hardening, not a confirmed exploit chain. No evidence of a signature-verification bypass is provided. No evidence of consensus or ledger divergence is provided. No evidence of memory safety impact is provided. No evidence establishes attacker-controlled redirects in normal deployment. Treat helper/test files as support code, not root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validator-site-redirect-retry-hardening`
Final impact type: `availability-hardening, bounded-network-fetch`
Final confidence: `medium`
Final tags: `validator-ops, validator-site-fetch, redirect-handling, retry-limit, url-validation, availability-hardening`

The evidence does not support the original serialization/RPC/client-view-divergence framing or a confirmed exploitable security bug. However, the patch is in validator-list site fetching, adds explicit URL scheme validation for Resource objects, introduces bounded redirect/retry behavior, and tracks redirect/request state. Because validator-list retrieval is security-sensitive infrastructure and the patch tightens externally influenced network-fetch behavior, it is reasonable to retain as security hardening rather than a concrete security fix.

## Security Evidence

1. ValidatorSite fetches validator-list site resources, a security-sensitive trust-data distribution path.
2. Resource construction validates parsed URLs and restricts schemes to http/https.
3. The patch adds MAX_REDIRECTS = 3, indicating redirects are explicitly bounded.
4. The commit body states retries per refresh interval are limited to 3.
5. Redirect/request state is made explicit through Resource, activeResource, startingResource, redirCount, and per-site refreshInterval.

## Missing Evidence

1. No evidence shows an exploitable redirect vulnerability before the patch.
2. No evidence shows attacker control over validator-site redirects in normal deployments.
3. No evidence shows signature verification bypass, consensus failure, or ledger divergence.
4. No evidence shows SSRF beyond allowed http/https targets or any host allowlist bypass.
5. No evidence shows a concrete denial-of-service incident or unbounded resource exhaustion path.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Do not claim consensus compromise, validator signature bypass, or ledger divergence.
3. Do not retain the original rpc-client-api or serialization/state-representation framing.
4. Security relevance is limited to bounded redirect/retry handling and URL validation in validator-site fetching.
5. Impact should be described conservatively as availability/network-fetch hardening.
