# Validation Card

## Metadata

- ID: `scroll-2025-07-02-scroll-rpc-client-api-adac0404`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verifier-artifact-validation`

## What Confirmed The Issue

- Evidence 1: In `coordinator/cmd/tool/verify.go`, the patch replaces `if len(proof.Vk) != 0 {` with `proof.Vk = vk`.
- Evidence 2: In `crates/prover-bin/src/prover.rs`, the patch replaces `Ok(())` with `// Copy verifier.bin from workspace bundle directory to output path`.
- Evidence 3: In `coordinator/cmd/tool/verify.go`, the patch replaces `if bytes.Equal(proof.Vk, vk) {` with `if !bytes.Equal(proof.Vk, vk) {`.

## What Could Have Invalidated It

- Compensating control 1: If the tooling is purely local and not used as a policy gate, a similar mismatch may remain a correctness issue rather than security hardening.
- Compensating control 2: Changing file-copy behavior alone is not enough; the security-relevant part is binding the correct verification key and verifier binary to the proof path.
- Compensating control 3: The evidence supports tool hardening, not a demonstrated production verifier bypass.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the tooling is purely local and not used as a policy gate, a similar mismatch may remain a correctness issue rather than security hardening.
- Caution 2: Changing file-copy behavior alone is not enough; the security-relevant part is binding the correct verification key and verifier binary to the proof path.
- Caution 3: The evidence supports tool hardening, not a demonstrated production verifier bypass.
