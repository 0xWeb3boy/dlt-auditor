# Validation Card

## Metadata

- ID: `sui-2025-10-02-sui-cryptography-553e16bfa4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Added validate_list_size rejects comma-separated bridge API lists larger than MAX_LIST_SIZE.
- Code comment explicitly states the guard is intended to prevent DoS attacks during u8 conversion in encoding.
- SuiToEthBridgeAction conversion changed from infallible From to fallible TryFrom returning BridgeResult.
- Invalid oversized input now returns InvalidBridgeClientRequest instead of proceeding into encoding/conversion.

## What Could Have Invalidated It

- No exact endpoint or externally reachable request path is shown.
- No concrete pre-patch crash, panic, resource exhaustion trace, or exploit demonstration is provided.
- No evidence of signature forgery, authorization bypass, replay, fund loss, or committee compromise.
- Crypto and digest changes appear to adapt to fallible encoding rather than fix a cryptographic weakness.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as bridge API input-validation and DoS hardening only.
- Do not claim a confirmed exploitable vulnerability from the supplied evidence.
- Do not classify the primary issue as cryptography despite touched crypto-related files.
- Do not claim financial loss or bridge message integrity compromise.
