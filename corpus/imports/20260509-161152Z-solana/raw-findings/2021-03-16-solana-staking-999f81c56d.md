---
case_id: case_20210316_999f81c56d
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: staking
confidence: medium
source_quality: high
date: 2021-03-16
source_refs:
  - git:999f81c56da44930de0cc946553f9b9b6170975f
  - "sdk/src/feature_set.rs:218"
  - "programs/bpf_loader/src/syscalls.rs:1309"
  - "programs/bpf_loader/src/syscalls.rs:1016"
  - "programs/bpf_loader/src/syscalls.rs:1456"
bug_class: missing-resource-metering
impact_type:
  - resource-exhaustion
tags:
  - blockchain-core
  - bpf-loader
  - cpi
  - compute-budget
  - resource-accounting
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is a resource-metering hardening change in Solana's BPF loader CPI path. It adds the `cpi_data_cost` feature gate and, when active, charges the compute meter for CPI account data bytes in both Rust and C account translation paths. The evidence supports CPI byte-accounting hardening, but not an access-control, staking, privilege-escalation, funds-loss, or proven denial-of-service finding.

## Observed Patch Facts

1. In `sdk/src/feature_set.rs`, the patch replaces `(check_program_owner::id(), "limit programs to operating on accounts owned by itself")` with `(check_program_owner::id(), "limit programs to operating on accounts owned by itself"),`.

2. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `let data = translate_slice_mut::<u8>(` with `if invoke_context.is_feature_active(&cpi_data_cost::id()) {`.

3. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `let translated = translate(` with `if invoke_context.is_feature_active(&cpi_data_cost::id()) {`.

4. In `programs/bpf_loader/src/syscalls.rs`, the patch replaces `F: Fn(&T) -> Result<TranslatedAccount<'a>, EbpfError<BpfError>>,` with `F: Fn(&T, &Ref<&mut dyn InvokeContext>) -> Result<TranslatedAccount<'a>, EbpfError<Bp...`.

## Project Context

The changed code sits primarily in `sdk/src`, `programs/bpf_loader/src`, `programs/bpf_loader`, which anchors the finding in the `staking` area of the project. Historical context from `sdk/src/process_instruction.rs`, `sdk/src/nonce_keyed_account.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/process_instruction.rs`, `sdk/src/nonce_keyed_account.rs`. The strongest project-level identifiers around this patch are `cpi_data_cost::id`, `check_program_owner::id`, `invoke_context`, and `data`.

## Before/After Behavior

Before the patch, the shown CPI account translation paths proceeded without the added per-byte compute-meter charge for account data passed through CPI, and the shared translation helper did not pass `invoke_context` into the translation closure. After the patch, `cpi_data_cost::id()` is registered in the feature set, both Rust `AccountInfo` and C `SolAccountInfo` CPI translation paths consume compute based on data length divided by `cpi_bytes_per_unit`, and the helper signature is widened so translation code can access `invoke_context`.

# Root Cause

CPI account-data byte accounting was missing at the shown BPF loader account translation points. The shared helper also lacked the invoke context parameter needed to perform feature-gated compute metering inside the translation closure.

## Walkthrough

1. A BPF program enters CPI account translation through `programs/bpf_loader/src/syscalls.rs`.

2. The runtime translates account metadata and account data for Rust `AccountInfo` or C `SolAccountInfo` representations.

3. Before this change, the supplied hunks do not show a per-byte CPI account-data compute charge at those translation points.

4. The patch registers the `cpi_data_cost` feature gate in `sdk/src/feature_set.rs`.

5. When the feature is active, the Rust path charges compute using `data.len() as u64 / cpi_bytes_per_unit`.

6. When the feature is active, the C path charges compute using `account_info.data_len / cpi_bytes_per_unit`.

7. The shared translation helper now passes `invoke_context` into the translation closure so the metering code can access the feature set, compute budget, and compute meter.

8. The supported interpretation is resource-accounting hardening for CPI data bytes.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/src/feature_set.rs | 218 | registers the `cpi_data_cost` feature gate for charging compute budget on CPI data bytes |
| programs/bpf_loader/src/syscalls.rs | 1016 | charges compute units for Rust `AccountInfo` data length during CPI account translation |
| programs/bpf_loader/src/syscalls.rs | 1309 | charges compute units for C `SolAccountInfo` data length during CPI account translation |
| programs/bpf_loader/src/syscalls.rs | 1456 | threads invoke context into account translation helper so compute metering can occur inside translation |

## Code Snippets

## Snippet 1

Context: `sdk/src/feature_set.rs:218` (changes bounds, limits, or capacity handling)

Before
```rust
(per_byte_logging_cost::id(), "charge the compute budget per byte for logging"),
        (check_init_vote_data::id(), "check initialized Vote data"),
        (check_program_owner::id(), "limit programs to operating on accounts owned by itself")
        /*************** ADD NEW FEATURES HERE ***************/
    ]
```
After
```rust
(per_byte_logging_cost::id(), "charge the compute budget per byte for logging"),
        (check_init_vote_data::id(), "check initialized Vote data"),
        (check_program_owner::id(), "limit programs to operating on accounts owned by itself"),
        (cpi_data_cost::id(), "charge the compute budger for data passed via CPI"),
        /*************** ADD NEW FEATURES HERE ***************/
    ]
```

## Snippet 2

Context: `programs/bpf_loader/src/syscalls.rs:1309` (changes a sensitive control or state-update path)

