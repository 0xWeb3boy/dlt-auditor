# Code-Shape Card

## Metadata

- ID: `solana-2020-02-26-solana-consensus-87cfac12dd`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `bootstrap-trust-validation`

## Code Shape Summary

The patch appears security relevant because the commit subject says it validates a genesis config downloaded over RPC before accepting it, and the code changes move genesis fetching from a generic ledger download path to a genesis-specific path that receives `ValidatorConfig`. However, the provided hunks do not show the actual validation logic, the fields being checked, or a concrete attacker-controlled RPC source, so the vulnerability thesis is not ful...

## Search Motifs

- search for bootstrap trust validation checks near consensus entrypoints
- compare validation before and after the freshness-and-origin-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for cached peer or state facts reused without slot/epoch/root freshness checks

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Separate consensus-critical bootstrap artifact handling from generic download logic and make local validator configuration available before accepting downloaded genesis data.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
