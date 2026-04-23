# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-05-15-go-ethereum-core-logic-5c1a7b965`
- Bug family: `authz_and_role_gates`
- Bug class: `p2p-sync-validation-bypass`

## Code Shape Summary

- A sync verifier accepts a remote sample because one field matches, but it forgets to verify the predecessor relationship that ties the sample back to the locally tracked chain segment.

## Search Motifs

- Motif 1: Pending check removed immediately after matching a block hash.
- Motif 2: Queue membership or parent-link validation added after the initial identity check.
- Motif 3: Regression tests create fake or disconnected chain segments to prove the bypass.

## Typical Asymmetry

- The defender tracks both object identity and graph context, but the vulnerable path validates only identity while the attacker controls graph context.

## Patch Pattern

- Require a local predecessor or queue-membership check before clearing remote-validation state.

## False Match Warnings

- Do not match on pure cache-deduplication code that never advances trust in remote chain state.
- Do not match if another earlier verifier already proved parent linkage for the same sampled object.
