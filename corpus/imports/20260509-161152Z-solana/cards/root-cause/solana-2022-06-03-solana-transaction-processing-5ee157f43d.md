# Root-Cause Card

## Metadata

- ID: `solana-2022-06-03-solana-transaction-processing-5ee157f43d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-domain-collision`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `nonce-state-consistency`

## Violated Invariant

- Protocol input must satisfy nonce state consistency before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

AdvanceNonceAccount used or exposed nonce values in the same value domain as normal recent blockhashes, violating replay-domain separation between normal transactions and durable nonce transactions.

## Impact Pattern

- Primary impact: transaction-replay, double-execution
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Medium

## Short Reusable Lesson

The commit fixes a replay-domain collision between Solana durable nonce values and normal blockhashes. The commit message explicitly states that AdvanceNonceAccount could update a nonce to a raw blockhash, allowing a durable transaction to be executed both as a normal transaction and as a nonce transaction when that blockhash was used as recent_blockhash. The patch separates the domains and updates observed runtime and CLI nonce consumers to use the non...
