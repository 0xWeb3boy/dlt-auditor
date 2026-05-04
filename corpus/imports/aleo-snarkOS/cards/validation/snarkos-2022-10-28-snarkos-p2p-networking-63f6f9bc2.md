# Validation Card

## Metadata

- ID: `snarkos-2022-10-28-snarkos-p2p-networking-63f6f9bc2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-protocol-validation-hardening`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Add envelope-vs-payload consistency checks and use stable envelope fields for outbound routing metadata.
- Root-cause evidence from the finding: The router did not validate that redundant envelope metadata for unconfirmed transactions and solutions matched the canonical identifiers derived from the deserialized payload. Separately, outbound routing logic depended on the local Data representation state even though the message already carried the needed identifiers. 1. A peer message for an unconfirmed transaction or solution contains both envelope metadata and a deferred-deserialized payload. 2. Before the patch, inbound routing accepted 

## What Could Have Invalidated It

- Mempool admission recomputes and rejects mismatched IDs.
- Router never trusts envelope metadata for propagation decisions.

## Severity Guidance

- Expected impact band: `mempool-routing-integrity`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls incorrect propagation metadata; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- If envelope fields are purely advisory and never stored, impact is low
- Downstream mempool validation may reject inconsistent objects
- Serialization refactors without added rejection logic may be non-security
