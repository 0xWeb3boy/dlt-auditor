# Code-Shape Card

## Metadata

- ID: `thor-2026-04-20-thor-transaction-processing-9b49413a`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-chain-id-validation`

## Code Shape Summary

- EIP-1559 typed transactions bypassed legacy chain-tag checks but lacked shown validation that their embedded Ethereum chain ID matched the active configured network domain; the fix adds fork gating and chain-ID comparisons in txpool and consensus and aligns runtime CHAINID.

## Search Motifs

- new typed transaction path bypasses legacy replay check
- EthChainID not compared with configured network ID
- mempool accepts transaction type before consensus fork gate
- runtime chain ID and signed transaction domain can diverge

## Typical Asymmetry

- The external or cross-context input is treated as already safe, while the later privileged sink assumes that admission, domain, or cardinality checks already happened upstream.

## Patch Pattern

- Apply the same fork-aware chain-ID validation at mempool and consensus boundaries and make runtime expose the post-fork configured Ethereum chain ID.

## False Match Warnings

- No issue if mismatched chain IDs fail during signature recovery before acceptance.
- No issue if the transaction type is unreachable until the fork activates.
- Do not flag duplicate fork plumbing without an acceptance path for signed transactions.
