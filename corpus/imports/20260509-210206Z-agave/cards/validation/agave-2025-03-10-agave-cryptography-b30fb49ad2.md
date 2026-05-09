# Validation Card

## Metadata

- ID: `agave-2025-03-10-agave-cryptography-b30fb49ad2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-invalid-transaction`

## What Confirmed The Issue

- The fix adds continue immediately after container.remove_by_id in invalid transaction branches.
- The surrounding path later uses expect("transaction must exist") on the same id.

## What Could Have Invalidated It

- The expect cannot run after removal because of another control-flow guard.
- The removed transaction id is never derived from untrusted packet input.

## Severity Guidance

- Expected impact band: `validator availability`
- Expected severity band: `medium`
- Rationale: A panic in transaction ingress can affect validator availability, but the evidence did not prove process-wide termination or network-wide denial of service.

## False-Positive Cautions

- A panic fix is not automatically exploitable unless untrusted input can reach it.
- Do not classify as cryptographic failure merely because it occurs near transaction verification.
