# Validation Card

## Metadata

- ID: `stellar-core-2015-09-22-stellar-core-core-logic-edd011e29`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `preauth-io-timeout-hardening`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Timeout handling moved from TCPPeer toward Peer.
- Peer::getIOTimeoutSeconds selects timeout based on authentication state.
- The commit subject states the pre-handshake timeout was tightened.

## What Could Have Invalidated It

- If connection establishment is already rate-limited before the peer object exists, blast radius is reduced.
- If the timeout only affects tests or loopback peers, security relevance is low.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium_or_low
- Rationale: Pre-auth connection stalls can consume node resources, but the evidence supports hardening rather than a demonstrated DoS exploit.

## False-Positive Cautions

- Do not flag slow authenticated application-level protocols as pre-auth DoS.
- Check for connection caps and accept throttles before rating severity.
