---
case_id: case_20260408_9021f430fb
project: agave
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: medium
date: 2026-04-08
source_refs:
  - git:9021f430fb902809566b82b2b162928a104bb8f9
  - "core/benches/sigverify_stage.rs:215"
  - "core/src/sigverify.rs:57"
  - "core/src/sigverify_stage.rs:328"
  - "core/src/sigverify_stage.rs:270"
bug_class: resource-exhaustion-hardening
impact_type:
  - denial-of-service
confidence: medium
tags:
  - blockchain-core
  - validator
  - sigverify
  - capacity-limit
  - backpressure
  - resource-exhaustion
  - denial-of-service-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds capacity-aware in-flight accounting to the sigverify packet pipeline and drops newly received packets when verifier capacity is already reached. This is plausibly security-relevant hardening against overload, but the provided evidence does not prove a vulnerability, exploitability, validator crash, consensus failure, invalid signature acceptance, or replay bypass.

## Observed Patch Facts

1. In `core/benches/sigverify_stage.rs`, the patch replaces `packet_s.send(batch).unwrap();` with `let start = completed_for_bench.load(Ordering::Relaxed);`.

2. In `core/src/sigverify.rs`, the patch replaces `type SendType = BankingPacketBatch;` with `fn verify_and_send_packets(`.

3. In `core/src/sigverify_stage.rs`, the patch replaces `if let Err(e) =` with `let in_flight_count = Arc::new(AtomicUsize::new(0));`.

4. In `core/src/sigverify_stage.rs`, the patch replaces `stats` with `stats.batches_hist.increment(batches_len as u64).unwrap();`.

## Project Context

The changed code sits primarily in `core/benches`, `core/src`, which anchors the finding in the `consensus` area of the project. Historical context from `core/src/stats_reporter_service.rs`, `core/src/shred_fetch_stage.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/shred_fetch_stage.rs`, `core/src/window_service.rs`. The strongest project-level identifiers around this patch are `stats`, `Self::verifier`, `unwrap`, and `batch`.

## Before/After Behavior

Before the patch, the shown sigverify service loop did not pass a shared in_flight_count into Self::verifier, and the shown verifier path did not immediately drop received packets based on existing in-flight verification/send capacity. After the patch, verifier_service creates an Arc<AtomicUsize> in_flight_count, passes it into verifier, checks it against verifier.capacity(), increments total_dropped_on_capacity when over capacity, and skips further processing for those packets. TransactionSigVerifier is refactored from send_packets to verify_and_send_packets so verification/send work can be tied to valid-packet and in-flight accounting. Benchmark changes adapt to the asynchronous completion model and are not vulnerability evidence.

# Root Cause

The grounded root cause is missing or incomplete in-flight capacity accounting at the sigverify receive/verify/send boundary. The commit body also mentions an in_flight leak, but the provided snippets do not show the leak mechanics or demonstrate a security impact.

## Walkthrough

1. Packet batches are received in core/src/sigverify_stage.rs using streamer::recv_packet_batches with SOFT_RECEIVE_CAP set to 5000.

2. The patched service loop creates a shared Arc<AtomicUsize> named in_flight_count.

3. Each verifier call now receives that in_flight_count.

4. The verifier checks in_flight_count.load(Ordering::Relaxed) against verifier.capacity().

5. If capacity is already reached, the code increments stats.total_dropped_on_capacity and marks the received packets for immediate drop.

6. Receive metrics are still updated even when packets are dropped immediately.

7. When not over capacity, processing continues through the normal deduplication, verification, and send path via verify_and_send_packets.

8. The benchmark update reflects changed asynchronous completion accounting and does not independently support a security finding.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/sigverify_stage.rs | 248 | Receives packet batches, checks verifier capacity via in_flight_count, and drops over-capacity packets before further processing. |
| core/src/sigverify_stage.rs | 314 | Creates and carries the shared in_flight_count through the long-running sigverify service loop. |
| core/src/sigverify.rs | 57 | Moves TransactionSigVerifier behavior into verify_and_send_packets with capacity/in-flight accounting around verified packet forwarding to banking/forward stages. |
| core/benches/sigverify_stage.rs | 194 | Benchmark adaptation for the changed asynchronous verify-and-send behavior and completion accounting. |

## Code Snippets

## Snippet 1

Context: `core/benches/sigverify_stage.rs:215` (changes the branch that decides whether execution stops or continues)

Before
```rust
);

        let mut sent_len = 0;
        for batch in batches.into_iter() {
            sent_len += batch.len();
            packet_s.send(batch).unwrap();
        }
        let mut received = 0;
```
After
```rust
);

        let start = completed_for_bench.load(Ordering::Relaxed);
        let mut sent_len = 0;
        for batch in batches.into_iter() {
            sent_len += batch.len();
            packet_s_for_bench.send(batch).unwrap();
        }
```

## Snippet 2

Context: `core/src/sigverify.rs:57` (changes a sensitive control or state-update path)

Before
```rust
impl SigVerifier for TransactionSigVerifier {
    type SendType = BankingPacketBatch;

    fn send_packets(
        &mut self,
        packet_batches: Vec<PacketBatch>,
    ) -> Result<(), SigVerifyServiceError<Self::SendType>> {
```
After
```rust
impl SigVerifier for TransactionSigVerifier {
    fn verify_and_send_packets(
        &mut self,
        batches: Vec<PacketBatch>,
        valid_packets: usize,
        in_flight_count: Arc<AtomicUsize>,
        total_valid_packets: Arc<AtomicUsize>,
```

