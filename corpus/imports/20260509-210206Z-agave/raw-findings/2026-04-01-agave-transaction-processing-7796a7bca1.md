---
case_id: case_20260401_7796a7bca1
project: agave
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-04-01
source_refs:
  - git:7796a7bca165ad857ad761d5424050412753d8ff
  - "perf/src/sigverify.rs:475"
  - "perf/src/sigverify.rs:443"
  - "perf/src/sigverify.rs:324"
  - "perf/src/sigverify.rs:53"
bug_class: malformed-transaction-rejection
impact_type:
  - input-validation-hardening
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - signature-verification
  - transaction-sanitization
  - malformed-input-rejection
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes `perf/src/sigverify.rs` so `verify_packet` obtains packet data and attempts `SanitizedTransactionView::try_new_sanitized(data, true)`, rejecting packets when data is unavailable or sanitization fails. Tests were updated to assert rejection of an unsupported message version and an invalid pubkey/account length through `verify_packet`. This may be security-relevant hardening in a signature verification path, but the supplied evidence does not establish that the previous behavior accepted malformed packets, enabled forgery, replay, consensus divergence, or any exploitable state transition.

## Observed Patch Facts

1. In `perf/src/sigverify.rs`, the patch replaces `let packet = BytesPacket::from_bytes(None, Bytes::from(data.clone()));` with `const MESSAGE_OFFSET: usize = 1 + core::mem::size_of::<Signature>();`.

2. In `perf/src/sigverify.rs`, the patch replaces `let packet = BytesPacket::from_bytes(None, Bytes::from(data.clone()));` with `const PUBKEY_OFFSET: usize =`.

3. In `perf/src/sigverify.rs`, the patch replaces `#[test]` with `fn packet_from_num_sigs(required_num_sigs: u8, actual_num_sigs: usize) -> BytesPacket {`.

4. In `perf/src/sigverify.rs`, the patch replaces `let packet_offsets = get_packet_offsets(packet, 0, reject_non_vote);` with `let Some(data) = packet.data(..) else {`.

## Project Context

The changed code sits primarily in `perf/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `perf/src/packet.rs`, `perf/src/data_budget.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `perf/src/packet.rs`, `perf/src/recycler.rs`. The strongest project-level identifiers around this patch are `packet`, `BytesPacket::from_bytes`, `Bytes::from`, and `data`.

## Before/After Behavior

Before the change, `verify_packet` relied on manual packet offset extraction such as signature, pubkey, and message offsets. After the change, it first reads packet bytes and constructs a `SanitizedTransactionView`, returning `false` if packet data is missing or sanitization fails. Related tests now mutate serialized transaction bytes at fixed offsets and verify that malformed packets are rejected by `verify_packet`.

# Root Cause

The evidence supports only that the old sigverify path used manual layout/offset parsing before the new sanitized transaction view gate. It does not prove that this caused a vulnerability or that invalid transactions previously passed verification.

## Walkthrough

1. `verify_packet` is part of the packet signature verification path in `perf/src/sigverify.rs`.

2. The old code derived packet offsets with `get_packet_offsets` and used those offsets in verification logic.

3. The new code calls `packet.data(..)` and rejects the packet if no data slice is available.

4. The new code attempts `SanitizedTransactionView::try_new_sanitized(data, true)` and rejects the packet if sanitization fails.

5. Updated tests cover rejection of an unsupported message version through `verify_packet`.

6. Updated tests cover rejection of an invalid pubkey/account length through `verify_packet`.

7. The evidence shows stricter or more canonical malformed-input rejection, but not a demonstrated vulnerability fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| perf/src/sigverify.rs | 49 | main packet verification path now constructs a sanitized transaction view from packet data and rejects failures |
| perf/src/sigverify.rs | 442 | test coverage for invalid pubkey/account length rejection through verify_packet |
| perf/src/sigverify.rs | 474 | test coverage for unsupported message version rejection through verify_packet |
| perf/src/packet.rs | 1 | incoming network packet abstraction supplying data to sigverify |

## Code Snippets

## Snippet 1

Context: `perf/src/sigverify.rs:475` (changes signature or replay validation logic)

Before
```rust
let tx = test_tx();
        let mut data = bincode::serialize(&tx).unwrap();
        let packet = BytesPacket::from_bytes(None, Bytes::from(data.clone()));

        let res = sigverify::do_get_packet_offsets(packet.as_ref(), 0);

        // set message version to 1
        data[res.unwrap().msg_start as usize] = MESSAGE_VERSION_PREFIX + 1;
```
After
```rust
let tx = test_tx();
        let mut data = bincode::serialize(&tx).unwrap();

        // set message version to 1
        const MESSAGE_OFFSET: usize = 1 + core::mem::size_of::<Signature>();
        data[MESSAGE_OFFSET] = MESSAGE_VERSION_PREFIX + 1;

        let mut packet = BytesPacket::from_bytes(None, Bytes::from(data));
```

## Snippet 2

Context: `perf/src/sigverify.rs:443` (changes signature or replay validation logic)

