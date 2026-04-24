# Validation Card

## Metadata

- ID: `reth-2025-05-28-reth-storage-1cfe50998`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`

## What Confirmed The Issue

- Adds ancestor walk to detect missing trie updates before treating a block as persistable.
- Changes canonical persistence path from infallible to fallible, surfacing state-root calculation failures.

## What Could Have Invalidated It

- No proof that an attacker could remotely trigger the bad state through network-delivered blocks
- No demonstration that the prior behavior accepted invalid blocks or caused a real chain split

## Severity Guidance

- Expected impact band: state_or_proof_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No proof that an attacker could remotely trigger the bad state through network-delivered blocks
- No demonstration that the prior behavior accepted invalid blocks or caused a real chain split
