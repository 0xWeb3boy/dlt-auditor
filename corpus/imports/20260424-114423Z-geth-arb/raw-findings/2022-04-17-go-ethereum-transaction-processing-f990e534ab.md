---
case_id: case_20220417_f990e534ab
project: go-ethereum
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2022-04-17
source_refs:
  - git:f990e534abd40688ad8ba633558acd5b4764cc7a
  - "cmd/conf/config.go:188"
  - "cmd/deploy/deploy.go:63"
  - "arbnode/node.go:266"
  - "arbnode/node.go:273"
bug_class: container-least-privilege-hardening
impact_type:
  - privilege-reduction
  - defense-in-depth
confidence: medium
tags:
  - container
  - docker
  - least-privilege
  - non-root
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

This is best classified as likely security hardening, not a demonstrated vulnerability fix. The commit metadata explicitly says the nitro-node-dist Docker image was made non-root, which supports a least-privilege container-hardening finding. The shown Go changes are deployment and configuration plumbing: honoring a caller-provided NitroMachineConfig for WASM module-root lookup and removing separate ChainData handling. They do not support the heuristic baseline's transaction-processing, panic, cryptographic, replay, or consensus vulnerability claims.

## Observed Patch Facts

1. In `cmd/conf/config.go`, the patch replaces `// Make data directory relative to chain directory if not already absolute` with `return nil`.

2. In `cmd/deploy/deploy.go`, the patch replaces `deployPtr, err := arbnode.DeployOnL1(ctx, l1client, l1TransactionOpts, l1TransactionO...` with `machineConfig := validator.DefaultNitroMachineConfig`.

3. In `arbnode/node.go`, the patch replaces `func DeployOnL1(ctx context.Context, l1client arbutil.L1Interface, deployAuth *bind.T...` with `func DeployOnL1(ctx context.Context, l1client arbutil.L1Interface, deployAuth *bind.T...`.

4. In `arbnode/node.go`, the patch replaces `wasmModuleRoot, err = validator.DefaultNitroMachineConfig.ReadLatestWasmModuleRoot()` with `wasmModuleRoot, err = machineConfig.ReadLatestWasmModuleRoot()`.

## Project Context

