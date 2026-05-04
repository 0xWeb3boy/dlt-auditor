---
case_id: case_20220217_d7ff8cc55
project: stellar-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2022-02-17
source_refs:
  - git:d7ff8cc55900a59acb5ea2398005139682462147
  - "src/overlay/TCPPeer.cpp:499"
  - "src/overlay/Peer.cpp:541"
  - "src/overlay/TCPPeer.cpp:643"
  - "src/overlay/Peer.cpp:687"
bug_class: p2p-overlay-flow-control-hardening
impact_type:
  - denial-of-service-hardening
  - resource-exhaustion-hardening
confidence: medium
tags:
  - blockchain-core
  - overlay
  - p2p
  - flow-control
  - resource-control
  - read-throttling
  - protocol-version-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Commit d7ff8cc55 implements overlay peer flow control in stellar-core. The evidence supports a resource-control and protocol-state change in the P2P overlay, including read throttling, SEND_MORE handling, flood-message gating, and version validation. It does not prove a concrete security vulnerability, denial of service condition, consensus impact, or authorization bypass, so this should be treated as security-relevant but unconfirmed rather than kept as a vulnerability fix.

## Observed Patch Facts

1. In `src/overlay/TCPPeer.cpp`, the patch replaces `if (mApp.getClock().shouldYield())` with `if (!hasReadingCapacity())`.

2. In `src/overlay/Peer.cpp`, the patch replaces `AuthenticatedMessage amsg;` with `case SEND_MORE:`.

3. In `src/overlay/TCPPeer.cpp`, the patch replaces `scheduleRead();` with `if (!hasReadingCapacity())`.

4. In `src/overlay/Peer.cpp`, the patch replaces `case MessageType::HELLO:` with `case HELLO:`.

## Project Context

The changed code sits primarily in `src/overlay`, which anchors the finding in the `storage` area of the project. Historical context from `src/overlay/PeerManager.h`, `src/overlay/PeerManager.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/overlay/Tracker.cpp`, `src/overlay/SurveyManager.cpp`. The strongest project-level identifiers around this patch are `case`, `Peer`, `mApp`, and `TCPPeer::readBodyHandler`. Nearby tests or test-like files include `src/overlay/test/TCPPeerTests.cpp`, `src/overlay/test/PeerManagerTests.cpp`.

## Before/After Behavior

Before the change, the shown TCPPeer read paths continued based on generic yielding or unconditionally scheduled another read after processing a body. After the change, those paths check hasReadingCapacity(), mark the peer throttled, and return when capacity is unavailable. Peer::sendMessage() now includes SEND_MORE metering and gates flood messages based on flow-control state. Peer::recvMessage() now handles SEND_MORE as a control message and drops peers that send it without negotiated overlay-version support.

# Root Cause

The supported root cause is absence of explicit flow-control checks and SEND_MORE protocol-state validation in the shown overlay peer read/send paths. The evidence does not establish that this absence caused an exploitable resource exhaustion bug.

## Walkthrough

1. A TCP peer reads a complete message body and calls recvMessage().

2. The patched startRead() path checks hasReadingCapacity() after processing a message.

3. If capacity is unavailable, the peer is marked throttled and the function returns.

4. The patched readBodyHandler() path likewise avoids scheduling another read when capacity is unavailable.

5. Peer::sendMessage() now accounts for SEND_MORE metrics and gates flood messages while flow-control state is unknown or enabled.

6. Peer::recvMessage() now treats SEND_MORE as a control message.

7. Peers that send SEND_MORE without sufficient negotiated overlay-version support are dropped.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/overlay/TCPPeer.cpp | 499 | Inbound read loop now stops reading and marks the peer throttled when per-peer reading capacity is exhausted. |
| src/overlay/TCPPeer.cpp | 643 | Body read handler now avoids scheduling more reads after processing a message if capacity is unavailable. |
| src/overlay/Peer.cpp | 541 | Outbound flood-message path now accounts for SEND_MORE metrics and gates flood sends based on flow-control state. |
| src/overlay/Peer.cpp | 687 | Inbound message dispatch handles SEND_MORE as a control message and drops peers that send it without negotiated version support. |

## Code Snippets

## Snippet 1

