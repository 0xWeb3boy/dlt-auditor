# Validation Card

## Metadata

- ID: `solana-2020-08-05-solana-transaction-processing-7b8e5a9f47`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-transaction-sanitization`

## What Confirmed The Issue

- RPC preflight sendTransaction test constructs a malformed transaction with program_id_index = 255 and expects TransactionError::SanitizeFailure.
- Bank::prepare_simulation_batch changed from vec![Ok(()); txs.len()] to calling tx.sanitize() for each transaction.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
