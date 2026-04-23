---
case_id: case_20220407_b5cf8b667
project: nitro
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2022-04-07
source_refs:
  - git:b5cf8b6671428a5a8149295b251c077bad94d49e
  - "validator/challenge_manager.go:415"
  - "arbnode/node.go:574"
  - "validator/challenge_manager.go:121"
  - "validator/nitro_machine.go:45"
bug_class: module-root-mismatch
impact_type:
  - validator-misexecution
confidence: medium
tags:
  - validator
  - challenge-manager
  - module-root
  - wasm-machine
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes challenge-related machine loading so the validator can select a machine by module root instead of implicitly using the latest machine directory, and it adds an explicit module-root equality check before using the loaded machine. That supports correctness across machine-version changes, but the supplied evidence does not prove a security bug beyond that mismatch risk.

## Observed Patch Facts

1. In `validator/challenge_manager.go`, the patch adds `haveModuleRoot := initialFrozenMachine.GetModuleRoot()`.

2. In `arbnode/node.go`, the patch replaces `var blockValidator *validator.BlockValidator` with `execfile, err := os.Executable()`.

3. In `validator/challenge_manager.go`, the patch replaces `genesisBlockNum, err := txStreamer.GetGenesisBlockNumber()` with `callOpts := &bind.CallOpts{Context: ctx}`.

4. In `validator/nitro_machine.go`, the patch replaces `DefaultNitroMachineConfig.RootPath = filepath.Join(projectDir, "target", "machines",...` with `DefaultNitroMachineConfig.RootPath = filepath.Join(projectDir, "target", "machines")`.

## Project Context

Historical context from `validator/block_validator.go`, `validator/staker.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `validator/block_validator.go`, `validator/staker.go`. The strongest project-level identifiers around this patch are `RootPath`, `filepath`, `Join`, and `config`.

## Before/After Behavior

Before the patch, the default machine root path pointed at `target/machines/latest`, and the shown `createInitialMachine()` code cloned the loaded zero-step machine without first checking that its module root matched the challenge's expected root. After the patch, the root path points at the broader machines directory, `ReadLatestWasmModuleRoot()` reads `latest/module_root`, `NewChallengeManager()` reads on-chain challenge metadata and the latest module root, and `createInitialMachine()` rejects a loaded machine whose module root differs from `m.wasmModuleRoot`.

# Root Cause

The loader/configuration path was oriented around the latest machine artifact and the shown initialization path did not validate the loaded machine's module root against the challenge-specific expected root before use.

## Walkthrough

1. `validator/nitro_machine.go` changes the default root from `target/machines/latest` to `target/machines` and adds `ReadLatestWasmModuleRoot()` for explicit latest-root lookup.

2. `arbnode/node.go` updates validator machine configuration to point at the machines directory rather than a single latest-version directory.

3. `validator/challenge_manager.go` now reads `challengeInfo` from `con.Challenges(...)` and reads the latest module root, indicating challenge setup can distinguish latest from non-latest machines.

4. `validator/challenge_manager.go:createInitialMachine()` now calls `initialFrozenMachine.GetModuleRoot()` and compares it to `m.wasmModuleRoot`.

5. If the roots differ, the code now returns an error instead of cloning and continuing with the mismatched machine.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| validator/challenge_manager.go | 121 | challenge manager initialization now binds machine selection to the on-chain challenge `WasmModuleRoot` |
| validator/challenge_manager.go | 415 | initial machine creation now verifies the loaded machine's module root matches the expected challenge root |
| validator/nitro_machine.go | 45 | machine config root is widened from `latest` to the machine set base and adds latest-root lookup support |
| arbnode/node.go | 574 | node validator setup now points machine configuration at the machine directory needed for per-challenge version loading |

## Code Snippets

## Snippet 1

Context: `validator/challenge_manager.go:415` (changes a sensitive control or state-update path)

Before
```go
return err
	}
	machine := initialFrozenMachine.Clone()
	var blockHeader *types.Header
```
After
```go
return err
	}
	haveModuleRoot := initialFrozenMachine.GetModuleRoot()
	if haveModuleRoot != m.wasmModuleRoot {
		return errors.Errorf("loaded wrong module root %v expecting %v", haveModuleRoot, m.wasmModuleRoot)
	}
	machine := initialFrozenMachine.Clone()
	var blockHeader *types.Header
