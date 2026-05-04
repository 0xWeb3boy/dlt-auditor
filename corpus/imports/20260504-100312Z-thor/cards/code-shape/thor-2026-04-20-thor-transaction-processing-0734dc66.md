# Code-Shape Card

## Metadata

- ID: `thor-2026-04-20-thor-transaction-processing-0734dc66`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `chain-id-validation-hardening`

## Code Shape Summary

- The Ethereum typed transaction path had to be bound to the fork activation point and configured Ethereum chain ID across txpool, consensus, and runtime CHAINID; the fix rejects pre-fork or mismatched-domain transactions.

## Search Motifs

- typed transaction skips legacy chain-tag validation
- EthChainID compared only after new fork activation
- mempool and consensus validators implement different chain-id rules
- runtime CHAINID differs from transaction signature domain

## Typical Asymmetry

- The external or cross-context input is treated as already safe, while the later privileged sink assumes that admission, domain, or cardinality checks already happened upstream.

## Patch Pattern

- Add fork-aware validation in both mempool and consensus, compare embedded typed-transaction chain ID with configured network domain, and align runtime CHAINID after the fork.

## False Match Warnings

- No issue if typed transactions are impossible before the fork.
- No issue if signature recovery independently rejects mismatched chain IDs everywhere.
- Fork configuration changes without admission checks are not enough to establish a security case.
