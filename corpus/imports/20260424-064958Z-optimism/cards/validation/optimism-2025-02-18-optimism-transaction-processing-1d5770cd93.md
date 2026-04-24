# Validation Card

## Metadata

- ID: `optimism-2025-02-18-optimism-transaction-processing-1d5770cd93`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-block-hash-verification`

## What Confirmed The Issue

- CheckBlockHash() reconstructs the header used for integrity verification, and the patch adds previously missing fields to that hash input.
- The commit message explicitly calls out fix withdrawals-root verification and missing check-block-hash attributes.
- RequestsHash handling is added both in header reconstruction and via ImpliesRequestsRoot(), tightening version-specific verification semantics.
- RPCBlock.Verify() is a validation path for block data, and the patch adjusts L2/genesis handling inside that verification flow.

## What Could Have Invalidated It

- No proof is shown that attackers could previously supply malformed blocks that passed all relevant production checks.
- No test or narrative demonstrates acceptance of invalid blocks, only that verification logic was incomplete.
- No concrete impact such as consensus split, fund loss, or trust-boundary bypass is established from the patch alone.
- The evidence does not show how broadly reachable CheckBlockHash() is on untrusted inputs in deployed configurations.

## Severity Guidance

- Expected impact band: state-or-proof-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- No proof is shown that attackers could previously supply malformed blocks that passed all relevant production checks.
- No test or narrative demonstrates acceptance of invalid blocks, only that verification logic was incomplete.
- No concrete impact such as consensus split, fund loss, or trust-boundary bypass is established from the patch alone.
