# Validation Card

Record: `omni-cantina-h02-post-quorum-vote-extension-poisoning`
Project: `omni-network`
Source finding: `Omni Cantina H-2`

## Positive Confirmation

Confirm VerifyVoteExtension rejects duplicates, CometBFT can include unverified post-quorum extensions, PrepareProposal trusts them, and ProcessProposal rejects the resulting MsgAddVotes.

## Preconditions To Confirm

- Network has more than two validators.
- Commit info includes post-quorum vote extensions not checked by VerifyVoteExtension.
- PrepareProposal trusts commit info and includes duplicate votes.
- ProcessProposal rejects the resulting duplicate aggregate votes.

## False-Positive Cautions

- The app revalidates and drops invalid commit-info extensions before proposal construction.
- The consensus layer version guarantees no unverified extension can enter commit info.
- Invalid extensions can only affect the malicious validator itself.

## Minimal Reproduction Or Check

Run a multi-validator devnet where one validator appends a duplicate vote extension after quorum and observe repeating proposal rejection.
