# Validation Card

## Metadata

- ID: `sui-2022-11-14-sui-cryptography-4935cdb5f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-epoch-binding`

## What Confirmed The Issue

- AuthoritySignature::new now requires EpochId and appends it to signed message bytes before signing.
- AuthoritySignature::verify now requires EpochId, indicating verification is against epoch-bound bytes.
- EpochId is made Signable via BCS serialization, giving it a defined signed representation.
- Consensus checkpoint fragment verification now calls verify with self.committee.load().epoch.

## What Could Have Invalidated It

- No advisory, CVE, exploit description, or explicit vulnerability statement is provided.
- No proof that signatures could actually be replayed across epochs in deployed configurations.
- No evidence about authority key reuse or committee/key rotation behavior across epochs.
- No demonstrated consensus safety break, chain halt, financial loss, or unauthorized action.

## Severity Guidance

- Expected impact band: cross-epoch-replay-risk
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Supports missing epoch/domain binding in authority signature material.
- Supports security hardening against cross-epoch replay risk.
- Does not support claims of signature forgery.
- Does not prove a concrete exploit or production incident.
