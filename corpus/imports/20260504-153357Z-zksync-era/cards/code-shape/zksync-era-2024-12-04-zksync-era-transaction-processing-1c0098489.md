# Code-Shape Card

## Metadata

- ID: `zksync-era-2024-12-04-zksync-era-transaction-processing-1c0098489`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cryptographic-configuration-validation`

## Code Shape Summary

- The patch fixes FFLONK verifier verification-key-hash reads by explicitly selecting the overloaded `verificationKeyHash` ABI entry and adds a genesis-time comparison against `fflonk_snark_wrapper_vk_hash`. This is plausibly security relevant because verification key hashes are cryptographic configuration, but the supplied evidence does not establish attacker control, exploitability, invalid proof acceptance, consensus divergence, or fund loss.

## Search Motifs

- Motif 1: Contract call helper selects a function by name when the ABI has overloaded entries.
- Motif 2: Verifier key hash or cryptographic config is read from L1 and compared to local genesis config.
- Motif 3: Patch adds exact ABI function selection plus mismatch rejection.

## Typical Asymmetry

- The local node trusts an on-chain configuration read, but an ambiguous ABI lookup may read the wrong value.

## Patch Pattern

- Bind calls to the exact overloaded ABI entry and reject cryptographic configuration mismatches during genesis validation.

## False Match Warnings

- Pure monitoring reads, non-overloaded functions, or values unused by proof/genesis validation are weaker matches.
