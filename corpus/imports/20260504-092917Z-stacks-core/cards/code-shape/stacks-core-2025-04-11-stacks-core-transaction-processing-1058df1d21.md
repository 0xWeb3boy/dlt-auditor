# Code-Shape Card

## Metadata

- ID: `stacks-core-2025-04-11-stacks-core-transaction-processing-1058df1d21`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-limit-validation-inconsistency`

## Code Shape Summary

- Commit 1058df1d21 changes block proposal replay validation so ChainError::BlockCostExceeded is inspected not only for TransactionResult::ProcessingError, but also for TransactionResult::Skipped and TransactionResult::Problematic. The evidence supports a likely validation bypass in a replay-sensitive resource-control path, but does not prove exploitability, consensus impact, or a broader transaction-processing flaw.

## Search Motifs

- Motif 1: request body decoded before max-size enforcement
- Motif 2: panic or unwrap reachable from peer-controlled protocol data
- Motif 3: execution cost or resource budget charged inconsistently across error cases

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Move size, cost, and error checks to the boundary and convert panic or ambiguous errors into explicit validation failures.

## False Match Warnings

- The input may already be bounded by transport framing.
- A panic in test-only or unreachable internal code is not an externally reachable denial of service.
