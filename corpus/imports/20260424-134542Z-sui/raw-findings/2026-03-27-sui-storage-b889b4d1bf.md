---
case_id: case_20260327_b889b4d1bf
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2026-03-27
source_refs:
  - git:b889b4d1bf1cdf15b6899eea6ce94ad3ca9985c7
  - "crates/sui-protocol-config/src/lib.rs:4770"
  - "crates/sui-benchmark/src/lib.rs:487"
  - "crates/sui-benchmark/src/drivers/bench_driver.rs:1135"
  - "crates/sui-protocol-config/src/lib.rs:306"
bug_class: resource-amplification-control
impact_type:
  - resource-exhaustion
confidence: medium
tags:
  - infrastructure
  - protocol-config
  - resource-control
  - amplification
  - validator
  - devnet-testnet
  - benchmark-support
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch re-enables `defer_unpaid_amplification` for protocol version 120 on non-mainnet chains and restores capped benchmark traffic that exercises amplified submissions. This may be security relevant as resource-control hardening, but the provided evidence does not establish a vulnerability fix: the enforcement implementation is absent, Mainnet is explicitly excluded, and much of the change is benchmark/load-generation support.

## Observed Patch Facts

1. In `crates/sui-protocol-config/src/lib.rs`, the patch replaces `120 => {}` with `120 => {`.

2. In `crates/sui-benchmark/src/lib.rs`, the patch replaces `let validators: Vec<_> = self.clients.values().take(num_validators).collect();` with `let validators: Vec<_> = self`.

3. In `crates/sui-benchmark/src/drivers/bench_driver.rs`, the patch replaces `// With 5% probability, submit to a random number of validators (3 to committee_size...` with `// With 5% probability, submit to 3 to N validators to trigger deferral logic.`.

4. In `crates/sui-protocol-config/src/lib.rs`, the patch adds `// Version 120: Re-enable defer_unpaid_amplification (devnet + testnet).`.

## Project Context

The changed code sits primarily in `crates/sui-protocol-config/src`, `crates/sui-protocol-config`, `crates/sui-benchmark/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/sui-benchmark/src/options.rs`, `crates/sui-benchmark/src/system_state_observer.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-benchmark/src/options.rs`, `crates/sui-benchmark/src/workloads/randomized_transaction.rs`. The strongest project-level identifiers around this patch are `rand::thread_rng`, `validators`, `Version`, and `deferral`. Nearby tests or test-like files include `crates/sui-benchmark/tests/simtest.rs`.

## Before/After Behavior

Before the patch, protocol version 120 had an empty config arm and did not re-enable `defer_unpaid_amplification` in the supplied evidence. After the patch, version 120 sets `cfg.feature_flags.defer_unpaid_amplification = true` only when `chain != Chain::Mainnet`. Benchmark amplification was previously disabled with `let use_amplification = false`; after the patch, benchmarks use a 5% random amplification rate with validator fanout capped at no more than 5 validators.

# Root Cause

The grounded issue is configuration and test coverage: the unpaid amplification deferral flag was not enabled for protocol version 120 on devnet/testnet, and benchmark amplification traffic was disabled. The evidence does not prove that this caused an exploitable denial-of-service or consensus vulnerability.

## Walkthrough

1. Protocol version 120 previously had an empty match arm in `crates/sui-protocol-config/src/lib.rs`.

2. The patch changes that arm to enable `cfg.feature_flags.defer_unpaid_amplification` for chains other than Mainnet.

3. A protocol history comment is updated to say version 120 re-enables the feature for devnet and testnet.

4. Benchmark code changes from disabling amplification to selecting amplified submissions with 5% probability.

5. Benchmark fanout is bounded between 3 validators and `committee_size.min(5)`.

6. The local validator aggregator benchmark path collects cloned validator clients for parallel submission setup.

7. The supplied test plan reports private-testnet validation and an active deferrals metric, but does not show the deferral implementation or an attack scenario.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-protocol-config/src/lib.rs | 4770 | Enables `defer_unpaid_amplification` for protocol version 120 on devnet/testnet, controlling whether unpaid amplification deferral protection is active. |
| crates/sui-protocol-config/src/lib.rs | 306 | Documents protocol-version history showing prior disablement for debugging and re-enablement in version 120 for devnet/testnet. |
| crates/sui-benchmark/src/drivers/bench_driver.rs | 1135 | Restores benchmark generation of occasional amplified transaction submissions and caps validator fanout to exercise deferral behavior. |
| crates/sui-benchmark/src/lib.rs | 487 | Adjusts local validator aggregator amplification submission setup for parallel validator submission behavior in benchmarks. |

## Code Snippets

## Snippet 1

Context: `crates/sui-protocol-config/src/lib.rs:4770` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
cfg.transfer_receive_object_type_cost_per_byte = Some(2);
                }
                120 => {}
                // Use this template when making changes:
                //
```
After
```rust
cfg.transfer_receive_object_type_cost_per_byte = Some(2);
                }
                120 => {
                    // Re-enable unpaid amplification deferral protection (testnet + devnet)
                    if chain != Chain::Mainnet {
                        cfg.feature_flags.defer_unpaid_amplification = true;
                    }
                }
```

## Snippet 2

Context: `crates/sui-benchmark/src/lib.rs:487` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
// Submit to multiple validators in parallel
        let validators: Vec<_> = self.clients.values().take(num_validators).collect();
        let request = SubmitTxRequest::new_transaction(tx.clone());

        let futures: Vec<_> = validators
            .iter()
            .map(|client| {
```
After
```rust
// Submit to multiple validators in parallel
        let validators: Vec<_> = self
            .clients
            .values()
            .take(num_validators)
            .cloned()
            .collect();
```