Context: `src/overlay/TCPPeer.cpp:499` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
noteFullyReadBody(length);
                recvMessage();
                if (mApp.getClock().shouldYield())
                {
```
After
```cpp
noteFullyReadBody(length);
                recvMessage();
                if (!hasReadingCapacity())
                {
                    // Break and wait until more capacity frees up
                    CLOG_TRACE(Overlay, "Throttle reading for peer {}!",
                               mApp.getConfig().toShortString(getPeerID()));
                    mIsPeerThrottled = true;
```

## Snippet 2

Context: `src/overlay/Peer.cpp:541` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
getOverlayMetrics().mSendSurveyResponseMeter.Mark();
        break;
    };

    AuthenticatedMessage amsg;
    amsg.v0().message = msg;
```
After
```cpp
getOverlayMetrics().mSendSurveyResponseMeter.Mark();
        break;
    case SEND_MORE:
        getOverlayMetrics().mSendSendMoreMeter.Mark();
        break;
    };

    if (mApp.getOverlayManager().isFloodMessage(*msg))
```

## Snippet 3

Context: `src/overlay/TCPPeer.cpp:643` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
// worth of input. Even when we weren't preempted, we still bounce off
        // the per-peer scheduler queue here, to balance input across peers.
        scheduleRead();
    }
```
After
```cpp
// worth of input. Even when we weren't preempted, we still bounce off
        // the per-peer scheduler queue here, to balance input across peers.
        if (!hasReadingCapacity())
        {
            // No more capacity after processing this message
            CLOG_TRACE(Overlay,
                       "TCPPeer::readBodyHandler: throttle reading from {}",
                       mApp.getConfig().toShortString(getPeerID()));
```

## Snippet 4

Context: `src/overlay/Peer.cpp:687` (changes how canonical state is encoded, returned, or reconstructed)

Before
```cpp
{
    // group messages used during handshake, process those synchronously
    case MessageType::HELLO:
    case MessageType::AUTH:
        Peer::recvRawMessage(stellarMsg);
        return;

    // control messages
```
After
```cpp
{
    // group messages used during handshake, process those synchronously
    case HELLO:
    case AUTH:
        Peer::recvRawMessage(stellarMsg);
        return;
    case SEND_MORE:
    {
```

# Fix Pattern

Add explicit overlay flow-control enforcement: capacity checks in inbound read paths, gating in outbound flood-message handling, SEND_MORE metrics, and protocol-version validation for SEND_MORE.

## How It Was Fixed

The patch added hasReadingCapacity() checks to TCPPeer::startRead() and TCPPeer::readBodyHandler(), setting mIsPeerThrottled and returning when capacity is exhausted. It added SEND_MORE handling in Peer::sendMessage() and Peer::recvMessage(), including flood-message gating and rejection of SEND_MORE from peers that did not negotiate support.

# Why It Matters

1. Bounds read continuation using per-peer capacity checks.

2. Avoids scheduling more reads after capacity is exhausted.

3. Avoids flood-message sends before flow-control state is established.

4. Rejects SEND_MORE from peers without negotiated support.

5. Evidence does not prove an exploitable vulnerability.

# Evidence Notes

Primary evidence is from src/overlay/TCPPeer.cpp around lines 499 and 643 and src/overlay/Peer.cpp around lines 541 and 687. The heuristic storage/serialization framing is unsupported by the provided diff. The mapper's overlay-p2p/resource-flow-control classification is supported as a change description, but the stronger security-hardening verdict is not proven by the supplied evidence. Protocol security invariant: Overlay peers should apply negotiated flow-control state and capacity checks before continuing inbound reads, sending flood messages, or accepting SEND_MORE control messages. The supplied evidence shows this invariant being introduced or enforced, but does not establish that the prior behavior was an exploitable vulnerability. Verification notes: The patch does not prove a remotely exploitable denial of service existed before it. The patch does not prove authentication, authorization, or privilege bypass. The patch does not prove consensus safety, ledger integrity, or economic loss impact. The patch does not show a serialization or canonical-state representation bug. The patch may be a protocol feature implementation with security-relevant resource-hardening effects rather than a vulnerability fix. No exploit scenario is shown in the supplied evidence. No crash, memory exhaustion, unbounded queue growth, or consensus failure is demonstrated. No authentication, authorization, or privilege boundary issue is shown. The patch may be a protocol feature implementation with security-relevant resource-control properties. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `p2p-overlay-flow-control-hardening`
Final impact type: `denial-of-service-hardening, resource-exhaustion-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, overlay, p2p, flow-control, resource-control, read-throttling, protocol-version-validation`

The supplied patch evidence supports retaining this as security hardening, not as a concrete security fix. The change adds explicit capacity-based throttling in remotely reachable TCP peer read paths, gates flood-message sending until flow-control state is known, handles SEND_MORE as a control message, and drops peers that send SEND_MORE without negotiated support. The evidence does not prove an exploitable denial-of-service vulnerability, consensus impact, storage issue, or serialization/state-representation bug, so the original storage/serialization framing should be corrected.

## Security Evidence

1. Inbound TCP peer reads now stop when hasReadingCapacity() is false and mark the peer throttled.
2. readBodyHandler no longer unconditionally schedules more reads after processing a message when capacity is exhausted.
3. Outbound flood messages are gated based on negotiated flow-control state.
4. SEND_MORE is explicitly handled as a control message.
5. Peers sending SEND_MORE without overlay-version support are dropped.

## Missing Evidence

1. No commit message or patch comment states that a vulnerability was fixed.
2. No exploit scenario, crash, memory exhaustion, or unbounded queue growth is demonstrated.
3. No authentication, authorization, privilege, consensus, storage, or serialization bug is shown.
4. No regression test evidence is supplied that proves a prior security failure.

## Claim Boundaries

1. Classify as security hardening for exposed P2P resource-control behavior, not as a confirmed vulnerability fix.
2. Do not claim consensus safety, ledger integrity, economic loss, or client-view divergence impact from the supplied evidence.
3. Do not retain the original storage or serialization/state-representation classification.
4. The strongest supported impact is conservative denial-of-service/resource-exhaustion risk reduction.
