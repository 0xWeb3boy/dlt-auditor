# Validation Card

## Metadata

- ID: `sui-2025-03-26-sui-cryptography-aba86cd0d7`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-consensus-object-ownership-authentication`

## What Confirmed The Issue

- Commit subject states authentication checks were implemented for ConsensusV2 objects.
- Commit body states object ownership is verified at signing time.
- Owner::authenticator() was added and returns authenticator metadata only for ConsensusV2 owners.
- Transaction checks separate ConsensusV2 handling from the shared-object start-version branch.

## What Could Have Invalidated It

- Full post-patch ConsensusV2 validation logic is not shown in the supplied snippets.
- No regression test excerpt demonstrates rejection of an unauthorized ConsensusV2 object use.
- No exploit transaction or proof of a prior authorization bypass is provided.
- No evidence supports replay, generic signature forgery, or consensus-finality impact.

## Severity Guidance

- Expected impact band: unauthorized-object-use_or_transaction-input-authorization-bypass
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Validate as security hardening for ConsensusV2 object ownership/authentication checks.
- Do not claim a proven replay vulnerability from the supplied evidence.
- Do not claim generic signature forgery from the supplied evidence.
- Do not treat formatting-only error message changes as security evidence.
