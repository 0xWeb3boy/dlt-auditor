# Validation Card

## Metadata

- ID: `snarkos-2026-01-27-snarkos-rpc-client-api-7cdc93d7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-peer-penalty-for-invalid-consensus-version`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `confirmed` and kept in the security corpus.
- The patch pattern matches the missing property: Add peer penalties at block-response ingress points for missing or mismatched consensus-version InsertBlockResponseError cases.
- Root-cause evidence from the finding: Invalid or forked block-sync peers were rejected or errored in the shown paths, but peer penalties were not consistently applied for consensus-version validation failures. This allowed peers that sent missing or mismatched consensus-version data to remain available as future block sources. 1. A peer sends a block response with blocks and an optional latest_consensus_version. 2. BlockSync::insert_block_responses checks the response and can return InsertBlockResponseError variants including NoCons

## What Could Have Invalidated It

- Peer manager already marks the peer unusable after failed insertion.
- Upgrade coordination layer disconnects mismatched peers.

## Severity Guidance

- Expected impact band: `peer-enforcement`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls forked/outdated peers remain in sync pool; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- During planned upgrades, temporary mismatch may be handled by softer policy
- This does not imply invalid block insertion if validation already rejects
- Trusted static peers may use different enforcement policy
