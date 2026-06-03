# Prompt Family: Terminal Range And Cursor Boundaries

## Use This For

- Storage range helpers, Merkle/index iterators, VM state range instructions, pagination helpers, sync ranges, and cursor loops.
- Inclusive/exclusive endpoint mistakes and cursor increments at numeric boundaries.
- Valid requests that end exactly at the last representable key, slot, height, index, or cursor.

## Prompt

```text
Hunt for bugs where a range, cursor, key, or iterator is valid for every item it touches, but the helper fails after the final item because it advances, increments, narrows, or validates one step too far.

Focus on:
- storage reads/writes/removes over contiguous keys
- VM or contract state range instructions
- database range scans and Merkle proof ranges
- GraphQL/REST pagination cursors and block/transaction ranges
- sync/header/transaction range chunkers
- snapshot, archive, pruning, rollback, and historical view iterators

Search patterns:
- loops that use a key/cursor, then increment it at the end of every iteration, including the final iteration
- post-use increments that can overflow even though no next item is needed
- `start + len`, `end + 1`, `inclusive_end + 1`, `saturating_add(1)`, or conversion from inclusive to exclusive ranges
- helper functions named range, chunk, next, increase, advance, cursor, page, window, scan, prefix, upper_bound, or lower_bound
- APIs that accept `(start, count)` or `(cursor, first/last)` and must allow terminal values
- empty, singleton, two-item-at-end, max-key, max-height, and max-index cases missing from tests
- range insert/remove paths copied from range read paths with the same terminal increment behavior
- typed big integer, fixed-width key, hash, slot, or byte-array cursors converted through smaller host integers
- error handling that treats a post-final cursor overflow as invalid input rather than successful completion

For every range helper or cursor helper with security relevance, produce a terminal-case proof table:
- empty range or count zero
- singleton at the last representable item
- two-item range ending at the last representable item
- first invalid range that would require one item beyond the end
- equivalent read, insert/write, remove/delete, proof, and pagination variants

If the helper rejects the terminal singleton after already touching or validating the only needed item, keep the issue as a candidate unless a spec, caller precondition, or parser explicitly forbids that terminal value. Missing spec proof should lower confidence or severity; it should not erase concrete helper evidence.

Questions to answer:
1. Is the input range itself valid, including the terminal element?
2. Does the code advance after processing the last element, and is that advance required?
3. Does overflow after the last useful item incorrectly fail the whole operation?
4. Are read, insert, remove, proof, and pagination variants consistent?
5. Are there tests for the last one and last two representable keys/items?
6. Is a saturated endpoint silently dropping the final item or causing zero progress?
7. Does a helper reject cursor-only or endpoint-only shapes based on an assumption not enforced by the caller?
8. Is the endpoint treated as inclusive, exclusive, or "one past" consistently across parser, helper, storage, proof, and caller?
9. If the issue is downgraded for spec uncertainty, what exact spec rule or minimal test would kill or confirm it?

Severity guidance:
- Medium when a valid contract/storage/query operation can incorrectly fail or halt a user-facing workflow.
- Raise only when the boundary bug can affect consensus validity, bridge accounting, or broad node availability.
```
