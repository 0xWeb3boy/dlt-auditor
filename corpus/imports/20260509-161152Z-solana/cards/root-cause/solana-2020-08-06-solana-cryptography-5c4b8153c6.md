# Root-Cause Card

## Metadata

- ID: `solana-2020-08-06-solana-cryptography-5c4b8153c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-off-curve-address-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-shape-validation`

## Violated Invariant

- Protocol input must satisfy input shape validation before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

The web3.js PDA derivation helper did not visibly enforce the off-curve requirement before constructing and returning a `PublicKey` from derived seed material.

## Impact Pattern

- Primary impact: security-invariant-bypass
- Expected band: defense_in_depth_or_input_hardening
- Severity guide: Low/Medium

## Short Reusable Lesson

The patch hardens Solana web3.js program-address derivation by adding an explicit ed25519 curve-membership rejection in `PublicKey.createProgramAddress`. The evidence supports a missing off-curve validation gate in the client helper, but does not establish a concrete exploit, known private key, replay issue, or runtime consensus vulnerability.
