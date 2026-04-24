---
case_id: case_20201204_e3a41dec7
project: zksync
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
confidence: medium
source_quality: high
date: 2020-12-04
source_refs:
  - git:e3a41dec742ea2387c247efb59ef6e0a0b4799ec
  - "core/bin/zksync_witness_generator/src/lib.rs:69"
  - "core/bin/prover/src/client.rs:164"
  - "core/bin/prover/src/client.rs:131"
  - "core/bin/prover/src/client.rs:258"
bug_class: missing-prover-api-authentication
impact_type:
  - unauthorized-access
tags:
  - blockchain-core
  - prover-server
  - authentication
  - authorization
  - jwt
  - bearer-token
  - access-control
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is that this patch adds bearer-token authorization to the prover server/prover client coordination path. The evidence shows new JWT validation support on the server side and prover client requests updated to generate and attach bearer tokens. Broader claims about consensus compromise, external exposure, or proof forgery are not established by the provided hunks.

## Observed Patch Facts

1. In `core/bin/zksync_witness_generator/src/lib.rs`, the patch replaces `async fn status() -> actix_web::Result<String> {` with `/// The structure that stores the secret key for checking JsonWebToken matching.`.

2. In `core/bin/prover/src/client.rs`, the patch replaces `.http_client` with `let auth_token_generator = self`.

3. In `core/bin/prover/src/client.rs`, the patch replaces `trace!("sending block_to_prove");` with `let auth_token_generator = self`.

4. In `core/bin/prover/src/client.rs`, the patch replaces `.post(self.stopped_url.as_str())` with `let auth_token_generator = self`.

## Project Context

The changed code sits primarily in `core/bin/zksync_witness_generator/src`, `core/bin/zksync_witness_generator`, `core/bin/prover/src`, which anchors the finding in the `storage` area of the project. Historical context from `core/bin/zksync_witness_generator/src/witness_generator.rs`, `core/bin/zksync_witness_generator/src/scaler.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/bin/zksync_witness_generator/src/witness_generator.rs`, `core/bin/zksync_witness_generator/src/scaler.rs`. The strongest project-level identifiers around this patch are `anyhow::Error`, `auth_token_generator`, `Result`, and `anyhow`. Nearby tests or test-like files include `core/bin/prover/tests/tests.rs`, `core/bin/zksync_witness_generator/tests/prover_server.rs`.

## Before/After Behavior

Before the patch, the shown prover client methods sent HTTP requests without bearer credentials. After the patch, those methods call `self.auth_token_generator.encode()` and attach the result with `.bearer_auth(...)`. The server-side code also adds an `AuthTokenValidator` backed by a JWT `DecodingKey` initialized from a shared secret.

# Root Cause

The prover coordination protocol lacked the shown bearer-authentication mechanism for the affected client requests, and the server-side code did not contain the shown shared-secret JWT validator in the provided before context.

## Walkthrough

1. The changed paths are in the prover client and witness generator/prover server code.

2. `core/bin/zksync_witness_generator/src/lib.rs` adds `AuthTokenValidator` with a JWT decoding key derived from a shared secret.

3. `block_to_prove` now generates an auth token before requesting a proof job and sends it as bearer authorization.

4. `working_on` now sends bearer authorization when reporting that a prover is working on a job.

5. The provided context shows `publish` now sends bearer authorization when posting a proof.

6. `prover_stopped` now sends bearer authorization when reporting prover lifecycle state.

7. The evidence supports adding authentication to prover coordination calls, but does not show full endpoint middleware wiring or network exposure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/bin/zksync_witness_generator/src/lib.rs | 69 | Defines server-side JWT validator backed by a shared secret for prover server request authorization. |
| core/bin/prover/src/client.rs | 131 | Adds bearer authorization to block_to_prove job-fetch requests. |
| core/bin/prover/src/client.rs | 164 | Adds bearer authorization to working_on job-claim/status requests. |
| core/bin/prover/src/client.rs | 214 | Adds bearer authorization to proof publication requests. |
| core/bin/prover/src/client.rs | 258 | Adds bearer authorization to prover_stopped lifecycle requests. |

## Code Snippets

## Snippet 1

Context: `core/bin/zksync_witness_generator/src/lib.rs:69` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

async fn status() -> actix_web::Result<String> {
    Ok("alive".into())
```
After
```rust
}

/// The structure that stores the secret key for checking JsonWebToken matching.
struct AuthTokenValidator<'a> {
    decoding_key: DecodingKey<'a>,
}

