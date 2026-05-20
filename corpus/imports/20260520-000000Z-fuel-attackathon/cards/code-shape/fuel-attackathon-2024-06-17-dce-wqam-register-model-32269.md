# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-dce-wqam-register-model-32269`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `optimizer-instruction-side-effect-misclassification`

## Code Shape Summary

- Instruction def/use metadata treated a pointer register as dead, allowing DCE to remove its initializer before a wide arithmetic memory operation.

## Search Motifs

- def_registers WQAM
- use_registers WQAM
- dead code elimination removes pointer init
- wide arithmetic instruction register model

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Correct WQAM register def/use metadata and add optimizer tests comparing optimized execution against unoptimized execution.

## False Match Warnings

- No issue if the instruction metadata exactly matches the VM semantics.
- Optimization is safe if the removed register cannot affect a sensitive memory address.
