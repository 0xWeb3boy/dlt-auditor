# Validation Card

## Metadata

- ID: `sui-2026-03-23-sui-storage-7c7e923e6b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-owner-resolution`

## What Confirmed The Issue

- Code change occurs under `enable_coin_deny_list_v2()` while processing written coin objects.
- Owner lookup changes from address-owner-only extraction to party-owner-aware extraction when `use_coin_party_owner` is enabled.
- A protocol feature flag is added, exposed, and enabled for version 118, indicating an intentional behavior change for party-owned coin handling.

## What Could Have Invalidated It

- No test or trace shows a deny-listed party-owned coin being incorrectly accepted before the patch.
- No advisory, commit text, or release note explicitly identifies a security vulnerability.
- No downstream enforcement code is shown proving the collected owner value controls transaction rejection or acceptance.
- No evidence supports the original state-corruption or storage-integrity framing.

## Severity Guidance

- Expected impact band: policy-enforcement_or_access-control
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Treat as deny-list policy hardening for party-owned coin owner resolution.
- Do not claim a confirmed deny-list bypass or exploit.
- Do not claim consensus failure, state corruption, RPC exposure, or storage corruption from the provided patch alone.
