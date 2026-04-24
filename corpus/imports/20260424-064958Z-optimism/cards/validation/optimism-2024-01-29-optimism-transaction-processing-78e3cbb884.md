# Validation Card

## Metadata

- ID: `optimism-2024-01-29-optimism-transaction-processing-78e3cbb884`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- Adds core.ProcessBeaconBlockRoot(...) when ParentBeaconRoot is present, changing actual state-transition behavior in block processing.
- Corrects EIP-4788 byte handling from Hex2Bytes("0x...") to FromHex("0x..."), consistent with tests that now assert non-empty deployment data.
- Adds a canonical EIP-4788 contract code hash, indicating stricter verification of deployed contract code.
- Touches upgrade and execution-path code, not only tests or refactoring, in a consensus-critical subsystem.

## What Could Have Invalidated It

- No advisory, CVE, or commit text explicitly states a security vulnerability.
- No proof of attacker-triggerable exploit, fund loss, or authorization bypass.
- No direct evidence that the old behavior caused a live consensus split or production incident.
- No demonstration that the previous byte-decoding bug was externally exploitable beyond protocol-correctness failure.

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No advisory, CVE, or commit text explicitly states a security vulnerability.
- No proof of attacker-triggerable exploit, fund loss, or authorization bypass.
- No direct evidence that the old behavior caused a live consensus split or production incident.
