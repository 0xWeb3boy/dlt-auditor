# Validation Card

## Metadata

- ID: `snarkos-2020-04-06-snarkos-cryptography-95e340487`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `merkle-membership-validation`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Use full Merkle parameters through setup and tree construction, then activate conditional membership constraints for non-dummy witnesses.
- Root-cause evidence from the finding: The supported root cause is inconsistent or incomplete enforcement of DPC Merkle membership: ledger code used the underlying hash parameter type instead of the full Merkle parameter object, and the extracted circuit path did not visibly enforce the Merkle path membership constraint before the patch. 1. Both real and ideal ledger setup previously returned `P::H::setup(rng)`, tying setup to the underlying CRH parameters rather than the full Merkle parameter type. 2. Both ledger constructors previo

## What Could Have Invalidated It

- Another circuit constraint proves the same membership relation.
- The affected proof path is unused or test-only.

## Severity Guidance

- Expected impact band: `state-integrity`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls invalid commitment membership accepted; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- Dummy/null commitments may intentionally skip membership checks
- A separate enforced membership check in the same circuit can compensate
- Parameter refactors without verifier constraint changes may be non-security
