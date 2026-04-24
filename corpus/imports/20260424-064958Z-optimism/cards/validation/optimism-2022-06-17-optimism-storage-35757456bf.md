# Validation Card

## Metadata

- ID: `optimism-2022-06-17-optimism-storage-35757456bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `oracle-output-key-mismatch`

## What Confirmed The Issue

- The proposer changed from using LatestBlockTimestamp and derived block lookup to directly using LatestBlockNumber for output selection.
- CraftTx now validates the fetched L2 header by exact block number equality instead of only timestamp equality.
- Commit metadata explicitly mentions oracle reorg protection and withdrawals logic, both security-sensitive protocol areas.
- Project context shows OptimismPortal.finalizeWithdrawalTransaction consumes _l2BlockNumber, tying oracle key correctness to withdrawal proof/finality behavior.

## What Could Have Invalidated It

- No contract-side excerpt shows the exact pre-patch faulty acceptance condition in L2OutputOracle.sol.
- No concrete exploit scenario or failing unauthorized-withdrawal path is demonstrated in the provided patch snippets.
- No evidence proves timestamps were attacker-influenced, ambiguous in practice, or sufficient to cause acceptance of the wrong output.
- The provided excerpts do not show the added tests, so the exact regression/security property being enforced is only implied.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No contract-side excerpt shows the exact pre-patch faulty acceptance condition in L2OutputOracle.sol.
- No concrete exploit scenario or failing unauthorized-withdrawal path is demonstrated in the provided patch snippets.
- No evidence proves timestamps were attacker-influenced, ambiguous in practice, or sufficient to cause acceptance of the wrong output.
