# Root-Cause Card

## Metadata

- ID: `solana-2021-06-06-solana-transaction-processing-8f5e773caf`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authorization`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-and-signer-binding`

## Violated Invariant

- Protocol input must satisfy signature and signer binding before it can reach account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment.

## Trust Boundary

- Boundary: signed client transaction to bank accounting and execution state

## Attack Surface

- Entrypoint type: transaction admission, sanitization, or execution path
- Sensitive sink: account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment

## Root Cause

A zero-value special case was placed before authorization validation in the transfer control flow, allowing the handler to accept a zero-lamport transfer without evaluating whether the source account was a signer.

## Impact Pattern

- Primary impact: unauthorized-instruction-acceptance
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The grounded security-relevant change is in the system-program transfer handler. Previously, `transfer` returned `Ok(())` immediately for `lamports == 0`, before checking whether the source account had signed. The patch feature-gates that legacy fast path so that, once `system_transfer_zero_check` is active, zero-lamport transfers continue to the existing missing-signature check. This supports a missing-authorization hardening finding, but the evidence...
