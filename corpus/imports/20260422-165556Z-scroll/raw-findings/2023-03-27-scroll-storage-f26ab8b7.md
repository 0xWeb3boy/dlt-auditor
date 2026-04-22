---
case_id: case_20230327_f26ab8b7
project: scroll
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: not-security
phase3_validated_as: not-security
phase3_keep_candidate: false
subsystem: storage
source_quality: medium
date: 2023-03-27
source_refs:
  - git:f26ab8b7273d2c5a9af80bfd431d7c34ea074104
  - "bridge/cmd/app/mock_app.go:76"
  - "common/docker/docker_app.go:121"
  - "common/docker/docker_app.go:153"
  - "common/docker/docker_app.go:201"
bug_class: insecure-file-permissions
impact_type:
  - local-information-disclosure
confidence: medium
tags:
  - filesystem-permissions
  - configuration-files
  - ci
  - test-infrastructure
  - local-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a narrow permission tightening in mock/CI helper code, not a demonstrated vulnerability fix. The commit is titled `fix ci`, most touched files are tests or mock helpers, and the other shown hunks are receiver renames with no evidenced security effect.

## Observed Patch Facts

1. In `bridge/cmd/app/mock_app.go`, the patch replaces `return os.WriteFile(b.bridgeFile, data, 0644)` with `return os.WriteFile(b.bridgeFile, data, 0600)`.

2. In `common/docker/docker_app.go`, the patch replaces `func (b *DockerApp) L1Client() (*ethclient.Client, error) {` with `func (b *App) L1Client() (*ethclient.Client, error) {`.

3. In `common/docker/docker_app.go`, the patch replaces `func (b *DockerApp) L2Client() (*ethclient.Client, error) {` with `func (b *App) L2Client() (*ethclient.Client, error) {`.

4. In `common/docker/docker_app.go`, the patch replaces `func (b *DockerApp) mockDBConfig() error {` with `func (b *App) mockDBConfig() error {`.

## Project Context

