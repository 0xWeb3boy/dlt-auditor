# Root-Cause Card

## Metadata

- ID: `scroll-2025-07-02-scroll-rpc-client-api-adac0404`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verifier-artifact-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `verifier-artifact-selection`

## Violated Invariant

- Invariant: Proof verification tooling should pair each proof with the intended verification key and required verifier assets instead of silently accepting mismatched or incomplete local artifacts.

## Trust Boundary

- Boundary: `operator-input->verification-tooling`

## Attack Surface

- Entrypoint type: `query-verification-path`
- Sensitive sink: `local proof verification result and exported verifier asset bundle`

## Impact Pattern

- Primary impact: `stale-trust-state`
- Secondary impact: `none`

## Short Reusable Lesson

- Proof verification tooling should pair each proof with the intended verification key and required verifier assets instead of silently accepting mismatched or incomplete local artifacts. The visible patch fixes verifier-tool behavior around verification-key handling and bundle verifier asset export. It corrects an inverted equality check for chunk and batch proofs, forces the bundle path to use the locally selected verifier key, and copies `verifier.bin` during asset export. That is clearly a correctness or hardening change in proof-verification tooling, but the provided evidence does not establish an exploitable vulnerability, a production attack boundary, or any on-chain security impact. The robust fix is to bind verification runs to the selected verification key, fix inverted artifact-consistency checks, and export the verifier binary required by the chosen proof path.
