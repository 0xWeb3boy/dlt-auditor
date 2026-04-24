---
case_id: case_20251112_b7c0afd57d
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: core-logic
source_quality: medium
date: 2025-11-12
source_refs:
  - git:b7c0afd57d1d14dea3b9f9bb1dabb2b7cfe88a59
  - "op-deployer/pkg/deployer/artifacts/download.go:149"
  - "op-service/ioutil/tar.go:23"
  - "op-service/ioutil/tar.go:69"
  - "op-deployer/pkg/deployer/artifacts/download.go:174"
bug_class: archive-path-validation-hardening
impact_type:
  - out-of-directory-file-write
confidence: medium
tags:
  - archive-extraction
  - tar
  - path-sanitization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The visible security-relevant part of the commit tightens tar-entry path validation in shared extraction code, but the provided evidence does not establish that the prior code was actually exploitable as a confirmed vulnerability. The zstd-related changes are format-support work, not security evidence.

## Observed Patch Facts

1. In `op-deployer/pkg/deployer/artifacts/download.go`, the patch replaces `defer gzr.Close()` with `var decompressor io.ReadCloser`.

2. In `op-service/ioutil/tar.go`, the patch replaces `cleanedName := path.Clean(hdr.Name)` with `cleanedName, err := sanitizeTarPath(hdr.Name, outDir)`.

3. In `op-service/ioutil/tar.go`, the patch adds `// sanitizeTarPath ensures the path is safe to extract within the specified output di...`.

4. In `op-deployer/pkg/deployer/artifacts/download.go`, the patch adds `// isGzipCompressed checks if the data starts with gzip magic bytes (0x1f 0x8b)`.

## Project Context

The changed code sits primarily in `op-deployer/pkg/deployer/artifacts`, `op-deployer/pkg/deployer`, `op-service/ioutil`, which anchors the finding in the `core-logic` area of the project. Historical context from `op-service/ioutil/gzip.go`, `op-service/ioutil/gzip_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-service/ioutil/gzip.go`, `op-deployer/pkg/deployer/forge/binary.go`. The strongest project-level identifiers around this patch are `data`, `path`, `gzip`, and `NewReader`. Nearby tests or test-like files include `op-deployer/pkg/deployer/integration_test/cli/upgrade_test.go`, `op-deployer/pkg/deployer/integration_test/cli/command_test.go`.

## Before/After Behavior

Before the patch, `Untar` normalized each tar header name with `path.Clean(hdr.Name)`, rejected names only when the cleaned string contained `..`, and then joined the result with `outDir`. After the patch, `Untar` delegates that validation to `sanitizeTarPath(...)`, and the shown helper explicitly rejects absolute cleaned paths and cleaned paths containing `..` before destination-path construction. Separately, the caller in `download.go` changed from gzip-only decompression to gzip-or-zstd selection based on magic bytes.

# Root Cause

The pre-patch extraction path used a narrow inline check on tar header names rather than a dedicated helper with more explicit validation rules. The evidence supports incomplete or ad hoc path validation, but not a fully demonstrated exploitable path-traversal bug.

## Walkthrough

1. `TarballExtractor.Extract` reads artifact bytes, checks integrity, chooses a decompressor, builds a `tar.Reader`, and calls `ioutil.Untar`.

2. In the pre-patch `Untar` snippet, header names were processed with `path.Clean(hdr.Name)` and rejected only if the cleaned name contained `..`.

3. The patch replaces that inline logic with `sanitizeTarPath(hdr.Name, outDir)` and returns an error on validation failure before constructing `dst`.

4. The new helper, as shown, uses `filepath.Clean`, rejects absolute cleaned paths, and rejects cleaned paths containing `..`.

5. The zstd additions change decompression support in the caller, but the only clearly security-relevant delta in the evidence is the stricter tar-path validation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-deployer/pkg/deployer/artifacts/download.go | 141 | artifact extraction entrypoint that verifies integrity, chooses decompressor, and invokes untar |
| op-service/ioutil/tar.go | 15 | shared tar extraction loop where each header path is validated before destination path construction |
| op-service/ioutil/tar.go | 69 | new sanitization helper enforcing tar path safety checks |

## Code Snippets

## Snippet 1

Context: `op-deployer/pkg/deployer/artifacts/download.go:149` (changes a sensitive control or state-update path)

Before
```go
}

	gzr, err := gzip.NewReader(bytes.NewReader(data))
	if err != nil {
		return fmt.Errorf("failed to create gzip reader: %w", err)
	}
	defer gzr.Close()
```
After
```go
}

	var decompressor io.ReadCloser
	if e.isGzipCompressed(data) {
		gzr, err := gzip.NewReader(bytes.NewReader(data))
		if err != nil {
			return fmt.Errorf("failed to create gzip reader: %w", err)
		}
```

## Snippet 2

Context: `op-service/ioutil/tar.go:23` (changes a sensitive control or state-update path)