The changed code sits primarily in `cmd/conf`, `cmd/deploy`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `arbnode/api.go`, `arbnode/transaction_streamer.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. The strongest project-level identifiers around this patch are `common`, `l1client`, `machineConfig`, and `wasmModuleRoot`.

## Before/After Behavior

Before the patch, according to commit metadata, the nitro-node-dist Docker image did not run non-root. After the patch, that distributed image was changed to run non-root, though the exact Dockerfile hunk is not included. Before the Go changes, cmd/deploy/deploy.go called DeployOnL1 without passing machine configuration, and DeployOnL1 used validator.DefaultNitroMachineConfig when wasmModuleRoot was empty. After the patch, the deploy command builds a NitroMachineConfig using wasmrootpath, passes it into DeployOnL1, and DeployOnL1 reads the latest WASM module root from that supplied config. PersistentConfig.ResolveDirectoryNames also stopped resolving and creating a separate ChainData directory, matching the commit note that --persistent.data was removed in favor of --persistent.chain.

# Root Cause

The only supported security-relevant cause is container privilege posture: the distributed Docker image was apparently running as root before this hardening change. The Go hunks show configuration correctness issues rather than an established security root cause: DeployOnL1 previously ignored caller-selected machine root path when deriving a missing WASM module root, and persistent storage had separate ChainData handling that was removed.

## Walkthrough

1. Commit metadata states that the nitro-node-dist Docker image was made non-root.

2. The file list includes Dockerfile, but no Dockerfile hunk is supplied, so the non-root claim is supported only at commit-metadata level.

3. cmd/deploy/deploy.go now initializes machineConfig from validator.DefaultNitroMachineConfig and sets RootPath from the wasmrootpath flag.

4. The deploy command passes machineConfig into arbnode.DeployOnL1.

5. arbnode/node.go changes DeployOnL1 to accept a validator.NitroMachineConfig parameter.

6. When wasmModuleRoot is empty, DeployOnL1 now calls machineConfig.ReadLatestWasmModuleRoot() instead of validator.DefaultNitroMachineConfig.ReadLatestWasmModuleRoot().

7. cmd/conf/config.go removes ChainData path resolution and directory creation from ResolveDirectoryNames.

8. No supplied hunk changes transaction decoding, mempool handling, block processing, cryptographic validation, replay protection, or consensus validation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| Dockerfile | 1 | Commit-level evidence says the distributed Docker image was changed to run non-root; exact hunk not provided. |
| cmd/deploy/deploy.go | 63 | Constructs a NitroMachineConfig from the wasmrootpath flag and passes it into rollup deployment. |
| arbnode/node.go | 266 | DeployOnL1 API now receives a validator.NitroMachineConfig instead of implicitly using the default config. |
| arbnode/node.go | 273 | Reads the latest WASM module root from the supplied machineConfig when no wasmModuleRoot is provided. |
| cmd/conf/config.go | 188 | Removes separate ChainData path resolution and directory creation from persistent configuration. |

## Code Snippets

## Snippet 1

Context: `cmd/conf/config.go:188` (changes a sensitive control or state-update path)

Before
```go
}

	// Make data directory relative to chain directory if not already absolute
	if !filepath.IsAbs(c.ChainData) {
		c.ChainData = path.Join(c.Chain, c.ChainData)
	}
	err = os.MkdirAll(c.ChainData, os.ModePerm)
	if err != nil {
```
After
```go
}

	return nil
}
```

## Snippet 2

Context: `cmd/deploy/deploy.go:63` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	deployPtr, err := arbnode.DeployOnL1(ctx, l1client, l1TransactionOpts, l1TransactionOpts.From, *authorizevalidators, common.HexToHash(*wasmmoduleroot), l2ChainId, arbnode.DefaultL1ReaderConfig)
	if err != nil {
		flag.Usage()
```
After
```go
}

	machineConfig := validator.DefaultNitroMachineConfig
	machineConfig.RootPath = *wasmrootpath

	deployPtr, err := arbnode.DeployOnL1(ctx, l1client, l1TransactionOpts, l1TransactionOpts.From, *authorizevalidators, common.HexToHash(*wasmmoduleroot), l2ChainId, arbnode.DefaultL1ReaderConfig, machineConfig)
	if err != nil {
		flag.Usage()
```

## Snippet 3

Context: `arbnode/node.go:266` (changes signature or replay validation logic)

Before
```go
}

func DeployOnL1(ctx context.Context, l1client arbutil.L1Interface, deployAuth *bind.TransactOpts, sequencer common.Address, authorizeValidators uint64, wasmModuleRoot common.Hash, chainId *big.Int, readerConfig L1ReaderConfig) (*RollupAddresses, error) {
	l1Reader := NewL1Reader(l1client, readerConfig)
	l1Reader.Start(ctx)
```
After
```go
}

func DeployOnL1(ctx context.Context, l1client arbutil.L1Interface, deployAuth *bind.TransactOpts, sequencer common.Address, authorizeValidators uint64, wasmModuleRoot common.Hash, chainId *big.Int, readerConfig L1ReaderConfig, machineConfig validator.NitroMachineConfig) (*RollupAddresses, error) {
	l1Reader := NewL1Reader(l1client, readerConfig)
	l1Reader.Start(ctx)
```

## Snippet 4

Context: `arbnode/node.go:273` (changes a consensus- or validator-sensitive branch)

