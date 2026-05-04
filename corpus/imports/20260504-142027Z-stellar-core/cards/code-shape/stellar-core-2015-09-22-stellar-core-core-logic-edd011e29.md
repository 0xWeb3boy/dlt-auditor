# Code-Shape Card

## Metadata

- ID: `stellar-core-2015-09-22-stellar-core-core-logic-edd011e29`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `preauth-io-timeout-hardening`

## Code Shape Summary

- Timeout handling lived in the TCP peer layer and did not clearly distinguish unauthenticated from authenticated peer states until moved into shared peer policy.

## Search Motifs

- same idle timeout before and after peer authentication
- pre handshake timeout tightened
- getIOTimeoutSeconds depends on authenticated state
- idle timer implemented only in TCP peer

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Centralize IO timeout selection in the peer abstraction and choose a short timeout for unauthenticated connections while preserving longer authenticated-peer behavior.

## False Match Warnings

- A low global connection cap may mitigate the issue.
- Long authenticated-peer timeouts are expected after identity and protocol negotiation.
- Timeout refactors without pre-auth policy changes are usually reliability work.
