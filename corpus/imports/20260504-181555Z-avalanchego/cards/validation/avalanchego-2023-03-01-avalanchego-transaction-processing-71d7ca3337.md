# Validation Card

## Metadata

- ID: `avalanchego-2023-03-01-avalanchego-transaction-processing-71d7ca3337`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-resource-metering`

## What Confirmed The Issue

- Evidence: Adds MaxInitCodeSize rejection for Cortina contract-creation transactions in tx pool validation.
- Evidence: Adds the same MaxInitCodeSize enforcement during state transition, a consensus-relevant execution path.
- Evidence: Adds EIP-3860 intrinsic gas charging for contract creation initcode words.

## What Could Have Invalidated It

- Compensating control: No advisory, CVE, exploit, crash, consensus split, or incident evidence is supplied.
- Compensating control: No proof that pre-patch oversized initcode caused practical node denial of service.
- Compensating control: No evidence that the unrelated bn256 test case fixes a cryptographic vulnerability.

## Severity Guidance

- Expected impact band: medium_availability
- Expected severity band: medium_or_low
- Severity rationale: Missing size and gas metering can create resource pressure; the record is hardening because no concrete DoS reproduction is included.

## False-Positive Cautions

- Caution: Classify as protocol resource hardening, not a confirmed vulnerability fix.
- Caution: Do not claim a proven remote DoS or consensus failure from the patch alone.
- Caution: Do not treat the bn256ScalarMul test addition as security evidence for this finding.
