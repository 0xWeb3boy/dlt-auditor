---
case_id: case_20181026_cda9ad8565
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2018-10-26
source_refs:
  - git:cda9ad8565eb99d4aac2bb9d46a986fcf056f479
  - "src/sigverify.rs:85"
  - "src/sigverify.rs:310"
  - "src/sigverify.rs:343"
  - "src/bin/bench-tps.rs:294"
bug_class: incomplete-signature-verification
impact_type:
  - authorization-integrity
tags:
  - infrastructure
  - transaction-processing
  - signature-verification
  - multi-signature
  - packet-verification
  - cryptographic-authorization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes incomplete packet-level signature verification for transactions with multiple signatures. In src/sigverify.rs::verify_packet, the old code performed one Ed25519 signature::verify call, while the patched code loops over sig_len, checks each signature/public-key range against packet.meta.size, and verifies each pair over the message. The evidence supports a cryptographic authorization bug at the packet verifier level, but does not establish an end-to-end exploit or whether later execution paths independently rejected such transactions.

## Observed Patch Facts

1. In `src/sigverify.rs`, the patch replaces `signature::verify(` with `for _ in 0..sig_len {`.

2. In `src/sigverify.rs`, the patch replaces `mod tests {` with `pub fn make_packet_from_transaction(tx: Transaction) -> Packet {`.

3. In `src/sigverify.rs`, the patch replaces `fn make_packet_from_transaction(tx: Transaction) -> Packet {` with `#[test]`.

4. In `src/bin/bench-tps.rs`, the patch replaces `if client.poll_for_signature(&tx.signature).is_err() {` with `if client.poll_for_signature(&tx.signatures[0]).is_err() {`.

## Project Context

The changed code sits primarily in `src`, `src/bin`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/packet.rs`, `src/window.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/window.rs`, `src/streamer.rs`. The strongest project-level identifiers around this patch are `packet`, `untrusted::Input::from`, `meta`, and `size`.

## Before/After Behavior

Before the patch, verify_packet derived the signature count and offsets but called signature::verify only once using one public-key slice and one signature slice. After the patch, verify_packet iterates once per declared signature, rejects malformed per-signature or per-pubkey bounds, and verifies each Ed25519 signature/public-key pair against the same transaction message. Other changes such as make_packet_from_transaction test helper extraction and bench-tps use of tx.signatures[0] appear supportive or compatibility-related, not the root cause.

# Root Cause

The packet verification logic handled signature verification as a single-signature check even though the transaction layout could declare multiple signatures. The missing check was iteration over the declared signature count during packet-level verification.

## Walkthrough

1. A serialized transaction packet includes metadata size and offsets for signatures, message data, and public keys.

2. verify_packet obtains sig_len, sig_start, msg_start, and pubkey_start from get_packet_offsets.

3. The old implementation checked that msg_start was within packet.meta.size, then verified only one signature/public-key pair.

4. For packets declaring multiple signatures, the provided evidence shows no loop in verify_packet to verify the remaining declared signatures.

5. The patched implementation makes the signature and public-key offsets advance through a loop over sig_len.

6. For each declared signature, it computes the current slice bounds, fails closed if the bounds are outside the packet size, and verifies that signature against the transaction message.

7. The bench-tps change from tx.signature to tx.signatures[0] is consistent with API adaptation to multiple signatures, but is not itself evidence of the vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/sigverify.rs | 71 | transaction packet signature verification; enforces per-signature Ed25519 checks and packet bounds before accepting a packet as verified |
| src/sigverify.rs | 304 | test helper extraction for constructing serialized transaction packets used by signature verification tests |
| src/sigverify.rs | 337 | regression test coverage for packet offset layout used by multi-signature verification |
| src/bin/bench-tps.rs | 294 | caller adaptation from single transaction signature field to signatures array when polling transaction confirmation |

## Code Snippets

## Snippet 1

Context: `src/sigverify.rs:85` (changes signature or replay validation logic)

Before
```rust
let msg_end = packet.meta.size;
    signature::verify(
        &signature::ED25519,
        untrusted::Input::from(&packet.data[pubkey_start..pubkey_end]),
        untrusted::Input::from(&packet.data[msg_start..msg_end]),
        untrusted::Input::from(&packet.data[sig_start..sig_end]),
    ).is_ok() as u8
