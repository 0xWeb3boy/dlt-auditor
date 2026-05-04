# Validation Card

## Metadata

- ID: `snarkos-2021-11-10-snarkos-storage-5b6e62d57`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-fork-choice`

## What Confirmed The Issue

- The raw finding was validated by phase 4 as `security-hardening` with verdict `likely` and kept in the security corpus.
- The patch pattern matches the missing property: Compute cumulative chain weight from the common ancestor and switch only when the peer fork is heavier under consensus rules.
- Root-cause evidence from the finding: The synchronization path used higher peer block height as the deciding condition for switching forks, even though the patched logic indicates the intended fork-choice criterion is aggregate difficulty-target weight from the common ancestor. 1. A node examines peer ledger states in `update_block_requests` and selects a candidate peer with a high reported block height and block locators. 2. The code checks locator hashes that already exist locally and updates the common ancestor where applicable. 

## What Could Have Invalidated It

- Finalization prevents rollback through the affected range.
- Consensus engine recomputes fork weight before committing ledger changes.

## Severity Guidance

- Expected impact band: `consensus-integrity`
- Expected severity band: `high`
- Rationale: High severity is appropriate when the affected boundary is reachable and the sink controls incorrect reorg choice; reduce severity when the change is only hardening or a compensating control already enforces the invariant.

## False-Positive Cautions

- Height-based rules may be valid for protocols with fixed uniform block weight
- If the code is only UI progress estimation, not fork choice, it is not security
- A later finality checkpoint may override this path
