# Validation Card

## Metadata

- ID: `snarkos-2021-07-11-snarkos-cryptography-9dfc4e2da`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-network-id-validation`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Add a miner-side network-id validation gate and prefer canonical consensus/DPC identifiers during construction.
- Root-cause evidence from the finding: No proven vulnerability root cause is established. The before code lacked an explicit miner-side network-id check in the shown function, but the supplied evidence does not show that cross-network transactions could actually be accepted into finalized blocks or bypass validation elsewhere. 1. Miner coinbase construction receives a set of transactions. 2. The before evidence does not show add_coinbase_transaction checking each transaction.network against the active consensus network id before crea

## What Could Have Invalidated It

- Mempool admission enforces the same network id invariant.
- Final block verification rejects mismatched network ids before propagation.

## Severity Guidance

- Expected impact band: `consensus-domain-separation`
- Expected severity band: `medium`
- Rationale: Medium severity is appropriate when the affected boundary is reachable and the sink controls cross-network transaction inclusion risk; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- Full node validation after mining may still reject mismatched transactions
- Testnet migration commits can be compatibility work rather than security
- If transactions are locally generated only, attacker control is limited
