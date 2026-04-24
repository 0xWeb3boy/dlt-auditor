# Validation Card

## Metadata

- ID: `bor-2021-09-13-bor-transaction-processing-b8d7c662c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `trace-output-exposure-hardening`

## What Confirmed The Issue

- core/vm/logger.go replaces DisableMemory and DisableReturnData with EnableMemory and EnableReturnData, changing the default semantics to opt-in capture.
- core/vm/logger_json.go now emits Memory and ReturnData only when the corresponding enable flags are set.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: confidentiality
- Expected severity band: low

## False-Positive Cautions

- No provided hunk shows the RPC-facing call path or another cross-trust-boundary surface consuming these traces.
- No supplied test diff or bug report demonstrates an actual information leak, exploit, or user-impacting incident.
