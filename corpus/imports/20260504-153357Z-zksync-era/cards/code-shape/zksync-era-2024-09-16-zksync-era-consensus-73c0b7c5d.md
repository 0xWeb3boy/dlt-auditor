# Code-Shape Card

## Metadata

- ID: `zksync-era-2024-09-16-zksync-era-consensus-73c0b7c5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `key-management-hardening`

## Code Shape Summary

- The supplied evidence shows a new zk_toolbox workflow for building unsigned L1 deployment transactions and related Forge setup changes that allow an explicit sender address instead of immediately using a private key in the shown path. This is security-relevant operational hardening for cold-storage or multisig signing. The evidence does not prove a prior private-key leak, unauthorized broadcast path, consensus issue, validator issue, or accounting/state-drift vulnerability.

## Search Motifs

- Motif 1: Deployment CLI constructs and broadcasts privileged L1 transactions in one step.
- Motif 2: Transaction builder requires a private key even when an offline signer or multisig should be used.
- Motif 3: Patch adds unsigned transaction output, explicit sender address, or removes automatic broadcast.

## Typical Asymmetry

- Transaction construction needs public parameters, but signing requires custody of privileged keys; coupling them forces hot-key exposure.

## Patch Pattern

- Add an offline build mode, accept sender addresses without private keys, and separate broadcast from transaction construction.

## False Match Warnings

- Local dev scripts, test-only deployments, or non-privileged calldata generation should not be treated as key-management findings without privileged signing context.
