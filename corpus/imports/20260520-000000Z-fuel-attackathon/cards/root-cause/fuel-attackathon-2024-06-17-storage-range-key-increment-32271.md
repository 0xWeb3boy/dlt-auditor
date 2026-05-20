# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-storage-range-key-increment-32271`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `storage-range-iteration-off-by-one`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `range-boundary-invariant`

## Violated Invariant

- Range helpers must read or mutate exactly the requested contiguous storage slots without extra key increments or spurious overflow errors.

## Trust Boundary

- Boundary: `vm-storage-instruction->contract-state`
- Entrypoint type: `state-access-helper`
- Sensitive sink: `contract storage range read/write/remove result`

## Attack Surface

- Trigger storage range instructions near key-space boundaries.
- Use valid range reads that expose helper iteration errors.

## Exploit Preconditions

- The helper increments the storage key too many times in or around the loop.
- The extra increment can overflow or skip a valid slot.

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `denial-of-service`
- Blast radius: `chain-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- State range helpers need boundary tests that verify both contents and cursor movement, especially near maximum keys.
