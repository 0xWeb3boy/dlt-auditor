# Vote Extension, Commit Info, And Signature Edges

## Family Objective

Find bugs in vote extensions, side votes, aggregate votes, quorum certificates, and attestation storage where data consumed from commit info or proposal bodies bypasses the verifier, validates expensive data before cheap rejection, mishandles duplicate or malleable signatures, or accumulates valid but useless state until liveness fails.

## Hunt Steps

1. Map the full lifecycle: vote creation, vote-extension verification, commit inclusion, proposal construction, proposal verification, finalization, persistence, quorum approval, query/export, and cleanup.
2. Identify upstream guarantees for every consumed vote or extension. Check whether entries added after quorum, recovered from commit info, loaded during replay, or included by a proposer are guaranteed to have run the same application verifier.
3. Compare duplicate, chain/domain, signer, validator-set membership, freshness/window, and per-validator limit checks across the original verifier, proposal builder, proposal verifier, finalizer, and persistence layer.
4. Check validation order for aggregate votes and certificates. Cheap size, count, duplicate, membership, and range checks should run before signature recovery, proof verification, decompression, database scans, or other expensive work.
5. Search for bytewise equality checks over signatures, public keys, proofs, or roots after cryptographic validity has been established. Determine whether multiple valid encodings can represent the same semantic signer/message.
6. Search persistence keys for missing validator-set, epoch, height, round, fork, or membership context. Pending signatures or roots should not later be counted under a different quorum context unless that is a proven protocol rule.
7. Model state growth. For each valid-but-useless vote, attestation root, certificate, pending object, or signature, compute how many a faulty or malicious participant can add per block, how long it is retained, and whether every block iterates over the retained set.
8. Inspect cleanup after proposal rejection, missed rounds, restart, rollback, pruning, state sync, and validator-set rotation.
9. Build a trusted-commit-data table. For each consumed entry, record the source phase, whether quorum had already been reached, whether the application verifier definitely ran, what upstream docs/code prove that, and which local sink would reject it if the guarantee is weaker.
10. If the code calls a shared vote-extension or certificate verifier in the normal path, search for every path that bypasses that normal call: post-threshold receipt, replay, proposer construction, state sync, recovery, local test harness, finalization after proposal acceptance, or direct aggregate message inclusion.
11. For signature/proof malleability, do not stop at "dependency likely rejects it". Add or propose the smallest semantic-equivalence test: produce or mock two valid byte encodings for one signer/message/proof and trace the duplicate or unique-key path.
12. For state growth, create a retention equation: per-block admitted objects times retention blocks or cleanup delay times repeated iteration cost. If exact constants are unknown, compute a symbolic upper bound from protocol limits.
13. For duplicate votes, distinguish duplicate semantic vote, duplicate attestation header, duplicate signer, duplicate signature bytes, and duplicate aggregate root. A path that rejects one duplicate dimension may still accept another.
14. Trace proposal-time validation and finalization-time mutation separately. If proposal validation rejects byte-different duplicates but finalization receives already accepted or replayed objects, prove the finalization path uses the same semantic duplicate rule.
15. For validation-order DoS, identify the first attacker-controlled expensive operation and the cheapest missing reject that could have preceded it. Include membership, chain support, window/range, count, duplicate, size, and per-signer limits.
16. For post-threshold data, require a replay-loop proof: late object enters commit or certificate data, local builder includes it, validators reject or persist it, and the same poisoned data or retained state affects future rounds/blocks.
17. For post-quorum data, compare pre-quorum verifier assumptions against post-quorum retention and proposal construction. If the upstream verifier stops after threshold or ignores late entries, local code must either drop the extras or re-run duplicate, signer, membership, chain, freshness, and domain checks before storing or including them.
18. For validation-order issues, separate "bounded by proposal size" from "cheaply rejectable before expensive work". A consensus path can still be a liveness risk when an attacker fills the allowed aggregate with unknown signers, unsupported roots, duplicate semantics, or stale windows that force crypto or database work before rejection.
19. For retained fake roots or useless attestations, trace whether a malicious minority can create many distinct keys for one semantic period. Record whether cleanup depends on approval, quorum, finalization, pruning, or a moving trim height that may lag attacker insertions.
20. For proposal-time versus finalization-time vote handling, prove both acceptance and mutation paths. A candidate is stronger when proposal verification lets poisoned metadata persist, but finalization or future proposal building is the first place it becomes fatal.

## Candidate Requirements

For every candidate, include:

- which verifier should have run;
- which consumed entries may bypass it or be verified under another context;
- exact ordering of cheap reject checks versus expensive work;
- signature/proof canonicalization assumptions;
- persistence key context and cleanup behavior;
- attacker role: proposer, validator, peer, user, operator, or governance;
- concrete impact: proposal rejection loop, finalization failure, state-growth DoS, bad quorum, or local liveness.
- upstream guarantee evidence or missing evidence for late/replayed/proposer-selected data.
- semantic-versus-byte duplicate table for signatures, roots, votes, and aggregate objects.
- post-quorum poisoning loop or retained-state capacity equation when the issue depends on late data or fake roots.

## False-Positive Controls

- Do not report broad "finalizer trusts consensus" unless a specific upstream guarantee is absent or weaker for a consumed subset.
- Do not report expensive crypto order unless attacker-controlled input can reach it before cheap rejection.
- Do not report state growth without a per-block insertion path, retention window, and repeated iteration or storage impact.
- Do not kill a late-data issue by pointing only to the normal verifier; show that the exact consumed entry necessarily passed it.