Before
```rust
let tx = test_tx();
        let mut data = bincode::serialize(&tx).unwrap();
        let packet = BytesPacket::from_bytes(None, Bytes::from(data.clone()));

        let offsets = sigverify::do_get_packet_offsets(packet.as_ref(), 0).unwrap();

        // make pubkey len huge
        data[offsets.pubkey_start as usize - 1] = 0x7f;
```
After
```rust
let tx = test_tx();
        let mut data = bincode::serialize(&tx).unwrap();

        // make pubkey len huge
        const PUBKEY_OFFSET: usize =
            1 + core::mem::size_of::<Signature>() + core::mem::size_of::<MessageHeader>();
        data[PUBKEY_OFFSET] = 0x7f;
```

## Snippet 3

Context: `perf/src/sigverify.rs:324` (changes persisted or aggregate state handling)

Before
```rust
}

    #[test]
    fn test_layout() {
        let tx = test_tx();
        let tx_bytes = serialize(&tx).unwrap();
        let packet = serialize(&tx).unwrap();
        assert_matches!(memfind(&packet, &tx_bytes), Some(0));
```
After
```rust
}

    fn packet_from_num_sigs(required_num_sigs: u8, actual_num_sigs: usize) -> BytesPacket {
        let message = Message {
```

## Snippet 4

Context: `perf/src/sigverify.rs:53` (changes signature or replay validation logic)

Before
```rust
}

    let packet_offsets = get_packet_offsets(packet, 0, reject_non_vote);
    let mut sig_start = packet_offsets.sig_start as usize;
    let mut pubkey_start = packet_offsets.pubkey_start as usize;
    let msg_start = packet_offsets.msg_start as usize;

    if packet_offsets.sig_len == 0 {
```
After
```rust
}

    let Some(data) = packet.data(..) else {
        return false;
    };

    let (is_simple_vote_tx, verified) = {
        let Ok(view) = SanitizedTransactionView::try_new_sanitized(data, true) else {
```

# Fix Pattern

Replace ad hoc transaction layout parsing in sigverify with the canonical sanitized transaction view before relying on transaction structure.

## How It Was Fixed

`verify_packet` was changed to read packet bytes and require successful construction of `SanitizedTransactionView`. Malformed packet cases in tests were adjusted to validate rejection at the `verify_packet` entry point.

# Why It Matters

1. Keeps sigverify parsing aligned with canonical transaction sanitization.

2. Reduces reliance on manually derived byte offsets in a sensitive path.

3. Rejects malformed unsupported-version and invalid-length test inputs.

4. Does not prove prior exploitability from the provided evidence.

# Evidence Notes

Grounded evidence is limited to `perf/src/sigverify.rs`: the main verification path now uses `SanitizedTransactionView::try_new_sanitized(data, true)`, and tests assert rejection for unsupported message versions and invalid pubkey/account lengths. The evidence does not show a prior successful bypass, accepted malformed transaction, replay condition, forgery, consensus impact, or reachable state-changing behavior. Protocol security invariant: Transaction packet bytes used by sigverify should be parsed consistently with the canonical sanitized transaction format before verification logic relies on their structure. Verification notes: Does not prove malformed packets previously passed signature verification successfully. Does not prove transaction forgery, replay, or consensus divergence. Does not show a state-changing execution path reached after failed sanitization. Commit also contains test cleanup and unused-function removal, so not every touched line is security-relevant. No exploitability claim is supported beyond stricter malformed packet rejection in sigverify. Security impact is not established by the provided diff evidence. Classified as unclear rather than likely security-hardening because exploitability and prior acceptance are unproven. Excluded from the security corpus under the provided skepticism rules. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `malformed-transaction-rejection`
Final impact type: `input-validation-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, signature-verification, transaction-sanitization, malformed-input-rejection`

The evidence supports retaining this as security hardening, not as a proven security fix. The patch changes a signature verification path for incoming packet data to require successful `SanitizedTransactionView::try_new_sanitized(data, true)` and to reject packets when packet data or sanitization is unavailable. Updated tests assert that unsupported message versions and invalid pubkey lengths are rejected by `verify_packet`. However, the supplied evidence does not prove prior exploitability, replay, forgery, consensus divergence, or that malformed packets previously passed signature verification into a state-changing path.

## Security Evidence

1. `verify_packet` is in the packet signature verification path and now rejects missing packet data.
2. `verify_packet` now rejects packets that fail canonical sanitized transaction view construction.
3. Tests assert `verify_packet` rejects unsupported message versions.
4. Tests assert `verify_packet` rejects invalid pubkey/account length encodings.
5. The changed inputs are serialized transaction packets from a network packet abstraction.

## Missing Evidence

1. No before/after proof that malformed packets previously passed verification.
2. No exploit, bypass, replay, forgery, or consensus-divergence demonstration.
3. No evidence that rejected packets previously reached transaction execution or state mutation.
4. No security advisory, vulnerability note, or explicit security rationale in the commit metadata.

## Claim Boundaries

1. Validate only as hardening of transaction packet sanitization in sigverify.
2. Do not claim a concrete signature bypass or replay vulnerability.
3. Do not claim consensus impact from the supplied evidence.
4. Do not classify as a security-fix without proof of prior vulnerable acceptance.
