# Validation Card

## Metadata

- ID: `optimism-2024-03-05-optimism-storage-c66091d31f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `insufficient-domain-separation`

## What Confirmed The Issue

- Commit message says local preimages used the wrong chain ID and could not distinguish two L2s sharing one L1.
- Patch adds _l2ChainId to the contract constructor ABI.
- Patch updates deployment code to require and pass _l2ChainId during contract creation.
- Patch adds an l2ChainId() getter, indicating the contract now stores chain-specific identity.

## What Could Have Invalidated It

- No Solidity diff is shown for where local preimages are constructed or checked.
- No test excerpt demonstrates the pre-fix cross-L2 ambiguity or a blocked exploit after the fix.
- No evidence shows concrete fund loss, privilege bypass, or successful replay in practice.
- No evidence shows whether already-deployed instances were vulnerable or only new deployments/configurations.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No Solidity diff is shown for where local preimages are constructed or checked.
- No test excerpt demonstrates the pre-fix cross-L2 ambiguity or a blocked exploit after the fix.
- No evidence shows concrete fund loss, privilege bypass, or successful replay in practice.
