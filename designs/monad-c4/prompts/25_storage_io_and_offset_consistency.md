# Prompt Family: Storage I/O And Offset Consistency

## Use This For

- Custom block devices, append logs, snapshot stores, archive stores, and trie or ledger persistence.
- Trim, discard, punch-hole, zero-fill, seek, write, read, compact, truncate, repair, and replay paths.
- C++/Rust/native storage adapters where a validated range can diverge from the actual device position.

## Prompt

```text
Hunt for storage I/O offset and range-consistency bugs in a blockchain or DLT codebase.

Focus on code that translates protocol state into byte-addressed operations. A storage bug can become security-relevant when it corrupts ledger data, weakens recovery, crashes replay, loses finalized state, or makes validators disagree after restart.

Search patterns:
- trim, discard, punch-hole, zero-fill, compact, truncate, preallocate, or sparse-file operations that validate one offset/length but execute at the current file cursor or another cached position
- APIs where a caller passes offset and length separately but the callee uses an internal write pointer, append pointer, block index, or previous seek state
- read-modify-write paths that seek for the read but not for the write, or seek with different units such as bytes, sectors, pages, chunks, blocks, words, or entries
- conversion between signed and unsigned offsets, block counts, byte counts, sector counts, and platform-specific file offsets
- integer overflow in `offset + length`, `index * block_size`, alignment rounding, page spanning, or chunk boundary math
- partial writes, short reads, interrupted syscalls, async completions, or retries that advance one cursor but not the authoritative logical position
- recovery, replay, snapshot import, state sync, or pruning paths that call lower-level storage helpers with different alignment or cursor assumptions than normal writes
- deletion or compaction logic that removes the old range before proving the replacement was durably written and fsynced
- caching layers that update in-memory block maps before the device operation succeeds, or that do not invalidate cache entries after trim/discard
- platform-specific branches for memory-mapped I/O, direct I/O, fallocate, truncate, and sparse files with weaker checks than the portable path
- test helpers or benchmark storage implementations reused in production with simplified cursor semantics

Questions to answer:
1. What is the authoritative logical address: byte offset, sector id, block number, page id, chunk id, file cursor, or append index?
2. Is the same address used for validation, actual I/O, cache invalidation, metadata update, and replay?
3. Are offset and length checked together for overflow, alignment, and bounds before every operation?
4. Can partial completion, retry, or error cleanup leave cursor state ahead of durable state?
5. Do normal write, trim/discard, compaction, snapshot import, and recovery use the same address translation?
6. If data is pruned or discarded, can later recovery or proof construction read stale, zeroed, or wrong-position data?

High-signal evidence:
- The operation validates `(offset, length)` but writes, zeros, trims, or invalidates at a different cursor or derived position.
- A block/sector offset is multiplied or narrowed differently in read and write paths.
- Recovery succeeds on live cache but fails after restart because durable bytes were changed at the wrong location.

False-positive filters:
- Do not report unreachable test-only devices unless the same implementation is wired into production or migration/recovery tooling.
- Do not report harmless sparse-file behavior if all readers treat holes and explicit zeroes identically and metadata remains correct.
- Do not report a cursor mismatch when the API explicitly documents append-only semantics and callers never pass independent offsets.

Severity guidance:
- High if finalized or consensus-critical state can be corrupted, lost, or replayed differently after restart.
- Medium for node crash, persistent local data corruption, or recoverability failure.
- Low for offline tooling or debug-only corruption without protocol impact.
```
