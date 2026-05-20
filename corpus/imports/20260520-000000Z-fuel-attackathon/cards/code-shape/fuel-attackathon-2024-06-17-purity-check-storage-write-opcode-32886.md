# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-purity-check-storage-write-opcode-32886`
- Bug family: `authz_and_role_gates`
- Bug class: `read-only-effect-gate-bypass`

## Code Shape Summary

- Static effect analysis recursively checked functions but mapped a storage-writing assembly instruction into the read category.

## Search Motifs

- check_function_purity
- SCWQ classified as read
- storage(read) modifies state
- read abi function writes storage

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Classify write-capable opcodes as mutations, strengthen cross-contract effect handling, and consider a runtime storage-mutation guard for read contexts.

## False Match Warnings

- No issue if VM runtime enforces no-storage-write mode for read calls.
- No issue if the function is not externally reachable or has explicit authorization.
