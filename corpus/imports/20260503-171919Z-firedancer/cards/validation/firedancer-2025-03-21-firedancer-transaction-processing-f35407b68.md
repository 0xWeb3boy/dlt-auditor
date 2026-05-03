# Validation Card

## Metadata

- ID: `firedancer-2025-03-21-firedancer-transaction-processing-f35407b68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `memory-lifetime`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says it fixes a memory corruption bug in CPI instruction info allocation.
- Evidence 2: CPI syscall changed from stack-local fd_instr_info_t storage to transaction-scoped cpi_instr_infos storage.

## What Could Have Invalidated It

- Compensating control 1: No concrete exploit path or attacker-controlled trigger is shown.
- Compensating control 2: No proof of consensus divergence, ledger corruption, or state-integrity violation is provided.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No concrete exploit path or attacker-controlled trigger is shown.
- Caution 2: No proof of consensus divergence, ledger corruption, or state-integrity violation is provided.
