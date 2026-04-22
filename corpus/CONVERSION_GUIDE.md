# Conversion Guide

This guide explains how to convert one prose finding into structured corpus artifacts.

## Goal

Do not preserve every sentence.

Extract the reusable security pattern.

## Step 1: Read For Structure

From the source finding, identify:

- what the code was supposed to protect,
- what property was missing,
- where untrusted input entered,
- what sensitive sink was reached,
- what the impact was,
- and how the patch changed the code shape.

## Step 2: Assign A Bug Family

Use the generic family, not the repo-specific subsystem, as the primary classifier.

Examples:

- missing auth check on RPC handler -> `authz_and_role_gates`
- valid signature accepted from wrong committee member -> `signature_binding_and_signer_scope`
- work done before gas charge -> `resource_accounting_and_limits`
- stale timeout not cleared on all transitions -> `state_machine_and_lifecycle_consistency`

## Step 3: Assign Confidence Tier

Use:

- `tier_a_confirmed`
  For findings with strong code evidence and clear security consequence.

- `tier_b_likely`
  For findings that are security-relevant but more hardening-like or less exploit-proven.

- `tier_c_provenance_only`
  For findings that help explain the taxonomy but should not be strong retrieval anchors.

## Step 4: Write The Record

Create one YAML file under `records/`.

Keep:

- the missing property,
- the violated invariant,
- the trust boundary,
- the impact,
- the code shape,
- the patch pattern.

Avoid:

- long copied prose,
- raw patch chunks,
- vague “security relevant” language without saying why.

## Step 5: Write The Cards

Create three short markdown cards:

### Root-Cause Card

Best for retrieval when the agent needs conceptual pattern matches.

Include:

- missing property,
- violated invariant,
- attack surface,
- impact pattern.

### Code-Shape Card

Best for retrieval when the agent is actively scanning code.

Include:

- code smell,
- asymmetry,
- typical file/function shape,
- likely search motifs,
- patch pattern.

### Validation Card

Best for keeping false positives down.

Include:

- what confirmed the issue,
- what compensating controls would invalidate it,
- what makes similar cases non-issues.

## Step 6: Write The Eval Record

Create one YAML eval record under `evals/`.

It should capture:

- expected bug family,
- expected missing property,
- expected impact band,
- expected severity band,
- and false-positive cautions.

## Retrieval Advice

During live auditing, retrieve:

- one normalized summary or record,
- plus up to two cards.

Do not retrieve:

- the entire original finding,
- many near-duplicates,
- or long prose reports by default.
