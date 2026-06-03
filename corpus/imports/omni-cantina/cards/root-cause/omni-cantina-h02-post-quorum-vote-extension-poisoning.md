# Root-Cause Card

Record: `omni-cantina-h02-post-quorum-vote-extension-poisoning`
Project: `omni-network`
Source finding: `Omni Cantina H-2`
Bug family: `attestation_trust_and_freshness`

## Core Failure

The application trusts a consensus data structure for an application-level validity property that CometBFT explicitly does not guarantee after quorum.

## Why It Matters

BFT systems must tolerate one faulty validator. Letting one invalid vote extension poison all future proposals violates that resilience boundary.

## Reusable Heuristic

When ABCI++ vote extensions are consumed from commit info, check whether the application revalidates every property it relied on in VerifyVoteExtension.

## Patch Direction

Revalidate vote extensions from commit info in PrepareProposal and ignore/report invalid duplicates instead of forming an invalid proposal.
