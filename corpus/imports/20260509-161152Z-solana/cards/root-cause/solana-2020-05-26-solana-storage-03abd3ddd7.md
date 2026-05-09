# Root-Cause Card

## Metadata

- ID: `solana-2020-05-26-solana-storage-03abd3ddd7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-privilege-check`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authorization-and-privilege-check`

## Violated Invariant

- Protocol input must satisfy authorization and privilege check before it can reach canonical bank state, account storage, snapshot acceptance, or ledger root.

## Trust Boundary

- Boundary: persisted or downloaded ledger/account state to trusted runtime reconstruction

## Attack Surface

- Entrypoint type: snapshot load, blockstore replay, accounts hash verification, or storage maintenance
- Sensitive sink: canonical bank state, account storage, snapshot acceptance, or ledger root

## Root Cause

The supported root cause is missing or insufficient instruction-level privilege validation in the BPF CPI syscall path before dispatch. The evidence does not support the earlier storage/state-corruption framing.

## Impact Pattern

- Primary impact: privilege-escalation, state-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

Commit 03abd3ddd7 is supported as a security fix for Solana's BPF cross-program invocation path. The strongest evidence is the new verify_instruction helper in programs/bpf_loader/src/syscalls.rs, explicitly introduced with a privilege-escalation check and invoked before Message construction and dispatch.
