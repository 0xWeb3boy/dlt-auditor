# Validation Card

## Metadata

- ID: `agave-2026-01-09-agave-consensus-8cebdeb9b0`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-vote-authorization-filtering`

## What Confirmed The Issue

- VoteStorage now checks cached epoch authorized voters before update_latest_vote.
- Votes with missing or mismatched authorized-voter entries are skipped and the commit explicitly describes filtering unauthorized votes.

## What Could Have Invalidated It

- Later validation always runs before latest-vote state affects any decision.
- The vote-storage path cannot receive attacker-controlled or relayed vote packets.

## Severity Guidance

- Expected impact band: `consensus authorization failure`
- Expected severity band: `medium_or_high`
- Rationale: The confirmed missing authorization check sits before consensus-facing latest-vote mutation; downstream impact is not fully proven, so high is a conservative upper band rather than critical.

## False-Positive Cautions

- Do not flag vote parsing changes unless authorization is checked before state mutation.
- Distinguish stake-account existence from authorized-voter signer validation.
