# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-graphql-transactions-pagination-panic-32486`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `graphql-pagination-unreachable-panic`

## Code Shape Summary

- The resolver used an unreachable branch for a user-controlled parameter combination that validation did not forbid.

## Search Motifs

- transactions after before without first last
- unreachable! pagination
- GraphQL public RPC crash
- Either first or last should be provided

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Reject queries with neither first nor last before resolver execution and add shared pagination tests for public GraphQL endpoints.

## False Match Warnings

- No issue if invalid combinations return typed GraphQL errors.
- No issue if panic is contained and cannot terminate the service process.
