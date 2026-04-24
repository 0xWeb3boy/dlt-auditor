# Validation Card

## Metadata

- ID: `sui-2023-03-06-sui-consensus-e4c9e8c80c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unverified-consensus-timestamp-source`

## What Confirmed The Issue

- Commit body explicitly identifies use of certificate metadata timestamps as a serious problem that could lead to security issues because metadata timestamps are not verified.
- Consensus handling changed from using leader metadata created_at to leader.header.created_at.
- Patched code comments that Narwhal enforces invariants on header.created_at.
- The selected header timestamp is passed into consensus commit prologue and commit boundary handling.

## What Could Have Invalidated It

- No concrete attacker model is shown.
- No exploit path from forged metadata timestamp to consensus failure or checkpoint corruption is demonstrated.
- The actual Narwhal invariants on header.created_at are referenced but not included in the supplied evidence.
- No tests or assertions demonstrate the rejected unsafe timestamp behavior.

## Severity Guidance

- Expected impact band: integrity-risk_or_consensus-timestamp-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Supported: the patch removes reliance on an unverified metadata timestamp in consensus commit processing.
- Supported: the change tightens timestamp trust assumptions in a consensus-sensitive path.
- Not supported: a confirmed exploitable vulnerability with a demonstrated impact.
- Not supported: classifying the impact specifically as consensus failure from the supplied patch alone.
