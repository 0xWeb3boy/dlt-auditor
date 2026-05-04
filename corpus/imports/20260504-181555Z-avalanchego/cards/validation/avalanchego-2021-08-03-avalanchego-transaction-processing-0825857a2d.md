# Validation Card

## Metadata

- ID: `avalanchego-2021-08-03-avalanchego-transaction-processing-0825857a2d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-rule-activation-mismatch`

## What Confirmed The Issue

- Evidence: core/vm/evm.go changes contract creation validation in a production EVM state-transition path.
- Evidence: The changed branch rejects returned contract code beginning with 0xEF earlier, at IsApricotPhase3 instead of IsApricotPhase4.
- Evidence: Contract creation validity can affect transaction and block acceptance under fork rules.

## What Could Have Invalidated It

- Compensating control: No params/config.go diff is supplied to prove ApricotPhase3 is definitely the intended EIP-3541 activation point.
- Compensating control: No evidence shows deployed network divergence, exploitability, or attacker impact.
- Compensating control: DummyEngine skipBlockFee changes are described as faker/test support and are not shown to affect production consensus.

## Severity Guidance

- Expected impact band: medium_high_integrity
- Expected severity band: medium_or_low
- Severity rationale: Wrong fork activation in state transition validation can cause invalid state acceptance, though this record does not prove an exploit beyond the corrected predicate.

## False-Positive Cautions

- Caution: Classify as fork-rule validation hardening rather than confirmed state corruption.
- Caution: Do not treat the DummyEngine skipBlockFee hunks as the root security issue.
- Caution: Do not claim theft, remote exploitation, or observed consensus failure from the supplied patch alone.
