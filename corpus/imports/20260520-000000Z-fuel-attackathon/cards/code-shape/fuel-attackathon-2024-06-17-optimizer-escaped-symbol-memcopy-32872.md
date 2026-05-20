# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-optimizer-escaped-symbol-memcopy-32872`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `optimizer-alias-clobber-miss`

## Code Shape Summary

- A peephole optimization replaced Load plus Store with MemCopyVal without rejecting pointers that were mutated through escaped aliases.

## Search Motifs

- load_store_to_memcopy
- escaped_symbols
- is_clobbered only current function
- MemCopyVal after function call

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Skip the optimization for escaped symbols or add interprocedural alias/clobber analysis, with regression tests around call-side mutation.

## False Match Warnings

- No issue if alias analysis proves the pointed-to data cannot be written.
- No issue if the type is immutable or copied before any escaping call.
