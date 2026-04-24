# Validation Card

## Metadata

- ID: `sui-2026-03-27-sui-storage-b889b4d1bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-amplification-control`

## What Confirmed The Issue

- Protocol version 120 now sets `cfg.feature_flags.defer_unpaid_amplification = true` when `chain != Chain::Mainnet`.
- The added code comment calls this `unpaid amplification deferral protection`.
- Protocol history documents re-enabling `defer_unpaid_amplification` for devnet and testnet.
- Benchmark code restores amplified multi-validator submissions at a 5% rate to trigger deferral logic.

## What Could Have Invalidated It

- No implementation of the deferral enforcement path is included in the supplied patch evidence.
- No failing-before/passing-after security test or exploit scenario is shown.
- Mainnet is explicitly excluded from the feature enablement.
- Most non-config changes are benchmark/load-generation support rather than validator enforcement code.

## Severity Guidance

- Expected impact band: resource-exhaustion
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Do not classify this as a serialization, storage, or state-representation bug.
- Do not claim a confirmed denial-of-service vulnerability from the supplied evidence alone.
- Do not claim Mainnet behavior was hardened by this patch.
- The supported claim is limited to resource-control hardening for devnet/testnet protocol configuration plus benchmark coverage.
