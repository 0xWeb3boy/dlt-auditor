# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-bytecode-root-empty-infinite-loop-33186`
- Bug family: `resource_accounting_and_limits`
- Bug class: `empty-input-nontermination`

## Code Shape Summary

- The bytecode-root loop assumed at least one chunk, so zero-length input never reached the branch that exits.

## Search Motifs

- _compute_bytecode_root empty bytecode
- verify_contract_bytecode infinite loop
- loop break not reached zero length
- compute_bytecode_root no chunks

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Add an explicit empty-bytecode case that returns the canonical empty root or rejects the input, with tests for all public wrappers.

## False Match Warnings

- No issue if callers reject empty bytecode before invoking the helper.
- No issue if VM gas reliably aborts without persistent liveness damage.
