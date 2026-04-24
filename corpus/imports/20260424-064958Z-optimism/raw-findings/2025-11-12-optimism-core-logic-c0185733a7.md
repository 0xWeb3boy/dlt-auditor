---
case_id: case_20251112_c0185733a7
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
  - git:c0185733a7d0371458d93b26434021ad9c6e5847
  - "op-deployer/pkg/deployer/artifacts/download.go:149"
  - "op-service/ioutil/tar.go:23"
  - "op-service/ioutil/tar.go:63"
  - "op-deployer/pkg/deployer/artifacts/download.go:174"
bug_class: archive-extraction-path-validation
impact_type:
  - path-traversal-risk-reduction
  - filesystem-write-confinement
confidence: medium
tags:
  - archive-extraction
  - tar
  - path-validation
  - filesystem-write
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The provided evidence supports a tar-extraction hardening change, not a clearly established vulnerability fix. In `op-service/ioutil/tar.go`, inline path handling was replaced with a dedicated `sanitizeTarPath` helper that rejects absolute paths and traversal-containing names before extraction continues. The same commit also adds gzip/zstd decompressor selection in the artifact download path, which is supported as compatibility or correctness work rather than a security fix.

## Observed Patch Facts

1. In `op-deployer/pkg/deployer/artifacts/download.go`, the patch replaces `defer gzr.Close()` with `var decompressor io.ReadCloser`.

2. In `op-service/ioutil/tar.go`, the patch replaces `cleanedName := path.Clean(hdr.Name)` with `cleanedName, err := sanitizeTarPath(hdr.Name, outDir)`.

3. In `op-service/ioutil/tar.go`, the patch adds `// sanitizeTarPath ensures the path is safe to extract within the specified output di...`.

4. In `op-deployer/pkg/deployer/artifacts/download.go`, the patch adds `// isGzipCompressed checks if the data starts with gzip magic bytes (0x1f 0x8b)`.

## Project Context

