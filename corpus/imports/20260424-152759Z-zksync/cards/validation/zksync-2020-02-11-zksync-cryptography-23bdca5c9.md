# Validation Card

## Metadata

- ID: `zksync-2020-02-11-zksync-cryptography-23bdca5c9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-binding-in-circuit`

## What Confirmed The Issue

- Nonce is added to ChangePubKey witness/public-data flow.
- The circuit constrains the public nonce to the current account nonce.
- Validation kept the case as likely hardening rather than confirmed exploit.

## What Could Have Invalidated It

- An existing mandatory nonce check already covered this exact path.
- The nonce is only added to display or logging data with no execution relevance.

## Severity Guidance

- Expected impact band: `replay_or_state_integrity`
- Expected severity band: `medium_or_low`
- Rationale: Nonce binding is security-relevant, but validation did not prove an accepted replay or unauthorized transition, so severity stays conservative.

## False-Positive Cautions

- If account nonce was already checked in a parent circuit or mempool gate, this may be consistency hardening only.
- Do not infer direct fund loss without a demonstrated accepted replay.
