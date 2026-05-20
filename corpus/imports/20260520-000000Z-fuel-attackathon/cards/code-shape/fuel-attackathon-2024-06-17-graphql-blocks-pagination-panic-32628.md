# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-graphql-blocks-pagination-panic-32628`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `graphql-pagination-unreachable-panic`

## Code Shape Summary

- Shared pagination logic assumed validated counts but exposed a cursor-only path to unreachable!().

## Search Motifs

- blocks after without first
- before without last
- schema.rs unreachable
- GraphQL query crashes core

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Move the first/last requirement into shared query_pagination validation and cover blocks, transactions, coins, and balances with invalid-combination tests.

## False Match Warnings

- No issue if the RPC layer catches panics and isolates the worker.
- No issue if the endpoint is authenticated and invalid input is rejected before resolver logic.
