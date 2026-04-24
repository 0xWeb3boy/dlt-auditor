# Validation Card

## Metadata

- ID: `sui-2022-07-15-sui-cryptography-da264c340e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-response-verification`

## What Confirmed The Issue

- Adds CheckpointResponse::verify(&Committee) for response-level verification of checkpoint/proposal data.
- safe_client now calls resp.verify(&self.committee)? immediately after receiving a remote checkpoint response.
- Proposal verification binds current proposal verification to optional detail and verifies the previous checkpoint separately.
- Past signed or certified checkpoint responses now reject missing detail when detail was requested as ByzantineAuthoritySuspicion.

## What Could Have Invalidated It

- No proof that invalid checkpoint responses were previously accepted into durable state.
- No demonstrated exploit path, transaction forgery, fund loss, or consensus finality failure.
- No end-to-end regression showing an attacker-controlled authority causing state corruption.
- Commit notes include some relaxed handling, so the patch is not purely a tightening of every checkpoint rule.

## Severity Guidance

- Expected impact band: checkpoint-integrity
- Expected severity band: low-medium
- Rationale: The finding is security relevant, but the validated evidence is bounded and should be weighted by reachability and compensating checks.

## False-Positive Cautions

- Classify as checkpoint response verification hardening, not a confirmed vulnerability fix.
- Do not claim proven state corruption or consensus compromise from the supplied evidence.
- Do not infer fund loss or transaction forgery impact.
- Security relevance is limited to remote checkpoint response integrity and committee/signature validation behavior.
