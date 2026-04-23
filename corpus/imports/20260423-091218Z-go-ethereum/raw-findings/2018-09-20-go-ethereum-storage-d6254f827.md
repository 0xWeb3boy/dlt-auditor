---
case_id: case_20180920_d6254f827
project: go-ethereum
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: storage
confidence: medium
source_quality: high
date: 2018-09-20
source_refs:
  - git:d6254f827bf493c1471a806b7b8a0e9b86c8c420
  - "core/blockchain.go:971"
  - "core/blockchain.go:137"
  - "core/blockchain_test.go:524"
  - "core/bench_test.go:288"
bug_class: fork-choice-tie-break-hardening
impact_type:
  - canonical-chain-integrity
  - reorg-resistance
tags:
  - consensus
  - fork-choice
  - reorg
  - selfish-mining
  - tie-break
  - local-miner
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a security-hardening finding, not a confirmed vulnerability. In go-ethereum commit d6254f827, the equal-total-difficulty reorg tie-break in core/blockchain.go was changed from random same-height selection to logic intended to prefer preserving self-mined blocks. This affects canonical chain selection, but the provided evidence does not establish remote exploitability, validation bypass, or state corruption.

## Observed Patch Facts

1. In `core/blockchain.go`, the patch replaces `// Split same-difficulty blocks by number, then at random` with `// Split same-difficulty blocks by number, then preferentially select`.

2. In `core/blockchain.go`, the patch replaces `func NewBlockChain(db ethdb.Database, cacheConfig *CacheConfig, chainConfig *params.C...` with `func NewBlockChain(db ethdb.Database, cacheConfig *CacheConfig, chainConfig *params.C...`.

3. In `core/blockchain_test.go`, the patch replaces `ncm, err := NewBlockChain(blockchain.db, nil, blockchain.chainConfig, ethash.NewFaker...` with `ncm, err := NewBlockChain(blockchain.db, nil, blockchain.chainConfig, ethash.NewFaker...`.

4. In `core/bench_test.go`, the patch replaces `chain, err := NewBlockChain(db, nil, params.TestChainConfig, ethash.NewFaker(), vm.Co...` with `chain, err := NewBlockChain(db, nil, params.TestChainConfig, ethash.NewFaker(), vm.Co...`.

## Project Context

