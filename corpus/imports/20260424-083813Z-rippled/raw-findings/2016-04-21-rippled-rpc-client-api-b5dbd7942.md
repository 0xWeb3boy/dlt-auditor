---
case_id: case_20160421_b5dbd7942
project: rippled
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: rpc-client-api
source_quality: high
date: 2016-04-21
source_refs:
  - git:b5dbd7942f8896367e65cbc8f58e9bfbce81d953
  - "src/ripple/overlay/impl/OverlayImpl.cpp:264"
  - "src/ripple/overlay/impl/OverlayImpl.cpp:233"
  - "src/ripple/overlay/impl/OverlayImpl.cpp:372"
  - "src/ripple/overlay/impl/OverlayImpl.h:277"
bug_class: failed-handshake-resource-accounting
impact_type:
  - resource-exhaustion
  - denial-of-service
confidence: medium
tags:
  - blockchain-core
  - overlay-network
  - peer-handshake
  - hello-validation
  - connection-accounting
  - resource-cleanup
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes overlay handoff rejection paths for malformed or unverifiable HELLO messages. Before the change, the shown failure paths returned the current handoff state without the added cleanup. After the change, they close the PeerFinder slot, mark the handoff as not moved, return HTTP 400, and disable keep-alive. The evidence supports a likely security fix for resource/accounting cleanup after failed security checks, not a cryptographic flaw or authentication bypass.

## Observed Patch Facts

1. In `src/ripple/overlay/impl/OverlayImpl.cpp`, the patch replaces `return handoff;` with `m_peerFinder->on_closed(slot);`.

2. In `src/ripple/overlay/impl/OverlayImpl.cpp`, the patch replaces `handoff.moved = true;` with `m_peerFinder->on_closed(slot);`.

3. In `src/ripple/overlay/impl/OverlayImpl.cpp`, the patch replaces `//------------------------------------------------------------------------------` with `std::shared_ptr<Writer>`.

4. In `src/ripple/overlay/impl/OverlayImpl.h`, the patch replaces `processRequest (http_request_type const& req,` with `std::shared_ptr<Writer>`.

## Project Context

The changed code sits primarily in `src/ripple/overlay/impl`, `src/ripple/overlay`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `src/ripple/overlay/impl/PeerImp.h`, `src/ripple/overlay/impl/PeerImp.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/ripple/overlay/impl/PeerImp.h`, `src/ripple/overlay/impl/PeerImp.cpp`. The strongest project-level identifiers around this patch are `handoff`, `slot`, `const`, and `std::shared_ptr`. Nearby tests or test-like files include `src/ripple/overlay/tests/short_read.test.cpp`, `src/ripple/overlay/tests/manifest_test.cpp`.

## Before/After Behavior

Before the patch, parseHello failure occurred after handoff.moved had been set true and returned handoff without the shown slot cleanup, error response, or keep-alive reset. A verifyHello/public-key failure also returned handoff directly. After the patch, both paths call m_peerFinder->on_closed(slot), set handoff.moved to false, create a 400 Bad Request response with a descriptive message, and set handoff.keep_alive to false.

# Root Cause

The failure paths for overlay HELLO parsing and HELLO verification did not perform the same PeerFinder slot/accounting cleanup as the patched code. Based on the commit body, this meant failed security-check connections could leave slot/IP connection counters unreleased. The provided evidence does not prove a bypass, replay issue, or quantified denial-of-service condition.

## Walkthrough

1. OverlayImpl::onHandoff handles an incoming overlay peer connection associated with a PeerFinder slot.

2. The code parses the peer HELLO with parseHello(true, request.headers, journal).

3. Before the patch, if parsing failed, the function returned handoff without the newly added cleanup actions.

4. After the patch, parse failure closes the PeerFinder slot, marks the handoff as not moved, returns a 400 error response, and disables keep-alive.

5. If parsing succeeds, the code verifies the HELLO and derives a public key with verifyHello.

6. Before the patch, if verification failed and no public key was produced, the function returned handoff directly.

7. After the patch, verification failure follows the same cleanup and 400-response pattern.

8. The new makeErrorResponse helper centralizes construction of the HTTP 400 response used by these rejection paths.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/ripple/overlay/impl/OverlayImpl.cpp | 233 | Handles parseHello failure during overlay handoff; now closes the PeerFinder slot, returns a 400 response, and prevents keep-alive. |
| src/ripple/overlay/impl/OverlayImpl.cpp | 264 | Handles verifyHello/public-key verification failure; now closes the PeerFinder slot, returns a 400 response, and prevents keep-alive. |
| src/ripple/overlay/impl/OverlayImpl.cpp | 372 | Adds makeErrorResponse helper used to return HTTP 400 with a descriptive rejection message. |
| src/ripple/overlay/impl/OverlayImpl.h | 277 | Declares the new error-response helper for overlay handoff rejection paths. |

## Code Snippets

## Snippet 1

