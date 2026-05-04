---
case_id: case_20260325_a64cc7be
project: thor
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-03-25
source_refs:
  - git:a64cc7be626c0acfaae5d13cbbc1df3cf2d49e1b
  - "tx/clause_test.go:17"
  - "tx/reserved.go:41"
  - "tx/reserved_test.go:32"
  - "tx/clause.go:17"
bug_class: unbounded-rlp-list-decoding
impact_type:
  - resource-exhaustion-risk
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - rlp
  - input-validation
  - resource-limits
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is that the patch adds bounded decoding for transaction-related RLP lists: reserved fields are capped by `MaxUnusedReservedFields+1`, and clauses are decoded through a new `Clauses` wrapper that counts list items before decoding. The evidence supports resource-bound hardening, but not a confirmed or likely vulnerability.

## Observed Patch Facts

1. In `tx/clause_test.go`, the patch replaces `func TestClauseTo(t *testing.T) {` with `func makeClausesRLP(n int) []byte {`.

2. In `tx/reserved.go`, the patch adds `if len(raws) > MaxUnusedReservedFields+1 { // +1 for Features itself`.

3. In `tx/reserved_test.go`, the patch replaces `func TestReservedDecoding(t *testing.T) {` with `func TestReservedCountLimit(t *testing.T) {`.

4. In `tx/clause.go`, the patch replaces `type clauseBody struct {` with `// Clauses is a slice of *Clause with limitation on RLP decode.`.

## Project Context

Historical context from `tx/transaction.go`, `tx/tx_legacy.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `api/accounts/accounts_test.go`, `api/accounts/accounts.go`. The strongest project-level identifiers around this patch are `raws`, `MaxUnusedReservedFields`, `Clause`, and `clauses`. Nearby tests or test-like files include `tx/transaction_fuzz_test.go`.

## Before/After Behavior

Before the patch, the shown `reserved.DecodeRLP` path decoded `raws` and proceeded to trimming validation without a visible maximum count check. After the patch, it rejects lists longer than `MaxUnusedReservedFields+1`. Before the patch, the provided clause context does not show a custom bounded slice decoder. After the patch, `Clauses.DecodeRLP` pre-scans the raw RLP list, enforces `MaxClausesPerTx`, and only then decodes clause objects. Tests add coverage for excessive reserved fields and helper construction of encoded clause lists.

# Root Cause

Missing explicit decode-time cardinality checks for some list-shaped transaction RLP fields. The evidence does not show that this caused a crash, consensus issue, externally triggerable denial of service, or other concrete security impact.

## Walkthrough

1. `reserved.DecodeRLP` decodes reserved data into `[]rlp.RawValue`.

2. The patch adds a guard rejecting raw reserved lists whose length exceeds `MaxUnusedReservedFields+1`.

3. `tx/clause.go` introduces `type Clauses []*Clause` with a custom RLP decoder.

4. The new clause decoder reads the raw list, counts entries, compares the count with `MaxClausesPerTx`, and decodes only if the count is acceptable.

5. Tests add coverage for rejecting too many reserved fields and support clause-count limit testing.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| tx/reserved.go | 41 | Rejects RLP reserved-field lists whose raw item count exceeds MaxUnusedReservedFields plus the Features field. |
| tx/clause.go | 17 | Introduces bounded Clauses RLP decoder that counts list elements before decoding into Clause objects. |
| tx/reserved_test.go | 32 | Regression test proving excessive reserved-field count is rejected. |
| tx/clause_test.go | 17 | Test helper for constructing RLP-encoded clause lists to exercise clause-count limits. |
| api/accounts/accounts.go | 33 | Accounts API context includes batchDataMaxSize, but the exact changed guard is not shown in the provided evidence. |

## Code Snippets

## Snippet 1

Context: `tx/clause_test.go:17` (changes a sensitive control or state-update path)

Before
```go
)

func TestClauseTo(t *testing.T) {
	var toAddress thor.Address
```
After
```go
)

