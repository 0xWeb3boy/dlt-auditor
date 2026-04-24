# Validation Card

## Metadata

- ID: `optimism-2026-04-22-optimism-transaction-processing-052c1d65dc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-validation`

## What Confirmed The Issue

- Adds an error path that rejects post-exec 0x7D transactions when SDM is Disabled or Invalid.
- Inline comment says the prior behavior could silently accept refund payloads that followers never validate.
- Adds an error path when produced refund exceeds raw gas used instead of masking it with saturating subtraction.
- Commit message frames both changes as preventing malformed payload acceptance and producer/verifier mismatch in block validation.

## What Could Have Invalidated It

- No proof that an external attacker, rather than a faulty or misconfigured producer, can trigger the bad states.
- No end-to-end exploit or accepted malicious block is shown in the supplied patch evidence.
- No evidence of fund theft, privilege escalation, or remote code execution.
- The constant renaming in the inspector does not independently demonstrate a vulnerability fix.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an external attacker, rather than a faulty or misconfigured producer, can trigger the bad states.
- No end-to-end exploit or accepted malicious block is shown in the supplied patch evidence.
- No evidence of fund theft, privilege escalation, or remote code execution.
