# Validation Card

## Metadata

- ID: `bor-2019-03-12-bor-transaction-processing-7504dbd6e`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `resource-accounting-overflow`

## What Confirmed The Issue

- Project context shows explicit overflow checks in core/vm/interpreter.go, including math.SafeMul(...) and returns of errGasUintOverflow.
- core/vm/gas_table.go changes memory gas accounting to uint64, indicating bounded arithmetic in resource accounting.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No end-to-end proof that the old arithmetic caused exploitable gas undercharge, OOG misbehavior, or consensus divergence.
- No reproducer, regression test, or bug report is provided showing attacker-controlled pre-patch failure.
