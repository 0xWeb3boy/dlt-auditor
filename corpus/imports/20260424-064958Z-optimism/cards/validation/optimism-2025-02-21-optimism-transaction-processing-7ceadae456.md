# Validation Card

## Metadata

- ID: `optimism-2025-02-21-optimism-transaction-processing-7ceadae456`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- BlockPayloadArgs.Check() now rejects chain IDs wider than 256 bits.
- BlockPayloadArgs.Check() now requires PayloadHash length to be exactly 32 bytes instead of merely non-empty.
- Local signing changed from raw encodedMsg []byte input to typed domain / chainID / payloadHash fields and constructs a BlockSigningMessage directly.
- Remote signing was changed to serialize explicit canonical fields rather than deriving signing input from raw payload bytes.

## What Could Have Invalidated It

- No proof that malformed payload hashes or oversized chain IDs were reachable from untrusted input before the patch.
- No evidence that peers accepted invalid signatures or that the old path enabled signature forgery.
- No evidence of an actual replay, cross-chain confusion, or consensus-impacting incident.
- No commit text, test, or patch fragment explicitly states a security bug or exploit was fixed.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that malformed payload hashes or oversized chain IDs were reachable from untrusted input before the patch.
- No evidence that peers accepted invalid signatures or that the old path enabled signature forgery.
- No evidence of an actual replay, cross-chain confusion, or consensus-impacting incident.
