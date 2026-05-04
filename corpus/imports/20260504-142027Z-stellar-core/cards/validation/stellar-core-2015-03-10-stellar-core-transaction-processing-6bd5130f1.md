# Validation Card

## Metadata

- ID: `stellar-core-2015-03-10-stellar-core-transaction-processing-6bd5130f1`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-amplification`
- Security verdict: `confirmed`
- Validated as: `security-fix`

## What Confirmed The Issue

- Commit subject names an amplification attack.
- TransactionFrame::checkSignature compares signature hints before PublicKey::verifySig.
- Validation and apply paths call checkAllSignaturesUsed.

## What Could Have Invalidated It

- A hard signature-count limit low enough to remove the amplification could lower severity.
- If verification was already constant-time per envelope elsewhere, this would be redundant hardening.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high_or_medium
- Rationale: The commit explicitly fixes an amplification attack in transaction authentication, a remote and attacker-controlled path, while not proving forgery or threshold bypass.

## False-Positive Cautions

- Do not flag cryptographic verification loops that already prefilter by key id or signature hint.
- Do not infer replay or forgery from verification-cost fixes.
