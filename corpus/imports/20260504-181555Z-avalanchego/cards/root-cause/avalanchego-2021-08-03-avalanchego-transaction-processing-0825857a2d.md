# Root-Cause Card

## Metadata

- ID: `avalanchego-2021-08-03-avalanchego-transaction-processing-0825857a2d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-rule-activation-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-activation-rule-binding`

## Violated Invariant

- Invariant: Consensus validation rules must activate at the exact fork height/phase specified by the protocol, not one upgrade earlier or later.

## Trust Boundary

- Boundary: Externally supplied transactions and contract-creation results cross into fork-gated EVM state transition validation.

## Attack Surface

- Entrypoint type: contract creation transaction validation during fork activation
- Sensitive sink: acceptance of contract bytecode under active consensus rules

## Impact Pattern

- Primary impact: consensus-integrity, state-integrity
- Secondary impact: medium_high_integrity

## Root Cause

- The EVM create path used the wrong fork-phase predicate for the 0xEF-prefix invalid-code rule, delaying enforcement from ApricotPhase3 to ApricotPhase4. The provided evidence does not establish the dummy skipBlockFee path as a production vulnerability. ## Walkthrough 1. EVM.create executes contract initcode and obtains the returned code in ret. 2.

## Short Reusable Lesson

- A consensus rule for rejecting invalid contract code was tied to the wrong fork predicate. The reusable shape is any fork-gated validation check whose implementation uses an adjacent upgrade flag rather than the protocol activation flag.
