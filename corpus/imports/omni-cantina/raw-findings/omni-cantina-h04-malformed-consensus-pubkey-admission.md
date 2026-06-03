# Raw Finding Summary

Source: Omni Cantina `H-4`
Title: Validator public key that is not on secp256k1 curve will halt the chain
Severity: `high`

## Normalized Summary

The report shows createValidator accepting any 33-byte key and deliverCreateValidator creating a Cosmos validator without curve validation. valsync later calls DecompressPubkey and fails in FinalizeBlock for off-curve keys.

## Reusable Failure Shape

The source contract and native adapter enforce key length but not curve membership; a later valsync path finally decompresses and fails.

## Missing Property

`semantic-public-key-validation`: A value-accepting validator registration boundary must reject public keys that downstream consensus consumers cannot parse on the required curve.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `H-4`
