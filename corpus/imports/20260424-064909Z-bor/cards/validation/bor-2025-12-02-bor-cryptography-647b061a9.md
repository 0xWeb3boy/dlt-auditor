# Validation Card

## Metadata

- ID: `bor-2025-12-02-bor-cryptography-647b061a9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- verifySeal now rejects nil or non-uint64 difficulty values before narrowing/comparing them.
- Header.SanityCheck lowers the allowed difficulty width from 80 bits to 64 bits.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: low

## False-Positive Cautions

- No proof that oversized difficulty could be used to bypass authorization or forge signatures.
- No demonstrated exploit, chain split, or concrete attacker-controlled impact from the patch alone.
