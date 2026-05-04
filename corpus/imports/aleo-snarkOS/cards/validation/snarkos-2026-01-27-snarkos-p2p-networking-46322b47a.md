# Validation Card

## Metadata

- ID: `snarkos-2026-01-27-snarkos-p2p-networking-46322b47a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-peer-misbehavior-enforcement`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `confirmed` and kept in the security corpus.
- The patch pattern matches the missing property: Preserve structured validation errors and map selected invalid block-response errors to ip_ban_peer/disconnect in client and BFT ingress paths.
- Root-cause evidence from the finding: The sync layer could report consensus-version-specific block response errors, but the client router did not distinguish those errors from generic insertion failures for peer enforcement. Peers that sent responses with invalid or missing consensus version information were therefore not shown to be banned by the old block_response path. 1. A peer sends a block response to the client block_response handler. 2. The handler calls self.sync.insert_block_responses(peer_ip, blocks, latest_consensus_vers

## What Could Have Invalidated It

- Separate reputation layer penalizes the same error.
- Sync source selection excludes the peer after any insertion failure.

## Severity Guidance

- Expected impact band: `peer-enforcement`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls invalid peers remain eligible as sync sources; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- If peer scoring elsewhere immediately removes the peer, duplicate ban may be unnecessary
- Benign upgrade mismatches may need grace-period policy
- This is enforcement hardening, not proof invalid blocks were accepted
