# Validation Card

## Metadata

- ID: `sui-2023-02-02-sui-cryptography-7ec4bccdd4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-quorum-hardening`

## What Confirmed The Issue

- CertifiedCheckpointSummary changed from AuthorityWeakQuorumSignInfo to AuthorityStrongQuorumSignInfo.
- Checkpoint aggregation now constructs AuthorityStrongQuorumSignInfo certificates.
- CheckpointSignatureAggregator now returns a strong quorum signature info type.
- Commit message states the prior weak quorum could allow larger fork blast radius if nondeterministic execution caused divergent checkpoint digests.

## What Could Have Invalidated It

- No demonstrated attacker-controlled exploit path is provided.
- No evidence of signature forgery, replay, nonce misuse, or invalid signature acceptance is shown.
- The referenced recent accident and nondeterministic execution bug are not included in the supplied evidence.
- The patch does not prove that weak quorum violated the protocol's stated minimal safety model.

## Severity Guidance

- Expected impact band: consensus-safety_or_fork-risk-reduction
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Treat as consensus/checkpoint quorum hardening, not as a replay or request-forgery fix.
- Do not claim concrete exploitability from the patch alone.
- Do not claim cryptographic signature validation was broken; the change is the quorum threshold/type used for checkpoint certification.
- Security relevance is fork/blast-radius reduction in a validator consensus subsystem.
