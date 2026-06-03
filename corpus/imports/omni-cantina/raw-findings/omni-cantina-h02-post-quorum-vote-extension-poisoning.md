# Raw Finding Summary

Source: Omni Cantina `H-2`
Title: Omni chain halt via post-quorum votes poisoning
Severity: `high`

## Normalized Summary

The report explains that CometBFT may include post-quorum vote extensions in commit info without calling VerifyVoteExtension. Omni trusts those extensions in PrepareProposal, so a duplicate extension poisons every next proposal and validators reject it.

## Reusable Failure Shape

Vote extensions are validated on the VerifyVoteExtension path, but PrepareProposal later trusts last-commit extensions that CometBFT may not have verified after quorum.

## Missing Property

`commit-info-vote-extension-revalidation`: PrepareProposal must not assume every vote extension in last commit info was accepted by VerifyVoteExtension; it must revalidate or safely discard invalid extensions.

## Source Evidence

- Ground-truth findings file: `/testing/dlt-ai-audit-system/design-lab/benchmarks/omni-network/ground-truth/findings.md`
- Source section: `H-2`
