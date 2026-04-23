# Root-Cause Card

## Metadata

- ID: `go-ethereum-2018-09-25-go-ethereum-cryptography-d3441ebb5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signer-policy-hardening`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signer-authorization`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The provided evidence supports a Clef/signer security-hardening finding, not a low-level cryptographic replay or signature-validation flaw. The strongest grounded change is that signer transaction validation warnings are rejected by default before the signing prompt/path, while advanced mode preserves warning behavior. The commit also removes or narrows some external API surface, including EcRecover in the shown code, but several other security claims are supported only by commit text rather than visible hunks.
