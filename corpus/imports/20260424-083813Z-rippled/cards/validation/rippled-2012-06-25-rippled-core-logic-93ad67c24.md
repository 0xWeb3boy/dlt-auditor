# Validation Card

## Metadata

- ID: `rippled-2012-06-25-rippled-core-logic-93ad67c24`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `hash-domain-separation`

## What Confirmed The Issue

- Evidence 1: Commit subject uses direct security language: "Close SHAMap node security hole".
- Evidence 2: Fetched nodes are reconstructed through a node-aware helper using both node id and expected hash.

## What Could Have Invalidated It

- Compensating control 1: No exploit scenario or attacker-controlled input path is shown.
- Compensating control 2: No advisory, test, or vulnerability description is provided.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: state-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No exploit scenario or attacker-controlled input path is shown.
- Caution 2: No advisory, test, or vulnerability description is provided.
