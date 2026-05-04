---
case_id: case_20231206_8a8cad6ce
project: zksync-era
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: core-logic
confidence: medium
source_quality: medium
date: 2023-12-06
source_refs:
  - git:8a8cad6ce62f2d34bb34adcd956f6920c08f94b8
  - "core/lib/object_store/Cargo.toml:18"
bug_class: dependency-vulnerability-remediation
impact_type:
  - timing-side-channel-risk-reduction
tags:
  - dependency-update
  - transitive-dependency
  - rustsec-2023-0071
  - rsa
  - timing-side-channel
  - object-store
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best classified as dependency-level security hardening for the GCS object store path. It updates google-cloud-storage and google-cloud-auth, with the stated goal of removing the transitive rsa v0.6.1 dependency flagged by cargo-deny for RUSTSEC-2023-0071. The evidence does not establish a reachable zksync-era timing oracle or application-specific private-key recovery exploit.

## Observed Patch Facts

1. In `core/lib/object_store/Cargo.toml`, the patch replaces `google-cloud-storage = "0.12.0"` with `google-cloud-storage = "0.15.0"`.

## Project Context

The changed code sits primarily in `core/lib/object_store`, `core/lib`, which anchors the finding in the `core-logic` area of the project. Historical context from `core/lib/object_store/README.md`, `core/lib/object_store/src/gcs.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/lib/object_store/src/gcs.rs`, `core/lib/zksync_core/src/sync_layer/tests.rs`. The strongest project-level identifiers around this patch are `cloud`, `storage`, `auth`, and `async`. Nearby tests or test-like files include `core/lib/multivm/src/versions/vm_latest/tracers/traits.rs`, `core/lib/zksync_core/src/state_keeper/batch_executor/tests/tester.rs`.

## Before/After Behavior

Before the patch, core/lib/object_store/Cargo.toml depended on google-cloud-storage 0.12.0 and google-cloud-auth 0.11.0. The provided cargo-deny output says google-cloud-storage 0.12.0 pulled in rsa v0.6.1, which was flagged for RUSTSEC-2023-0071. After the patch, the manifest uses google-cloud-storage 0.15.0 and google-cloud-auth 0.13.0, and the commit states that this removes the rsa dependency. No local object-store logic, authorization check, or protocol behavior change is shown.

# Root Cause

The grounded root cause is the object_store crate's reliance on google-cloud-storage 0.12.0, which the supplied cargo-deny output identifies as introducing rsa v0.6.1 transitively. The vulnerable property is in the transitive rsa crate, not in project-local code shown in the evidence.

## Walkthrough

1. The object_store crate includes a GCS-backed ObjectStore implementation that imports google_cloud_auth and google_cloud_storage.

2. Before the patch, core/lib/object_store/Cargo.toml specified google-cloud-storage 0.12.0 and google-cloud-auth 0.11.0.

3. The provided cargo-deny output reports rsa v0.6.1 as vulnerable under RUSTSEC-2023-0071 and shows it reached the project through google-cloud-storage 0.12.0.

4. The dependency path continues into zksync_object_store and higher-level crates, establishing that the vulnerable package was in the project dependency graph.

5. The patch updates google-cloud-storage to 0.15.0 and google-cloud-auth to 0.13.0.

6. The commit states that google-cloud-storage 0.15.0 no longer depends on rsa, which is the basis for treating the change as security hardening.

7. The supplied evidence does not prove that attackers could observe timing behavior in this application or recover any zksync-era private key.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/lib/object_store/Cargo.toml | 18 | dependency manifest for the object_store crate; upgrades google-cloud-storage and google-cloud-auth to versions that avoid the vulnerable rsa transitive dependency |
| Cargo.lock | 759 | lockfile entry reported by cargo-deny for rsa v0.6.1 before the upgrade; transitive through google-cloud-storage v0.12.0 |
| core/lib/object_store/src/gcs.rs | 1 | GCS-based ObjectStore implementation that imports google_cloud_auth and google_cloud_storage and is the traced business-logic consumer of the upgraded dependencies |

## Code Snippets

## Snippet 1

Context: `core/lib/object_store/Cargo.toml:18` (changes an authorization or privilege gate)

