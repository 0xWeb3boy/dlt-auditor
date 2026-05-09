# Root-Cause Card

## Metadata

- ID: `solana-2021-03-16-solana-staking-999f81c56d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-resource-metering`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting-and-bounds`

## Violated Invariant

- Protocol input must satisfy resource accounting and bounds before it can reach account owner/write privilege, executable program state, or runtime syscall side effect.

## Trust Boundary

- Boundary: untrusted program instruction/CPI frame to runtime account and privilege enforcement

## Attack Surface

- Entrypoint type: native program, loader, SBF/BPF, or CPI invocation
- Sensitive sink: account owner/write privilege, executable program state, or runtime syscall side effect

## Root Cause

CPI account-data byte accounting was missing at the shown BPF loader account translation points. The shared helper also lacked the invoke context parameter needed to perform feature-gated compute metering inside the translation closure.

## Impact Pattern

- Primary impact: resource-exhaustion
- Expected band: availability_or_resource_exhaustion
- Severity guide: Medium

## Short Reusable Lesson

The patch is a resource-metering hardening change in Solana's BPF loader CPI path. It adds the `cpi_data_cost` feature gate and, when active, charges the compute meter for CPI account data bytes in both Rust and C account translation paths. The evidence supports CPI byte-accounting hardening, but not an access-control, staking, privilege-escalation, funds-loss, or proven denial-of-service finding.
