# Raw Finding Summary

Source: Omni Cantina `M-5`
Title: Malicious validator can create too many fake attestation roots to halt the chain.
Severity: `medium`

## Normalized Summary

The report describes a malicious validator creating many fake roots that pass vote validation and are inserted as pending attestations. Consensus-chain pending rows are retained for cTrimLag, and Approve iterates pending rows every EndBlock.

## Reusable Failure Shape

Valid-looking fake attestation roots from a validator are admitted and retained long enough that EndBlock approval and cleanup paths must iterate growing pending state.

## Missing Property

`attestation-root-admission-and-retention-bound`: A single validator must not be able to create long-retained fake attestation roots that consensus lifecycle scans process without gas or tight cleanup bounds.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `M-5`
