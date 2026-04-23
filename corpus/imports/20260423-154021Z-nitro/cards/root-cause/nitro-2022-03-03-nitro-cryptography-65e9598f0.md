# Root-Cause Card

## Metadata

- ID: `nitro-2022-03-03-nitro-cryptography-65e9598f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `structured-protocol-input-validation`

## Violated Invariant

- Invariant: Protocol messages and certificates should be decoded with the canonical structure before embedded bytes are reused as lookup keys, hashes, or commitments.

## Trust Boundary

- Boundary: `protocol message bytes->DAS lookup and validation path`

## Attack Surface

- Entrypoint type: `rpc-or-protocol-message-validation`
- Sensitive sink: `using parsed message content as a data lookup key or commitment`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Protocol messages and certificates should be decoded with the canonical structure before embedded bytes are reused as lookup keys, hashes, or commitments. The patch changes DAS-backed message handling from using raw bytes after the DAS header as a lookup key to first deserializing a `DataAvailabilityCertificate` and then using `cert.DataHash`. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
