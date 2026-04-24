# Validation Card

## Metadata

- ID: `zksync-2019-07-09-zksync-cryptography-3833fee9c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-circuit-constraint`

## What Confirmed The Issue

- The patch adds a signer public key equality check in transfer circuit code.
- The equality compares operation signer data against the left/source account public key.
- The result is added to validity flags that gate transfer execution.

## What Could Have Invalidated It

- Another mandatory constraint already bound the same signer field to the account key.
- The touched code is only test scaffolding or unreachable circuit code.

## Severity Guidance

- Expected impact band: `authorization_integrity`
- Expected severity band: `high_or_medium`
- Rationale: A missing circuit constraint in transfer authorization can be high impact, but this case remains likely because the full pre-fix circuit and exploit path were not proven.

## False-Positive Cautions

- Do not count formatting-only circuit changes.
- If the same equality was already enforced in another mandatory constraint, the patch may be refactor or defense-in-depth.
