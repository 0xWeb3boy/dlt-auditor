# Validation Card

## Metadata

- ID: `rippled-2018-10-23-rippled-cryptography-c1a02440d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-list-redirect-scheme-hardening`

## What Confirmed The Issue

- Evidence 1: ValidatorSite::processRedirect now rejects redirect targets whose scheme is not http or https.
- Evidence 2: The commit adds explicit configured file:// validator-list support, making redirect/source boundaries security-relevant.

## What Could Have Invalidated It

- Compensating control 1: No proof that an attacker could control a validator-list redirect in a meaningful threat model.
- Compensating control 2: No proof of local file disclosure, validator-list validation bypass, replay, signature bypass, or consensus compromise.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: validator-list-source-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No proof that an attacker could control a validator-list redirect in a meaningful threat model.
- Caution 2: No proof of local file disclosure, validator-list validation bypass, replay, signature bypass, or consensus compromise.
