# Validation Card

## Metadata

- ID: `bor-2022-06-29-bor-cryptography-d12b1a91c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-transition-validation`

## What Confirmed The Issue

- Adds explicit terminal-block validation via verifyTerminalPoWBlock in mixed PoW/PoS header verification.
- Introduces ErrInvalidTerminalBlock, showing the change targets invalid consensus-transition handling rather than generic cleanup.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No full before/after body is shown proving exactly which invalid headers were previously accepted.
- No test assertions are included to demonstrate the concrete bad pre-patch behavior.
