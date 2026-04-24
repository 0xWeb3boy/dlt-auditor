# Validation Card

## Metadata

- ID: `optimism-2022-09-19-optimism-storage-af3e56b124`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control-invariant-bypass`

## What Confirmed The Issue

- Commit message explicitly says the owner/proposer distinctness requirement was circumventable.
- Commit message says the fix enforces the invariant in transferOwnership and initialize.
- Post-patch L2OutputOracle artifact shows revert paths for proposer/owner equality in initialization and ownership transfer.
- The change affects privileged-role assignment in an oracle contract, which is security-sensitive.

## What Could Have Invalidated It

- No direct Solidity diff for packages/contracts-bedrock/contracts/L1/L2OutputOracle.sol was provided.
- No test hunk was provided to confirm the exact pre-patch and post-patch behavior.
- No evidence shows a concrete exploit, attacker path, or real-world impact beyond policy circumvention.
- The supplied OptimismPortal and L2ToL1MessagePasser changes look like regeneration fallout, not independent security proof.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No direct Solidity diff for packages/contracts-bedrock/contracts/L1/L2OutputOracle.sol was provided.
- No test hunk was provided to confirm the exact pre-patch and post-patch behavior.
- No evidence shows a concrete exploit, attacker path, or real-world impact beyond policy circumvention.
