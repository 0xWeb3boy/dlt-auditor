# Validation Card

## Metadata

- ID: `bor-2019-01-24-bor-transaction-processing-c7664b063`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-rule-hardening`

## What Confirmed The Issue

- core/vm/gas_table.go switches SSTORE metering away from Constantinople behavior when IsPetersburg is active, explicitly noting removal of EIP-1283.
- params/config.go adds compatibility enforcement for PetersburgBlock, reducing risk of nodes running divergent fork rules.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No provided test excerpt demonstrates an attacker-triggerable exploit or failing security regression.
- No snippet shows concrete impact such as theft, privilege bypass, or remote compromise in this client.
