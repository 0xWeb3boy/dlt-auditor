---
case_id: case_20250702_adac0404
project: scroll
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: medium
date: 2025-07-02
source_refs:
  - git:adac0404a03362600ca1c630cad5b434c236ad1b
  - "coordinator/cmd/tool/verify.go:95"
  - "crates/prover-bin/src/prover.rs:226"
  - "coordinator/cmd/tool/verify.go:54"
  - "coordinator/cmd/tool/verify.go:75"
bug_class: verifier-artifact-validation
impact_type:
  - integrity
confidence: medium
tags:
  - blockchain-core
  - proof-verification
  - verifier-key
  - trusted-artifact-selection
  - tooling
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The visible patch fixes verifier-tool behavior around verification-key handling and bundle verifier asset export. It corrects an inverted equality check for chunk and batch proofs, forces the bundle path to use the locally selected verifier key, and copies `verifier.bin` during asset export. That is clearly a correctness or hardening change in proof-verification tooling, but the provided evidence does not establish an exploitable vulnerability, a production attack boundary, or any on-chain security impact.

## Observed Patch Facts

1. In `coordinator/cmd/tool/verify.go`, the patch replaces `if len(proof.Vk) != 0 {` with `proof.Vk = vk`.

2. In `crates/prover-bin/src/prover.rs`, the patch replaces `Ok(())` with `// Copy verifier.bin from workspace bundle directory to output path`.

3. In `coordinator/cmd/tool/verify.go`, the patch replaces `if bytes.Equal(proof.Vk, vk) {` with `if !bytes.Equal(proof.Vk, vk) {`.

4. In `coordinator/cmd/tool/verify.go`, the patch replaces `if bytes.Equal(proof.Vk, vk) {` with `if !bytes.Equal(proof.Vk, vk) {`.

## Project Context

The changed code sits primarily in `coordinator/cmd/tool`, `coordinator/cmd`, `crates/prover-bin/src`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `coordinator/cmd/tool/tool.go`, `crates/prover-bin/src/zk_circuits_handler.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/prover-bin/src/zk_circuits_handler/euclidV2.rs`, `coordinator/cmd/tool/tool.go`. The strongest project-level identifiers around this patch are `proof`, `expected`, `Equal`, and `Errorf`.

## Before/After Behavior

Before the patch, the chunk and batch caller-side checks in `verify.go` returned an `unmatch vk` error when `proof.Vk` was equal to the expected local VK, so the shown precheck logic was inverted. The bundle path previously only populated `proof.Vk` conditionally; after the patch it overwrites `proof.Vk` with the locally loaded VK before calling `VerifyBundleProof`. In `prover.rs`, verifier asset dumping previously wrote `openVmVk.json` and returned; after the patch it also copies `bundle/verifier.bin` into the output directory when present.

# Root Cause

The shown root cause is inconsistent verifier-artifact handling in tooling: the chunk and batch mismatch predicate was reversed, the bundle path did not always normalize `proof.Vk` to the locally selected verifier key, and bundle asset export omitted `verifier.bin`. The evidence supports a tooling logic bug and packaging gap, not a demonstrated protocol-level vulnerability.

## Walkthrough

1. The `verify` CLI reads a proof file, selects a fork name, and loads fork-specific verifier material from local configuration.

2. In the chunk path, the pre-patch code returned an `unmatch vk` error when `bytes.Equal(proof.Vk, vk)` was true; the patch changes that to `!bytes.Equal(...)`, so the visible caller-side mismatch test now matches its error message.

3. The same predicate correction is applied to the batch path.

4. In the bundle path, the patch removes the older conditional handling and assigns `proof.Vk = vk` immediately before `VerifyBundleProof`, so the proof object passed onward uses the locally chosen VK.