The changed code sits primarily in `bridge/cmd/app`, `bridge/cmd`, `common/docker`, which anchors the finding in the `storage` area of the project. Historical context from `common/docker/docker_test.go`, `common/docker/interface.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `common/docker/docker_test.go`, `common/docker/interface.go`. The strongest project-level identifiers around this patch are `ethclient`, `error`, `running`, and `L1Client`.

## Before/After Behavior

Before the patch, `BridgeApp.MockBridgeConfig(store bool)` marshaled a generated bridge config and wrote it with `os.WriteFile(..., 0644)`. After the patch, the same helper writes the file with `0600`. The supplied `common/docker/docker_app.go` hunks only rename method receivers from `*DockerApp` to `*App` and do not show a behavioral security change.

# Root Cause

A mock/test helper persisted its generated config file with broader filesystem permissions than after the patch. The provided material does not show that this was a production code path, that the file necessarily contained secrets, or that an actual vulnerability or exploit path existed.

## Walkthrough

1. The only direct behavioral change in the evidence is `os.WriteFile(b.bridgeFile, data, 0644)` becoming `os.WriteFile(b.bridgeFile, data, 0600)` in `bridge/cmd/app/mock_app.go`.

2. The function name `MockBridgeConfig` and file name `mock_app.go` indicate helper or test-support code rather than a clearly production-facing path.

3. The surrounding context shows the helper fills a config with runtime endpoint values and a DB DSN, then optionally stores it to a temp file.

4. That supports a local file-permission hardening reading, but not a stronger claim about a proven credential leak or remotely exploitable issue.

5. The other supplied hunks in `common/docker/docker_app.go` are receiver renames only; no changed checks, parsing, authorization, or state-transition logic is shown.

6. The commit subject `fix ci` and the heavy concentration of changed test files further support classifying this as CI/test infrastructure work rather than a confirmed security fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| bridge/cmd/app/mock_app.go | 53 | writes the mock bridge configuration to disk; file mode changed from world-readable to owner-only |
| common/docker/docker_app.go | 102 | test/docker helper for L1 client access; receiver rename only, no direct security invariant shown |
| common/docker/docker_app.go | 134 | test/docker helper for L2 client access; receiver rename only, no direct security invariant shown |
| common/docker/docker_app.go | 197 | test/docker DB config helper; receiver rename only, no direct security invariant shown |

## Code Snippets

## Snippet 1

Context: `bridge/cmd/app/mock_app.go:76` (changes a sensitive control or state-update path)

Before
```go
return err
	}
	return os.WriteFile(b.bridgeFile, data, 0644)
}
```
After
```go
return err
	}
	return os.WriteFile(b.bridgeFile, data, 0600)
}
```

## Snippet 2

Context: `common/docker/docker_app.go:121` (changes a sensitive control or state-update path)

Before
```go
// L1Client returns a ethclient by dialing running l1geth
func (b *DockerApp) L1Client() (*ethclient.Client, error) {
	if b.L1gethImg == nil || reflect2.IsNil(b.L1gethImg) {
		return nil, fmt.Errorf("l1 geth is not running")
```
After
```go
// L1Client returns a ethclient by dialing running l1geth
func (b *App) L1Client() (*ethclient.Client, error) {
	if b.L1gethImg == nil || reflect2.IsNil(b.L1gethImg) {
		return nil, fmt.Errorf("l1 geth is not running")
```

## Snippet 3

Context: `common/docker/docker_app.go:153` (changes a sensitive control or state-update path)

Before
```go
// L2Client returns a ethclient by dialing running l2geth
func (b *DockerApp) L2Client() (*ethclient.Client, error) {
	if b.L2gethImg == nil || reflect2.IsNil(b.L2gethImg) {
		return nil, fmt.Errorf("l2 geth is not running")
```
After
```go
// L2Client returns a ethclient by dialing running l2geth
func (b *App) L2Client() (*ethclient.Client, error) {
	if b.L2gethImg == nil || reflect2.IsNil(b.L2gethImg) {
		return nil, fmt.Errorf("l2 geth is not running")
```

## Snippet 4

Context: `common/docker/docker_app.go:201` (changes a sensitive control or state-update path)

Before
```go
}

func (b *DockerApp) mockDBConfig() error {
	if b.DBConfig == nil {
		b.DBConfig = &database.DBConfig{
```
After
```go
}

func (b *App) mockDBConfig() error {
	if b.DBConfig == nil {
		b.DBConfig = &database.DBConfig{
```

# Fix Pattern

Tighten filesystem permissions on a generated helper file in test or CI support code.

## How It Was Fixed

The patch changes the file mode used when storing the mock bridge config from `0644` to `0600`, limiting access to the owner. No additional security-relevant logic change is established by the provided receiver-rename hunks.

# Why It Matters

1. It shows a local permission hardening on a file write.

2. It does not, by itself, prove a production confidentiality bug.

3. The surrounding change set is dominated by CI, tests, and mock helpers.

4. The receiver renames do not provide evidence for a broader security thesis.

# Evidence Notes

Grounded evidence is limited to one permission change in `bridge/cmd/app/mock_app.go` and three receiver renames in `common/docker/docker_app.go`. The draft's broader security framing overreaches what the supplied code proves. The config content may be operationally useful, but the evidence does not establish mandatory secrets, production exposure, or exploitability. Protocol security invariant: No production or protocol security invariant is established by the provided evidence. The only concrete semantic change is that a mock bridge configuration file in helper/test-oriented code is written with mode `0600` instead of `0644`. Verification notes: The patch does not prove the config file contains credentials in every execution path. No remote attack path or privilege-escalation path is demonstrated by the diff alone. The DockerApp-to-App receiver changes appear structural and are not evidenced as security fixes. The diff shows local file-permission hardening, not a protocol-level bridge validation change. No evidence shows `mock_app.go` is on a production execution path. No evidence shows the written DSN necessarily contains credentials rather than only connectivity data. No exploit path, privilege boundary crossing, or protocol violation is demonstrated. The `common/docker/docker_app.go` changes are structural receiver renames only. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `insecure-file-permissions`
Final impact type: `local-information-disclosure`
Final confidence: `medium`
Final tags: `filesystem-permissions, configuration-files, ci, test-infrastructure, local-hardening`

The supplied patch does not support a concrete vulnerability fix, but it does show a real security-relevant hardening: a generated bridge configuration file is no longer written world-readable (`0644`) and is instead owner-only (`0600`). The same helper populates `DBConfig.DSN` before writing, so the file plausibly carries sensitive configuration data. The rest of the shown hunks are structural receiver renames and do not add security weight. Given the CI/mock context, this should be retained only as a narrow local hardening case, not as a confirmed security bug fix.

## Security Evidence

1. `os.WriteFile(b.bridgeFile, data, 0644)` changed to `os.WriteFile(..., 0600)`.
2. The written object includes `b.Config.DBConfig.DSN` before serialization.
3. The change reduces exposure from broadly readable to owner-only file permissions.
4. This is a direct mitigation of local configuration-file exposure risk, even if limited to helper/CI paths.

## Missing Evidence

1. No proof that `DBConfig.DSN` always contains credentials or other secrets.
2. No proof that `mock_app.go` is used in a production-facing execution path.
3. No demonstrated exploit, attacker model, or observed confidentiality breach.
4. No evidence that the receiver renames in `common/docker/docker_app.go` affect security behavior.

## Claim Boundaries

1. Treat this as local filesystem-permission hardening, not a confirmed exploitable vulnerability fix.
2. Do not claim remote attack impact, privilege escalation, or protocol-level security effects.
3. Do not generalize the receiver-renaming hunks as security changes.
4. Scope the finding to mock/CI helper code that writes generated bridge configuration files.
