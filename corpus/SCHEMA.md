# Findings Schema

This schema is designed for blockchain and DLT security findings.

It is intentionally generic and should work across L1s, rollups, bridges, validators, sequencers, MPC systems, TEEs, and related infrastructure.

## Canonical Record Fields

Each finding record should capture the following fields.

## Identity

- `id`
  Stable internal ID.

- `source_finding`
  Original filename or source identifier.

- `project`
  Project or repo name.

- `date`
  Date of the source finding or fix.

- `language_tags`
  Example: `["go", "rust"]`

## Classification

- `bug_family`
  One of the generic operational families:
  - `authz_and_role_gates`
  - `signature_binding_and_signer_scope`
  - `attestation_trust_and_freshness`
  - `input_validation_and_invariant_enforcement`
  - `resource_accounting_and_limits`
  - `state_machine_and_lifecycle_consistency`
  - `staking_registry_and_accountability`
  - `checked_arithmetic_and_parameter_bounds`

- `bug_class`
  More specific class, e.g. `missing-authentication`, `slashability-bypass`, `missing-gas-accounting`.

- `subsystem`
  Repo-specific subsystem, e.g. `staking`, `consensus`, `bridge`, `rpc`, `mempool`, `proof-verifier`.

- `architecture_tags`
  Example:
  - `validator-based`
  - `committee-based`
  - `bridge`
  - `rollup`
  - `light-client`
  - `tee`
  - `mempool`
  - `governance`

## Confidence And Use

- `confidence_tier`
  One of:
  - `tier_a_confirmed`
  - `tier_b_likely`
  - `tier_c_provenance_only`

- `security_verdict`
  Example: `confirmed`, `likely`, `unclear`

- `validated_as`
  Example: `security-fix`, `security-hardening`

- `recommended_uses`
  Example:
  - `retrieval_exemplar`
  - `eval_positive`
  - `taxonomy_refinement`
  - `provenance_only`

## Security Semantics

- `missing_property`
  What was missing or incomplete, e.g.:
  - `authentication`
  - `authorization`
  - `signer-authorization`
  - `domain-separation`
  - `freshness`
  - `policy-gating`
  - `resource-accounting`
  - `lifecycle-cleanup`
  - `state-coordinate-consistency`
  - `arithmetic-bounds`

- `violated_invariant`
  Short plain-English invariant that should have held.

- `trust_boundary`
  Example:
  - `user->mempool`
  - `peer->node`
  - `validator->consensus`
  - `bridge-domain->settlement-domain`
  - `operator->admin-api`
  - `host->enclave`

- `entrypoint_type`
  Example:
  - `transaction-handler`
  - `rpc-handler`
  - `p2p-message-handler`
  - `state-transition`
  - `registration-path`
  - `query-verification-path`
  - `session-setup`

- `sensitive_sink`
  The privileged or security-sensitive action/state reached by the bug.

## Attack Model

- `attacker_capabilities`
  Short list describing what the attacker needs to control or send.

- `exploit_preconditions`
  Preconditions beyond ordinary access.

- `blast_radius`
  Example:
  - `client-local`
  - `node-local`
  - `validator-local`
  - `chain-wide`
  - `cross-domain`

## Impact

- `impact_types`
  Example:
  - `consensus-integrity`
  - `state-integrity`
  - `unauthorized-action`
  - `denial-of-service`
  - `fee-bypass`
  - `slashing-bypass`
  - `stale-trust-state`
  - `privileged-disclosure`

- `severity_guess`
  Example: `critical`, `high`, `medium`, `low`, `informational`

- `severity_rationale`
  Short justification.

## Code Pattern

- `code_shape_summary`
  Short description of what the buggy code looked like.

- `search_motifs`
  Searchable motifs or code smells.

- `negative_signals`
  What would make a superficially similar candidate not a real issue.

- `patch_pattern`
  Short description of what the fix changed structurally.

## Sources

- `source_refs`
  Relevant files, commits, reports, advisories, or patch refs.

- `notes`
  Any extra structured notes.

## Minimum Useful Record

If you want a smaller MVP, start with these fields:

- `id`
- `project`
- `bug_family`
- `bug_class`
- `subsystem`
- `confidence_tier`
- `missing_property`
- `violated_invariant`
- `trust_boundary`
- `entrypoint_type`
- `sensitive_sink`
- `impact_types`
- `severity_guess`
- `code_shape_summary`
- `search_motifs`
- `patch_pattern`
