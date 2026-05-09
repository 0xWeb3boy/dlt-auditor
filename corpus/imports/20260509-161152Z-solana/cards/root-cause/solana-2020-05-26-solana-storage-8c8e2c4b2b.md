# Root-Cause Card

## Metadata

- ID: `solana-2020-05-26-solana-storage-8c8e2c4b2b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-program-invocation-privilege-escalation`
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

The BPF CPI syscall path lacked, or did not have sufficient context for, an early check that requested callee account privileges were limited to the caller's account privileges and valid signer derivations.

## Impact Pattern

- Primary impact: privilege-escalation, authorization-bypass, state-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch is a security fix for privilege escalation in Solana's BPF cross-program invocation path. The grounded evidence shows a new `verify_instruction` check in `programs/bpf_loader/src/syscalls.rs`, a call to that verification before callee message construction, and VM setup changed to pass caller parameter accounts so the syscall layer has the account privilege context needed for the check.
