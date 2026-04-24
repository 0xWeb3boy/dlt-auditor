# Validation Card

## Metadata

- ID: `reth-2022-12-15-reth-transaction-processing-9208f2fd9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-selection-logic`

## What Confirmed The Issue

- execute() assigns config.spec_upgrades.revm_spec(header.number) to evm.env.cfg.spec_id, so the patched logic directly affects live block execution semantics.
- revm_spec() changed from reversed comparisons like self.shanghai >= b to b >= self.shanghai, which fixes fork activation selection in production code.

## What Could Have Invalidated It

- No evidence shows the buggy spec selection was exploitable by an attacker in deployed configurations
- No observed consensus split, chain acceptance failure, or state divergence is documented in the provided material

## Severity Guidance

- Expected impact band: consensus_or_protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No evidence shows the buggy spec selection was exploitable by an attacker in deployed configurations
- No observed consensus split, chain acceptance failure, or state divergence is documented in the provided material