Before
```go
if wasmModuleRoot == (common.Hash{}) {
		var err error
		wasmModuleRoot, err = validator.DefaultNitroMachineConfig.ReadLatestWasmModuleRoot()
		if err != nil {
			return nil, err
```
After
```go
if wasmModuleRoot == (common.Hash{}) {
		var err error
		wasmModuleRoot, err = machineConfig.ReadLatestWasmModuleRoot()
		if err != nil {
			return nil, err
```

# Fix Pattern

Apply least-privilege defaults to the distributed container image, and make deployment configuration explicit by passing caller-selected machine configuration into downstream deployment code instead of relying on global defaults.

## How It Was Fixed

The Docker distribution image was changed to run non-root according to commit metadata. The deployment path was updated so cmd/deploy/deploy.go constructs a NitroMachineConfig using the wasmrootpath flag and passes it to DeployOnL1; DeployOnL1 then uses that supplied config when reading the latest WASM module root. Persistent directory handling was simplified by removing separate ChainData resolution and creation.

# Why It Matters

1. Running the distributed node container as non-root reduces privileges available after container compromise.

2. The Go changes improve deployment/configuration correctness but do not prove a protocol vulnerability.

3. The evidence does not establish remote exploitability or denial of service.

4. The heuristic transaction-processing narrative is unsupported.

# Evidence Notes

The non-root security-hardening classification relies on commit subject/body and the listed Dockerfile change, not on an included Dockerfile diff hunk. The line-level evidence supports only deployment/configuration behavior in cmd/deploy/deploy.go, arbnode/node.go, and cmd/conf/config.go. Claims about malformed transactions, panics, mempool or block-processing interruption, cryptographic validation, replay protection, or consensus security should be removed. Protocol security invariant: No protocol-level consensus, replay, cryptographic, or transaction-validation invariant is established by the supplied hunks. The only security-relevant invariant supported by the input is least privilege for the distributed nitro-node-dist Docker image: it should run as a non-root user. Verification notes: The provided hunks do not prove remote exploitability. The provided hunks do not show malformed transaction handling, panic prevention, or mempool/block-processing behavior. The provided hunks do not show cryptographic validation or replay protection changes. The Docker non-root hardening is inferred from commit metadata because the Dockerfile diff hunk is not included. The WASM root path change supports deployment/configuration correctness, not a demonstrated consensus vulnerability. Verified against supplied evidence only; no external files or commands were used. Dockerfile behavior cannot be line-verified from the provided hunks. Security classification is limited to likely container hardening. Go hunks should be treated as supporting configuration changes, not as the root of a demonstrated vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `container-least-privilege-hardening`
Final impact type: `privilege-reduction, defense-in-depth`
Final confidence: `medium`
Final tags: `container, docker, least-privilege, non-root, security-hardening`

The strongest supported security relevance is container hardening: the commit subject/body explicitly say the distributed Docker image was made non-root, and Dockerfile is in the changed file list. That is a credible least-privilege improvement worth retaining as security-hardening, but the supplied line-level hunks mostly show deployment and configuration plumbing and do not support the original transaction-processing, liveness, consensus, replay, or cryptographic claims.

## Security Evidence

1. Commit subject says "Make docker dist image non-root".
2. Commit body says the nitro-node-dist Docker image was made non-root.
3. Dockerfile is listed among changed files.
4. Running a distributed node container as non-root is a least-privilege hardening measure.

## Missing Evidence

1. No Dockerfile hunk is supplied showing the actual USER change or permission adjustments.
2. No evidence of a concrete exploitable vulnerability or privilege-escalation path.
3. No supplied hunk shows transaction processing, mempool, block validation, replay protection, or cryptographic validation changes.
4. No test evidence specifically verifies non-root container execution.

## Claim Boundaries

1. Retain only as likely container security hardening, not a demonstrated vulnerability fix.
2. Do not classify as transaction-processing or liveness failure based on the supplied evidence.
3. The Go hunks support configuration/deployment correctness, not a protocol security fix.
4. No claim of remote exploitability, consensus failure, or validator compromise is supported.