## Snippet 3

Context: `core/src/sigverify_stage.rs:328` (changes a sensitive control or state-update path)

Before
```rust
let mut rng = rand::rng();
                let mut deduper = Deduper::<2, [u8]>::new(&mut rng, DEDUPER_NUM_BITS);
                loop {
                    if deduper.maybe_reset(&mut rng, DEDUPER_FALSE_POSITIVE_RATE, MAX_DEDUPER_AGE) {
                        stats.num_deduper_saturations += 1;
                    }
                    if let Err(e) =
                        Self::verifier(&deduper, &packet_receiver, &mut verifier, &mut stats)
```
After
```rust
let mut rng = rand::rng();
                let mut deduper = Deduper::<2, [u8]>::new(&mut rng, DEDUPER_NUM_BITS);
                let in_flight_count = Arc::new(AtomicUsize::new(0));
                loop {
                    if deduper.maybe_reset(&mut rng, DEDUPER_FALSE_POSITIVE_RATE, MAX_DEDUPER_AGE) {
                        stats.num_deduper_saturations += 1;
                    }
                    if let Err(e) = Self::verifier(
```

## Snippet 4

Context: `core/src/sigverify_stage.rs:270` (changes the branch that decides whether execution stops or continues)

Before
```rust
.increment(recv_duration.as_micros() as u64)
            .unwrap();
        stats
            .verify_batches_pp_us_hist
            .increment(verify_time.as_us() / (num_packets as u64))
            .unwrap();
        stats
            .dedup_packets_pp_us_hist
```
After
```rust
.increment(recv_duration.as_micros() as u64)
            .unwrap();
        stats.batches_hist.increment(batches_len as u64).unwrap();
        stats.packets_hist.increment(num_packets as u64).unwrap();
        stats.total_batches += batches_len;
        stats.total_packets += num_packets;

        if !should_drop {
```

# Fix Pattern

Add explicit capacity checks and shared in-flight accounting around an asynchronous packet verification/send pipeline, with metrics for packets dropped due to capacity.

## How It Was Fixed

The patch introduces a shared in_flight_count in the sigverify service loop, passes it into the verifier path, checks it against SigVerifier::capacity(), drops received packets when already over capacity, records dropped_on_capacity statistics, and refactors TransactionSigVerifier into verify_and_send_packets so send behavior and accounting are handled together.

# Why It Matters

1. Bounds sigverify work under load in the shown pipeline.

2. Improves operational backpressure before packets continue to later stages.

3. Adds visibility into capacity-based packet drops.

4. Does not establish invalid signature acceptance, replay bypass, or consensus corruption.

5. Does not prove an externally exploitable denial of service from the provided evidence.

# Evidence Notes

Strong evidence supports a capacity/backpressure change in core/src/sigverify_stage.rs and an interface refactor in core/src/sigverify.rs. The commit body mentions capacity, dropped_on_capacity, and an in_flight leak. However, the supplied snippets do not show an exploit path, memory exhaustion, crash, consensus divergence, or authorization failure. Claims of a confirmed security fix would be unsupported. Protocol security invariant: The sigverify pipeline should keep packet verification and forwarding work bounded under load, but the provided evidence does not establish that the pre-patch behavior violated a security invariant or enabled an exploitable denial of service. Verification notes: No evidence that invalid signatures were previously accepted. No evidence that replayed transactions bypassed deduplication or replay protection. No proof of remote exploitability or validator crash from the provided patch alone. No demonstrated consensus divergence or state corruption. Benchmark changes are not themselves security-relevant. No evidence of invalid signatures being accepted before the patch. No evidence of replay protection being bypassed before the patch. No evidence of validator crash or consensus failure from the pre-patch behavior. No test or reproduction demonstrating security impact is provided. Classify as unclear security relevance rather than confirmed security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-exhaustion-hardening`
Final impact type: `denial-of-service`
Final confidence: `medium`
Final tags: `blockchain-core, validator, sigverify, capacity-limit, backpressure, resource-exhaustion, denial-of-service-hardening`

The evidence supports retaining this as security hardening, not as a confirmed signature-validation or replay fix. The patch adds explicit in-flight capacity accounting and immediate packet drops when the sigverify pipeline is already at capacity, which tightens resource bounds on a security-sensitive validator packet verification path. However, the supplied evidence does not prove exploitability, invalid signature acceptance, replay bypass, validator crash, or consensus divergence.

## Security Evidence

1. Sigverify receives packet batches and now checks in_flight_count against verifier.capacity().
2. Over-capacity packets are immediately dropped and counted in total_dropped_on_capacity.
3. The service loop creates shared in_flight_count state and passes it through the verifier path.
4. The refactor ties verification, forwarding, valid-packet accounting, and in-flight accounting together in the sigverify pipeline.
5. Commit metadata explicitly mentions dropping over capacity and fixing an in_flight leak.

## Missing Evidence

1. No proof that the prior behavior allowed remote denial of service.
2. No reproduction showing validator crash, memory exhaustion, or thread-pool exhaustion.
3. No evidence of invalid signatures being accepted.
4. No evidence of replay protection or deduplication bypass.
5. No demonstrated consensus failure or state corruption.

## Claim Boundaries

1. Classify as resource-exhaustion or backpressure hardening only.
2. Do not claim a confirmed exploitable vulnerability from the patch alone.
3. Do not classify as replay-or-signature-validation correctness.
4. Benchmark changes are not security evidence except as support for the asynchronous refactor.
5. Security relevance is limited to bounding work in a validator packet verification path.
