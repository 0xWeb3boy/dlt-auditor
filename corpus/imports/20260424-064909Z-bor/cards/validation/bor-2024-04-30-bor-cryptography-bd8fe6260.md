# Validation Card

## Metadata

- ID: `bor-2024-04-30-bor-cryptography-bd8fe6260`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `operand-decoding-error`

## What Confirmed The Issue

- core/vm/eips.go is the substantive runtime change; AUTHCALL now consumes one fewer stack item.
- opAuthCall explicitly depends on scope.Authorized, tying the bug to an authorization-sensitive execution path.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No proof of a practical exploit, privilege escalation, fund loss, or consensus impact is provided.
- No spec excerpt or advisory is included to show the exact security invariant violated.
