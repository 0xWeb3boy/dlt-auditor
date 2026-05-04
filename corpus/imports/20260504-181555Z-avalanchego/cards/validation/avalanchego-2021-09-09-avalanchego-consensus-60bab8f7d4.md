# Validation Card

## Metadata

- ID: `avalanchego-2021-09-09-avalanchego-consensus-60bab8f7d4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- Evidence: Commit subject says "patched pre-fork-block exploit".
- Evidence: `verifyPreForkChild` now rejects parents inconsistent with pre-fork status after activation.
- Evidence: The new checks consult accepted post-fork state via `GetLastAccepted()` and post-fork tree membership via `Tree.Contains`.

## What Could Have Invalidated It

- Compensating control: No full attacker workflow or exploit reproduction is provided.
- Compensating control: No explicit demonstration of consensus divergence, chain halt, or asset loss is shown.
- Compensating control: No advisory, issue, or external vulnerability description is supplied.

## Severity Guidance

- Expected impact band: high_integrity
- Expected severity band: high_or_medium
- Severity rationale: This is the only confirmed security fix in the bundle; fork-boundary verification errors can affect consensus safety if invalid block relationships are accepted.

## False-Positive Cautions

- Caution: Classify as a proposer VM fork-boundary consensus validation fix.
- Caution: Do not claim cryptographic primitive failure.
- Caution: Do not claim direct fund theft or asset loss.
