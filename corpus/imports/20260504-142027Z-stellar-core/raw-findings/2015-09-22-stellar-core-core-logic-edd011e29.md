---
case_id: case_20150922_edd011e29
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
source_quality: high
date: 2015-09-22
source_refs:
  - git:edd011e291566094bb3d95faa8be5de71ef10475
  - "src/overlay/TCPPeer.cpp:90"
  - "src/overlay/Peer.cpp:183"
  - "src/overlay/TCPPeer.cpp:33"
  - "src/overlay/OverlayTests.cpp:23"
bug_class: preauth-io-timeout-hardening
impact_type:
  - availability-hardening
  - resource-exhaustion-mitigation
confidence: medium
tags:
  - blockchain-core
  - overlay-network
  - peer-handshake
  - pre-authentication
  - timeout
  - resource-control
  - availability-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch moves idle timeout handling from TCPPeer toward the generic Peer layer and adds authentication-state-dependent timeout selection. The commit subject says the pre-handshake timeout was tightened to 2 seconds, while the visible Peer.cpp hunk shows authenticated peers receive 30 seconds. This may be availability hardening, but the provided evidence does not establish an exploitable resource-exhaustion vulnerability or other concrete security impact.

## Observed Patch Facts

1. In `src/overlay/TCPPeer.cpp`, the patch replaces `void` with `std::string`.

2. In `src/overlay/Peer.cpp`, the patch replaces `void` with `size_t`.

3. In `src/overlay/TCPPeer.cpp`, the patch removes `, mIdleTimer(app)`.

4. In `src/overlay/OverlayTests.cpp`, the patch replaces `for (size_t i = 0; i < 100 && clock.crank(false) > 0; ++i)` with `auto start = clock.now();`.

## Project Context

The changed code sits primarily in `src/overlay`, which anchors the finding in the `core-logic` area of the project. Historical context from `src/overlay/OverlayManagerImpl.cpp`, `src/overlay/TCPPeerTests.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/overlay/OverlayManagerImpl.cpp`, `src/overlay/TCPPeerTests.cpp`. The strongest project-level identifiers around this patch are `clock`, `std::chrono::seconds`, `TCPPeer::startIdleTimer`, and `Peer::getIOTimeoutSeconds`.

## Before/After Behavior

Before the patch, TCPPeer initialized idle timer state and implemented TCPPeer::startIdleTimer using a single IO timeout path. After the patch, TCPPeer no longer owns that timer setup in the shown constructor, TCPPeer::startIdleTimer is removed from TCPPeer.cpp, and Peer.cpp adds Peer::getIOTimeoutSeconds() that branches on isAuthenticated(). OverlayTests.cpp also bounds virtual-clock cranking by elapsed virtual time.

# Root Cause

A concrete security root cause is not established. The supported technical issue is that timeout policy was being corrected and centralized so peer IO timeout duration can depend on authentication state.

## Walkthrough

1. TCPPeer previously initialized idle timer, strand, last-read/write tracking, and IO metric state in its constructor.

2. TCPPeer::startIdleTimer previously scheduled mIdleTimer using IO_TIMEOUT_SECONDS.

3. The patch removes that TCPPeer-specific timer initialization and startIdleTimer implementation from the shown TCPPeer.cpp hunks.

4. Peer.h contains shared peer state including mStrand, mIdleTimer, mLastRead, and mLastWrite.

5. Peer.cpp adds Peer::getIOTimeoutSeconds().

6. The new timeout method returns 30 seconds when isAuthenticated() is true.

7. The commit subject states the pre-handshake phase was tightened to 2 seconds, but the visible hunk does not independently show the exact unauthenticated return value.

8. OverlayTests.cpp changes crankSome() to stop after one second of virtual-clock time, consistent with timeout-sensitive tests.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/overlay/Peer.cpp | 183 | Defines Peer::getIOTimeoutSeconds with different timeout behavior for authenticated versus unauthenticated peers. |
| src/overlay/Peer.h | 47 | Places strand, idle timer, and last-read/write tracking in the base Peer state used by overlay peers. |
| src/overlay/TCPPeer.cpp | 33 | Removes TCPPeer-local ownership/initialization of timeout and IO metrics state, implying timeout responsibility moved to Peer. |
| src/overlay/TCPPeer.cpp | 90 | Removes TCPPeer::startIdleTimer implementation from the TCP-specific layer. |
| src/overlay/OverlayTests.cpp | 23 | Updates virtual-clock cranking behavior to account for bounded timeout-driven events in overlay tests. |

## Code Snippets

## Snippet 1

Context: `src/overlay/TCPPeer.cpp:90` (changes bounds, limits, or capacity handling)

Before
```cpp
}

void
TCPPeer::startIdleTimer()
{
    if (shouldAbort())
    {
        return;
```
After
```cpp
}

std::string
TCPPeer::getIP()
```

## Snippet 2

Context: `src/overlay/Peer.cpp:183` (changes bounds, limits, or capacity handling)

Before
```cpp
}

void
Peer::sendAuth()
```
After
```cpp
}


size_t
Peer::getIOTimeoutSeconds() const
{
    if (isAuthenticated())
    {
```

