# Root-Cause Card

## Metadata

- ID: `solana-2021-06-07-solana-transaction-processing-b777bbf7db`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authorization-check`
- Confidence tier: `tier_a_confirmed`

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

A value-based fast path in `runtime/src/system_instruction_processor.rs::transfer` treated zero-lamport transfers as immediate success before evaluating the source-account signature requirement. That allowed unsigned zero-value transfer operations to avoid the normal authorization failure.

## Impact Pattern

- Primary impact: authorization-bypass
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: High

## Short Reusable Lesson

The supported finding is limited to authorization hardening in Solana's runtime system-program transfer path. Before the patch, `transfer` returned `Ok(())` immediately for `lamports == 0`, before checking whether the source account signed. After the patch, that early return is feature-gated, so once `system_transfer_zero_check` is active, zero-lamport transfers enter the normal signer-validation path and unsigned transfers fail with `InstructionError::...
