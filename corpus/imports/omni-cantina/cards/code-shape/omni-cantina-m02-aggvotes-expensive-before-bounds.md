# Code-Shape Card

Record: `omni-cantina-m02-aggvotes-expensive-before-bounds`
Project: `omni-network`
Source finding: `Omni Cantina M-2`

## Search Shape

verifyAggVotes performs aggregate signature recovery before checking whether claimed validators are in the valset or within vote bounds.

## Motifs

- `verifyAggVotes`
- `AggVote.Verify`
- `SigToPub`
- `vote from unknown validator`
- `voteExtLimit`
- `100 MB signatures`
- `ProcessProposal MsgAddVotes`

## Negative Signals

- Membership and signature count are checked before recovery.
- Only locally generated aggregates reach the path.
- A small local proposal byte/count limit applies before decoding.

## Likely Fix Shape

Move count, chain, window, duplicate, and claimed-membership checks ahead of signature recovery; enforce explicit local byte/count limits.
