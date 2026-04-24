# Code-Shape Card

## Metadata

- ID: `geth-arb-2015-03-25-go-ethereum-cryptography-de7af720d6`
- Bug family: `resource_accounting_and_limits`
- Bug class: `udp-reflection-amplification`

## Code Shape Summary

- The discovery handler could answer a small unauthenticated request with larger neighbor traffic before sender reachability was established.

## Search Motifs

- UDP request triggers larger response before source validation
- find-node or peer lookup runs before endpoint bonding
- reflection-prone response path lacks nonce/token/reachability gate
- attacker-controlled count or loop bound reaches allocation or scheduling
- metadata validation happens after network or storage work is queued
- duplicate, stale, or known items consume work instead of being skipped

## Typical Asymmetry

- The vulnerable asymmetry is cost mismatch: cheap attacker-controlled input could trigger more expensive work at amplified network response and peer-table mutation before bounds or progress checks ran.

## Patch Pattern

- Require bonding or reachability proof before table lookup, table mutation, or neighbor response generation.

## False Match Warnings

- a hard request cap is enforced before allocation or network work
- peer scoring or authentication makes repeated abuse impractical
- the path is operator-only and unreachable from untrusted clients
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
