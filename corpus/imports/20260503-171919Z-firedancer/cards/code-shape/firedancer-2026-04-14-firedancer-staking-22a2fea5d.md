# Code-Shape Card

## Metadata

- ID: `firedancer-2026-04-14-firedancer-staking-22a2fea5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-owner-check`

## Code Shape Summary

- The refresh path trusted account shape and initialization state before checking the owner program, so non-vote accounts could be interpreted as vote-state data.

## Search Motifs

- Motif 1: owner-aware helper added before vote-state parsing
- Motif 2: vote-account validation now checks owner program
- Motif 3: metadata parser consumes account contents before owner gate

## Typical Asymmetry

- The attacker can supply account metadata with plausible contents, but only accounts from the right owner program should reach the parser.

## Patch Pattern

- Centralize owner-aware validation and reject accounts from the wrong program before parsing their inner state.

## False Match Warnings

- No evidence shows that an attacker can create or route a non-vote-owned account into these paths.
- No regression test or exploit scenario is supplied demonstrating the bad pre-patch behavior.
