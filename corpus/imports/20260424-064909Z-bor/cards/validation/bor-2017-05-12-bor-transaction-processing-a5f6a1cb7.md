# Validation Card

## Metadata

- ID: `bor-2017-05-12-bor-transaction-processing-a5f6a1cb7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `chain-config-validation`

## What Confirmed The Issue

- checkCompatible gained a new isForkIncompatible(c.MetropolisBlock, newcfg.MetropolisBlock, head) check.
- The new branch returns ConfigCompatError for a mismatched historical Metropolis fork block.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: medium

## False-Positive Cautions

- No evidence shows an external attacker can influence local chain configuration.
- No exploit, incident, or consensus split is demonstrated in the supplied material.