## Snippet 3

Context: `crates/sui-benchmark/src/drivers/bench_driver.rs:1135` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
// Occasionally submit to multiple validators to test unpaid amplification deferral.
                        // With 5% probability, submit to a random number of validators (3 to committee_size - 1)
                        // to trigger the deferral logic. Randomizing increases chances of testing longer deferrals.
                        // let use_amplification = rand::thread_rng().gen_bool(0.05);
                        // TODO: temporarily disable amplification.
                        let use_amplification = false;
                        let committee_size = committee.num_members();
```
After
```rust
// Occasionally submit to multiple validators to test unpaid amplification deferral.
                        // With 5% probability, submit to 3 to N validators to trigger deferral logic.
                        let use_amplification = rand::thread_rng().gen_bool(0.05);
                        let committee_size = committee.num_members();
                        let proxy = worker.execution_proxy.clone_new();
                        let res = async move {
                            let (client_type, res) = if use_amplification {
```

## Snippet 4

Context: `crates/sui-protocol-config/src/lib.rs:306` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
//              Enable address aliases on mainnet.
//              Relax ValidDuring requirement for transactions with owned inputs.
//              Disable defer_unpaid_amplification (debugging).
// Version 116: Enable Display Registry.
// Version 117: Update Sui System metadata handling.
// Version 118: Adds `transfer_migration_cap` to display registry
// Version 119: Enable the new VM.
```
After
```rust
//              Enable address aliases on mainnet.
//              Relax ValidDuring requirement for transactions with owned inputs.
// Version 116: Enable Display Registry.
//              Disable defer_unpaid_amplification (debugging).
// Version 117: Update Sui System metadata handling.
// Version 118: Adds `transfer_migration_cap` to display registry
// Version 119: Enable the new VM.
// Version 120: Re-enable defer_unpaid_amplification (devnet + testnet).
```

# Fix Pattern

Enable an existing protocol-gated resource-control feature for selected non-mainnet networks and add bounded benchmark traffic to exercise it.

## How It Was Fixed

The version-120 protocol configuration now sets `defer_unpaid_amplification` for non-mainnet chains. Benchmark code was updated to generate occasional amplified submissions and cap validator fanout, with supporting changes to cloned validator client handling for parallel submissions.

# Why It Matters

1. Unpaid transaction submission fanout can be a resource-control concern.

2. The patch makes the deferral feature active on devnet/testnet protocol version 120.

3. The benchmark changes help exercise the deferral path under bounded load.

4. Mainnet behavior is explicitly unchanged.

5. The evidence does not establish a confirmed vulnerability or exploit path.

# Evidence Notes

The strongest evidence is the protocol config change enabling `defer_unpaid_amplification` under `if chain != Chain::Mainnet`. Supporting evidence is limited to comments, benchmark traffic generation, capped fanout, and the commit test plan. Unsupported claims removed: this is not shown to be a serialization/state-representation issue, not shown to be a confirmed denial-of-service fix, and not shown to alter production Mainnet enforcement. Protocol security invariant: The evidence suggests a possible resource-control invariant around deferring unpaid amplified transaction submissions, but the actual deferral mechanism and any exploitable failure mode are not shown in the provided patch. Verification notes: The patch does not show the implementation of unpaid amplification deferral itself. The patch does not prove a remotely exploitable denial-of-service condition. The protection is enabled only for devnet and testnet, not mainnet. Benchmark driver changes are test/load-generation support and are not direct production validator enforcement. No cryptographic, authorization, or serialization invariant change is shown. No deferral implementation code is included in the provided evidence. No exploit, regression test, or failing-before/passing-after security test is shown. Benchmark files should be treated as support code, not root-cause enforcement. Classification remains unclear rather than confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `resource-amplification-control`
Final impact type: `resource-exhaustion`
Final confidence: `medium`
Final tags: `infrastructure, protocol-config, resource-control, amplification, validator, devnet-testnet, benchmark-support`

The supplied patch supports a security-hardening classification, not a confirmed security fix. It re-enables an existing feature flag explicitly described as unpaid amplification deferral protection for non-mainnet chains and restores bounded benchmark traffic to exercise that path. The evidence is resource-control oriented, but it does not show the underlying deferral implementation, an exploit, or a production Mainnet vulnerability.

## Security Evidence

1. Protocol version 120 now sets `cfg.feature_flags.defer_unpaid_amplification = true` when `chain != Chain::Mainnet`.
2. The added code comment calls this `unpaid amplification deferral protection`.
3. Protocol history documents re-enabling `defer_unpaid_amplification` for devnet and testnet.
4. Benchmark code restores amplified multi-validator submissions at a 5% rate to trigger deferral logic.
5. Benchmark fanout is capped to limit amplification traffic.

## Missing Evidence

1. No implementation of the deferral enforcement path is included in the supplied patch evidence.
2. No failing-before/passing-after security test or exploit scenario is shown.
3. Mainnet is explicitly excluded from the feature enablement.
4. Most non-config changes are benchmark/load-generation support rather than validator enforcement code.

## Claim Boundaries

1. Do not classify this as a serialization, storage, or state-representation bug.
2. Do not claim a confirmed denial-of-service vulnerability from the supplied evidence alone.
3. Do not claim Mainnet behavior was hardened by this patch.
4. The supported claim is limited to resource-control hardening for devnet/testnet protocol configuration plus benchmark coverage.