The changed code sits primarily in `op-deployer/pkg/deployer/artifacts`, `op-deployer/pkg/deployer`, `op-service/ioutil`, which anchors the finding in the `core-logic` area of the project. Historical context from `op-service/ioutil/gzip.go`, `op-service/ioutil/gzip_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `op-service/ioutil/gzip.go`, `op-deployer/pkg/deployer/forge/binary.go`. The strongest project-level identifiers around this patch are `data`, `path`, `gzip`, and `NewReader`. Nearby tests or test-like files include `op-deployer/pkg/deployer/integration_test/cli/upgrade_test.go`, `op-deployer/pkg/deployer/integration_test/cli/command_test.go`.

## Before/After Behavior

Before the patch, the extractor always created a gzip reader and `Untar` used `path.Clean(hdr.Name)` plus a `strings.Contains(cleanedName, "..")` check before joining the result under `outDir`. After the patch, the extractor chooses gzip or zstd based on magic bytes and fails on unsupported formats, while `Untar` calls `sanitizeTarPath(hdr.Name, outDir)`, with visible checks for absolute paths and traversal-containing names.

# Root Cause

Tar member name validation was handled inline with a narrow ad hoc check instead of a dedicated sanitizer. The evidence shows that validation was tightened, but it does not prove that the previous behavior was exploitable in a real security sense.

## Walkthrough

1. `TarballExtractor.Extract` reads the archive, checks integrity, and then hands a decompressed stream to `ioutil.Untar`.

2. The decompression logic changed from unconditional gzip handling to explicit gzip-or-zstd detection with an error on unsupported formats.

3. Inside `Untar`, the old code cleaned `hdr.Name` and rejected names only when the cleaned string contained `..`.

4. The patch replaces that inline logic with `sanitizeTarPath(hdr.Name, outDir)`.

5. The visible helper code uses `filepath.Clean` and rejects absolute paths and traversal-containing names before path construction continues.

6. These changes clearly strengthen extraction-path validation, but the supplied snippets do not establish a concrete exploit path or show that the prior checks were bypassable in practice.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| op-deployer/pkg/deployer/artifacts/download.go | 141 | artifact extraction entrypoint that reads the tarball, checks integrity, chooses gzip or zstd decompression, and invokes untar |
| op-service/ioutil/tar.go | 15 | shared untar loop that validates each tar header name before creating output paths |
| op-service/ioutil/tar.go | 63 | new tar-path sanitization helper enforcing extraction confinement within the destination directory |

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

Context: `op-service/ioutil/tar.go:63` (changes a sensitive control or state-update path)

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

Replace inline archive-member path checks with a dedicated sanitizer in the shared extraction path, while making decompressor selection explicit and fail-closed for unsupported formats.

## How It Was Fixed

The shared untar routine now delegates member-name validation to `sanitizeTarPath` instead of performing a local `path.Clean` plus substring check. The new helper visibly rejects absolute paths and traversal-containing names. Separately, the artifact extractor was updated to detect gzip versus zstd input and reject unsupported compression formats before calling `Untar`.

# Why It Matters

1. Archive extraction writes files, so path validation deserves a centralized check.

2. The patch makes the acceptance policy for tar entry names more explicit.

3. The zstd-related changes should not be treated as evidence of a security issue by themselves.

4. The supplied evidence shows hardening, but not a proven vulnerability with a demonstrated exploit path.

# Evidence Notes

Grounded evidence exists for two changes: stronger tar member-name validation in `op-service/ioutil/tar.go`, and gzip/zstd decompressor dispatch in `op-deployer/pkg/deployer/artifacts/download.go`. The commit message mentions 'tar transversal attack protection', which supports security intent, but the code shown does not by itself prove exploitability, remote reachability, or that the old `path.Clean` plus `strings.Contains("..")` logic was insufficient in all relevant environments. The helper snippet also does not establish handling of symlinks, hardlinks, or other tar-header edge cases. Protocol security invariant: Archive extraction should validate member names before creating output paths, rejecting unsafe names such as absolute paths or traversal-like entries. Verification notes: The patch does not prove a remote exploit path; it shows a dangerous extraction invariant was previously under-enforced. The patch does not show whether attacker-controlled archives can bypass the existing integrity checker in normal deployments. The zstd support additions are not themselves evidence of a security bug. The visible hunks do not prove whether symlink, hardlink, or other tar header edge cases were also affected. The visible code supports classifying this as extraction-path hardening. The visible code does not prove a confirmed archive path traversal vulnerability. The zstd support changes are better treated as adjacent compatibility work. A stricter security classification would need stronger evidence of prior unsafe behavior or a concrete bypass. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `archive-extraction-path-validation`
Final impact type: `path-traversal-risk-reduction, filesystem-write-confinement`
Final confidence: `medium`
Final tags: `archive-extraction, tar, path-validation, filesystem-write, security-hardening`

The supplied patch evidence supports retaining this as a security-hardening case. The strongest security-relevant change is the untar path validation tightening: extraction now routes member names through a dedicated sanitizer that explicitly rejects absolute paths and traversal-like inputs before writing files. That is a clear hardening of a security-sensitive file-extraction path. The same commit also contains gzip/zstd support and packaging changes, so the evidence does not justify claiming a proven exploitable vulnerability fix.

## Security Evidence

1. Commit metadata explicitly mentions "tar transversal attack protection".
2. The untar path check changed from ad hoc inline validation to a dedicated sanitizeTarPath helper.
3. The new helper visibly rejects absolute paths during extraction.
4. The new helper also rejects traversal-containing paths, tightening confinement of extracted files under the output directory.

## Missing Evidence

1. No concrete exploit or test case shows the prior logic was bypassable.
2. The patch does not prove attacker-controlled archives are reachable in a real deployment path.
3. The visible hunks do not show whether symlink, hardlink, or other tar-header edge cases were also affected.

## Claim Boundaries

1. Supported: the patch hardens archive extraction path validation in a security-sensitive code path.
2. Not supported: the evidence proves a confirmed exploitable tar path traversal vulnerability existed before the patch.
3. Not supported: the gzip/zstd decompression changes are themselves security fixes rather than adjacent compatibility work.
