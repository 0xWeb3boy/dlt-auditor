# Root-Cause Card

## Metadata

- ID: `snarkvm-2025-09-04-snarkvm-transaction-processing-fa65b01b8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-input-validation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `cryptographic-input-shape-validation`

## Violated Invariant

- Invariant: Cryptographic verification opcodes and versioned syntax must reject malformed operand encodings before parsing, execution, or deployment admission.

## Trust Boundary

- Boundary: program operands and deployment syntax -> VM cryptographic verifier

## Attack Surface

- Entrypoint type: transaction-or-deployment-validation
- Sensitive sink: ECDSA verification operation and V11 syntax admission

## Impact Pattern

- Primary impact: cryptographic input validation
- Secondary impact: consensus-version gate hardening

## Short Reusable Lesson

- Opcode validators should enforce concrete operand shapes at admission, especially when syntax activation is consensus-versioned.
