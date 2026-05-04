# Root-Cause Card

## Metadata

- ID: `zksync-era-2024-08-07-zksync-era-storage-d5f8f3892`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `strict-consensus-genesis-parsing`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `strict-consensus-schema-validation`

## Violated Invariant

- Invariant: Consensus-critical configuration must be decoded with the exact schema supported by the node before it is hashed or used.

## Trust Boundary

- Boundary: Stored or fetched genesis bytes cross into the local consensus genesis representation.

## Attack Surface

- Entrypoint type: Consensus genesis loading and external-node genesis fetch.
- Sensitive sink: GenesisRaw construction and genesis hash derivation.

## Impact Pattern

- Primary impact: Unsupported consensus genesis state is rejected before canonical hashing.
- Secondary impact: Reduced risk of schema drift during protocol-version migrations.

## Short Reusable Lesson

- Decode consensus-critical genesis and validator configuration strictly. Unknown fields are not harmless when the decoded value is later hashed, compared, or used as canonical protocol state.
