# Raw Finding Summary

Source: Omni Cantina `M-2`
Title: An incorrect order of checks in verifyAggVotes may lead to liveness issues
Severity: `medium`

## Normalized Summary

The report shows verifyAggVotes validating signatures before checking valset membership. A malicious proposer can include a near-block-limit aggregate of random-key signatures and make validators recover them before rejection.

## Reusable Failure Shape

verifyAggVotes performs aggregate signature recovery before checking whether claimed validators are in the valset or within vote bounds.

## Missing Property

`cheap-rejection-before-expensive-crypto`: Proposal validation should enforce cheap size, count, membership, supported-chain, and window bounds before attacker-selected cryptographic recovery.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `M-2`