Before
```rust
)?;
            let vm_data_addr = account_info.data_addr;
            let data = translate_slice_mut::<u8>(
                memory_mapping,
```
After
```rust
)?;
            let vm_data_addr = account_info.data_addr;

            if invoke_context.is_feature_active(&cpi_data_cost::id()) {
                invoke_context.get_compute_meter().consume(
                    account_info.data_len
                        / invoke_context.get_bpf_compute_budget().cpi_bytes_per_unit,
                )?;
```

## Snippet 3

Context: `programs/bpf_loader/src/syscalls.rs:1016` (changes a sensitive control or state-update path)

Before
```rust
self.loader_id,
                )?;
                let translated = translate(
                    memory_mapping,
```
After
```rust
self.loader_id,
                )?;

                if invoke_context.is_feature_active(&cpi_data_cost::id()) {
                    invoke_context.get_compute_meter().consume(
                        data.len() as u64
                            / invoke_context.get_bpf_compute_budget().cpi_bytes_per_unit,
                    )?;
```

## Snippet 4

Context: `programs/bpf_loader/src/syscalls.rs:1456` (changes a sensitive control or state-update path)

Before
```rust
) -> Result<TranslatedAccounts<'a>, EbpfError<BpfError>>
where
    F: Fn(&T) -> Result<TranslatedAccount<'a>, EbpfError<BpfError>>,
{
    let mut accounts = Vec::with_capacity(account_keys.len());
```
After
```rust
) -> Result<TranslatedAccounts<'a>, EbpfError<BpfError>>
where
    F: Fn(&T, &Ref<&mut dyn InvokeContext>) -> Result<TranslatedAccount<'a>, EbpfError<BpfError>>,
{
    let mut accounts = Vec::with_capacity(account_keys.len());
```

# Fix Pattern

Add feature-gated resource accounting at the point where CPI account data length is known, and apply the same accounting across equivalent Rust and C CPI translation paths by threading shared runtime context into the helper.

## How It Was Fixed

The fix adds `cpi_data_cost::id()` to the runtime feature set, inserts feature-gated `get_compute_meter().consume(...)` calls in both CPI account translation paths, and changes the account translation helper signature from a closure over only the account info object to one that also receives `invoke_context`.

# Why It Matters

1. CPI account data translation is runtime work and should be reflected in compute-budget accounting.

2. Both Rust and C CPI account representations receive byte-based metering.

3. The change reduces the risk that large CPI data payloads are processed outside the intended compute cost model.

4. The provided evidence does not establish authorization bypass, staking impact, funds loss, or a concrete denial-of-service exploit.

# Evidence Notes

Grounded evidence is limited to `sdk/src/feature_set.rs` registering `cpi_data_cost::id()` and `programs/bpf_loader/src/syscalls.rs` adding compute-meter consumption based on CPI account data length in Rust and C translation paths, plus helper context plumbing. The heuristic baseline's staking and access-control framing is unsupported by the changed code. No exploit transaction, denial-of-service threshold, consensus failure, account corruption, privilege escalation, or funds-loss behavior is demonstrated. Protocol security invariant: Cross-program invocation work should be covered by Solana's compute-budget accounting. Account data bytes passed through CPI should consume compute units so byte-heavy CPI account translation is not left outside the runtime cost model. Verification notes: No authorization, signer, ownership, or staking invariant is shown to be fixed by this patch. No concrete exploit path, denial-of-service threshold, or transaction construction is proven by the provided evidence. No account data corruption, privilege escalation, or funds-loss behavior is demonstrated. The feature-gated rollout suggests compatibility-controlled hardening as much as an immediate vulnerability fix. Confirmed changed files and hunks are in feature registration and BPF loader syscall account translation. Confirmed the added charge is feature-gated by `cpi_data_cost::id()`. Confirmed both Rust and C CPI account translation paths are covered by the shown evidence. No tests or exploit reproduction are provided in the input. Security classification is limited to likely hardening because practical exploitability is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-resource-metering`
Final impact type: `resource-exhaustion`
Final tags: `blockchain-core, bpf-loader, cpi, compute-budget, resource-accounting, security-hardening`

The evidence supports a security-hardening classification, not the original staking/access-control framing. The patch adds a feature-gated compute-budget charge for bytes passed through CPI account translation in both Rust and C BPF loader paths, which tightens resource accounting for runtime work. The supplied evidence does not prove a concrete exploitable denial-of-service bug, privilege misuse, staking impact, or funds loss.

## Security Evidence

1. Registers a new cpi_data_cost feature described as charging compute budget for data passed via CPI.
2. Adds compute-meter consumption based on CPI account data length in the Rust AccountInfo translation path.
3. Adds compute-meter consumption based on account_info.data_len in the C SolAccountInfo translation path.
4. Threads invoke_context into translation helper so feature-gated compute metering can be applied during account translation.

## Missing Evidence

1. No exploit transaction or reproduction demonstrating resource exhaustion is provided.
2. No denial-of-service threshold, consensus failure, or validator impact is shown.
3. No authorization, signer, ownership, staking, or privilege boundary fix is demonstrated.
4. No tests or commit text explicitly identify a security vulnerability.

## Claim Boundaries

1. Keep the finding limited to CPI data byte resource-accounting hardening.
2. Do not classify it as staking-related based on the shown patch.
3. Do not claim access-control, privilege escalation, funds loss, or confirmed DoS from this evidence alone.
4. The patch supports likely hardening against under-metered CPI data processing, not a proven security fix.