5. In `dump_verifier_assets`, the patch adds a copy of `workspace_path/bundle/verifier.bin` into the output directory, which indicates bundle verification expects that binary alongside the JSON VK dump.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| coordinator/cmd/tool/verify.go | 54 | chunk proof VK mismatch guard corrected so locally expected VK is the acceptance criterion |
| coordinator/cmd/tool/verify.go | 75 | batch proof VK mismatch guard corrected with the same equality inversion fix |
| coordinator/cmd/tool/verify.go | 95 | bundle proof verification now injects the trusted fork-specific VK before calling `VerifyBundleProof` |
| crates/prover-bin/src/prover.rs | 226 | bundle verifier asset export now copies `verifier.bin` so bundle verification uses the expected verifier binary |

## Code Snippets

## Snippet 1

Context: `coordinator/cmd/tool/verify.go:95` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
return fmt.Errorf("no vk loaded for fork %s", forkName)
		}
		if len(proof.Vk) != 0 {
			if bytes.Equal(proof.Vk, vk) {
				return fmt.Errorf("unmatch vk with expected: expected %s, get %s",
					base64.StdEncoding.EncodeToString(vk),
					base64.StdEncoding.EncodeToString(proof.Vk),
				)
```
After
```go
return fmt.Errorf("no vk loaded for fork %s", forkName)
		}
		proof.Vk = vk

		ret, err = vf.VerifyBundleProof(proof, forkName)
```

## Snippet 2

Context: `crates/prover-bin/src/prover.rs:226` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
serde_json::to_writer(f, &dump)?;

        Ok(())
    }
```
After
```rust
serde_json::to_writer(f, &dump)?;

        // Copy verifier.bin from workspace bundle directory to output path
        let bundle_verifier_path = Path::new(workspace_path)
            .join("bundle")
            .join("verifier.bin");
        if bundle_verifier_path.exists() {
            let dest_path = out_path.join("verifier.bin");
```

## Snippet 3

Context: `coordinator/cmd/tool/verify.go:54` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}
		if len(proof.Vk) != 0 {
			if bytes.Equal(proof.Vk, vk) {
				return fmt.Errorf("unmatch vk with expected: expected %s, get %s",
					base64.StdEncoding.EncodeToString(vk),
```
After
```go
}
		if len(proof.Vk) != 0 {
			if !bytes.Equal(proof.Vk, vk) {
				return fmt.Errorf("unmatch vk with expected: expected %s, get %s",
					base64.StdEncoding.EncodeToString(vk),
```

## Snippet 4

Context: `coordinator/cmd/tool/verify.go:75` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}
		if len(proof.Vk) != 0 {
			if bytes.Equal(proof.Vk, vk) {
				return fmt.Errorf("unmatch vk with expected: expected %s, get %s",
					base64.StdEncoding.EncodeToString(vk),
```
After
```go
}
		if len(proof.Vk) != 0 {
			if !bytes.Equal(proof.Vk, vk) {
				return fmt.Errorf("unmatch vk with expected: expected %s, get %s",
					base64.StdEncoding.EncodeToString(vk),
```

# Fix Pattern

Normalize verifier inputs to trusted local artifacts, correct inverted mismatch checks, and export the full verifier asset set required by the verification path.

## How It Was Fixed

The patch changes the chunk and batch VK guard from `bytes.Equal(...)` to `!bytes.Equal(...)`, making unequal keys trigger the mismatch error rather than equal ones. It also sets `proof.Vk = vk` unconditionally in the bundle path before calling `VerifyBundleProof`. Separately, the prover-side asset export now copies `bundle/verifier.bin` into the output directory after writing `openVmVk.json`.

# Why It Matters

1. It fixes a visible logic error where equal verifier keys were treated as mismatches in the caller-side chunk and batch checks.

2. It makes the bundle verification call use the locally selected verifier key rather than leaving behavior dependent on proof-carried VK state.

3. It exports the verifier binary needed by the bundle verification asset set instead of only JSON metadata.

4. The evidence still stops at tooling behavior; exploitability and protocol impact are not shown.

# Evidence Notes

Direct evidence is limited but specific: `coordinator/cmd/tool/verify.go` changes the chunk and batch condition from `bytes.Equal(proof.Vk, vk)` to `!bytes.Equal(proof.Vk, vk)` at the shown lines, and the bundle path now assigns `proof.Vk = vk` immediately before `VerifyBundleProof`. `crates/prover-bin/src/prover.rs` adds logic to copy `bundle/verifier.bin` into the output directory after writing `openVmVk.json`. The supplied material does not include tests, `Verify*` implementation internals, or any evidence of an attacker-controlled production boundary. Protocol security invariant: Verification tooling should use the verifier artifacts selected by trusted local fork configuration. Embedded proof metadata should not override that selection, mismatch checks must reject unequal verifier keys rather than equal ones, and bundle verification assets must include the required verifier binary. Verification notes: The patch does not prove on-chain consensus or contract verification accepted invalid proofs. The patch does not prove `VerifyChunkProof` or `VerifyBundleProof` lacked additional internal defenses beyond the shown caller-side checks. The patch does not prove an attacker could reach this path in a production trust boundary rather than only operator tooling. The added `verifier.bin` copy could partly be a correctness or packaging fix; the diff alone does not show a full exploit chain. No test additions or execution results are provided in the supplied evidence. The visible diff does not show whether `VerifyChunkProof`, `VerifyBatchProof`, or `VerifyBundleProof` independently enforce the same verifier-artifact checks. The evidence does not show on-chain verifier behavior, consensus consequences, or a demonstrated exploit path. The added `verifier.bin` copy is consistent with a packaging or correctness fix; the security significance is plausible but not established by the provided patch alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `verifier-artifact-validation`
Final impact type: `integrity`
Final confidence: `medium`
Final tags: `blockchain-core, proof-verification, verifier-key, trusted-artifact-selection, tooling`

The patch is in a security-sensitive proof-verification path and clearly tightens how verifier artifacts are selected and checked: mismatched verification keys are now rejected, and bundle verification is forced to use the locally loaded trusted key instead of proof-supplied state. That supports keeping this as a security-hardening case. The evidence does not, however, prove a concrete exploitable vulnerability, production attack path, or invalid-proof acceptance in consensus-critical flows, so this should not be upgraded to a confirmed security fix.

## Security Evidence

1. The chunk and batch checks change from `bytes.Equal(proof.Vk, vk)` to `!bytes.Equal(proof.Vk, vk)`, so unequal verifier keys now trigger rejection instead of equal ones.
2. The bundle path now unconditionally sets `proof.Vk = vk` before `VerifyBundleProof`, preventing proof-carried VK state from controlling verifier selection in the shown caller path.
3. `dump_verifier_assets` now copies `bundle/verifier.bin`, indicating the verifier path depends on a complete trusted verifier artifact set rather than partial metadata alone.
4. All touched code is in proof/verifier handling rather than unrelated product or maintenance code.

## Missing Evidence

1. No implementation of `VerifyChunkProof`, `VerifyBatchProof`, or `VerifyBundleProof` is shown, so it is unclear whether deeper layers already enforced the same checks.
2. No tests, exploit demonstration, or bug report show that invalid proofs could actually be accepted before the change.
3. No evidence ties this CLI/tooling path to an exposed production trust boundary or on-chain consensus impact.
4. The `verifier.bin` copy could still be partly a packaging or reliability fix rather than a directly exploitable security issue.

## Claim Boundaries

1. This supports a security-hardening classification, not a proven exploitable security-fix classification.
2. The patch shows safer verifier-key and artifact handling in tooling; it does not prove consensus compromise or contract-level proof acceptance bugs.
3. It is safe to claim reduced risk of incorrect verifier selection or artifact misuse in proof verification.
4. It is not safe to claim a demonstrated integrity bypass, remote attack, or invalid-proof acceptance from the patch alone.
