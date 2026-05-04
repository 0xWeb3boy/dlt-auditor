# Validation Card

## Metadata

- ID: `snarkos-2020-03-02-snarkos-p2p-networking-01d3ecd83`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-panic-hardening`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Replace unwrap/silent failure paths with explicit result handling, logging, and normalized disconnect messages.
- Root-cause evidence from the finding: The root cause was brittle error handling for expected network failures in the server peer path. The supplied evidence shows panic-prone unwrap handling for handshake errors and unclear prior handling of channel read EOF/errors through silent_disconnect. 1. An inbound peer connects to Server::listen. 2. The server attempts receive_request_new(...) for the peer handshake. 3. Before the patch, a handshake error reached .unwrap(). 4. After the patch, only Ok(handshake) enters the branch that stores

## What Could Have Invalidated It

- Task supervisor catches the panic without process or service impact.
- Handshake failures are reachable only from trusted in-process tests.

## Severity Guidance

- Expected impact band: `availability-hardening`
- Expected severity band: `low`
- Rationale: Low severity is appropriate when the affected boundary is reachable and the sink controls node availability degradation; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- Only local test harnesses or non-production crawler code may reduce severity
- A surrounding supervisor that catches panics and isolates all peer state lowers impact
- If the error source is not peer-controlled, this is robustness rather than security
