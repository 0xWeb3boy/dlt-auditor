# Code-Shape Card

## Metadata

- ID: `reth-2024-12-04-reth-transaction-processing-d298fb1b8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`

## Code Shape Summary

- The OP consensus validator relied on a generic EIP-1559 parent check at this header-admission site instead of an explicit Optimism Holocene rule. Based on the supplied diff, that left the fork-specific base-fee validation incomplete or absent in the main consensus path.

## Search Motifs

- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `OpBeaconConsensus::validate_header_against_parent` call sites that derive, cache, or validate security-sensitive state
- search for `parent.timestamp` call sites that derive, cache, or validate security-sensitive state
- search for `header.base_fee_per_gas()` call sites that derive, cache, or validate security-sensitive state
- consensus-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses transaction execution/precompile call -> gas accounting state, but protocol-rule-enforcement is incomplete before the code updates or relies on gas reservoir, receipt, and execution accounting.

## Patch Pattern

- Add an explicit fork-specific consensus validation branch in the primary header-validation path instead of relying only on shared generic validation logic.

## False Match Warnings

- No test, exploit, or incident evidence shows that invalid Holocene headers were accepted before the patch
- The provided snippet does not show the full new validation branch, so exact mismatch checks and full rejection conditions are not all visible
- Nothing in the supplied evidence proves replay, signer-authentication, or cryptographic validation issues
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
