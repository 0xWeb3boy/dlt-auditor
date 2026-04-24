---
case_id: case_20201210_e81d133a7
project: zksync
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2020-12-10
source_refs:
  - git:e81d133a712221e18ff2fcffdb67b25a920c5723
  - "core/lib/config/src/lib.rs:116"
  - "core/lib/config/src/lib.rs:83"
  - "core/bin/zksync_api/src/api_server/admin_server.rs:129"
  - "core/bin/zksync_witness_generator/src/lib.rs:361"
bug_class: insecure-default-secret-detection
impact_type:
  - unauthorized-access-risk
  - insecure-configuration
confidence: medium
tags:
  - auth-configuration
  - jwt
  - default-secret
  - admin-api
  - prover-api
  - warning-only-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is security hardening around admin/prover authentication configuration. The patch adds checks in configuration loading for `ADMIN_SERVER_SECRET_AUTH` and `PROVER_SECRET_AUTH`, logging an error if either secret is `"sample"` while `ETH_NETWORK` is not `"localhost"`. It also replaces `.unwrap()` with `.expect(...)` in two auth paths, which improves panic diagnostics only. The evidence does not support transaction-processing, malformed-input, or panic-to-DoS claims.

## Observed Patch Facts

1. In `core/lib/config/src/lib.rs`, the patch replaces `Self {` with `let secret_auth = get_env("ADMIN_SERVER_SECRET_AUTH");`.

2. In `core/lib/config/src/lib.rs`, the patch replaces `Self {` with `let secret_auth = get_env("PROVER_SECRET_AUTH");`.

3. In `core/bin/zksync_api/src/api_server/admin_server.rs`, the patch replaces `let secret_auth = req.app_data::<AppState>().unwrap().secret_auth.clone();` with `let secret_auth = req`.

4. In `core/bin/zksync_witness_generator/src/lib.rs`, the patch replaces `.unwrap()` with `.expect("failed get AppState upon receipt of the authentication token")`.

## Project Context

The changed code sits primarily in `core/lib/config/src`, `core/lib/config`, `core/bin/zksync_api/src/api_server`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/bin/zksync_api/src/api_server/tx_sender.rs`, `core/bin/zksync_witness_generator/src/witness_generator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/bin/zksync_api/src/api_server/tx_sender.rs`, `core/bin/zksync_witness_generator/src/witness_generator.rs`. The strongest project-level identifiers around this patch are `secret_auth`, `log::error`, `get_env`, and `AppState`. Nearby tests or test-like files include `core/bin/zksync_witness_generator/tests/prover_server.rs`.

## Before/After Behavior

Before the patch, admin and prover options read their configured auth secrets directly from environment variables with no shown check for the public sample value. After the patch, each path reads the secret and `ETH_NETWORK`, logs an error if the secret is `"sample"` outside localhost, and then stores the same secret. The bearer-auth paths still retrieve `secret_auth` from `AppState` and pass it to `AuthTokenValidator`; changing `.unwrap()` to `.expect(...)` preserves panic behavior while making the panic message clearer.

# Root Cause

The grounded issue is an unsafe-configuration risk: admin and prover HTTP authorization depends on secrets loaded from environment variables, but the previous config loading did not flag the known sample secret in non-localhost environments. The patch adds warning-only detection; it does not prove that affected deployments existed or that endpoint exposure made this exploitable.

## Walkthrough

1. `AdminServerOptions::from_env` previously assigned `secret_auth` directly from `ADMIN_SERVER_SECRET_AUTH`.

2. The patched admin config path reads `ADMIN_SERVER_SECRET_AUTH` and `ETH_NETWORK` before constructing the options.

3. If the admin secret is `"sample"` and the network is not `"localhost"`, the patched code logs an error about an incorrect production JWT authorization secret.

4. `ProverOptions::from_env` receives the same warning pattern for `PROVER_SECRET_AUTH`.

5. The admin server auth middleware still retrieves `secret_auth` from `AppState` and constructs `AuthTokenValidator::new(&secret_auth)`.

6. The prover server auth middleware still retrieves `secret_auth` from `web::Data<AppState>` and constructs `AuthTokenValidator::new(&secret_auth)`.

7. The `.unwrap()` to `.expect(...)` edits only clarify failure diagnostics if `AppState` is missing; they do not alter access control or remove the panic condition.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/lib/config/src/lib.rs | 116 | loads admin server JWT secret and logs an error when the sample secret is used outside localhost |
| core/lib/config/src/lib.rs | 83 | loads prover JWT secret and logs an error when the sample secret is used outside localhost |
| core/bin/zksync_api/src/api_server/admin_server.rs | 129 | admin HTTP bearer-auth path retrieves secret_auth from AppState for token validation; changed panic message only |
| core/bin/zksync_witness_generator/src/lib.rs | 361 | prover HTTP bearer-auth path retrieves secret_auth from AppState for token validation; changed panic message only |

## Code Snippets

## Snippet 1

Context: `core/lib/config/src/lib.rs:116` (changes an authorization or privilege gate)

Before
```rust
/// Panics if any of options is missing or has inappropriate value.
    pub fn from_env() -> Self {
        Self {
            admin_http_server_url: parse_env("ADMIN_SERVER_API_URL"),
            admin_http_server_address: addr_from_port(parse_env("ADMIN_SERVER_API_PORT")),
            secret_auth: get_env("ADMIN_SERVER_SECRET_AUTH"),
        }
    }
