# Validation Card

## Metadata

- ID: `bor-2015-05-21-bor-core-logic-52db6d8be`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-bypass`

## What Confirmed The Issue

- The fix replaces !d.queue.Has(block.ParentHash()) with block.ParentHash() != check.parent, tightening validation from local membership to exact expected ancestry.
- A new crossCheck structure stores the expected parent hash, showing the prior state was insufficient for later verification.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: high

## False-Positive Cautions

- The patch does not show whether the forged chain would survive later consensus or full block validation stages.
- The evidence does not demonstrate measurable resource exhaustion or a reliable remote denial-of-service condition.
