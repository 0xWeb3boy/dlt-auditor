# Validation Card

## Metadata

- ID: `scroll-2024-08-06-scroll-cryptography-72f88bae`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-preimage-mismatch`

## What Confirmed The Issue

- Evidence 1: In `coordinator/internal/types/auth.go`, the patch replaces `// Message the login message struct` with a temporary compatibility note for the Darwin upgrade.
- Evidence 2: In `coordinator/internal/types/auth.go`, the patch replaces `hash, err := a.Message.Hash()` with `curieIdentity := identity{`.
- Evidence 3: In `common/version/version.go`, the patch replaces `var tag = "v4.4.41"` with `var tag = "v4.4.42"`.

## What Could Have Invalidated It

- Compensating control 1: If the legacy and current payloads serialize identically or the compatibility path is disabled, the practical risk drops sharply.
- Compensating control 2: Message-shape cleanup alone is not enough; the important question is whether signer recovery and the prover signer bind to the same bytes.
- Compensating control 3: The evidence supports a compatibility hardening fix, not a demonstrated forged-login exploit.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the legacy and current payloads serialize identically or the compatibility path is disabled, the practical risk drops sharply.
- Caution 2: Message-shape cleanup alone is not enough; the important question is whether signer recovery and the prover signer bind to the same bytes.
- Caution 3: The evidence supports a compatibility hardening fix, not a demonstrated forged-login exploit.