## Snippet 3

Context: `src/overlay/TCPPeer.cpp:33` (changes bounds, limits, or capacity handling)

Before
```cpp
: Peer(app, role)
    , mSocket(socket)
    , mIdleTimer(app)
    , mLastRead(app.getClock().now())
    , mLastWrite(app.getClock().now())
    , mStrand(app.getClock().getIOService())
    , mMessageRead(
          app.getMetrics().NewMeter({"overlay", "message", "read"}, "message"))
```
After
```cpp
: Peer(app, role)
    , mSocket(socket)
{
}
```

## Snippet 4

Context: `src/overlay/OverlayTests.cpp:23` (changes a sensitive control or state-update path)

Before
```cpp
void crankSome(VirtualClock& clock)
{
    for (size_t i = 0; i < 100 && clock.crank(false) > 0; ++i)
        ;
}
```
After
```cpp
void crankSome(VirtualClock& clock)
{
    auto start = clock.now();
    for (size_t i = 0;
         (i < 100 &&
          clock.now() < (start + std::chrono::seconds(1)) &&
          clock.crank(false) > 0);
         ++i)
```

# Fix Pattern

Centralize peer IO timeout policy in the shared Peer abstraction and select timeout duration based on authentication state.

## How It Was Fixed

The patch removes TCPPeer-local idle timer handling shown in TCPPeer.cpp and introduces Peer::getIOTimeoutSeconds(), allowing the base peer logic to distinguish authenticated from unauthenticated peers. The authenticated timeout is visibly 30 seconds; the 2-second pre-handshake timeout is supported by the commit subject rather than the shown code lines.

# Why It Matters

1. Pre-authentication peer connections can consume resources.

2. Shorter pre-handshake timeouts can reduce exposure to stalled or incomplete handshakes.

3. The evidence supports hardening or correctness, not a confirmed vulnerability.

4. No concrete attack path or impact is demonstrated.

# Evidence Notes

Grounded evidence comes from TCPPeer.cpp constructor and removed startIdleTimer hunks, Peer.h shared peer state, Peer.cpp getIOTimeoutSeconds(), and OverlayTests.cpp clock-cranking changes. Unsupported claims removed or downgraded: confirmed security fix, proven preauth resource-exhaustion vulnerability, concrete exploitability, consensus impact, authentication bypass, cryptographic failure, and LoopbackPeer behavior. Protocol security invariant: Potential availability invariant: overlay peers should apply shorter IO timeouts before authentication than after authentication so incomplete handshakes do not hold peer resources as long as authenticated connections. The provided evidence supports a timeout policy change, but not a demonstrated vulnerability. Verification notes: No concrete remote exploit path is proven by the provided patch evidence. No authentication bypass or cryptographic failure is shown. No consensus safety or ledger integrity impact is demonstrated. The evidence supports availability/resource-control hardening, not confirmed vulnerability exploitation. LoopbackPeer impact is implied by changed files but not reconstructable from the provided hunks. No commands or external inspection were performed. The exact unauthenticated timeout value is inferred from the commit subject, not fully visible in the provided Peer.cpp hunk. The patch may be security relevant, but the vulnerability thesis is not established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `preauth-io-timeout-hardening`
Final impact type: `availability-hardening, resource-exhaustion-mitigation`
Final confidence: `medium`
Final tags: `blockchain-core, overlay-network, peer-handshake, pre-authentication, timeout, resource-control, availability-hardening`

The evidence supports retaining this as security hardening, not a confirmed vulnerability fix. The commit explicitly tightens the pre-handshake IO timeout, and the patch centralizes timeout policy in Peer with behavior depending on authentication state. That is a security-sensitive resource-control change for unauthenticated network peers, but the supplied hunks do not prove exploitation, denial-of-service impact, or the exact unauthenticated timeout implementation independently of the commit subject.

## Security Evidence

1. Commit subject states the pre-handshake IO timeout was tightened to 2 seconds.
2. Peer::getIOTimeoutSeconds() branches on isAuthenticated(), separating authenticated and unauthenticated timeout policy.
3. Authenticated peers visibly receive a longer 30 second timeout, implying stricter handling before authentication.
4. The touched code is in src/overlay peer connection handling, an exposed network subsystem.
5. TCPPeer-local idle timer logic is moved toward shared Peer behavior, making timeout enforcement apply at the peer abstraction.

## Missing Evidence

1. No concrete exploit path or attacker-controlled resource exhaustion scenario is shown.
2. The provided Peer.cpp hunk does not show the unauthenticated return value directly.
3. No advisory, CVE, test name, or commit body states a security vulnerability.
4. No evidence shows consensus safety, authentication bypass, cryptographic failure, or ledger integrity impact.

## Claim Boundaries

1. Classify as availability-oriented hardening only, not a proven security bug fix.
2. Do not claim a confirmed denial-of-service vulnerability from the supplied patch alone.
3. Do not claim the exact 2 second unauthenticated timeout is code-visible; it is supported by the commit subject.
4. Do not retain misleading database or validator-specific tags for the final corpus entry.
