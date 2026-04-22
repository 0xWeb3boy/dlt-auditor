---
case_id: case_20260313_d54fbf46f
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2026-03-13
source_refs:
  - git:d54fbf46fce66f5713131f062a152c7181954431
  - "crates/proof/tee/core/src/types/config.rs:117"
  - "crates/proof/tee/core/src/types/config.rs:484"
  - "crates/proof/tee/nitro/src/enclave/server.rs:277"
  - "crates/proof/tee/nitro/src/enclave/server.rs:244"
bug_class: configuration-integrity
impact_type:
  - integrity
confidence: medium
tags:
  - tee
  - config-pinning
  - chain-allowlist
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a configuration-pinning and supported-chain enforcement change in the TEE proof path, but it does not establish a concrete vulnerability or attacker-controlled misuse in the prior code. This is best treated as security-relevant hardening with unproven exploitability, not a confirmed security fix.

## Observed Patch Facts

1. In `crates/proof/tee/core/src/types/config.rs`, the patch replaces `/// Serialize the config to binary format matching Go's 'MarshalBinary()'.` with `/// Create a 'PerChainConfig' from a ['RollupConfig'].`.

2. In `crates/proof/tee/core/src/types/config.rs`, the patch adds `/// Print config hashes for supported chains so they can be hardcoded in the`.

3. In `crates/proof/tee/nitro/src/enclave/server.rs`, the patch adds `#[test]`.

4. In `crates/proof/tee/nitro/src/enclave/server.rs`, the patch replaces `/// Create a server for testing (no NSM, no PCR0 verification).` with `mod tests {`.

## Project Context

The changed code sits primarily in `crates/proof/tee/core/src/types`, `crates/proof/tee/core/src`, `crates/proof/tee/nitro/src/enclave`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/proof/tee/nitro/src/enclave/crypto.rs`, `crates/proof/tee/core/src/types/rpc.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/proof/tee/nitro/src/enclave/crypto.rs`, `crates/proof/tee/core/src/types/rpc.rs`. The strongest project-level identifiers around this patch are `genesis`, `test`, `config`, and `ProofResult::Tee`.

## Before/After Behavior

Before the patch, the provided snippets show a test-only `new_for_testing(config: &EnclaveConfig)` path that copied `config.config_hash` into server state, and the cited `config.rs` location did not yet show `PerChainConfig::from_rollup_config`. After the patch, `config.rs` adds `PerChainConfig::from_rollup_config(cfg: &RollupConfig) -> Option<Self>`, adds an ignored helper test that prints config hashes for three supported chains so they can be hardcoded, and `server.rs` adds tests that an unknown chain ID errors and that hardcoded hashes match registry-derived values. That is evidence of tighter chain/config pinning, but not direct evidence of a previously exploitable flaw.

# Root Cause

At most, the evidence suggests the earlier design used a more flexible configuration path instead of clearly deriving and pinning enclave parameters from canonical per-chain data. The provided material does not prove that this flexibility created an actual vulnerability in production or that untrusted parties could control the old configuration source.

## Walkthrough

1. `crates/proof/tee/core/src/types/config.rs` adds `PerChainConfig::from_rollup_config`, which derives per-chain values from `RollupConfig` and returns `None` when `genesis.system_config` is absent.

2. The same file adds an ignored test helper that prints config hashes for three named chains and explicitly says those hashes can be hardcoded in the enclave server.

3. `crates/proof/tee/nitro/src/enclave/server.rs` adds tests showing `config_hash_for_chain(999999)` returns an error and that expected hashes match registry-derived values for supported chains.

4. A pre-patch snippet shows a test-only constructor taking `&EnclaveConfig` and copying `config.config_hash` into server state; this supports a refactor away from that pattern but does not by itself show unsafe production behavior.

5. The combined evidence supports deterministic configuration selection and allowlisting for known chains, but the record does not demonstrate replay, forgery, chain-confusion exploitation, or bypass of existing attestation checks.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/proof/tee/core/src/types/config.rs | 117 | Builds canonical per-chain config from `RollupConfig`, which is the basis for stable config-hash binding. |
| crates/proof/tee/core/src/types/config.rs | 484 | Defines the supported-chain config-hash baseline used to hardcode enclave-side parameters. |
| crates/proof/tee/nitro/src/enclave/server.rs | 277 | Enclave-side config-hash selection and rejection path for unknown chain IDs. |

## Code Snippets

## Snippet 1

Context: `crates/proof/tee/core/src/types/config.rs:117` (changes signature or replay validation logic)

Before
```rust
impl PerChainConfig {
    /// Serialize the config to binary format matching Go's `MarshalBinary()`.
    ///
```
After
```rust
impl PerChainConfig {
    /// Create a `PerChainConfig` from a [`RollupConfig`].
    ///
    /// Returns `None` if the rollup config is missing `genesis.system_config`.
    #[must_use]
    pub fn from_rollup_config(cfg: &RollupConfig) -> Option<Self> {
        let sc = cfg.genesis.system_config.as_ref()?;
```

## Snippet 2

Context: `crates/proof/tee/core/src/types/config.rs:484` (changes signature or replay validation logic)

Before
```rust
assert_eq!(rollup_config.hardforks.regolith_time, Some(0));
    }
}
```
After
```rust
assert_eq!(rollup_config.hardforks.regolith_time, Some(0));
    }

    /// Print config hashes for supported chains so they can be hardcoded in the
    /// enclave server. Run with:
    /// `cargo test -p base-enclave print_real_config_hashes -- --nocapture --ignored`
    #[test]
    #[ignore]