```
After
```rust
let msg_end = packet.meta.size;
    for _ in 0..sig_len {
        let pubkey_end = pubkey_start as usize + size_of::<Pubkey>();
        let sig_end = sig_start as usize + size_of::<Signature>();

        if pubkey_end >= packet.meta.size || sig_end >= packet.meta.size {
            return 0;
```

## Snippet 2

Context: `src/sigverify.rs:310` (changes signature or replay validation logic)

Before
```rust
}

#[cfg(test)]
mod tests {
    use bincode::serialize;
    use packet::{Packet, SharedPackets};
    use sigverify;
    use system_transaction::{memfind, test_tx};
```
After
```rust
}

#[cfg(test)]
pub fn make_packet_from_transaction(tx: Transaction) -> Packet {
    use bincode::serialize;

    let tx_bytes = serialize(&tx).unwrap();
    let mut packet = Packet::default();
```

## Snippet 3

Context: `src/sigverify.rs:343` (changes persisted or aggregate state handling)

Before
```rust
}

    fn make_packet_from_transaction(tx: Transaction) -> Packet {
        let tx_bytes = serialize(&tx).unwrap();
        let mut packet = Packet::default();
        packet.meta.size = tx_bytes.len();
        packet.data[..packet.meta.size].copy_from_slice(&tx_bytes);
        return packet;
```
After
```rust
}

    #[test]
    fn test_get_packet_offsets() {
        let tx = test_tx();
        let packet = sigverify::make_packet_from_transaction(tx);
        let (sig_len, sig_start, msg_start_offset, pubkey_offset) =
            sigverify::get_packet_offsets(&packet, 0);
```

## Snippet 4

Context: `src/bin/bench-tps.rs:294` (changes signature or replay validation logic)

Before
```rust
const MAX_SPENDS_PER_TX: usize = 5;
fn verify_transfer(client: &mut ThinClient, tx: &Transaction) -> bool {
    if client.poll_for_signature(&tx.signature).is_err() {
        println!("no signature");
        return false;
```
After
```rust
const MAX_SPENDS_PER_TX: usize = 5;
fn verify_transfer(client: &mut ThinClient, tx: &Transaction) -> bool {
    if client.poll_for_signature(&tx.signatures[0]).is_err() {
        println!("no signature");
        return false;
```

# Fix Pattern

Replace a single cryptographic authorization check with cardinality-aware verification over all declared authorization entries, with bounds checks before slicing untrusted packet data.

## How It Was Fixed

src/sigverify.rs::verify_packet was changed from one signature::verify call to a loop over sig_len. Each loop iteration computes the current public-key and signature slice ends, rejects malformed packet bounds, and verifies the corresponding Ed25519 signature over the transaction message. Test helper code was exposed for constructing packets in tests, and related callers were updated for the signatures array representation.

# Why It Matters

1. Prevents packet-level verification from treating a multi-signature transaction as verified after checking only one signature.

2. Preserves the authorization meaning of the transaction signature count.

3. Adds per-entry bounds checks before reading signature and public-key slices from packet data.

4. Security impact beyond packet-level verification is not proven by the supplied evidence.

# Evidence Notes

Primary evidence is src/sigverify.rs::verify_packet, where the implementation changes from one signature::verify call to for _ in 0..sig_len with per-signature bounds checks. The commit message states that multiple instructions in a transaction may need multiple signatures. The evidence does not prove fund theft, consensus failure, or whether downstream bank execution independently rechecked signatures, so the verdict is likely rather than confirmed. Protocol security invariant: When transaction packet verification treats a packet as signature-verified, it must verify each declared signature/public-key pair over the transaction message, not just the first pair. Verification notes: The patch evidence does not prove a complete end-to-end exploit or fund theft scenario. The patch does not show whether downstream bank execution independently rechecked all required signatures. The bench-tps change is caller compatibility, not itself proof of a security flaw. The exact transaction format and sig_len derivation are inferred only from provided sigverify context. Supported: old verify_packet performed one signature verification despite deriving sig_len. Supported: patched verify_packet loops over sig_len and verifies each signature/public-key pair. Supported: helper and test changes are support code, not the root cause. Not established: complete exploitability or downstream acceptance of incompletely verified packets. Not established: state corruption; that draft classification should be removed. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incomplete-signature-verification`
Final impact type: `authorization-integrity`
Final tags: `infrastructure, transaction-processing, signature-verification, multi-signature, packet-verification, cryptographic-authorization`

The supplied patch evidence supports retaining this as security hardening: packet-level transaction verification changed from verifying a single Ed25519 signature to iterating over the declared signature count with per-signature bounds checks. That clearly tightens authorization-sensitive behavior for multi-signature transactions. However, the evidence does not prove that incompletely verified packets could be executed or cause state corruption, so the original security-fix and state-corruption framing is too strong.

## Security Evidence

1. src/sigverify.rs changed verify_packet from one signature::verify call to a loop over sig_len.
2. The patched code verifies each signature/public-key pair against the transaction message.
3. The patched code adds per-entry packet size bounds checks before using signature and public-key slices.
4. The commit message explicitly references transactions needing multiple signatures.

## Missing Evidence

1. No evidence shows downstream bank execution accepted packets based only on this packet-level verifier.
2. No concrete exploit path, unauthorized transfer, or consensus/state corruption outcome is shown.
3. No full before/after test demonstrates that a transaction with missing secondary signatures was previously accepted end to end.
4. The bench-tps change is API compatibility evidence, not vulnerability evidence.

## Claim Boundaries

1. Supported: packet-level verification previously checked only one signature despite handling a signature count.
2. Supported: the patch hardens multi-signature transaction verification in a cryptographic authorization path.
3. Not supported: classifying the issue as state corruption from the supplied evidence alone.
4. Not supported: claiming confirmed exploitable fund theft, consensus failure, or end-to-end authorization bypass.