```
After
```rust
/// Panics if any of options is missing or has inappropriate value.
    pub fn from_env() -> Self {
        let secret_auth = get_env("ADMIN_SERVER_SECRET_AUTH");
        let network = get_env("ETH_NETWORK");

        // Checks if an untrusted key is being used for production.
        if &secret_auth == "sample" && &network != "localhost" {
            log::error!("Admin server secret for JWT authorization set to 'sample', this is an incorrect value for production");
```

## Snippet 2

Context: `core/lib/config/src/lib.rs:83` (changes a sensitive control or state-update path)

Before
```rust
/// Panics if any of options is missing or has inappropriate value.
    pub fn from_env() -> Self {
        Self {
            secret_auth: get_env("PROVER_SECRET_AUTH"),
            prepare_data_interval: Duration::from_millis(parse_env("PROVER_PREPARE_DATA_INTERVAL")),
            heartbeat_interval: Duration::from_millis(parse_env("PROVER_HEARTBEAT_INTERVAL")),
```
After
```rust
/// Panics if any of options is missing or has inappropriate value.
    pub fn from_env() -> Self {
        let secret_auth = get_env("PROVER_SECRET_AUTH");
        let network = get_env("ETH_NETWORK");

        // Checks if an untrusted key is being used for production.
        if &secret_auth == "sample" && &network != "localhost" {
            log::error!("Prover secret for JWT authorization set to 'sample', this is an incorrect value for production");
```

## Snippet 3

Context: `core/bin/zksync_api/src/api_server/admin_server.rs:129` (changes the branch that decides whether execution stops or continues)

Before
```rust
HttpServer::new(move || {
        let auth = HttpAuthentication::bearer(move |req, credentials| async {
            let secret_auth = req.app_data::<AppState>().unwrap().secret_auth.clone();
            AuthTokenValidator::new(&secret_auth)
                .validator(req, credentials)
```
After
```rust
HttpServer::new(move || {
        let auth = HttpAuthentication::bearer(move |req, credentials| async {
            let secret_auth = req
                .app_data::<AppState>()
                .expect("failed get AppState upon receipt of the authentication token")
                .secret_auth
                .clone();
            AuthTokenValidator::new(&secret_auth)
```

## Snippet 4

Context: `core/bin/zksync_witness_generator/src/lib.rs:361` (changes the branch that decides whether execution stops or continues)

Before
```rust
let secret_auth = req
                            .app_data::<web::Data<AppState>>()
                            .unwrap()
                            .secret_auth
                            .clone();
```
After
```rust
let secret_auth = req
                            .app_data::<web::Data<AppState>>()
                            .expect("failed get AppState upon receipt of the authentication token")
                            .secret_auth
                            .clone();
```

# Fix Pattern

Detect a known unsafe default secret during configuration loading and emit an operator-visible error when it appears outside the local development network. This is warning-based hardening, not fail-closed enforcement.

## How It Was Fixed

The patch introduced local `secret_auth` and `network` variables in both admin and prover configuration loaders, compared the configured secret to `"sample"`, checked that `ETH_NETWORK` is not `"localhost"`, and logged service-specific error messages. It also replaced two auth-path `.unwrap()` calls with `.expect(...)` messages without changing runtime behavior beyond diagnostics.

# Why It Matters

1. Admin and prover HTTP endpoints rely on configured bearer-auth secrets.

2. A public sample secret is unsuitable outside local development.

3. The patch helps surface insecure deployment configuration.

4. The patch does not prevent startup or reject requests by itself.

5. No evidence proves actual production exposure or exploitation.

# Evidence Notes

Evidence is limited to config-loading checks in `core/lib/config/src/lib.rs` and diagnostic changes in `core/bin/zksync_api/src/api_server/admin_server.rs` and `core/bin/zksync_witness_generator/src/lib.rs`. The log messages explicitly describe `"sample"` as incorrect for production JWT authorization. No supplied evidence supports transaction-processing, malformed transaction handling, checked integer conversion, or a remote crash vulnerability. Protocol security invariant: Admin and prover HTTP endpoints use bearer-token validation backed by configured shared secrets. For non-localhost deployments, those secrets should not be the public sample value; otherwise authorization may rely on a known credential. The patch detects this condition and logs an error, but does not reject the configuration or change authentication semantics. Verification notes: The patch does not prove that production deployments actually used the sample secret. The patch does not reject insecure configuration or stop startup; it only logs an error. The unwrap-to-expect changes do not remove a panic condition, only clarify its message. No transaction-processing or malformed-transaction vulnerability is supported by the provided patch evidence. No remote exploitability is proven without evidence that these endpoints are exposed and configured with the sample secret. Confirmed supported subsystem is admin/prover auth configuration, not transaction processing. Confirmed the main behavior change is logging on sample secret outside localhost. Confirmed `.unwrap()` to `.expect(...)` is diagnostic-only. No evidence of fail-closed enforcement. No evidence of real deployment exposure or exploitability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insecure-default-secret-detection`
Final impact type: `unauthorized-access-risk, insecure-configuration`
Final confidence: `medium`
Final tags: `auth-configuration, jwt, default-secret, admin-api, prover-api, warning-only-hardening`

The patch evidence supports security hardening, not a concrete security fix. It adds explicit detection and error logging when admin or prover JWT authorization secrets are set to the public sample value outside localhost. That is security-relevant configuration hardening, but the change does not fail closed, reject requests, rotate secrets, or prove any exposed vulnerable deployment. The original transaction-processing and liveness framing is misleading.

## Security Evidence

1. Config loading now checks ADMIN_SERVER_SECRET_AUTH against "sample" outside localhost.
2. Config loading now checks PROVER_SECRET_AUTH against "sample" outside localhost.
3. Added log messages explicitly call the sample JWT authorization secret incorrect for production.
4. Affected values are used by bearer-token authentication paths via AuthTokenValidator.

## Missing Evidence

1. No evidence that production deployments actually used the sample secret.
2. No evidence that the admin or prover endpoints were remotely exposed to attackers.
3. No fail-closed behavior was added; the code only logs an error.
4. The unwrap-to-expect changes preserve panic behavior and are diagnostic-only.
5. No evidence supports transaction-processing or liveness-failure impact.

## Claim Boundaries

1. Keep only as warning-based auth configuration hardening.
2. Do not claim a confirmed exploit or vulnerability remediation.
3. Do not claim denial-of-service mitigation from the expect-message changes.
4. Do not classify this as transaction-processing; it is admin/prover authentication configuration.
