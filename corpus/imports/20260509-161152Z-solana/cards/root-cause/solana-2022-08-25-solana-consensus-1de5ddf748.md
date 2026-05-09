# Root-Cause Card

## Metadata

- ID: `solana-2022-08-25-solana-consensus-1de5ddf748`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-overflow-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `checked-arithmetic-bounds`

## Violated Invariant

- Protocol input must satisfy checked arithmetic bounds before it can reach bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status.

## Trust Boundary

- Boundary: peer-provided ledger/vote evidence to local consensus and fork-choice state

## Attack Surface

- Entrypoint type: block replay, vote processing, fork-choice update, or duplicate-slot recovery
- Sensitive sink: bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status

## Root Cause

The grounded root cause is unchecked slot arithmetic while converting between full and compact vote state representations. Compact vote data stores root-relative and inter-lockout offsets, and the old code added those offsets without explicit overflow checks.

## Impact Pattern

- Primary impact: consensus-integrity
- Expected band: integrity_or_funds
- Severity guide: High

## Short Reusable Lesson

The patch adds checked arithmetic and fallible handling around Solana VoteStateUpdate and CompactVoteStateUpdate conversion. The evidence supports an arithmetic-overflow correctness and hardening change in vote-state compaction, but it does not establish a concrete vulnerability, exploit path, remote trigger, denial of service, or consensus divergence.
