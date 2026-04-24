# Validation Card

## Metadata

- ID: `sui-2024-08-20-sui-consensus-dab9bad618`
- Bug family: `resource_accounting_and_limits`
- Bug class: `consensus-resource-limit-hardening`

## What Confirmed The Issue

- SignedBlockVerifier previously contained a deferred guard to check transaction size, total size, and count before accepting block transactions.
- The patch adds a protocol-configured per-transaction size limit check and returns TransactionTooLarge on violation.
- Protocol config adds consensus transaction byte and transaction count limits for blocks.
- ConsensusError gains explicit errors for too-large transactions, too many transactions, and too many transaction bytes.

## What Could Have Invalidated It

- No exploit scenario or externally triggerable denial-of-service path is demonstrated.
- The provided hunks do not fully show implementation of aggregate byte and transaction count checks.
- No evidence shows a pre-patch consensus divergence, signature bypass, replay issue, or safety failure.
- No operational incident, advisory, or security-labeled commit metadata is provided.

## Severity Guidance

- Expected impact band: denial-of-service_or_resource-exhaustion
- Expected severity band: low-medium
- Rationale: The primary risk is availability or resource amplification; severity depends on reachable volume, default exposure, and whether throttling exists elsewhere.

## False-Positive Cautions

- Classify as consensus resource-limit hardening, not a confirmed vulnerability fix.
- Do not claim consensus safety compromise from the supplied evidence.
- Do not claim cryptographic, replay, or authentication impact.
- Do not claim all block limit checks are visible in the supplied patch snippets, only that the commit and errors/config indicate them.
