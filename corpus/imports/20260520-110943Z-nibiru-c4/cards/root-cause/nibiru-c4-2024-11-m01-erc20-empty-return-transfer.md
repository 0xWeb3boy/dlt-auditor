# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m01-erc20-empty-return-transfer`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `strict-erc20-return-decoding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `token-return-value compatibility handling`

## Violated Invariant

- Invariant: Token integration code should distinguish call success from optional ERC20 return-data conventions when the supported token set includes missing-return tokens.

## Trust Boundary

- Boundary: external ERC20 contract->FunToken conversion logic

## Attack Surface

- Entrypoint type: ERC20 transfer helper
- Sensitive sink: FunToken conversion transfer result decoding

## Impact Pattern

- Primary impact: supported token conversion DoS
- Secondary impact: user funds stuck in unsupported conversion paths

## Short Reusable Lesson

- ERC20 Transfer called UnpackIntoInterface for a bool even when resp.Ret was empty, converting successful missing-return transfers into errors.
