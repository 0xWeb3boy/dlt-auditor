# Code-Shape Card

## Metadata

- ID: `bor-2025-08-13-bor-storage-2d1aa4ab5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-header-validation`

## Code Shape Summary

- The supplied evidence supports a non-security test fix, not a vulnerability fix. The concrete, supported change is that receipt-oriented tests now insert headers explicitly before continuing, while the production-code snippets only show anchor movement or refactoring and do not prove a new runtime security check. Root cause: Test/setup drift: the receipt-oriented test paths were using an import path that did not explicitly perform the header insertion step that later chain-state assertions rely on. The provided evidence does not establish a production security flaw.

## Search Motifs

- state or trie data is loaded from disk or peer response without recomputing the expected root/hash
- path or key material from an external source reaches storage lookup/write before normalization
- missing mismatch handling lets corrupt or stale state be treated as canonical

## Typical Asymmetry

- Attacker-controlled data crosses untrusted block, header, transaction, or state data to consensus engine boundary and reaches canonical chain selection, state root commitment, or consensus state mutation before the missing property is enforced.

## Patch Pattern

- Align tests with the intended import contract by making prerequisite header insertion explicit and improving failure reporting, without establishing a new security boundary.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