impl<'a> AuthTokenValidator<'a> {
```

## Snippet 2

Context: `core/bin/prover/src/client.rs:164` (changes persisted or aggregate state handling)

Before
```rust
fn working_on(&self, job_id: i32) -> Result<(), anyhow::Error> {
        trace!("sending working_on {}", job_id);
        let res = self
            .http_client
            .post(self.working_on_url.as_str())
            .json(&client::WorkingOnReq {
                prover_run_id: job_id,
```
After
```rust
fn working_on(&self, job_id: i32) -> Result<(), anyhow::Error> {
        trace!("sending working_on {}", job_id);
        let auth_token_generator = self
            .auth_token_generator
            .encode()
            .map_err(|e| format_err!("failed generate authorization token: {}", e))?;

        let res = self
```

## Snippet 3

Context: `core/bin/prover/src/client.rs:131` (changes persisted or aggregate state handling)

Before
```rust
impl crate::ApiClient for ApiClient {
    fn block_to_prove(&self, block_size: usize) -> Result<Option<(i64, i32)>, anyhow::Error> {
        let op = || -> Result<Option<(i64, i32)>, anyhow::Error> {
            trace!("sending block_to_prove");
```
After
```rust
impl crate::ApiClient for ApiClient {
    fn block_to_prove(&self, block_size: usize) -> Result<Option<(i64, i32)>, anyhow::Error> {
        let auth_token_generator = self
            .auth_token_generator
            .encode()
            .map_err(|e| format_err!("failed generate authorization token: {}", e))?;

        let op = || -> Result<Option<(i64, i32)>, anyhow::Error> {
```

## Snippet 4

Context: `core/bin/prover/src/client.rs:258` (changes persisted or aggregate state handling)

Before
```rust
fn prover_stopped(&self, prover_run_id: i32) -> Result<(), anyhow::Error> {
        self.http_client
            .post(self.stopped_url.as_str())
            .json(&prover_run_id)
            .send()
```
After
```rust
fn prover_stopped(&self, prover_run_id: i32) -> Result<(), anyhow::Error> {
        let auth_token_generator = self
            .auth_token_generator
            .encode()
            .map_err(|e| format_err!("failed generate authorization token: {}", e))?;

        self.http_client
```

# Fix Pattern

Add an explicit shared-secret JWT bearer-authentication boundary to prover coordination APIs, with server-side token validation support and client-side token generation on each affected request.

## How It Was Fixed

The patch adds `AuthTokenValidator` using `DecodingKey::from_secret(...)` in the server-side code and updates prover client methods to encode an authorization token, propagate token-generation errors, and attach the token using `.bearer_auth(...)` before sending requests.

# Why It Matters

1. Prevents unauthenticated clients from using the shown prover coordination requests if server validation is wired to these routes.

2. Adds a consistent authorization mechanism for job fetch, job status, proof publication, and lifecycle reporting.

3. The evidence does not establish broader consensus impact or external attackability.

# Evidence Notes

The commit title is `Add authorization for prover server`. The strongest evidence is in `core/bin/zksync_witness_generator/src/lib.rs` adding `AuthTokenValidator` and in `core/bin/prover/src/client.rs` adding token generation and `.bearer_auth(...)` to multiple client calls. The heuristic baseline's storage, panic, and malformed transaction claims are unsupported and removed. Confidence is medium rather than high because the provided excerpts do not show complete server route enforcement, JWT claims, expiration policy, deployment exposure, or exploitability. Protocol security invariant: Prover coordination endpoints should require an authorized prover client before allowing job fetches, job status updates, proof publication, or prover lifecycle reports. Verification notes: The patch does not prove the prover server was exposed to untrusted networks. The patch does not prove that unauthenticated requests could compromise consensus or forge accepted proofs. The patch does not show the full JWT claims, expiration policy, or endpoint middleware wiring. The patch does not establish privilege escalation beyond missing authentication on prover coordination APIs. The heuristic baseline's panic/storage interpretation is not supported by the provided hunks. Verified only against the provided input; no commands or external context used. Claim boundaries from the mapper are preserved. Unsupported storage/liveness/panic interpretation was discarded. Kept in security corpus because the patch likely fixes missing authentication, not mere cleanup or refactor. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-prover-api-authentication`
Final impact type: `unauthorized-access`
Final tags: `blockchain-core, prover-server, authentication, authorization, jwt, bearer-token, access-control`

The supplied evidence supports retaining this as security hardening: the patch adds JWT-based bearer authorization to prover client requests and introduces a server-side token validator for the prover server path. The evidence does not prove a concrete exploitable vulnerability, full endpoint enforcement, network exposure, or consensus compromise, so security-fix is too strong and the original storage/liveness framing is misleading.

## Security Evidence

1. Commit subject explicitly says authorization was added for the prover server.
2. Server-side code adds AuthTokenValidator using a JWT DecodingKey derived from a shared secret.
3. Client methods for block_to_prove, working_on, publish, and prover_stopped generate auth tokens.
4. Affected client requests now attach bearer authorization before sending prover coordination calls.

## Missing Evidence

1. No full route or middleware wiring is shown to prove every endpoint rejects unauthenticated requests.
2. No evidence shows the prover server was exposed to untrusted networks.
3. No exploit scenario, incident, CVE, or concrete bypass is provided.
4. No proof is provided that unauthenticated access could directly compromise consensus or forge accepted proofs.

## Claim Boundaries

1. Validate only as added authentication/authorization for prover coordination APIs.
2. Do not classify as storage, database, liveness, consensus, or proof-forgery based on the supplied hunks.
3. Treat as security-hardening rather than a proven security-fix.
4. Impact should be limited to potential unauthorized access to prover server coordination endpoints.
