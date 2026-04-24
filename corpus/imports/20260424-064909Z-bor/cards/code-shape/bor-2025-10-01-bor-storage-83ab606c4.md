# Code-Shape Card

## Metadata

- ID: `bor-2025-10-01-bor-storage-83ab606c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- The patch adds consistency checks to the network-facing witness page receiver in eth/peer.go. The evidence supports protocol/input validation hardening against malformed peer pagination metadata, but it does not establish a concrete vulnerability impact beyond preventing inconsistent local bookkeeping and processing. Root cause: Missing validation of peer-controlled witness pagination fields in receiveWitnessPage. The code used page.Page and page.TotalPages to drive local witness-page accounting without enforcing basic consistency constraints.

## Search Motifs

- state or trie data is loaded from disk or peer response without recomputing the expected root/hash
- path or key material from an external source reaches storage lookup/write before normalization
- missing mismatch handling lets corrupt or stale state be treated as canonical

## Typical Asymmetry

- Attacker-controlled data crosses remote peer to node networking boundary and reaches peer table mutation, sync scheduling, or message acceptance before the missing property is enforced.

## Patch Pattern

- Add receiver-side validation for untrusted protocol metadata and reject packets that violate previously established bounds or consistency rules.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
