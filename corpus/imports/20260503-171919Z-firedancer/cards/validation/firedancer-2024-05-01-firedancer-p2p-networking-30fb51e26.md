# Validation Card

## Metadata

- ID: `firedancer-2024-05-01-firedancer-p2p-networking-30fb51e26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-input-validation`

## What Confirmed The Issue

- Evidence 1: Post-Retry Initial handling now rejects destination connection IDs that do not match the locally chosen FD_QUIC_CONN_ID_SZ.
- Evidence 2: Retry packet handling now rejects zero-length source connection IDs, with an inline comment noting possible attack handling.

## What Could Have Invalidated It

- Compensating control 1: No advisory, CVE, exploit, test case, or commit body explains a concrete security impact.
- Compensating control 2: No evidence shows resource exhaustion, connection hijacking, authentication bypass, or memory corruption.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No advisory, CVE, exploit, test case, or commit body explains a concrete security impact.
- Caution 2: No evidence shows resource exhaustion, connection hijacking, authentication bypass, or memory corruption.
