# Validation Card

## Metadata

- ID: `firedancer-2025-12-01-firedancer-core-logic-d94e26080`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-input-bounds-hardening`

## What Confirmed The Issue

- Evidence 1: Rejects pcapng blocks larger than FD_PCAPNG_BLOCK_SZ before copying into iter->block_buf.
- Evidence 2: Adds block-buffer cursor checks before reading option headers and option values.

## What Could Have Invalidated It

- Compensating control 1: No concrete exploit path is shown.
- Compensating control 2: No proof of attacker-controlled production reachability is supplied.

## Severity Guidance

- Expected impact band: low
- Expected severity band: low

## False-Positive Cautions

- Caution 1: No concrete exploit path is shown.
- Caution 2: No proof of attacker-controlled production reachability is supplied.
