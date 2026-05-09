---
case_id: case_20260427_7b7ffdd747
project: agave
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: validator-ops
source_quality: high
date: 2026-04-27
source_refs:
  - git:7b7ffdd7479b9fb4185b2187764e82fcd29cb450
  - "cli/src/validator_info.rs:130"
  - "cli/src/validator_info.rs:317"
  - "cli/src/validator_info.rs:615"
  - "cli/src/validator_info.rs:632"
bug_class: cli-validator-info-signer-check
impact_type:
  - metadata-authenticity-hardening
  - cli-trust-decision-hardening
confidence: medium
tags:
  - validator-ops
  - cli
  - validator-info
  - signer-check
  - metadata-authenticity
  - malformed-input-handling
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens CLI handling of validator-info accounts by carrying the validator pubkey signer flag out of parsing, skipping unsigned records when selecting existing publish metadata, and gracefully ignoring malformed or short validator-info data. The evidence supports CLI authenticity/display/selection hardening and robustness fixes, but does not establish an exploitable vulnerability or protocol-level security flaw.

## Observed Patch Facts

1. In `cli/src/validator_info.rs`, the patch replaces `pubkey: &Pubkey,` with `) -> Option<(Pubkey, bool, Map<String, serde_json::value::Value>)> {`.

2. In `cli/src/validator_info.rs`, the patch replaces `.find(|(pubkey, account)| {` with `.find(|(_, account)| {`.

3. In `cli/src/validator_info.rs`, the patch replaces `parse_validator_info(` with `parse_validator_info(&Account {`.

4. In `cli/src/validator_info.rs`, the patch replaces `parse_validator_info(` with `parse_validator_info(&Account {`.

## Project Context

The changed code sits primarily in `cli/src`, which anchors the finding in the `validator-ops` area of the project. Historical context from `cli/src/nonce.rs`, `cli/src/wallet.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `cli/src/nonce.rs`, `cli/src/wallet.rs`. The strongest project-level identifiers around this patch are `account`, `Account::default`, `Account`, and `solana_config_interface::id`.

## Before/After Behavior

Before the change, validator-info parsing returned only a validator pubkey and metadata, used fallible deserialization and indexing, and the publish path unwrapped parse results while scanning accounts. A malformed or one-key entry could break command processing, and a matching unsigned validator pubkey entry could be selected as existing metadata. After the change, parsing returns None for rejected or malformed data and includes signer status on success; the publish path only accepts a matching existing entry when signer status is true.

# Root Cause

CLI validator-info parsing did not preserve the validator pubkey signer bit for downstream selection logic, and scan-time parsing used error/unwrap-oriented behavior on account data that could be malformed or structurally incomplete.

## Walkthrough

1. The CLI scans config-program accounts while handling validator-info operations.

2. The old parser returned validator pubkey and JSON metadata but not whether the validator pubkey entry was marked signed.

3. The publish path selected an existing account by matching the validator pubkey to the configured signer without checking that signer flag.

4. The old scan also unwrapped parse results, so malformed validator-info-like data could abort command processing.

5. The new parser returns None for non-config-owned or unparsable data and returns the signer flag when parsing succeeds.

6. The publish path now ignores entries unless parsing succeeds with signer=true and the validator pubkey matches the configured signer.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| cli/src/validator_info.rs | 130 | Parses validator-info config accounts, rejects non-config-owned or malformed data, and returns the validator pubkey plus signer status. |
| cli/src/validator_info.rs | 317 | When publishing validator info, searches existing config accounts and now skips entries unless the matching validator pubkey is marked signed. |
| cli/src/validator_info.rs | 615 | Regression coverage for non-validator-info accounts now expecting parse failure as None rather than command-breaking errors. |
| cli/src/validator_info.rs | 632 | Regression coverage for malformed or empty-key validator-info data now expecting graceful rejection. |

## Code Snippets

## Snippet 1

Context: `cli/src/validator_info.rs:130` (changes a consensus- or validator-sensitive branch)

Before
```rust
fn parse_validator_info(
    pubkey: &Pubkey,
    account: &Account,
) -> Result<(Pubkey, Map<String, serde_json::value::Value>), Box<dyn error::Error>> {
    if account.owner != solana_config_interface::id() {
        return Err(format!("{pubkey} is not a validator info account").into());
    }
```
After
```rust
fn parse_validator_info(
    account: &Account,
) -> Option<(Pubkey, bool, Map<String, serde_json::value::Value>)> {
    if account.owner != solana_config_interface::id() {
        return None;
    }
    let key_list: ConfigKeys = deserialize(&account.data).ok()?;
```

## Snippet 2

Context: `cli/src/validator_info.rs:317` (changes a consensus- or validator-sensitive branch)

Before
```rust
},
        )
        .find(|(pubkey, account)| {
            let (validator_pubkey, _) = parse_validator_info(pubkey, account).unwrap();
            validator_pubkey == config.signers[0].pubkey()
        });
