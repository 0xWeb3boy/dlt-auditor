# Code-Shape Card

## Metadata

- ID: `optimism-2025-11-12-optimism-core-logic-b7c0afd57d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `archive-path-validation-hardening`

## Code Shape Summary

- The buggy shape was a archive-extraction or file-materialization path that allowed data or state to approach filesystem write outside the intended extraction or artifact directory before fully enforcing path-confinement. The pre-patch extraction path used a narrow inline check on tar header names rather than a dedicated helper with more explicit validation rules.

## Search Motifs

- archive extraction joins paths without containment check
- tar entry names, links, or absolute paths reach filesystem writes
- cleanup/overwrite logic trusts paths from the artifact
- archive-extraction or file-materialization path reaches filesystem write outside the intended extraction or artifact directory with partial validation
- path-confinement is enforced in one path but missing in an alternate path

## Typical Asymmetry

- The vulnerable asymmetry is that path-confinement was enforced only partially, late, or in one lifecycle branch while another branch could still reach filesystem write outside the intended extraction or artifact directory.

## Patch Pattern

- Replace ad hoc inline archive-path checks with a shared sanitization helper and add explicit rejection of obviously unsafe path forms.

## False Match Warnings

- an earlier boundary already rejects the same malformed field under all reachable modes
- the changed code is test-only, generated-only, logging-only, or pure refactor with no runtime decision change
- the input is not attacker-influenced and cannot be affected by a faulty peer, operator, backend, or sequencer
- downstream consensus/proof verification recomputes the property fail-closed before any state or privilege is committed
