# Validation Card

## Metadata

- ID: `optimism-2026-04-13-optimism-consensus-e2253914e7`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `untrusted-input-in-protocol-activation-check`

## What Confirmed The Issue

- The patch changes the Fjord activation check from cfg.is_fjord_active(batch.timestamp()) to cfg.is_fjord_active(self.origin_timestamp).
- BatchReader now stores origin_timestamp, indicating the gate should use trusted derivation context rather than decoded batch contents.
- channel_reader passes origin.timestamp into BatchReader::new, showing the fix propagates trusted L1 state into the validation path.
- The commit message explicitly states a malicious batcher could craft input that made kona reject a channel while op-node accepted it, causing consensus deviation.

## What Could Have Invalidated It

- No test diff is shown demonstrating the divergence before the fix or agreement after the fix.
- The patch does not quantify whether the mismatch could cause chain split, node desync, or only local derivation failure.
- The evidence does not show whether similar activation checks elsewhere had the same trust-boundary mistake.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: consensus-or-state-integrity
- Expected severity band: high_or_medium

## False-Positive Cautions

- No test diff is shown demonstrating the divergence before the fix or agreement after the fix.
- The patch does not quantify whether the mismatch could cause chain split, node desync, or only local derivation failure.
- The evidence does not show whether similar activation checks elsewhere had the same trust-boundary mistake.
