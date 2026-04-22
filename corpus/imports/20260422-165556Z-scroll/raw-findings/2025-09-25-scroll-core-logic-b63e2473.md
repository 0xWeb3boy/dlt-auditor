---
case_id: case_20250925_b63e2473
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
source_quality: high
date: 2025-09-25
source_refs:
  - git:b63e2473ddf323e5ad0c14394b44dcc61547c934
  - "coordinator/internal/logic/verifier/verifier.go:27"
  - "coordinator/internal/utils/version.go:1"
  - "crates/libzkp/src/verifier.rs:70"
  - "coordinator/cmd/tool/verify.go:37"
bug_class: verifier-configuration-mismatch
impact_type:
  - verification-integrity
confidence: medium
tags:
  - blockchain-core
  - proof-verification
  - validium
  - verifier-config
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a correctness fix in verifier initialization and configuration plumbing: version is now carried explicitly and can be derived from fork name plus validium mode. That is plausibly relevant to PI-hash checking, but the snippets do not establish a concrete vulnerability, exploit path, or even whether the pre-fix behavior caused false accepts rather than only false rejects or misconfiguration.

## Observed Patch Facts

1. In `coordinator/internal/logic/verifier/verifier.go`, the patch replaces `func newRustCircuitConfig(cfg config.AssetConfig) *rustCircuitConfig {` with `Version uint 'json:"version"'`.

2. In `coordinator/internal/utils/version.go`, the patch adds `// version get the version for the chain instance`.

3. In `crates/libzkp/src/verifier.rs`, the patch replaces `tracing::info!("load verifier config for fork {}", cfg.fork_name);` with `tracing::info!("load verifier config for fork {} (ver {})", cfg.fork_name, cfg.version);`.

4. In `coordinator/cmd/tool/verify.go`, the patch replaces `vf, err := verifier.NewVerifier(cfg.ProverManager.Verifier)` with `vf, err := verifier.NewVerifier(cfg.ProverManager.Verifier, cfg.L2.ValidiumMode)`.

## Project Context

The changed code sits primarily in `coordinator/internal/logic/verifier`, `coordinator/internal/logic`, `coordinator/internal/utils`, which anchors the finding in the `core-logic` area of the project. Historical context from `crates/libzkp/src/lib.rs`, `coordinator/internal/logic/verifier/verifier_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/libzkp/src/lib.rs`, `coordinator/internal/config/config_test.go`. The strongest project-level identifiers around this patch are `tracing::info`, `fork_name`, `version`, and `verifier`.

## Before/After Behavior

Before the patch, the shown Go-side verifier config struct did not include a `version` field, and the shown CLI verifier construction did not pass `cfg.L2.ValidiumMode` into `verifier.NewVerifier`. After the patch, the Go-side config includes `Version`, missing versions are derived with `utils.Version(cfg.ForkName, validiumMode)`, and verifier construction receives `cfg.L2.ValidiumMode`. The Rust-side supplied context after the change shows verifier config carrying `cfg.version` and logging fork plus version, but the provided diff for Rust directly proves only the logging change.

# Root Cause

Verifier setup did not consistently carry explicit version and mode context into proof verification, leaving PI-hash checking dependent on incomplete or implicit configuration.

## Walkthrough

1. `coordinator/internal/logic/verifier/verifier.go` adds `Version` to `rustCircuitConfig`, where the earlier excerpt only showed `ForkName` and `AssetsPath`.

2. The same file adds fallback logic that uses `cfg.Version` when present and otherwise derives a version with `utils.Version(cfg.ForkName, validiumMode)`.

3. `coordinator/internal/utils/version.go` introduces a helper whose inputs are hard fork name and validium mode, showing that version selection is intended to depend on both.

4. `coordinator/cmd/tool/verify.go` changes verifier construction to pass `cfg.L2.ValidiumMode` into `verifier.NewVerifier`, so runtime verification becomes mode-aware.

5. In `crates/libzkp/src/verifier.rs`, the proved diff changes logging from fork-only to fork-plus-version. The surrounding supplied context also shows `Verifier::new(&cfg.assets_path, cfg.version)`, but the before/after hunk for that constructor call is not provided.

6. The commit subject says this is a fix for PI-hash checking in validium mode, but the provided snippets do not show the PI-hash check itself or demonstrate the exact pre-fix failure mode.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| coordinator/internal/logic/verifier/verifier.go | 21 | Builds the Rust verifier config and now includes an explicit circuit `version`, using fork/mode-derived fallback when absent. |
| coordinator/internal/utils/version.go | 1 | Derives verifier version from hard fork name and `ValidiumMode`, shaping which PI-hash/version semantics the verifier uses. |
| crates/libzkp/src/verifier.rs | 59 | Initializes each Rust verifier instance with `cfg.version`, making version part of the active verification context. |
| coordinator/cmd/tool/verify.go | 20 | Threads `cfg.L2.ValidiumMode` into verifier construction so CLI/runtime verification uses the correct mode-specific context. |

## Code Snippets

## Snippet 1

Context: `coordinator/internal/logic/verifier/verifier.go:27` (changes a consensus- or validator-sensitive branch)

