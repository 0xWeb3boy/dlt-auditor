# Root-Cause Card

## Metadata

- ID: `solana-2022-06-08-solana-cryptography-165ee12ed4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-authority-validation`
- Confidence tier: `tier_b_likely`

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

The supported root cause is that nonce verification collapsed successful validation to a boolean, so nonce account state such as authority data was not carried across this verification boundary. The provided snippets do not directly prove that callers accepted unauthorized durable nonce transactions, but the commit message identifies missing nonce-authority signing as the rejected case.

## Impact Pattern

- Primary impact: unauthorized-transaction-acceptance, replay-risk
- Expected band: integrity_or_funds
- Severity guide: Low/Medium

## Short Reusable Lesson

The commit message states that durable nonce transactions not signed by the nonce authority are rejected. The shown code evidence supports part of that fix: nonce account verification now returns Option<Data> instead of a boolean, preserving initialized nonce account state for downstream validation. The exact authority-signature rejection branch is not present in the provided snippets, so this should be treated as a likely security fix rather than a ful...
