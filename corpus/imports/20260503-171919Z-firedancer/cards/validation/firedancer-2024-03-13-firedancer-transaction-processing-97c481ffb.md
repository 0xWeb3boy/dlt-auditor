# Validation Card

## Metadata

- ID: `firedancer-2024-03-13-firedancer-transaction-processing-97c481ffb`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: Commit body explicitly says it fixes an overly permissive writable check.
- Evidence 2: Commit body describes the failure mode: aliased instruction accounts with the same address could be mishandled.

## What Could Have Invalidated It

- Compensating control 1: No exploit transaction or reproduction is provided.
- Compensating control 2: No concrete asset theft, lamport loss, or consensus impact is shown.

## Severity Guidance

- Expected impact band: high
- Expected severity band: high

## False-Positive Cautions

- Caution 1: No exploit transaction or reproduction is provided.
- Caution 2: No concrete asset theft, lamport loss, or consensus impact is shown.
