# Validation Card

## Metadata

- ID: `moonbeam-2021-12-15-moonbeam-transaction-processing-aa99e9353b`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `replay-or-signature-validation`

## What Confirmed The Issue

- Runtime configs add moonbeam/moonriver/moonbase SignatureNetworkIdentifier constants.
- Reward address association/change origins are explicitly signed in Moonbeam config.

## What Could Have Invalidated It

- Signature construction already included an equivalent non-replayable domain separator
- The affected operations were not callable before this feature enablement

## Severity Guidance

- Expected impact band: authorization_or_replay_hardening
- Expected severity band: medium

## False-Positive Cautions

- Verifier may already include genesis hash, chain id, or pallet-specific domain elsewhere
- Root-only operations before feature activation may not be externally exploitable