Before
```go
}

		cleanedName := path.Clean(hdr.Name)
		if strings.Contains(cleanedName, "..") {
			return fmt.Errorf("invalid file path: %s", hdr.Name)
		}
		dst := path.Join(outDir, cleanedName)
```
After
```go
}

		cleanedName, err := sanitizeTarPath(hdr.Name, outDir)
		if err != nil {
			return fmt.Errorf("invalid file path %q: %w", hdr.Name, err)
		}
		dst := path.Join(outDir, cleanedName)
```

## Snippet 3

Context: `op-service/ioutil/tar.go:69` (changes a sensitive control or state-update path)

Before
```go
return nil
}
```
After
```go
return nil
}

// sanitizeTarPath ensures the path is safe to extract within the specified output directory.
func sanitizeTarPath(tarPath, outDir string) (string, error) {
	cleaned := filepath.Clean(tarPath)

	if filepath.IsAbs(cleaned) {
```

## Snippet 4

Context: `op-deployer/pkg/deployer/artifacts/download.go:174` (changes a sensitive control or state-update path)

Before
```go
return nil
}
```
After
```go
return nil
}

// isGzipCompressed checks if the data starts with gzip magic bytes (0x1f 0x8b)
func (e *TarballExtractor) isGzipCompressed(data []byte) bool {
	return len(data) >= 2 && data[0] == 0x1f && data[1] == 0x8b
}
```

# Fix Pattern

Replace ad hoc inline archive-path checks with a shared sanitization helper and add explicit rejection of obviously unsafe path forms.

## How It Was Fixed

`Untar` now calls `sanitizeTarPath(...)` for each archive entry instead of performing its own minimal inline check. The shown helper makes absolute-path rejection explicit and preserves traversal-style rejection before path joining and file output. The same commit also adds zstd decompression support, which appears orthogonal to the path-validation change.

# Why It Matters

1. Shared extraction code is a better enforcement point than scattered per-call-site checks.

2. Explicit rejection of absolute archive paths narrows the set of names accepted during extraction.

3. The visible security relevance is limited to path-validation hardening; zstd support should not be treated as the vulnerability fix itself.

# Evidence Notes

In deep context, the real business path is artifact download and extraction in `op-deployer`, which delegates archive unpacking to `op-service/ioutil.Untar`. The security-significant change is replacing a simple `path.Clean` plus `strings.Contains("..")` check with dedicated tar-path sanitization that rejects absolute paths and traversal indicators before joining and writing files. That is a direct fix for archive extraction path traversal. The zstd-related hunks look like correctness/feature work attached to the same commit, not the main security classification. Protocol security invariant: When untarring deployment artifacts, archive entry names should resolve only to intended paths under the chosen output directory, and obviously unsafe names such as absolute paths should be rejected before files are written. Verification notes: The patch shows directory-escape prevention during untar, but does not by itself prove a remotely exploitable attack path. The evidence does not prove coverage for every tar edge case such as symlinks, hard links, or platform-specific path quirks beyond the shown checks. The zstd support and script changes are not, on the visible evidence, security fixes. The patch does not show a change to the integrity-check model itself; only extraction-path handling is clearly security-relevant. No proof-of-exploit or failing pre-patch test is provided in the input. The visible code supports a claim of stricter validation, not a fully confirmed path-traversal vulnerability. The zstd and script changes should be treated as adjacent feature/correctness work unless separate evidence shows security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `archive-path-validation-hardening`
Final impact type: `out-of-directory-file-write`
Final confidence: `medium`
Final tags: `archive-extraction, tar, path-sanitization`

The patch contains a clearly security-relevant change in shared tar extraction logic: it replaces an ad hoc path check with a dedicated sanitization helper and explicitly rejects absolute archive paths in addition to traversal markers. The commit body also names "tar transversal attack protection," which matches the code change. However, the provided evidence does not fully prove that the pre-patch code was exploitable in practice, so this is better retained as security hardening rather than a confirmed security bug fix. The zstd-related hunks are feature/correctness work and should not drive the classification.

## Security Evidence

1. Commit metadata explicitly mentions tar traversal attack protection.
2. Shared untar logic now calls a dedicated sanitizeTarPath helper before writing files.
3. New helper explicitly rejects absolute paths.
4. Validation still rejects traversal-style path components using ".." checks.
5. The change sits on an archive extraction path that writes files to disk.

## Missing Evidence

1. No failing pre-patch test or proof of exploit is shown.
2. The full sanitizeTarPath implementation is not provided, so complete before/after semantics are not visible.
3. The patch evidence does not show whether the old logic allowed escaping the output directory on all supported platforms.
4. No evidence is provided for symlink, hardlink, or other tar-header edge cases.

## Claim Boundaries

1. Supported claim: the commit hardens tar path validation during extraction.
2. Supported claim: absolute-path rejection was added explicitly.
3. Not supported: a fully confirmed exploitable path traversal vulnerability existed before the patch.
4. Not supported: the zstd decompression changes are themselves security fixes.
5. Not supported: the patch eliminates every archive extraction abuse case.
