---
case_id: case_20201224_ba3bb4b61
project: zksync
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2020-12-24
source_refs:
  - git:ba3bb4b61cc8750b6cc4007a3f25c70fca60ba3e
  - "core/bin/prover/src/lib.rs:225"
  - "core/bin/prover/src/lib.rs:202"
  - "core/bin/prover/src/lib.rs:126"
  - "core/bin/zksync_witness_generator/src/lib.rs:449"
bug_class: missing-authentication
impact_type:
  - unauthorized-api-access
confidence: medium
tags:
  - authentication
  - api-boundary
  - actix-middleware
  - prover-server
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The security-relevant change is the restoration of Actix authentication middleware in the witness generator/prover server. The patch changes a commented-out `.wrap(auth)` line marked `TODO: restore auth` into an active `.wrap(auth)`, applying the available `AuthTokenValidator` to the prover coordination API. Other prover changes in the supplied evidence are logging or failure-handling changes and do not establish separate vulnerability fixes.

## Observed Patch Facts

1. In `core/bin/prover/src/lib.rs`, the patch replaces `.unwrap();` with `.unwrap_or_default();`.

2. In `core/bin/prover/src/lib.rs`, the patch replaces `let (ret_prover, proof) = futures::select! {` with `log::info!(`.

3. In `core/bin/prover/src/lib.rs`, the patch adds `log::info!("Starting sending heartbeats for job with ID: {}", job_id);`.

4. In `core/bin/zksync_witness_generator/src/lib.rs`, the patch replaces `// .wrap(auth) // TODO: restore auth` with `.wrap(auth)`.

## Project Context

The changed code sits primarily in `core/bin/prover/src`, `core/bin/prover`, `core/bin/zksync_witness_generator/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/bin/prover/src/exit_proof.rs`, `core/bin/zksync_witness_generator/src/witness_generator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/bin/prover/src/cli_utils.rs`, `core/bin/zksync_witness_generator/src/witness_generator.rs`. The strongest project-level identifiers around this patch are `log::info`, `proof`, `log::warn`, and `info`. Nearby tests or test-like files include `core/bin/zksync_witness_generator/tests/prover_server.rs`, `core/bin/prover/tests/tests.rs`.

## Before/After Behavior

Before the patch, `run_prover_server` built the Actix app with `// .wrap(auth) // TODO: restore auth`, so the provided server construction snippet registered prover coordination routes without the visible auth middleware. After the patch, the app builder calls `.wrap(auth)` before app data and route registration, restoring server-side authentication for those routes.

# Root Cause

The authentication middleware for the prover server was present but disabled in the observed app construction path by being commented out, leaving the API routes without the intended shared-secret auth wrapper.

## Walkthrough

1. `run_prover_server` constructs an Actix `App` in `core/bin/zksync_witness_generator/src/lib.rs`.

2. The code creates an `AuthTokenValidator` from `secret_auth` before app construction, showing server-side authentication was intended in this path.

3. Before the patch, the middleware application was commented out as `// .wrap(auth) // TODO: restore auth`.

4. The same app registers `/status`, `/get_job`, `/working_on`, and `/publish`.

5. The patch replaces the commented-out middleware with active `.wrap(auth)`.

6. Related client context shows clients generate short-lived auth tokens from a shared secret, supporting the intended authentication model.

7. The `.unwrap_or_default()` and added `log::info!` changes in the prover are treated as operational changes, not as the root security fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/bin/zksync_witness_generator/src/lib.rs | 449 | Restores auth middleware on the prover server Actix app before registering status, get_job, working_on, and publish routes. |
| core/bin/prover/src/client.rs | 29 | Related client-side context showing authenticated API clients generate short-lived auth tokens from the shared secret. |
| core/bin/prover/src/lib.rs | 219 | Operational proof publication path; changed failure handling from unwrap panic to warning/default, not the primary security invariant. |
| core/bin/prover/src/lib.rs | 113 | Operational heartbeat path; adds logging only. |

## Code Snippets

## Snippet 1

Context: `core/bin/prover/src/lib.rs:225` (changes the branch that decides whether execution stops or continues)

Before
```rust
.await
            .map_err(|e| log::warn!("Failed to publish proof: {}", e))
            .unwrap();
    }
}
```
After
```rust
.await
            .map_err(|e| log::warn!("Failed to publish proof: {}", e))
            .unwrap_or_default();

        log::info!(
            "finished and published proof for blocks: [{}, {}]",
            first_block,
            last_block
```

## Snippet 2

Context: `core/bin/prover/src/lib.rs:202` (changes a sensitive control or state-update path)