Historical context from `core/dao_test.go`, `core/chain_makers_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `accounts/abi/bind/backends/simulated.go`, `cmd/utils/flags.go`. The strongest project-level identifiers around this patch are `NumberU64`, `block`, `NewBlockChain`, and `Config`. Nearby tests or test-like files include `core/vm/runtime/fuzz.go`.

## Before/After Behavior

Before the patch, WriteBlockWithState reorged to a lower-number equal-total-difficulty block and randomly reorged with 50% probability for same-number equal-total-difficulty competitors. After the patch, the lower-number behavior remains, while same-height equal-total-difficulty handling is expanded to prefer the locally mined canonical block using a local-author callback. Constructor call sites were updated to pass the new callback argument, often nil in tests and benchmarks.

# Root Cause

The root cause was a random equal-total-difficulty, same-height fork-choice tie-break that did not account for whether the current canonical block was locally mined. This could cause a self-mined canonical block to be replaced by an external competitor solely due to randomness. The evidence does not support classifying this as persisted state corruption or a block validation flaw.

## Walkthrough

1. WriteBlockWithState writes block-related data and then evaluates whether an imported block should become canonical.

2. The old equal-total-difficulty branch used block number first, then a random 50% same-height tie-break.

3. That random tie-break did not consult local-author information, so self-mined blocks were not explicitly protected.

4. The patch adds an isLocalFn callback to BlockChain and NewBlockChain for local miner account detection.

5. The equal-total-difficulty branch is rewritten to make the same-height decision local-miner-aware rather than purely random.

6. Clique is excluded from the self-reorg-preserving behavior because the patch comment says it could introduce a deadlock.

7. Tests and benchmarks shown in the evidence only update constructor calls and do not independently prove the security property.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/blockchain.go | 965 | canonical chain selection after writing block state and receipts; decides whether equal-total-difficulty external block triggers reorg |
| core/blockchain.go | 90 | BlockChain state gains isLocalFn hook used to determine whether a block author is a local miner account |
| core/blockchain.go | 137 | NewBlockChain API accepts local-author detection callback so fork-choice can protect self-mined blocks |
| core/blockchain_test.go | 494 | test construction updated for new BlockChain signature; not direct security behavior |
| core/bench_test.go | 268 | benchmark construction updated for new BlockChain signature; not direct security behavior |

## Code Snippets

## Snippet 1

Context: `core/blockchain.go:971` (changes a sensitive control or state-update path)

Before
```go
currentBlock = bc.CurrentBlock()
	if !reorg && externTd.Cmp(localTd) == 0 {
		// Split same-difficulty blocks by number, then at random
		reorg = block.NumberU64() < currentBlock.NumberU64() || (block.NumberU64() == currentBlock.NumberU64() && mrand.Float64() < 0.5)
	}
	if reorg {
```
After
```go
currentBlock = bc.CurrentBlock()
	if !reorg && externTd.Cmp(localTd) == 0 {
		// Split same-difficulty blocks by number, then preferentially select
		// the block generated by the local miner as the canonical block.
		if block.NumberU64() < currentBlock.NumberU64() {
			reorg = true
		} else if block.NumberU64() == currentBlock.NumberU64() {
			if _, ok := bc.engine.(*clique.Clique); ok {
```

## Snippet 2

Context: `core/blockchain.go:137` (changes a consensus- or validator-sensitive branch)

Before
```go
// available in the database. It initialises the default Ethereum Validator and
// Processor.
func NewBlockChain(db ethdb.Database, cacheConfig *CacheConfig, chainConfig *params.ChainConfig, engine consensus.Engine, vmConfig vm.Config) (*BlockChain, error) {
	if cacheConfig == nil {
		cacheConfig = &CacheConfig{
```
After
```go
// available in the database. It initialises the default Ethereum Validator and
// Processor.
func NewBlockChain(db ethdb.Database, cacheConfig *CacheConfig, chainConfig *params.ChainConfig, engine consensus.Engine, vmConfig vm.Config, isLocalFn func(common.Address) bool) (*BlockChain, error) {
	if cacheConfig == nil {
		cacheConfig = &CacheConfig{
```

## Snippet 3

Context: `core/blockchain_test.go:524` (changes persisted or aggregate state handling)

Before
```go
// Create a new BlockChain and check that it rolled back the state.
	ncm, err := NewBlockChain(blockchain.db, nil, blockchain.chainConfig, ethash.NewFaker(), vm.Config{})
	if err != nil {
		t.Fatalf("failed to create new chain manager: %v", err)
```
After
```go
// Create a new BlockChain and check that it rolled back the state.
	ncm, err := NewBlockChain(blockchain.db, nil, blockchain.chainConfig, ethash.NewFaker(), vm.Config{}, nil)
	if err != nil {
		t.Fatalf("failed to create new chain manager: %v", err)
```

## Snippet 4

Context: `core/bench_test.go:288` (changes persisted or aggregate state handling)

Before
```go
b.Fatalf("error opening database at %v: %v", dir, err)
		}
		chain, err := NewBlockChain(db, nil, params.TestChainConfig, ethash.NewFaker(), vm.Config{})
		if err != nil {
			b.Fatalf("error creating chain: %v", err)
```
After
```go
b.Fatalf("error opening database at %v: %v", dir, err)
		}
		chain, err := NewBlockChain(db, nil, params.TestChainConfig, ethash.NewFaker(), vm.Config{}, nil)
		if err != nil {
			b.Fatalf("error creating chain: %v", err)
```

# Fix Pattern

Replace random consensus-adjacent tie-break behavior with explicit policy-aware fork-choice logic that can consult local node state, while preserving stronger-chain total-difficulty selection.

## How It Was Fixed

The patch added an isLocalFn func(common.Address) bool field to BlockChain and threaded it through NewBlockChain. The equal-total-difficulty reorg branch in core/blockchain.go was changed from a single random expression to explicit block-number comparison followed by same-height handling that preferentially preserves locally authored blocks. Non-exercising call sites pass nil for the new callback.

# Why It Matters

1. Canonical-head selection is security-sensitive consensus-adjacent behavior.

2. Random same-height equal-TD replacement could discard a locally mined canonical block.

3. The change reduces reliance on randomness in a reorg tie-break path.

4. The evidence supports hardening, not a proven exploit or validation bypass.

# Evidence Notes

Strongest evidence is core/blockchain.go around WriteBlockWithState line 965, where the equal-total-difficulty branch changes from random same-height selection to local-miner-preferential logic. Supporting evidence is the BlockChain struct and NewBlockChain signature gaining isLocalFn for local-author detection. The provided tests and benchmarks mainly show API call-site updates. Unsupported claims removed: storage/state corruption, remote attacker control, validation bypass, and confirmed vulnerability status. Protocol security invariant: When an imported block has total difficulty equal to the current canonical chain, fork choice should not randomly replace a locally authored canonical block with an external same-height competitor. The patch makes local-author preservation an explicit tie-break input, with Clique exempted due to a documented deadlock concern. Verification notes: The patch does not prove a remote attacker can force the losing reorg condition. The patch does not show persisted state corruption or validation bypass. The patch does not change block validity rules or total-difficulty comparison for stronger chains. Clique behavior is explicitly exempted because preserving self-reorg there may introduce deadlock. Most touched files are API call-site updates or tests rather than independent security fixes. No direct exploit or regression test output is provided in the input. The full replacement logic is only partially shown, so confidence is medium rather than high. The finding is bounded to equal-total-difficulty fork-choice hardening. Clique behavior is explicitly carved out by the patch comment. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `fork-choice-tie-break-hardening`
Final impact type: `canonical-chain-integrity, reorg-resistance`
Final tags: `consensus, fork-choice, reorg, selfish-mining, tie-break, local-miner`

The patch evidence supports retaining this as security hardening, not as a confirmed vulnerability or state-corruption fix. The key change removes a random same-height equal-total-difficulty reorg tie-break and replaces it with local-miner-aware canonical block selection in a consensus-adjacent path. The surrounding comment explicitly frames the reorg logic as reducing selfish-mining vulnerability, but the evidence does not prove exploitability, validation bypass, or persisted state corruption.

## Security Evidence

1. core/blockchain.go changes canonical-chain reorg selection for equal total difficulty blocks.
2. Old behavior randomly reorged on same-height equal-TD competitors with 50% probability.
3. New behavior preferentially preserves locally mined blocks as canonical, except for Clique.
4. BlockChain gains isLocalFn to determine whether a block author is a local miner account.
5. Adjacent code comment says the reorg clause reduces vulnerability to selfish mining.

## Missing Evidence

1. No exploit scenario or attacker-controlled path is shown.
2. No regression test directly demonstrating the security property is provided in the supplied evidence.
3. No evidence shows state corruption, storage corruption, or validation bypass.
4. Full replacement logic is only partially included in the evidence.

## Claim Boundaries

1. Classify as fork-choice hardening, not a confirmed security fix.
2. Do not claim remote exploitability from the supplied patch alone.
3. Do not retain the original storage or state-corruption framing.
4. Do not claim changed block validity rules; the change is limited to equal-total-difficulty canonical selection.
