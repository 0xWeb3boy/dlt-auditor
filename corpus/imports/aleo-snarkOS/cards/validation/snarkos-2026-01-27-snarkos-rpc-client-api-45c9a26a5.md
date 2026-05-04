# Validation Card

## Metadata

- ID: `snarkos-2026-01-27-snarkos-rpc-client-api-45c9a26a5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-peer-misbehavior-enforcement`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `confirmed` and kept in the security corpus.
- The patch pattern matches the missing property: Preserve structured validation errors and map selected invalid block-response errors to ip_ban_peer/disconnect in client and BFT ingress paths.
- Root-cause evidence from the finding: The supported root cause is incomplete escalation after detecting invalid consensus-version block responses. The code already surfaced structured InsertBlockResponseError variants, but some inbound block-response handlers did not consistently ban the peer after those errors. 1. A peer sends a block response with blocks and latest_consensus_version metadata. 2. BlockSync::insert_block_responses derives the relevant block height and checks the expected consensus version. 3. Invalid cases are repor

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
