# Raw Finding Summary

Source: Omni Cantina `H-5`
Title: A malicious validator can permanently DOS one new validator, leading to huge $Omni loss.
Severity: `high`

## Normalized Summary

The report describes an allowed attacker front-running a victim createValidator with the victim pubkey. Cosmos staking creates the attacker operator with that pubkey first, and the victim event later fails duplicate pubkey handling after funds are accepted.

## Reusable Failure Shape

The source staking contract accepts any 33-byte consensus key from an allowed operator, while the native uniqueness check happens after source-side value acceptance.

## Missing Property

`proof-of-possession-before-key-reservation`: A consensus public key must not be reserved for an operator until the registering actor proves control of the corresponding private key or an authoritative source binding.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `H-5`
