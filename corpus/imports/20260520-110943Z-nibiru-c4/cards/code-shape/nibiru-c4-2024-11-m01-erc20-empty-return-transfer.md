# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m01-erc20-empty-return-transfer`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `strict-erc20-return-decoding`

## Code Shape Summary

- ERC20 Transfer called UnpackIntoInterface for a bool even when resp.Ret was empty, converting successful missing-return transfers into errors.

## Search Motifs

- UnpackIntoInterface ERC20Bool transfer resp.Ret
- empty return data while arguments are expected
- weird ERC20 missing return value
- transfer did not revert but decode failed

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Treat a non-reverting transfer with empty return data as success, while still rejecting non-empty data that decodes to false or invalid values.

## False Match Warnings

- No issue if the protocol explicitly excludes missing-return tokens.
- No issue if token deployment is constrained to compliant contracts.
- No issue if empty return data is already accepted after a non-reverting call.
