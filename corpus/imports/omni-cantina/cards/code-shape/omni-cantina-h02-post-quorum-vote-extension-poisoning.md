# Code-Shape Card

Record: `omni-cantina-h02-post-quorum-vote-extension-poisoning`
Project: `omni-network`
Source finding: `Omni Cantina H-2`

## Search Shape

Vote extensions are validated on the VerifyVoteExtension path, but PrepareProposal later trusts last-commit extensions that CometBFT may not have verified after quorum.

## Motifs

- `VerifyVoteExtension duplicate votes`
- `PrepareVotes last commit info`
- `post-quorum vote extension`
- `baseapp.ValidateVoteExtensions`
- `commit trusted valid VEs`
- `ProcessProposal AddVotes duplicate`

## Negative Signals

- PrepareProposal revalidates all commit-info extensions with the same duplicate checks.
- Invalid commit-info votes are ignored instead of included or fatal.
- CometBFT guarantees all extensions in commit info were application-verified.

## Likely Fix Shape

Revalidate vote extensions from commit info in PrepareProposal and ignore/report invalid duplicates instead of forming an invalid proposal.
