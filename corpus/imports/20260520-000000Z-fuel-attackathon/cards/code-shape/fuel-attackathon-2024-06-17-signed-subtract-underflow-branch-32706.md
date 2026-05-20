# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-underflow-branch-32706`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-underflow`

## Code Shape Summary

- Branch-specific arithmetic on biased underlying values did not normalize operands before subtraction.

## Search Motifs

- self.value < indent
- other.value > indent
- subtract signed integer
- biased signed representation

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Rework signed subtraction around the formula a_underlying - b_underlying + indent using checked ordering for all sign combinations.

## False Match Warnings

- No issue if all construction paths canonicalize values so the vulnerable branch is unreachable.
- A panic is lower severity if no user funds or queues depend on the call.
