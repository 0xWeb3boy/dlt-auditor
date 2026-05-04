# Validation Card

## Metadata

- ID: `snarkos-2022-12-13-snarkos-p2p-networking-e8c8f3bd9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-peer-address-resolution`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Resolve the connection address to the router-tracked listener address before invoking disconnect enforcement.
- Root-cause evidence from the finding: The code treated the process_message SocketAddr as the address identity suitable for router disconnect enforcement. The patch implies that this observed connection address can differ from the listener address tracked by the router, so direct use could target disconnect handling at the wrong address representation. 1. A message is received by a role-specific Reading::process_message implementation. 2. The handler calls inbound(peer_addr, message). 3. If inbound returns an error, the code treats t

## What Could Have Invalidated It

- Router disconnect internally canonicalizes addresses.
- Peer table stores both connection and listener addresses.

## Severity Guidance

- Expected impact band: `peer-enforcement-correctness`
- Expected severity band: `low`
- Rationale: Low severity is appropriate when the affected boundary is reachable and the sink controls wrong peer disconnect target; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- If connection and listener addresses are always identical, issue is correctness only
- Errors from trusted local peers reduce attack relevance
- No security issue if disconnect is advisory
