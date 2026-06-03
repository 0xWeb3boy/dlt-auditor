# Corpus Import Summary

- Project: `omni-network`
- Import name: `omni-cantina`
- Source report: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/omni-cantina`
- Finding count: `12`

## Imported Findings

- `M-1`: FinalizeBlock is non-deterministic; will lead to consensus failures
- `H-1`: Blob transactions can halt the chain
- `H-2`: Omni chain halt via post-quorum votes poisoning
- `M-2`: An incorrect order of checks in verifyAggVotes may lead to liveness issues
- `M-3`: Malicious proposer can stop blocks finalization through signature malleability
- `H-3`: Malicious proposer can halt the chain through payload that causes JSON RPC error
- `H-4`: Validator public key that is not on secp256k1 curve will halt the chain
- `M-4`: Malicious proposer can include empty transactions in a valid proposal
- `M-5`: Malicious validator can create too many fake attestation roots to halt the chain.
- `H-5`: A malicious validator can permanently DOS one new validator, leading to huge $Omni loss.
- `H-6`: Validator deposit will be lost if delegation happens in the same block as validator creation
- `M-6`: Delays in updating the l1BridgeBalance can lead to user fund losses.

## Bug Family Counts

- `attestation_trust_and_freshness`: `2`
- `input_validation_and_invariant_enforcement`: `2`
- `resource_accounting_and_limits`: `2`
- `signature_binding_and_signer_scope`: `1`
- `staking_registry_and_accountability`: `1`
- `state_machine_and_lifecycle_consistency`: `4`

## Severity Counts

- `high`: `6`
- `medium`: `6`

## What Was Created

- `records/`: enriched normalized YAML records
- `cards/root-cause/`: conceptual retrieval cards
- `cards/code-shape/`: code-search retrieval cards
- `cards/validation/`: confirmation and false-positive caution cards
- `evals/`: expected detector-output records
- `raw-findings/`: concise source summaries
- `manifest.json`: machine-readable import index

## Notes

- This bundle imports all 12 sections from `findings.md` as `tier_a_confirmed` source-report ground-truth examples.
- Raw findings are concise summaries and pointers to the local ground-truth file, not long embedded report copies.