Context: `src/ripple/overlay/impl/OverlayImpl.cpp:264` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
remote_endpoint), journal, app_);
    if(! publicKey)
        return handoff;

    auto const result = m_peerFinder->activate (slot, *publicKey,
```
After
```cpp
remote_endpoint), journal, app_);
    if(! publicKey)
    {
        m_peerFinder->on_closed(slot);
        handoff.moved = false;
        handoff.response = makeErrorResponse (slot, request,
            remote_endpoint.address(),
            "Unable to verify HELLO message");
```

## Snippet 2

Context: `src/ripple/overlay/impl/OverlayImpl.cpp:233` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
}

    handoff.moved = true;

    auto hello = parseHello (true, request.headers, journal);
    if(! hello)
        return handoff;
```
After
```cpp
}

    auto hello = parseHello (true, request.headers, journal);
    if(! hello)
    {
        m_peerFinder->on_closed(slot);
        handoff.moved = false;
        handoff.response = makeErrorResponse (slot, request,
```

## Snippet 3

Context: `src/ripple/overlay/impl/OverlayImpl.cpp:372` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
}

//------------------------------------------------------------------------------
```
After
```cpp
}

std::shared_ptr<Writer>
OverlayImpl::makeErrorResponse (PeerFinder::Slot::ptr const& slot,
    http_request_type const& request,
    address_type remote_address,
    std::string msg)
{
```

## Snippet 4

Context: `src/ripple/overlay/impl/OverlayImpl.h:277` (changes how canonical state is encoded, returned, or reconstructed)

Before
```c
http_request_type const& request, address_type remote_address);

    bool
    processRequest (http_request_type const& req,
```
After
```c
http_request_type const& request, address_type remote_address);

    std::shared_ptr<Writer>
    makeErrorResponse (PeerFinder::Slot::ptr const& slot,
        http_request_type const& request, address_type remote_address,
        std::string msg);

    bool
```

# Fix Pattern

Convert failed handshake validation paths from plain early returns into terminal rejection paths that release connection accounting, prevent handoff ownership transfer, send an explicit error response, and close persistence.

## How It Was Fixed

OverlayImpl::onHandoff now calls m_peerFinder->on_closed(slot), sets handoff.moved = false, assigns handoff.response from makeErrorResponse(...), and sets handoff.keep_alive = false for both parseHello and verifyHello failures. OverlayImpl.cpp adds makeErrorResponse, and OverlayImpl.h declares it as a private helper.

# Why It Matters

1. Failed security-check paths should not consume PeerFinder slots indefinitely.

2. IP connection counters must be decremented when rejected attempts close.

3. Malformed or unverifiable HELLO messages are rejected without persistent connection reuse.

4. The evidence supports resource-accounting cleanup, not a cryptographic vulnerability.

# Evidence Notes

Strong evidence comes from OverlayImpl.cpp changes around parseHello failure, verifyHello/publicKey failure, and the added makeErrorResponse helper, plus the OverlayImpl.h declaration. The commit body explicitly states that the patch returns HTTP 400 and releases the slot while decrementing IP connection counters. The provided evidence does not show exploitability, counter limits, on_closed internals, or an authentication bypass, so confidence is medium and the verdict is likely rather than confirmed. Protocol security invariant: Overlay peer connection attempts that fail HELLO parsing or HELLO verification must be rejected without being handed off as active peers, and any PeerFinder slot or IP connection accounting associated with the attempt must be released. Verification notes: The patch does not prove an attacker can bypass HELLO verification or become an authenticated peer. The patch does not show a cryptographic primitive flaw or replay vulnerability. The patch does not quantify denial-of-service impact, only that slots/IP counters were previously not released on these rejection paths. The descriptive HTTP 400 response is secondary; the security-relevant change is cleanup and non-persistent failed handoff handling. Confirmed changed paths are in src/ripple/overlay/impl/OverlayImpl.cpp and OverlayImpl.h. Commit body directly supports the slot release and IP counter decrement interpretation. No evidence provided for HELLO verification bypass or cryptographic weakness. No tests or runtime verification are included in the supplied input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `failed-handshake-resource-accounting`
Final impact type: `resource-exhaustion, denial-of-service`
Final confidence: `medium`
Final tags: `blockchain-core, overlay-network, peer-handshake, hello-validation, connection-accounting, resource-cleanup`

The evidence supports retaining this as security hardening, not the originally claimed serialization/state-consistency issue. The patch changes overlay peer HELLO parse/verification failure paths, which are explicitly described as failed security checks, so rejected peers now close the PeerFinder slot, decrement IP connection accounting, return HTTP 400, and disable keep-alive. The supplied evidence does not prove a concrete exploit or bypass, but it does show cleanup of a security-sensitive connection rejection path that could plausibly affect resource exhaustion resistance.

## Security Evidence

1. Commit subject explicitly says connections that fail security checks are being handled correctly.
2. Commit body states the fix releases the slot and decrements IP connection counters.
3. Patch adds cleanup on malformed HELLO parse failure before returning the handoff.
4. Patch adds cleanup on unverifiable HELLO/public-key failure before returning the handoff.
5. Patch disables keep-alive and returns a 400 response for rejected overlay handshakes.

## Missing Evidence

1. No proof that an attacker could exhaust slots or IP counters in practice.
2. No evidence of a successful authentication, cryptographic, or replay bypass.
3. No details for PeerFinder::on_closed internals or exact counter behavior beyond the commit body.
4. No tests, advisory, CVE, or exploit scenario are provided.

## Claim Boundaries

1. Validate as security-hardening rather than confirmed security-fix.
2. Do not classify as rpc-client-api serialization or client-view divergence.
3. Supported impact is limited to failed handshake cleanup and connection resource accounting.
4. Do not claim a cryptographic flaw, authentication bypass, or quantified denial-of-service condition.
