# Code-Shape Card

## Metadata

- ID: `snarkvm-2022-10-15-snarkvm-cryptography-8b2735410`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-consensus-target-validation`

## Code Shape Summary

- Coinbase and prover solution verification APIs lacked explicit target parameters, leaving correctness dependent on caller context or hidden state.

## Search Motifs

- verify(solution, key, challenge) without target threshold
- coinbase puzzle target checked in some call sites but not others
- mempool admits prover solution without latest proof target

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `consensus-target-validation`.

## Patch Pattern

- Thread coinbase and proof target thresholds through verification APIs, ledger call sites, and tests.

## False Match Warnings

- The verifier obtains the active target internally from a trusted snapshot.
- The changed API is only a refactor with identical target checks in all old paths.
- The solution is revalidated with the correct target before block acceptance.
