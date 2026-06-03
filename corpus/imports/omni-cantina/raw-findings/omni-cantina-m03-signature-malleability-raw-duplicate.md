# Raw Finding Summary

Source: Omni Cantina `M-3`
Title: Malicious proposer can stop blocks finalization through signature malleability
Severity: `medium`

## Normalized Summary

The report shows a proposer replaying a valid prior vote with a malleated signature. Proposal verification accepts the recovered signer, but finalization hits a unique key and isDoubleSign errors because raw signature bytes differ.

## Reusable Failure Shape

Signature verification uses semantic address recovery, while duplicate persistence treats raw byte differences for the same signer/root as a fatal bug.

## Missing Property

`canonical-signature-representation`: Duplicate handling for an accepted signer/message must be idempotent across valid byte encodings of the same signature.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `M-3`
