# Validation Card

## Metadata

- ID: `optimism-2024-05-28-optimism-cryptography-926ba71288`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- validatePlasmaConfig now rejects unsupported commitment types instead of accepting config and returning success.
- The config validator enforces different DAChallengeAddress requirements for keccak versus generic commitments, tightening mode-specific invariants.
- GetOPPlasmaConfig() now parses and carries CommitmentType into runtime plasma config rather than leaving it implicit.
- DA.GetInput(...) now rejects commitment data whose runtime type does not match the configured commitment mode before continuing processing.

## What Could Have Invalidated It

- No evidence shows an attacker could previously exploit commitment-type confusion from an external boundary.
- No proof that mismatched commitment types previously led to unsafe state transition, consensus failure, or acceptance of invalid data.
- No demonstrated fund-loss, authorization bypass, or concrete integrity break tied to the pre-patch behavior.
- Part of the commit is feature/config plumbing for generic commitments, which weakens a claim that the whole change is a pure vulnerability fix.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No evidence shows an attacker could previously exploit commitment-type confusion from an external boundary.
- No proof that mismatched commitment types previously led to unsafe state transition, consensus failure, or acceptance of invalid data.
- No demonstrated fund-loss, authorization bypass, or concrete integrity break tied to the pre-patch behavior.
