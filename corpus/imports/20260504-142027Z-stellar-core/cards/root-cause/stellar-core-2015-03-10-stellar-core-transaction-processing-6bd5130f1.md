# Root-Cause Card

## Metadata

- ID: `stellar-core-2015-03-10-stellar-core-transaction-processing-6bd5130f1`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-amplification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `cheap-signer-candidate-binding`

## Violated Invariant

- Invariant: Attacker-supplied signatures must be cheaply bound to plausible signer keys before expensive cryptographic verification is attempted.

## Trust Boundary

- Boundary: untrusted-transaction-envelope -> cryptographic-signature-verifier

## Attack Surface

- Entrypoint type: transaction-authentication
- Sensitive sink: public-key signature verification loop and transaction commit gate
- Attacker capability: Submit transactions with many decorated signatures.
- Main precondition: Verification loops over supplied signatures and signer keys without a cheap hint prefilter.

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-exhaustion, transaction-authentication-hardening
- Severity guess: high because The commit explicitly fixes an amplification attack in transaction authentication, a remote and attacker-controlled path, while not proving forgery or threshold bypass.

## Short Reusable Lesson

- Authentication paths should bind user-controlled proof material to a narrow candidate set before spending asymmetric cryptographic work.
