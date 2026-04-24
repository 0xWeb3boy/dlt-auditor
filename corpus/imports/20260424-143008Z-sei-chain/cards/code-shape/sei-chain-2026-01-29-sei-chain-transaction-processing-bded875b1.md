# Code-Shape Card

## Metadata

- ID: `sei-chain-2026-01-29-sei-chain-transaction-processing-bded875b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mock-balance-mainnet-guard`

## Code Shape Summary

- The evidence supports security hardening in the mock_balances build-tag implementation. The patch adds direct pacific-1 panic guards around mock balance mutation/top-off paths and removes lazy minting from GetBalance.

## Search Motifs

- Motif 1: GetBalance lazily mints or tops off balances
- Motif 2: mock balance mutation lacks direct mainnet panic
- Motif 3: test helper state mutation reachable from read path

## Typical Asymmetry

- The vulnerable shape separates a protocol decision from the later state-changing or resource-consuming sink, so one path observes or validates a value while another path commits effects using a broader, stale, defaulted, or unverified value.

## Patch Pattern

- Remove lazy mutation from read paths and add direct production-network guards on mock funding helpers.

## False Match Warnings

- The build tag cannot be enabled in production artifacts.
- Every mutation path has a direct chain-ID or network guard.
