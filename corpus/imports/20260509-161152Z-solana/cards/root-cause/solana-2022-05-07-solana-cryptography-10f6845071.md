# Root-Cause Card

## Metadata

- ID: `solana-2022-05-07-solana-cryptography-10f6845071`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-transaction-sanitization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach RPC method execution, account scan, or transaction forwarding.

## Trust Boundary

- Boundary: untrusted RPC caller to node query/transaction service

## Attack Surface

- Entrypoint type: JSON-RPC request or RPC transaction submission
- Sensitive sink: RPC method execution, account scan, or transaction forwarding

## Root Cause

The supported root cause is an incomplete sanitization policy boundary: the versioned transaction/message sanitization path shown did not carry a caller requirement that instruction program ids remain static message keys when that property was required.

## Impact Pattern

- Primary impact: security-policy-bypass
- Expected band: state_integrity_or_policy_bypass
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch changes versioned transaction sanitization to carry an explicit require_static_program_ids policy and makes the shown RPC transaction sanitization path pass true for that policy. This supports a likely security fix for rejecting v0 transactions where program dispatch identity depends on lookup-table-loaded addresses, but the provided snippets do not show the full v0 sanitizer or prove an exploit.