Before
```go
// in `*config.CircuitConfig` being changed
type rustCircuitConfig struct {
	ForkName   string `json:"fork_name"`
	AssetsPath string `json:"assets_path"`
}

func newRustCircuitConfig(cfg config.AssetConfig) *rustCircuitConfig {
	return &rustCircuitConfig{
```
After
```go
// in `*config.CircuitConfig` being changed
type rustCircuitConfig struct {
	Version    uint   `json:"version"`
	ForkName   string `json:"fork_name"`
	AssetsPath string `json:"assets_path"`
}

var validiumMode bool
```

## Snippet 2

Context: `coordinator/internal/utils/version.go:1` (changes a consensus- or validator-sensitive branch)

Before
```go
(no before snippet captured)
```
After
```go
package utils

import (
	"errors"
	"strings"
)

// version get the version for the chain instance
```

## Snippet 3

Context: `crates/libzkp/src/verifier.rs:70` (changes a consensus- or validator-sensitive branch)

Before
```rust
cfg.fork_name
        );
        tracing::info!("load verifier config for fork {}", cfg.fork_name);
    }
```
After
```rust
cfg.fork_name
        );
        tracing::info!("load verifier config for fork {} (ver {})", cfg.fork_name, cfg.version);
    }
```

## Snippet 4

Context: `coordinator/cmd/tool/verify.go:37` (changes a sensitive control or state-update path)

Before
```go
}

	vf, err := verifier.NewVerifier(cfg.ProverManager.Verifier)
	if err != nil {
		return err
```
After
```go
}

	vf, err := verifier.NewVerifier(cfg.ProverManager.Verifier, cfg.L2.ValidiumMode)
	if err != nil {
		return err
```

# Fix Pattern

Thread required version and mode parameters explicitly through verifier initialization instead of relying on omitted fields or implicit defaults.

## How It Was Fixed

The patch adds a `version` field to the Go-to-Rust verifier configuration, derives that version from fork name and validium mode when configuration leaves it unset, and passes `ValidiumMode` into verifier construction. The supplied Rust context then shows version being present in verifier configuration and surfaced in logging.

# Why It Matters

1. PI-hash checks depend on using the correct version and mode context.

2. Fork name alone was not treated as sufficient after this change.

3. Mode-aware initialization reduces the chance of verifier/config mismatch.

4. The evidence supports a verifier-correctness fix in a sensitive path, but not a confirmed vulnerability.

# Evidence Notes

Strong evidence exists for added version plumbing in Go and for passing `ValidiumMode` into verifier construction. The new helper explicitly depends on fork name and validium mode, and the commit subject names PI-hash checking in validium mode. However, the supplied Rust diff directly proves only a logging change; the `Verifier::new(&cfg.assets_path, cfg.version)` line appears in surrounding context, not in a before/after hunk. No supplied snippet shows the PI-hash comparison logic, no test or trace demonstrates acceptance of an invalid proof, and no attacker-controlled path is established. Protocol security invariant: Proof verification should run with the circuit version and mode that match the active fork and validium setting when checking public inputs. Verification notes: The patch does not by itself prove that invalid proofs were previously accepted. The patch does not show a concrete attacker-controlled input path to force the wrong version or mode. The patch does not establish that a consensus split or production incident actually occurred. The new version-derivation helper itself notes incomplete coverage, so the exact pre-fix failure surface is not fully proven from this diff alone. No provided test diff or runtime evidence shows whether the old behavior caused false accepts, false rejects, or configuration-only failures. The commit subject is suggestive, but the snippets do not prove a security impact. The new `utils.Version(...)` helper includes a TODO noting incomplete coverage, which further weakens any strong security claim. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `verifier-configuration-mismatch`
Final impact type: `verification-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, proof-verification, validium, verifier-config`

The patch evidence supports a security-hardening classification. It shows that verifier initialization in a proof-validation path now carries explicit circuit version and validium-mode context, instead of relying on incomplete or implicit inputs, and the commit subject ties that change to PI-hash checking in validium mode. That is a meaningful tightening in a security-sensitive path. However, the supplied hunks do not show the PI-hash check itself, do not prove that invalid proofs were previously accepted, and do not establish a concrete exploit path, so this should not be treated as a confirmed security-fix.

## Security Evidence

1. Verifier config gains an explicit `version` field where the shown pre-patch struct had only `fork_name` and `assets_path`.
2. `NewVerifier` is changed to receive `cfg.L2.ValidiumMode`, making verifier setup mode-aware.
3. New helper `Version(hardForkName, ValidiumMode)` indicates the selected verification version depends on both fork and validium mode.
4. Supplied project context shows Rust verifier initialization using `Verifier::new(&cfg.assets_path, cfg.version)`, consistent with version-specific verification behavior.
5. Commit subject explicitly says it fixes PI-hash checking in validium mode, aligning with the config-plumbing changes.

## Missing Evidence

1. No before/after hunk shows the actual PI-hash checking logic being corrected.
2. No supplied test, trace, or incident evidence shows prior acceptance of invalid proofs.
3. No evidence proves the old behavior was attacker-triggerable rather than a correctness or misconfiguration issue.
4. The direct Rust diff proves logging changes; the functional verifier behavior is only inferred from surrounding context.

## Claim Boundaries

1. Supported: the change hardens verifier initialization by threading explicit version and validium-mode context.
2. Supported: the affected path is security-sensitive because it is part of proof verification / validator behavior.
3. Not supported: a concrete proof-validation bypass definitely existed before the patch.
4. Not supported: the patch alone proves consensus corruption, invalid state acceptance, or an exploitable vulnerability.
