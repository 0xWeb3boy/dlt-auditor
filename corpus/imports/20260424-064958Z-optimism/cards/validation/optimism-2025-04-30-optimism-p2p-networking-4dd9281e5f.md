# Validation Card

## Metadata

- ID: `optimism-2025-04-30-optimism-p2p-networking-4dd9281e5f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `p2p-identity-handling`

## What Confirmed The Issue

- The builder no longer silently generates a fresh secp256k1 keypair when identity material is missing; it now fails with MissingKeyPair.
- The changed code is in p2p identity/discovery handling, which is a security-sensitive subsystem.
- Static-IP mode now disables AutoNAT listen behavior in addition to ENR updates, reducing risky automatic discovery behavior.
- A new regression test verifies that a specific ENR maps to the expected PeerId, reinforcing identity consistency expectations.

## What Could Have Invalidated It

- No shown diff demonstrates unauthorized peer acceptance, impersonation, or message forgery before the fix.
- The provided excerpts do not show the identify-protocol enablement logic named in the commit subject.
- No exploit narrative, incident reference, or security-specific commit message is provided.
- The event-handler refactor is not shown to enforce a concrete security check by itself.

## Severity Guidance

- Expected impact band: configuration-safety
- Expected severity band: low_or_informational

## False-Positive Cautions

- No shown diff demonstrates unauthorized peer acceptance, impersonation, or message forgery before the fix.
- The provided excerpts do not show the identify-protocol enablement logic named in the commit subject.
- No exploit narrative, incident reference, or security-specific commit message is provided.