Before
```rust
pin_mut!(heartbeat_future_handle, compute_proof_future);

        let (ret_prover, proof) = futures::select! {
            comp_proof = compute_proof_future => {
```
After
```rust
pin_mut!(heartbeat_future_handle, compute_proof_future);

        log::info!(
            "starting to compute proof for blocks: [{}, {}]",
            first_block,
            last_block
        );
```

## Snippet 3

Context: `core/bin/prover/src/lib.rs:126` (changes a sensitive control or state-update path)

Before
```rust
Duration::from_secs((heartbeat_interval.as_secs_f64() * random_multiplier) as u64)
        };

        tokio::time::delay_for(timeout_value).await;
        client
            .working_on(job_id, &prover_name)
```
After
```rust
Duration::from_secs((heartbeat_interval.as_secs_f64() * random_multiplier) as u64)
        };
        tokio::time::delay_for(timeout_value).await;

        log::info!("Starting sending heartbeats for job with ID: {}", job_id);

        client
            .working_on(job_id, &prover_name)
```

## Snippet 4

Context: `core/bin/zksync_witness_generator/src/lib.rs:449` (changes an authorization or privilege gate)

Before
```rust
// `Arc` wrapping of the object.
                    App::new()
                        // .wrap(auth) // TODO: restore auth
                        .app_data(web::Data::new(app_state))
                        .route("/status", web::get().to(status))
```
After
```rust
// `Arc` wrapping of the object.
                    App::new()
                        .wrap(auth)
                        .app_data(web::Data::new(app_state))
                        .route("/status", web::get().to(status))
```

# Fix Pattern

Restore disabled authentication middleware at the API boundary before registering sensitive coordination routes.

## How It Was Fixed

The patch activates `.wrap(auth)` in the Actix app builder for the prover server, applying `AuthTokenValidator` middleware to the app exposing prover coordination routes.

# Why It Matters

1. The affected code is an API boundary for prover and witness-generator coordination.

2. The routes include job retrieval, heartbeat/working status, and proof publication endpoints.

3. The client-side context indicates the API is expected to use shared-secret, short-lived authentication tokens.

4. The evidence supports missing server-side authentication, but does not prove public exposure or downstream proof acceptance behavior.

# Evidence Notes

Primary evidence is `core/bin/zksync_witness_generator/src/lib.rs` line 449, where `// .wrap(auth) // TODO: restore auth` becomes `.wrap(auth)`. Supporting evidence is `core/bin/prover/src/client.rs` showing clients construct an auth token generator from `PROVER_SECRET_AUTH`. The supplied evidence does not support claims about transaction input validation, cryptographic verification bypass, public network reachability, or unauthorized proof acceptance downstream. Protocol security invariant: The prover server API must enforce the configured shared-secret authentication middleware before allowing access to prover coordination endpoints such as /status, /get_job, /working_on, and /publish. Verification notes: No exploitability is proven from the patch alone. No evidence shows whether the prover server was reachable from untrusted networks in deployment. No evidence shows a cryptographic proof verification bypass. The prover `.unwrap_or_default()` and logging changes appear to be availability/observability changes, not authentication fixes. The patch does not prove that unauthorized published proofs would be accepted downstream. Confirmed from the provided diff snippets only; no external context was used. Authentication restoration is directly supported by the changed middleware line. Exploitability and deployment exposure remain unproven by the supplied evidence. Other changed prover hunks are not treated as separate security fixes. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-authentication`
Final impact type: `unauthorized-api-access`
Final confidence: `medium`
Final tags: `authentication, api-boundary, actix-middleware, prover-server`

The supplied patch directly shows authentication middleware being restored on the witness generator/prover server Actix app: a commented `// .wrap(auth) // TODO: restore auth` becomes active `.wrap(auth)` before API route registration. That clearly tightens a security-sensitive API boundary, but the evidence does not prove deployment exposure, exploitability, or downstream acceptance of malicious proofs. The original input-validation and transaction-processing framing is too specific and misleading; this is best retained as security hardening for missing/disabled authentication middleware.

## Security Evidence

1. AuthTokenValidator is constructed immediately before the Actix app setup.
2. The patch changes disabled middleware `// .wrap(auth) // TODO: restore auth` into active `.wrap(auth)`.
3. The middleware is applied before routes such as `/status`, `/get_job`, `/working_on`, and `/publish` are registered.
4. Related client context shows clients use a shared secret auth token model.

## Missing Evidence

1. No evidence that the server was reachable from untrusted networks.
2. No evidence of an observed exploit or unauthorized caller.
3. No evidence that unauthorized published proofs would be accepted downstream.
4. No evidence that the prover logging or unwrap changes are security fixes.

## Claim Boundaries

1. Validate only as authentication hardening at a prover coordination API boundary.
2. Do not classify as input validation.
3. Do not claim a cryptographic proof verification bypass.
4. Do not claim confirmed transaction-processing compromise or concrete exploitability.
