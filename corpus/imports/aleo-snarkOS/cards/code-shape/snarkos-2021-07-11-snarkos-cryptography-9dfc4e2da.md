# Code-Shape Card

## Metadata

- ID: `snarkos-2021-07-11-snarkos-cryptography-9dfc4e2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-network-id-validation`

## Code Shape Summary

- Miner-side coinbase or block-construction logic lacks an explicit network-id check before using transaction data in consensus construction.

## Search Motifs

- transaction.network_id compared only outside miner path
- coinbase creation accepts transaction without consensus-parameter network check
- canonical noop/program id replaces ad hoc identifier

## Typical Asymmetry

- The code has a validation, authentication, sizing, correlation, or peer-enforcement concept nearby, but the specific inbound path either does not call it, ignores its result, signs too little data, or maps failure to a log/return instead of a state-changing rejection.

## Patch Pattern

- Add a miner-side network-id validation gate and prefer canonical consensus/DPC identifiers during construction.

## False Match Warnings

- Full node validation after mining may still reject mismatched transactions
- Testnet migration commits can be compatibility work rather than security
- If transactions are locally generated only, attacker control is limited
