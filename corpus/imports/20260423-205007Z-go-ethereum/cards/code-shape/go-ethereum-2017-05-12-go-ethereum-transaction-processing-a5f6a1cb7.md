# Code-Shape Card

## Metadata

- ID: `go-ethereum-2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-configuration-hardening`

## Code Shape Summary

- MetropolisBlock was omitted from the same chain configuration compatibility boundary used for earlier consensus fork blocks. Based on the shown code, that meant a replacement ChainConfig could avoid rejection solely because the changed field was the Metropolis activation height.

## Search Motifs

- Motif 1: wallet or signing api missing exact checks for consensus configuration hardening
- Motif 2: security-sensitive path reaches transaction or message signing under local account authority before rejecting malformed or unauthorized input
- Motif 3: Extend fork-configuration compatibility checks to cover the newly supported fork boundary, using the same shared predicates already used for earlier forks

## Typical Asymmetry

- A low-trust caller can reach signature authority or privileged wallet actions if policy checks are too permissive or poorly bound.

## Patch Pattern

- Extend fork-configuration compatibility checks to cover the newly supported fork boundary, using the same shared predicates already used for earlier forks.

## False Match Warnings

- Classify as consensus configuration hardening, not a confirmed security fix.
- Do not claim transaction-processing, signature, replay, or VM impact from this evidence.
