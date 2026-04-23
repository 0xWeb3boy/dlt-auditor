# Code-Shape Card

## Metadata

- ID: `go-ethereum-2025-12-11-go-ethereum-transaction-processing-56d201b0f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-metadata-validation`

## Code Shape Summary

- The fetcher accepted peer-supplied announcement metadata far enough to schedule fetches without first checking whether the announced transaction type was supported by the local txpool. The commit text says later body validation still rejected mismatched or unsupported responses, so the root cause is early metadata validation missing in the P2P fetch path.

## Search Motifs

- Motif 1: transaction admission path missing exact checks for p2p metadata validation
- Motif 2: security-sensitive path reaches shared txpool reservation, scheduling, or eviction state before rejecting malformed or unauthorized input
- Motif 3: Validate untrusted P2P announcement metadata at the scheduling boundary using the same local capability model that downstream txpool acceptance relies on

## Typical Asymmetry

- Small externally controlled inputs can reach a disproportionately sensitive state, validation, or resource-management sink.

## Patch Pattern

- Validate untrusted P2P announcement metadata at the scheduling boundary using the same local capability model that downstream txpool acceptance relies on.

## False Match Warnings

- Keep only as low-impact P2P resource-hardening, not as a state-integrity fix.
- Do not claim transaction bodies were accepted incorrectly; later validation still applies according to the commit body.
