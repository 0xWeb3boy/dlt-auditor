# Code-Shape Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-abi-supertrait-external-dispatch-33351`
- Bug family: `authz_and_role_gates`
- Bug class: `supertrait-method-dispatch-exposure`

## Code Shape Summary

- ABI generation and dispatch generation disagreed: metadata hid supertrait methods, but runtime selector dispatch still routed to them.

## Search Motifs

- ABI supertrait excluded from contract-abi.json
- selector dispatch includes inherited trait method
- methods not available externally comment
- IR function dispatch supertrait

## Typical Asymmetry

- The vulnerable shape appears when one path carries a security, arithmetic, resource, or lifecycle invariant while a sibling path or generated artifact omits the same enforcement.
- Look for helper APIs, compiler metadata, opcode wrappers, or SDK state caches that are treated as authoritative by downstream code.

## Patch Pattern

- Exclude ABI supertrait methods from external dispatch selector tables and add compiler tests that external calls to supertrait-only methods fail.

## False Match Warnings

- No issue if the method is intentionally listed in the public ABI.
- No issue if the exposed helper has complete independent authorization checks.