func makeClausesRLP(n int) []byte {
	clauses := make([]*Clause, n)
	for i := range clauses {
		clauses[i] = NewClause(nil).WithValue(big.NewInt(int64(i)))
	}
	data, err := rlp.EncodeToBytes(clauses)
```

## Snippet 2

Context: `tx/reserved.go:41` (changes bounds, limits, or capacity handling)

Before
```go
}

	if len := len(raws); len > 0 {
		if isEmptyRLPRaw(raws[len-1]) {
```
After
```go
}

	if len(raws) > MaxUnusedReservedFields+1 { // +1 for Features itself
		return fmt.Errorf("reserved field count exceeds limit: %d > %d", len(raws)-1, MaxUnusedReservedFields)
	}

	if len := len(raws); len > 0 {
		if isEmptyRLPRaw(raws[len-1]) {
```

## Snippet 3

Context: `tx/reserved_test.go:32` (changes bounds, limits, or capacity handling)

Before
```go
}

func TestReservedDecoding(t *testing.T) {
	cases := []struct {
```
After
```go
}

func TestReservedCountLimit(t *testing.T) {
	// MaxUnusedReservedFields+1 unused fields (MaxUnusedReservedFields+2 raws including Features) must be rejected.
	n := MaxUnusedReservedFields + 2
	raws := make([]rlp.RawValue, n)
	for i := range raws {
		raws[i] = rlp.RawValue{0x01}
```

## Snippet 4

Context: `tx/clause.go:17` (changes bounds, limits, or capacity handling)

Before
```go
)

type clauseBody struct {
	To    *thor.Address `rlp:"nil"`
```
After
```go
)

// Clauses is a slice of *Clause with limitation on RLP decode.
// DecodeRLP pre-scans raw items to enforce MaxClausesPerTx before
// allocating any Clause structs, preventing invalid clause list.
type Clauses []*Clause

// DecodeRLP implements rlp.Decoder.
```

# Fix Pattern

Add explicit list-size checks at RLP decoding boundaries before allocating or decoding per-item structures.

## How It Was Fixed

`tx/reserved.go` now returns an error when too many reserved raw fields are decoded. `tx/clause.go` now routes clause-list decoding through a bounded `Clauses.DecodeRLP` implementation. Tests were added or adjusted to exercise these bounds.

# Why It Matters

1. Bounds decoder work for oversized list-shaped inputs.

2. Keeps decoded transaction fields aligned with protocol constants.

3. Reduces resource-use risk, but exploitability is not shown.

# Evidence Notes

Grounded evidence comes from `tx/reserved.go`, `tx/clause.go`, `tx/reserved_test.go`, and `tx/clause_test.go`. The commit title mentions an accounts API return-size limit, but no concrete account API guard hunk is provided. Claims of panic, node crash, consensus divergence, liveness failure, or confirmed denial of service are unsupported by the supplied evidence. Protocol security invariant: RLP-decoded transaction list fields should respect protocol-defined count limits before downstream decoding or allocation. The provided evidence shows new count checks, but does not establish an exploitable security failure. Verification notes: No exploitability path is proven by the provided patch evidence. No process crash or panic condition is directly shown. No consensus divergence is shown. The account API wildcard return-size change is suggested by the commit title and file list, but not evidenced by a concrete hunk. This should be treated as resource-bound hardening unless additional evidence shows an externally triggerable denial of service. Count-limit checks are directly visible for reserved fields and clauses. Regression coverage is visible for reserved-field count rejection. No externally reachable attack path is demonstrated. No runtime failure mode beyond oversized decode acceptance is demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unbounded-rlp-list-decoding`
Final impact type: `resource-exhaustion-risk`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, rlp, input-validation, resource-limits, security-hardening`

The supplied evidence directly shows new decode-time cardinality limits for transaction RLP structures: reserved fields are capped and clause lists are pre-scanned against MaxClausesPerTx before allocating Clause objects. That is enough to treat the change as security hardening of untrusted or security-sensitive transaction parsing, but not enough to call it a confirmed security fix or liveness vulnerability because no exploit path, crash, consensus failure, or externally triggerable denial of service is demonstrated.

## Security Evidence

1. reserved.DecodeRLP now rejects raw reserved-field lists longer than MaxUnusedReservedFields+1.
2. Clauses.DecodeRLP is introduced to count RLP list items and enforce MaxClausesPerTx before decoding per-clause objects.
3. Tests add coverage for rejecting excessive reserved-field counts.
4. The changed code is in transaction-processing RLP decoding, a security-sensitive blockchain-core boundary.

## Missing Evidence

1. No demonstrated crash, panic, node halt, or consensus divergence.
2. No proof that oversized RLP inputs are externally reachable in an exploitable way.
3. No concrete denial-of-service measurement or resource exhaustion example.
4. The commit subject references an accounts API return-size limit, but no account API guard hunk is supplied.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Do not claim a confirmed liveness failure or denial of service.
3. Do not rely on the accounts API title beyond noting it is unsupported by the provided hunks.
4. Validated finding should be limited to bounded RLP decoding for transaction reserved fields and clauses.
