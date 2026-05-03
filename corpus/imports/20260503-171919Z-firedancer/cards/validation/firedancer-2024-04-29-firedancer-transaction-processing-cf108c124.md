# Validation Card

## Metadata

- ID: `firedancer-2024-04-29-firedancer-transaction-processing-cf108c124`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says it fixes a required signature check.
- Evidence 2: Patch replaces `instr_acc_idxs[7] >= ctx.txn_ctx->txn_descriptor->signature_cnt` with `!fd_instr_acc_is_signer_idx(ctx.instr, 7)`.

## What Could Have Invalidated It

- Compensating control 1: No full exploit scenario is provided showing unauthorized deployment in practice.
- Compensating control 2: Test contents are not provided, only test file metadata.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No full exploit scenario is provided showing unauthorized deployment in practice.
- Caution 2: Test contents are not provided, only test file metadata.
