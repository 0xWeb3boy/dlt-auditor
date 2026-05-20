# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-storage-map-variable-slot-collision-32884`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `storage-slot-domain-collision`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `storage-domain-separation`

## Violated Invariant

- Distinct storage declarations and map entries must not be able to derive the same storage slot from valid source-level names and keys.

## Trust Boundary

- Boundary: `contract-developer-or-user-input->contract-storage`
- Entrypoint type: `storage-layout-derivation`
- Sensitive sink: `contract storage slots shared by variables and StorageMap entries`

## Attack Surface

- Craft storage names and map keys whose byte preimages collide under the layout scheme.
- Deploy a contract that hides a backdoor storage alias.

## Exploit Preconditions

- Simple variables and map entries use compatible unframed hash preimages.
- A map key can be caller-controlled or chosen to match a variable-name preimage.

## Impact Pattern

- Primary impact: `storage-integrity`
- Secondary impact: `unauthorized-action`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Storage layout hashes need domain tags and unambiguous framing whenever different declaration kinds share one key space.
