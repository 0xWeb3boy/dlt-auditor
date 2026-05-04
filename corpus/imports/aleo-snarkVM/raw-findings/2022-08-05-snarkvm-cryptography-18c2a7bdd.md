---
case_id: case_20220805_18c2a7bdd
project: snarkvm
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2022-08-05
source_refs:
  - git:18c2a7bddf8f2f971cdb2bef43d01030b470c14c
  - "vm/compiler/src/ledger/store/transaction/get.rs:164"
  - "vm/compiler/src/ledger/store/transaction/get.rs:182"
  - "vm/compiler/src/ledger/store/transaction/contains.rs:65"
  - "vm/compiler/src/ledger/store/transaction/contains.rs:85"
bug_class: fail-open-ledger-lookup
impact_type:
  - incorrect-record-state-classification
tags:
  - blockchain-core
  - ledger-store
  - record-scanner
  - serial-number
  - fail-closed-error-handling
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes fail-open handling in the output-record scanner's unspent classification path. Before the change, `OutputRecordsFilter::AllUnspent` treated any result other than `Ok(true)` from `contains_serial_number` as absence, so `Err(_)` caused the scanner to return the commitment as unspent. After the change, only `Ok(false)` returns the commitment; lookup errors are logged and excluded.

## Observed Patch Facts

1. In `vm/compiler/src/ledger/store/transaction/get.rs`, the patch replaces `_ => return None,` with `Ok(false) => return None,`.

2. In `vm/compiler/src/ledger/store/transaction/get.rs`, the patch replaces `_ => *commitment,` with `Ok(false) => *commitment,`.

3. In `vm/compiler/src/ledger/store/transaction/contains.rs`, the patch replaces `/// Returns 'true' if the given serial number exists.` with `/// Returns 'true' if the given origin exists.`.

4. In `vm/compiler/src/ledger/store/transaction/contains.rs`, the patch replaces `/// Returns 'true' if the given origin exists.` with `pub fn contains_nonce(&self, nonce: &Group<N>) -> Result<bool> {`.

## Project Context

The changed code sits primarily in `vm/compiler/src/ledger/store/transaction`, `vm/compiler/src/ledger/store`, which anchors the finding in the `cryptography` area of the project. Historical context from `vm/compiler/src/ledger/store/transaction/mod.rs`, `vm/compiler/src/ledger/store/transaction/iterators.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vm/compiler/src/ledger/store/block/mod.rs`, `vm/compiler/src/ledger/store/transaction/mod.rs`. The strongest project-level identifiers around this patch are `serial_number`, `None`, `serial`, and `number`.

## Before/After Behavior

Before the patch, `AllUnspent` matched `Ok(true) => return None` and `_ => *commitment`, collapsing `Ok(false)` and `Err(_)` into the same unspent result. After the patch, it explicitly handles `Ok(true)`, `Ok(false)`, and `Err(e)`, returning a commitment only on `Ok(false)`. The `AllSpent` path was also made explicit, but its prior wildcard arm already excluded lookup errors.

# Root Cause

The scanner used wildcard match arms around `contains_serial_number`, causing lookup errors to be handled like successful negative lookups in the unspent-record path.

## Walkthrough

1. The scanner iterates transaction output records and derives a serial number from the private key and record commitment.

2. It calls `self.contains_serial_number(&serial_number)` to determine whether the record appears spent.

3. In the pre-fix `AllUnspent` branch, `Ok(true)` excluded the record and `_` returned the commitment.

4. That wildcard included both `Ok(false)` and `Err(_)`, so lookup failure was treated as serial-number absence.

5. The patch changes the match so only `Ok(false)` reports the record as unspent.

6. On lookup error, the scanner now logs the failed serial-number check and returns `None`.

7. The provided evidence does not show consensus validation, transaction acceptance, or proof verification changes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vm/compiler/src/ledger/store/transaction/get.rs | 164 | Filters output records for `AllSpent` by deriving a serial number and checking whether it exists in the ledger; errors are now handled explicitly and excluded. |
| vm/compiler/src/ledger/store/transaction/get.rs | 182 | Filters output records for `AllUnspent`; the fix prevents `contains_serial_number` errors from being treated as `Ok(false)` unspent status. |
| vm/compiler/src/ledger/store/transaction/contains.rs | 65 | Ledger-store containment API area for serial-number/origin lookup used by transaction record scanning. |

## Code Snippets

## Snippet 1

Context: `vm/compiler/src/ledger/store/transaction/get.rs:164` (changes a sensitive control or state-update path)

Before
```rust
Ok(serial_number) => match self.contains_serial_number(&serial_number) {
                                Ok(true) => *commitment,
                                _ => return None,
                            },
                            Err(e) => {
                                warn!("Failed to derive serial number for output record: {e}");
                                return None;
                            }
```
After
```rust
Ok(serial_number) => match self.contains_serial_number(&serial_number) {
                                Ok(true) => *commitment,
                                Ok(false) => return None,
                                Err(e) => {
                                    warn!("Failed to check serial number '{serial_number}' in the ledger: {e}");
                                    return None;
                                }
                            },
```

## Snippet 2

Context: `vm/compiler/src/ledger/store/transaction/get.rs:182` (changes a sensitive control or state-update path)