```

## Snippet 3

Context: `crates/proof/tee/nitro/src/enclave/server.rs:277` (changes signature or replay validation logic)

Before
```rust
assert_eq!(pk1, pk2);
    }
}
```
After
```rust
assert_eq!(pk1, pk2);
    }

    #[test]
    fn config_hash_unknown_chain() {
        assert!(config_hash_for_chain(999999).is_err());
    }
```

## Snippet 4

Context: `crates/proof/tee/nitro/src/enclave/server.rs:244` (changes signature or replay validation logic)

Before
```rust
Ok(ProofResult::Tee { aggregate_proposal, proposals })
    }

    /// Create a server for testing (no NSM, no PCR0 verification).
    #[cfg(test)]
    pub fn new_for_testing(config: &EnclaveConfig) -> Result<Self> {
        let signer_key = Ecdsa::generate(&mut rand_08::rngs::OsRng)?;
        Ok(Self {
```
After
```rust
Ok(ProofResult::Tee { aggregate_proposal, proposals })
    }
}

#[cfg(test)]
mod tests {
    use base_consensus_registry::Registry;
    use base_enclave::PerChainConfig;
```

# Fix Pattern

Replace a flexible configuration path with deterministic derivation of per-chain values from canonical rollup data, pin expected hashes for a fixed supported-chain set, and make unknown chain IDs fail explicitly.

## How It Was Fixed

The patch introduces a constructor that builds `PerChainConfig` from `RollupConfig`, adds support code to generate hardcoded config-hash baselines for specific chains, and adds tests asserting unknown chains are rejected and pinned hashes match registry-derived values. Those are concrete hardening steps toward deterministic enclave configuration, but the supplied evidence does not prove they remediate an already-exploitable bug.

# Why It Matters

1. It reduces ambiguity in how enclave configuration is selected for supported chains.

2. It makes unsupported chain IDs fail explicitly instead of leaving behavior open-ended.

3. It adds regression checks that pinned hashes stay aligned with canonical registry data.

4. It may strengthen a trust boundary, but the provided evidence does not establish a concrete prior vulnerability.

# Evidence Notes

Strongest evidence is limited to: the new `PerChainConfig::from_rollup_config` constructor, the added helper test that prints hashes intended for hardcoding, the new tests for unknown-chain rejection and hash matching, and the pre-patch test-only `new_for_testing(config: &EnclaveConfig)` snippet. The input does not show the full production data flow before and after, does not prove attacker control over `EnclaveConfig`, and does not show a concrete incorrect acceptance case. Claims about replay resistance, forgery prevention, PCR verification, or a confirmed host-to-enclave trust-boundary vulnerability are therefore unsupported by the supplied excerpts. Protocol security invariant: If this path is security-sensitive, enclave-side proof generation should use deterministic, canonical per-chain parameters for a known chain set and reject unsupported chains rather than relying on loosely supplied configuration. Verification notes: The patch does not prove the previous `EnclaveConfig` source was attacker-controlled in production. The diff alone does not demonstrate a working replay, chain-confusion, or forgery exploit. The evidence does not show a break in signature verification, PCR verification, or enclave key handling. Part of the change is baseline/test work to pin expected hashes; those additions alone do not establish exploitability. Verified only from the provided snippets and summaries; no independent code inspection was available. The evidence supports hardening/refactor claims more strongly than vulnerability claims. Unknown-chain rejection is directly evidenced by a test, but prior unsafe acceptance is not shown. Hardcoded-hash consistency is directly evidenced by tests, but exploitability of the old design is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `configuration-integrity`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `tee, config-pinning, chain-allowlist`

The supplied patch evidence supports a security-relevant hardening change in a sensitive TEE proof path: configuration is derived from canonical rollup data, config hashes are pinned for a fixed supported-chain set, and unknown chains are explicitly rejected. That narrows a trust boundary and reduces risky configuration flexibility. However, the excerpts do not prove that the prior behavior was attacker-controlled, exploitable in production, or already causing a concrete security failure, so this should be retained only as security-hardening, not as a confirmed security fix.

## Security Evidence

1. The commit subject/body explicitly says enclave configuration was removed and enclave parameters were hardcoded.
2. `PerChainConfig::from_rollup_config` derives per-chain values from `RollupConfig` and returns `None` when required system config is absent.
3. A new helper test says config hashes for supported chains are intended to be hardcoded in the enclave server.
4. A new enclave test asserts `config_hash_for_chain(999999)` returns an error, showing explicit rejection of unknown chains.
5. A new enclave test checks hardcoded config hashes against registry-derived values, evidencing deterministic pinning to canonical chain data.

## Missing Evidence

1. No production-path excerpt shows how the old `EnclaveConfig` was sourced or whether untrusted input could influence it.
2. No before/after code proves the enclave previously accepted an incorrect or attacker-chosen chain/config hash.
3. No concrete exploit, bypass, or integrity break is demonstrated in the supplied snippets.
4. No evidence shows a signature-verification, attestation, or PCR-verification flaw being fixed.

## Claim Boundaries

1. Supported: the patch hardens enclave configuration selection and supported-chain enforcement.
2. Supported: the change reduces ambiguity by pinning config hashes to known chains and rejecting unknown ones.
3. Not supported: the patch fixes a proven exploitable vulnerability in the prior code.
4. Not supported: the correct bug class is `liveness-failure`; the evidence points to configuration-integrity hardening instead.