Before
```text
async-trait = "0.1"
bincode = "1"
google-cloud-storage = "0.12.0"
google-cloud-auth = "0.11.0"
http = "0.2.9"
tokio = { version = "1.21.2", features = ["full"] }
```
After
```text
async-trait = "0.1"
bincode = "1"
google-cloud-storage = "0.15.0"
google-cloud-auth = "0.13.0"
http = "0.2.9"
tokio = { version = "1.21.2", features = ["full"] }
```

# Fix Pattern

Upgrade or replace a dependency chain to remove a known vulnerable transitive cryptographic package, rather than changing application logic.

## How It Was Fixed

core/lib/object_store/Cargo.toml was changed from google-cloud-storage 0.12.0 to 0.15.0 and from google-cloud-auth 0.11.0 to 0.13.0. According to the commit rationale, this eliminates the transitive rsa v0.6.1 dependency that triggered the cargo-deny advisory.

# Why It Matters

1. Removes a dependency flagged for a known RSA timing-side-channel advisory.

2. Addresses a cargo-deny security failure at the dependency boundary.

3. Does not demonstrate a project-local exploit path.

4. Does not change local authentication, authorization, or object-store protocol logic.

# Evidence Notes

Strong evidence: manifest hunk showing the google-cloud-storage and google-cloud-auth upgrades; commit body naming RUSTSEC-2023-0071; cargo-deny output showing rsa v0.6.1 reached via google-cloud-storage 0.12.0. Limitations: the supplied evidence does not include an after-upgrade dependency tree, does not show the lockfile diff, and does not establish application-level exploitability. Protocol security invariant: The GCS object-store dependency graph should not include a cryptographic dependency with a known private-key timing-side-channel advisory when that dependency is used through storage/auth libraries. The supplied evidence supports this as a dependency-boundary invariant, not a project-local protocol or access-control invariant. Verification notes: No project-local authentication, authorization, or privilege check change is shown. No reachable remote timing side channel in zksync-era is proven by the patch evidence. No concrete private-key recovery exploit against this application is demonstrated. The google-cloud-auth compatibility update is not independently shown to fix a vulnerability. The change is dependency removal/upgrade hardening, not evidence of a protocol logic bug in object storage. Verify Cargo.lock after the patch no longer contains rsa v0.6.1 through google-cloud-storage. Run cargo-deny or equivalent advisory scanning on the patched dependency graph. Do not infer a reachable timing oracle without additional runtime or code-path evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `dependency-vulnerability-remediation`
Final impact type: `timing-side-channel-risk-reduction`
Final tags: `dependency-update, transitive-dependency, rustsec-2023-0071, rsa, timing-side-channel, object-store, security-hardening`

The supplied evidence supports retaining this as dependency-level security hardening: the commit explicitly cites RUSTSEC-2023-0071 for rsa v0.6.1, shows the vulnerable crate reached the project through google-cloud-storage v0.12.0, and updates google-cloud-storage to a version stated to remove that dependency. The patch does not prove an application-level timing oracle, private-key recovery path, or local authorization/protocol bug, so it should not be classified as a concrete security-fix.

## Security Evidence

1. Commit body says the dependency update was primarily to address the rsa Marvin Attack advisory RUSTSEC-2023-0071.
2. Cargo-deny output shows rsa v0.6.1 was present transitively through google-cloud-storage v0.12.0.
3. Patch updates google-cloud-storage from 0.12.0 to 0.15.0 and google-cloud-auth from 0.11.0 to 0.13.0.
4. Commit rationale states google-cloud-storage v0.15.0 no longer depends on rsa.

## Missing Evidence

1. No after-upgrade dependency tree or lockfile excerpt proves rsa v0.6.1 is absent after the patch.
2. No project-local code change shows a fixed timing oracle, auth bug, privilege check, or protocol invariant.
3. No evidence shows attackers could observe rsa timing behavior in this application deployment.
4. No concrete key recovery or exploit path is demonstrated for zksync-era.

## Claim Boundaries

1. Valid as dependency security hardening, not as a proven exploitable project-local vulnerability fix.
2. Do not claim the object-store logic or access control behavior changed.
3. Do not claim private-key recovery was possible against this project from the supplied patch alone.
4. The google-cloud-auth update is supported only as compatibility work unless separately evidenced.
