# Validation Card

## Metadata

- ID: `sui-2022-07-20-sui-storage-ede61fb385`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `authenticated-epoch-storage-hardening`

## What Confirmed The Issue

- Commit subject explicitly says "Add authenticated epoch".
- AuthorityState replaces insert_new_epoch_info with sign_new_epoch_and_update_committee.
- New store path signs new epoch data using authority identity and signer material.
- Epoch transition logic threads last_checkpoint into the committee update flow.

## What Could Have Invalidated It

- No direct exploit path is shown.
- No attacker-controlled input path to the old insertion behavior is shown.
- No proof that a stale, forged, or malicious committee could previously be persisted.
- No regression test excerpt demonstrates prior acceptance of unauthenticated epoch state.

## Severity Guidance

- Expected impact band: consensus-integrity_or_state-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Classify as security hardening, not a confirmed security fix.
- Do not claim remote exploitation, privilege escalation, asset theft, or transaction forgery.
- Do not claim proven state corruption from the supplied patch alone.
- The supported claim is authenticated epoch/committee transition persistence hardening.
