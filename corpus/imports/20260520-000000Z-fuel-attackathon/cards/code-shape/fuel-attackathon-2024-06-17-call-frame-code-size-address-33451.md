# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-call-frame-code-size-address-33451`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `call-frame-field-dereference-error`

## Code Shape Summary

- The accessor differed from neighboring call-frame helpers by returning the field pointer rather than reading the u64 value at that pointer.

## Search Motifs

- call_frames::code_size returns address
- code size security check
- call frame offset not dereferenced
- first_param reads value but code_size does not

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Dereference the call-frame code-size slot consistently with adjacent accessors and add tests that compare returned size to actual bytecode length.

## False Match Warnings

- No issue if code_size is used only for logging.
- No issue if the function is documented and named as returning an address.