```

## Snippet 2

Context: `arbnode/node.go:574` (changes signature or replay validation logic)

Before
```go
}

	var blockValidator *validator.BlockValidator
	if config.BlockValidator.Enable {
		nitroMachineConfig := validator.DefaultNitroMachineConfig
		if config.Wasm.RootPath != "" {
			nitroMachineConfig.RootPath = config.Wasm.RootPath
		} else {
```
After
```go
}

	nitroMachineConfig := validator.DefaultNitroMachineConfig
	if config.Wasm.RootPath != "" {
		nitroMachineConfig.RootPath = config.Wasm.RootPath
	} else {
		execfile, err := os.Executable()
		if err != nil {
```

## Snippet 3

Context: `validator/challenge_manager.go:121` (changes signature or replay validation logic)

Before
```go
}

	genesisBlockNum, err := txStreamer.GetGenesisBlockNumber()
	if err != nil {
```
After
```go
}

	callOpts := &bind.CallOpts{Context: ctx}
	challengeInfo, err := con.Challenges(callOpts, new(big.Int).SetUint64(challengeIndex))
	if err != nil {
		return nil, err
	}
	latestModuleRoot, err := machineConfig.ReadLatestWasmModuleRoot()
```

## Snippet 4

Context: `validator/nitro_machine.go:45` (changes signature or replay validation logic)

Before
```go
_, thisfile, _, _ := runtime.Caller(0)
	projectDir := filepath.Dir(filepath.Dir(thisfile))
	DefaultNitroMachineConfig.RootPath = filepath.Join(projectDir, "target", "machines", "latest")
}

func (c NitroMachineConfig) ReadWasmModuleRoot() (common.Hash, error) {
	fileToRead := path.Join(c.RootPath, "module_root")
	fileBytes, err := ioutil.ReadFile(fileToRead)
```
After
```go
_, thisfile, _, _ := runtime.Caller(0)
	projectDir := filepath.Dir(filepath.Dir(thisfile))
	DefaultNitroMachineConfig.RootPath = filepath.Join(projectDir, "target", "machines")
}

func (c NitroMachineConfig) ReadLatestWasmModuleRoot() (common.Hash, error) {
	fileToRead := path.Join(c.RootPath, "latest", "module_root")
	fileBytes, err := ioutil.ReadFile(fileToRead)
```

# Fix Pattern

Replace implicit default artifact selection with identifier-based selection, then add a fail-closed validation check at use time.

## How It Was Fixed

The fix broadens machine configuration from a hardwired `latest` directory to the machine-set base directory, adds a helper to read the latest module root separately, consults challenge metadata during challenge-manager setup, and rejects any loaded machine whose computed module root does not match the expected challenge root.

# Why It Matters

1. Prevents silent use of the wrong machine version for a challenge.

2. Makes challenge execution depend on the expected module root instead of an implicit latest-path assumption.

3. Improves correctness during machine-version transitions or upgrades.

4. Does not by itself prove consensus impact, fund loss, or attacker-controlled exploitation.

# Evidence Notes

The strongest evidence is limited to machine-path selection and a new module-root equality check in `validator/challenge_manager.go`, plus configuration changes in `validator/nitro_machine.go` and `arbnode/node.go`. The commit subject, `Support loading a different machine for a challenge`, also reads like compatibility/correctness work. The provided excerpts do not show the full loader-selection branch, do not demonstrate an adversarial trigger, and do not establish a concrete security failure mode beyond possible validator-local mismatch or failed challenge handling. Protocol security invariant: Challenge execution should use a Nitro/WASM machine whose module root matches the challenge's expected `WasmModuleRoot`. The patch enforces that correctness invariant, but the provided evidence does not establish a concrete vulnerability or exploit path. Verification notes: The patch does not prove a remote attacker could choose arbitrary machine roots or bypass on-chain challenge data. It does not prove consensus state corruption; the likely failure mode may have been validator-local misexecution or failed challenge participation. It does not prove fund loss, slashing, or successful exploitation in production. It is not shown whether this was triggered by ordinary machine-version upgrades rather than adversarial behavior. Tests were updated alongside the implementation, but the supplied input does not show their assertions. The code supports a correctness invariant strongly. The security thesis is not established strongly enough from the provided evidence, so this should not be kept as a confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `module-root-mismatch`
Final impact type: `validator-misexecution`
Final confidence: `medium`
Final tags: `validator, challenge-manager, module-root, wasm-machine, hardening`

The patch adds a fail-closed check that the loaded WASM/Nitro machine’s module root matches the challenge’s expected on-chain `WasmModuleRoot`, and it changes loading logic from an implicit `latest` artifact to explicit per-challenge selection. In validator challenge execution, that is a meaningful integrity hardening step on a security-sensitive path. The evidence does not prove a concrete exploitable vulnerability, attacker control, or real-world impact, so this should be retained only as security hardening, not as a confirmed security bug fix.

## Security Evidence

1. `createInitialMachine()` now rejects a loaded machine when `GetModuleRoot()` does not equal the expected challenge module root.
2. `NewChallengeManager()` now reads `challengeInfo.WasmModuleRoot` from the contract and uses module-root-aware setup logic.
3. The default machine root changed from a hardwired `target/machines/latest` path to the broader machine set, enabling explicit artifact selection instead of implicit latest-version use.
4. The new behavior is fail-closed: a mismatch returns an error instead of cloning and using the machine.

## Missing Evidence

1. No proof that an attacker could influence machine selection or exploit the prior behavior remotely.
2. No patch evidence showing consensus break, fund loss, slashing, or a demonstrated security incident.
3. The supplied tests are not shown, so their assertions do not confirm a concrete security failure mode.

## Claim Boundaries

1. The evidence supports integrity hardening around validator challenge-machine selection and validation.
2. It does not prove a previously exploitable vulnerability; `security-fix` would be too strong.
3. The change may also be motivated by upgrade/version-compatibility correctness, as suggested by the commit subject.
