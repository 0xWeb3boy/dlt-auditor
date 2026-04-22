# Code-Shape Card

## Metadata

- ID: `scroll-2023-03-27-scroll-storage-f26ab8b7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insecure-file-permissions`

## Code Shape Summary

- Short description of what the buggy code looked like: The evidence supports a narrow permission tightening in mock/CI helper code, not a demonstrated vulnerability fix. The commit is titled `fix ci`, most touched files are tests or mock helpers, and the other shown hunks are receiver renames with no evidenced security effect.

## Search Motifs

- Motif 1: temporary or generated config file written with 0644 or world-readable mode
- Motif 2: test or CI helper writes secrets, endpoints, or credentials without tightening file permissions
- Motif 3: os.WriteFile on privileged local config material with permissive defaults

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Tighten generated-file permissions at creation time so local config artifacts default to owner-only access instead of inheriting permissive filesystem modes.

## False Match Warnings

- Warning 1: If the generated file contains only public test data and no privileged material, the case is usually just hygiene rather than security hardening.
- Warning 2: If the file lives in an isolated ephemeral sandbox where no other principal can read it, the practical security impact is much lower.
- Warning 3: Receiver renames or helper refactors in nearby files are not the core issue; the security-relevant part is the permission mode on the file write.
