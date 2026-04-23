# Validation Card

## Metadata

- ID: `go-ethereum-2020-12-04-go-ethereum-transaction-processing-15339cf1c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signed-vulnerability-advisory-check`

## What Confirmed The Issue

- Evidence 1: The commit explicitly introduces a vulnerability checker and signed advisory-feed verification material.
- Evidence 2: The file set includes trusted key material, detached signatures, advisory JSON, and tests centered on version-check behavior.

## What Could Have Invalidated It

- Compensating control 1: Pre-fix code already authenticated advisory data before using it, making the new mechanism a convenience feature rather than hardening.
- Compensating control 2: The advisory content could never influence any operator decision or warning path.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Keep the claim focused on advisory authenticity, not on fixing the underlying CorruptedDAG runtime bug.
- Caution 2: Because the diff snippets do not show the implementation body, avoid stronger claims about exact runtime enforcement details.
