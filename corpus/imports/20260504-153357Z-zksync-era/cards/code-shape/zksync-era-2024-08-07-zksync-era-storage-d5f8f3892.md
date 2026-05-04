# Code-Shape Card

## Metadata

- ID: `zksync-era-2024-08-07-zksync-era-storage-d5f8f3892`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `strict-consensus-genesis-parsing`

## Code Shape Summary

- The patch tightens consensus genesis parsing in the stored-genesis and external-node fetch paths by denying unknown protobuf fields before converting to `GenesisRaw` and returning a hashed genesis. This is plausibly security-relevant because genesis is consensus-critical, but the evidence only shows earlier rejection of unsupported fields, not an established vulnerability or attacker-controlled exploit path.

## Search Motifs

- Motif 1: Permissive protobuf or JSON decode of genesis, validator set, fork config, or consensus metadata.
- Motif 2: Unknown fields ignored before a canonical hash or consensus identifier is computed.
- Motif 3: Patch adds `deny_unknown_fields` or equivalent strict decode option on stored and fetched paths.

## Typical Asymmetry

- Producers may include fields that old consumers do not understand; consumers still derive canonical state unless unsupported fields are rejected.

## Patch Pattern

- Decode with strict schema options before constructing consensus types or computing hashes.

## False Match Warnings

- Unknown fields may be intentional forward-compatible extensions if they are included in canonical encoding or separately version-gated. Diagnostic-only decoding is a weaker match.