```
After
```rust
},
        )
        .find(|(_, account)| {
            let Some((validator_pubkey, true, _)) = parse_validator_info(account) else {
                return false;
            };
            validator_pubkey == config.signers[0].pubkey()
        });
```

## Snippet 3

Context: `cli/src/validator_info.rs:615` (changes an authorization or privilege gate)

Before
```rust
fn test_parse_validator_info_not_validator_info_account() {
        assert!(
            parse_validator_info(
                &Pubkey::default(),
                &Account {
                    owner: solana_pubkey::new_rand(),
                    ..Account::default()
                }
```
After
```rust
fn test_parse_validator_info_not_validator_info_account() {
        assert!(
            parse_validator_info(&Account {
                owner: solana_pubkey::new_rand(),
                ..Account::default()
            })
            .is_none()
        );
```

## Snippet 4

Context: `cli/src/validator_info.rs:632` (changes an authorization or privilege gate)

Before
```rust
assert!(
            parse_validator_info(
                &Pubkey::default(),
                &Account {
                    owner: solana_config_interface::id(),
                    data,
                    ..Account::default()
```
After
```rust
assert!(
            parse_validator_info(&Account {
                owner: solana_config_interface::id(),
                data,
                ..Account::default()
            },)
            .is_none()
```

# Fix Pattern

Propagate authenticity metadata from parsing to the trust decision, and replace unwrap-based iteration over account data with graceful rejection of invalid entries.

## How It Was Fixed

parse_validator_info was changed to take only an Account, return Option<(Pubkey, bool, Map<...>)>, reject invalid inputs with None, and expose the validator pubkey signer flag. process_publish_validator_info now filters for Some((validator_pubkey, true, _)) before treating an entry as existing validator info. Tests were updated to expect None for non-validator-info, empty-key, or malformed data cases.

# Why It Matters

1. Prevents unsigned validator-info entries from being treated as normal existing metadata in the CLI publish path.

2. Prevents malformed validator-info-like accounts from breaking CLI scans.

3. Improves CLI trust decisions around validator metadata.

4. Does not prove on-chain signature bypass, consensus impact, fund loss, or validator takeover.

# Evidence Notes

Grounded evidence is limited to cli/src/validator_info.rs parser changes, publish-path filtering, and regression tests. The commit message explicitly mentions signer checks and malformed/one-key validator-info fixes. Claims about consensus-critical validator logic, replay protection, state transitions, or on-chain authorization are unsupported by the supplied evidence. Protocol security invariant: No protocol-level security invariant is established by the supplied evidence. At the CLI layer, validator-info records should only be treated as normal existing validator metadata when they are config-program-owned, parse successfully, and the validator pubkey entry is marked signed. Verification notes: Does not prove a consensus-critical validator logic flaw. Does not prove transaction signature verification was bypassed on chain. Does not prove remote code execution, fund loss, or validator takeover. Does not prove malformed accounts can be created by an attacker in all relevant deployments. The demonstrated impact is CLI trust/display/selection hardening plus denial-of-service robustness. Code evidence supports a CLI behavior change, not a protocol vulnerability. Signer-status enforcement is shown in publish existing-account selection; get/display behavior is mentioned in the commit body but not fully evidenced in the supplied snippets. Malformed-account robustness is supported by parser return-type changes and tests. Keep out of a vulnerability corpus unless additional evidence demonstrates a concrete security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cli-validator-info-signer-check`
Final impact type: `metadata-authenticity-hardening, cli-trust-decision-hardening`
Final confidence: `medium`
Final tags: `validator-ops, cli, validator-info, signer-check, metadata-authenticity, malformed-input-handling`

The supplied patch evidence supports a conservative security-hardening classification: validator-info parsing now carries the signer flag, publish-time selection requires the matching validator pubkey to be signed, and malformed or structurally invalid records are ignored instead of unwrapped. This tightens CLI trust decisions around validator metadata, but the evidence does not prove an exploitable protocol vulnerability, replay flaw, consensus impact, or on-chain signature bypass.

## Security Evidence

1. Commit body explicitly says signer checks were added for validator-info get and publish.
2. parse_validator_info now returns a signer boolean alongside the validator pubkey and metadata.
3. process_publish_validator_info now requires Some((validator_pubkey, true, _)) before treating an existing record as matching.
4. Malformed or invalid validator-info-like accounts are rejected with None rather than causing unwrap/error-based command failure.

## Missing Evidence

1. No evidence of on-chain authorization bypass or transaction signature verification failure.
2. No demonstrated attacker-controlled exploit path beyond unsigned or malformed validator-info records being encountered by CLI commands.
3. No proof of consensus, fund-loss, validator takeover, or protocol-state impact.
4. Get/display behavior is described in the commit body but not fully shown in the supplied code snippets.

## Claim Boundaries

1. Classify as CLI validator metadata authenticity hardening, not a protocol security fix.
2. Do not retain the original replay-or-signature-validation framing; replay is not supported by the patch evidence.
3. Malformed-account handling is partly reliability/robustness and should not be overstated as a standalone vulnerability.
4. Security relevance is limited to rejecting unsigned validator-info records in CLI trust/display/selection paths.