Before
```rust
Ok(serial_number) => match self.contains_serial_number(&serial_number) {
                                Ok(true) => return None,
                                _ => *commitment,
                            },
                            Err(e) => {
                                warn!("Failed to derive serial number for output record: {e}");
                                return None;
                            }
```
After
```rust
Ok(serial_number) => match self.contains_serial_number(&serial_number) {
                                Ok(true) => return None,
                                Ok(false) => *commitment,
                                Err(e) => {
                                    warn!("Failed to check serial number '{serial_number}' in the ledger: {e}");
                                    return None;
                                }
                            },
```

## Snippet 3

Context: `vm/compiler/src/ledger/store/transaction/contains.rs:65` (changes a sensitive control or state-update path)

Before
```rust
}

    /// Returns `true` if the given serial number exists.
    pub fn contains_serial_number(&self, serial_number: &Field<N>) -> Result<bool> {
```
After
```rust
}

    /// Returns `true` if the given origin exists.
    pub fn contains_origin(&self, origin: &Origin<N>) -> Result<bool> {
        self.origins.contains_key(origin)
    }

    // /// Returns `true` if the given tag exists.
```

## Snippet 4

Context: `vm/compiler/src/ledger/store/transaction/contains.rs:85` (changes a sensitive control or state-update path)

Before
```rust
}

    /// Returns `true` if the given origin exists.
    pub fn contains_origin(&self, origin: &Origin<N>) -> Result<bool> {
        self.origins.contains_key(origin)
    }

    /// Returns `true` if the given nonce exists.
```
After
```rust
}

    /// Returns `true` if the given nonce exists.
    pub fn contains_nonce(&self, nonce: &Group<N>) -> Result<bool> {
```

# Fix Pattern

Replace wildcard error handling in security-sensitive classification logic with explicit success and error arms, and fail closed on lookup errors.

## How It Was Fixed

In `vm/compiler/src/ledger/store/transaction/get.rs`, the patch replaced `_` match arms around `contains_serial_number` with explicit `Ok(true)`, `Ok(false)`, and `Err(e)` handling. The unspent path now returns a commitment only on a successful negative lookup and excludes records on lookup error. The spent path now logs lookup errors explicitly while still excluding the record.

# Why It Matters

1. Lookup failure is not the same as ledger absence.

2. The pre-fix scanner could report a record as unspent without successfully checking its serial number.

3. The fix limits unspent classification to successful ledger queries.

4. The evidence supports a scanner classification flaw, not a proven double-spend or consensus flaw.

# Evidence Notes

The strongest evidence is in `vm/compiler/src/ledger/store/transaction/get.rs`: `AllUnspent` changed from `Ok(true) => return None, _ => *commitment` to separate `Ok(true)`, `Ok(false)`, and `Err(e)` arms. The commit subject says "Fixes vulnerability in record scanner," which supports security relevance, but the supplied code does not prove attacker control over lookup errors or impact beyond record scanning. The `contains.rs` changes appear related to containment API organization and are not established as the root cause. Protocol security invariant: A ledger record scanner must distinguish a successful negative serial-number lookup from a lookup failure. A record should only be classified as unspent when serial-number derivation succeeds and the ledger lookup successfully returns absence. Verification notes: The patch does not show transaction validation or consensus state-transition logic being changed. The patch does not prove that an attacker can force `contains_serial_number` to return an error. The patch does not prove double-spend acceptance; it only shows fail-open unspent classification in the scanner path. The `contains.rs` changes appear related to lookup API organization and do not independently prove a security fix. Confirmed fail-open behavior is directly visible in the `AllUnspent` before/after match arms. Confirmed the `AllSpent` behavior was clarified but not materially fail-open in the provided evidence. No supplied tests demonstrate exploitability or regression coverage. No supplied evidence shows transaction validation or consensus behavior was changed. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `fail-open-ledger-lookup`
Final impact type: `incorrect-record-state-classification`
Final tags: `blockchain-core, ledger-store, record-scanner, serial-number, fail-closed-error-handling`

The supplied patch clearly changes record-scanner behavior from treating a serial-number lookup error like a successful absence check to failing closed and excluding the record. That is security-relevant hardening in a blockchain ledger scanner, and the commit subject explicitly calls it a vulnerability. However, the evidence does not prove consensus impact, double-spend acceptance, request replay, or attacker-controlled lookup failure, so the original security-fix and replay/signature framing is too strong.

## Security Evidence

1. AllUnspent previously used `_ => *commitment`, so `Err(_)` from `contains_serial_number` could classify a record as unspent.
2. The fix explicitly separates `Ok(false)` from `Err(e)` and returns `None` on lookup errors.
3. The changed logic involves serial numbers and spent/unspent record classification in the ledger store.
4. The commit subject states "Fixes vulnerability in record scanner."

## Missing Evidence

1. No evidence shows transaction acceptance, consensus validation, or proof verification was affected.
2. No evidence shows an attacker can cause `contains_serial_number` to return an error.
3. No tests or exploit scenario demonstrate double-spend, replay, or forgery impact.
4. The `contains.rs` evidence appears to be API reorganization and does not independently establish the vulnerability.

## Claim Boundaries

1. Supported claim: lookup errors in the unspent scanner are now handled fail-closed.
2. Supported claim: this is security-relevant hardening of record classification behavior.
3. Unsupported claim: the patch fixes a proven replay or signature-validation vulnerability.
4. Unsupported claim: the bug allowed consensus-level double spending or forged requests.
