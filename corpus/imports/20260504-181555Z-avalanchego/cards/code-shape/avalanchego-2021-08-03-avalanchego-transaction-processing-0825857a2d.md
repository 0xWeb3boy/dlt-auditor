# Code-Shape Card

## Metadata

- ID: `avalanchego-2021-08-03-avalanchego-transaction-processing-0825857a2d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-rule-activation-mismatch`

## Code Shape Summary

- A consensus rule for rejecting invalid contract code was tied to the wrong fork predicate. The reusable shape is any fork-gated validation check whose implementation uses an adjacent upgrade flag rather than the protocol activation flag.

## Search Motifs

- IsForkNPlusOne used around code that implements a ForkN rule
- contract creation validity checks guarded by upgrade predicates
- tests for transactions valid before a fork and invalid immediately after it

## Typical Asymmetry

- The sensitive sink is protected in some paths or under some fork/configuration states, while a neighboring path, boundary case, or compatibility exception omits the same property.
- The vulnerable-looking code often appears as a small predicate, arithmetic expression, allowlist exception, or proof/header check near a much larger protocol feature.

## Patch Pattern

- Move the validation guard to the exact activation predicate and add fork-boundary tests for before, at, and after activation.
- Add focused regression tests for the boundary case, not only broad happy-path coverage.

## False Match Warnings

- Feature flags in dummy/test engines may be support plumbing only
- A wrong-looking predicate is non-security if the fork phases are aliases
- Do not claim consensus split without showing divergent validation across nodes
