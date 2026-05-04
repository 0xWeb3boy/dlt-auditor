---
case_id: case_20240802_07b7f15dc1
project: avalanchego
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2024-08-02
source_refs:
  - git:07b7f15dc1a8f6be9acb13e295ae1525052ec7df
  - "plugin/evm/block_verification.go:288"
  - "consensus/dummy/consensus.go:264"
  - "plugin/evm/vm_test.go:4093"
  - "core/state_processor_test.go:118"
bug_class: invalid-header-validation
impact_type:
  - consensus-integrity
confidence: medium
tags:
  - consensus
  - header-validation
  - eip-4844
  - blob-gas
  - protocol-invariant
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Likely security fix for a Cancun header validation gap. The patch adds explicit rejection of Avalanche EVM headers that report positive BlobGasUsed, enforcing the local no-blobs rule in both EVM block syntactic verification and dummy consensus header verification.

## Observed Patch Facts

1. In `plugin/evm/block_verification.go`, the patch replaces `return nil` with `if ethHeader.BlobGasUsed == nil {`.

2. In `consensus/dummy/consensus.go`, the patch adds `if *header.BlobGasUsed > 0 { // VerifyEIP4844Header ensures BlobGasUsed is non-nil`.

3. In `plugin/evm/vm_test.go`, the patch replaces `func TestMinFeeSetAtEUpgrade(t *testing.T) {` with `func TestNoBlobsAllowed(t *testing.T) {`.

4. In `core/state_processor_test.go`, the patch replaces `blockchain, _ = NewBlockChain(db, DefaultCacheConfig, gspec, dummy.NewCoinbaseFaker()...` with `// FullFaker used to skip header verification that enforces no blobs.`.

## Project Context

The changed code sits primarily in `plugin/evm`, `consensus/dummy`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/state_transition.go`, `core/state_processor.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `plugin/evm/vm.go`, `plugin/evm/tx.go`. The strongest project-level identifiers around this patch are `BlobGasUsed`, `gspec`, `Errorf`, and `ethHeader`. Nearby tests or test-like files include `core/vm/contracts_fuzz_test.go`, `core/types/rlp_fuzzer_test.go`.

## Before/After Behavior

Before the patch, the shown Cancun validation paths checked ParentBeaconRoot and EIP-4844 header structure but did not enforce that BlobGasUsed was zero. After the patch, Cancun headers with nil BlobGasUsed are rejected in block syntactic verification, and headers with BlobGasUsed greater than zero are rejected in both block and consensus header verification.

# Root Cause

The Cancun header validation logic did not fully encode Avalanche's local protocol rule that blobs are disabled. Generic Cancun/EIP-4844 field-shape validation was present, but the Avalanche-specific zero BlobGasUsed invariant was missing from the shown acceptance paths.

## Walkthrough

1. A Cancun-era block header reaches EVM syntactic verification.

2. The pre-patch code validates ParentBeaconRoot but the provided snippet shows no BlobGasUsed presence or zero-value enforcement before success.

3. A Cancun-era header can also reach dummy consensus header verification.

4. That path calls VerifyEIP4844Header, which the patch comment says ensures BlobGasUsed is non-nil.

5. Before the patch, the shown consensus path did not reject a header solely because BlobGasUsed was positive.

6. After the patch, both validation paths return an error when BlobGasUsed is greater than zero.

7. The added test constructs a Cancun block with a blob transaction to cover the no-blobs rejection behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| plugin/evm/block_verification.go | 288 | EVM block syntactic verification now requires BlobGasUsed to be non-nil in Cancun and rejects positive blob gas on Avalanche networks. |
| consensus/dummy/consensus.go | 264 | Consensus header verification now rejects Cancun headers with BlobGasUsed greater than zero after EIP-4844 header validation. |
| plugin/evm/vm_test.go | 4093 | Regression test constructs a Cancun block with a blob transaction and expects rejection. |
| core/state_processor_test.go | 118 | Test harness switches to a faker that skips header verification where blob rejection would otherwise block state-processor error tests. |

## Code Snippets

## Snippet 1

Context: `plugin/evm/block_verification.go:288` (changes a sensitive control or state-update path)

Before
```go
return fmt.Errorf("invalid parentBeaconRoot: have %x, expected empty hash", ethHeader.ParentBeaconRoot)
		}
	}
	return nil
```
After
```go
return fmt.Errorf("invalid parentBeaconRoot: have %x, expected empty hash", ethHeader.ParentBeaconRoot)
		}
		if ethHeader.BlobGasUsed == nil {
			return fmt.Errorf("blob gas used must not be nil in Cancun")
		} else if *ethHeader.BlobGasUsed > 0 {
			return fmt.Errorf("blobs not enabled on avalanche networks: used %d blob gas, expected 0", *ethHeader.BlobGasUsed)
		}
	}
```

## Snippet 2

Context: `consensus/dummy/consensus.go:264` (changes a sensitive control or state-update path)

Before
```go
return err
		}
	}
	return nil
```
After
```go
return err
		}
		if *header.BlobGasUsed > 0 { // VerifyEIP4844Header ensures BlobGasUsed is non-nil
			return fmt.Errorf("blobs not enabled on avalanche networks: used %d blob gas, expected 0", *header.BlobGasUsed)
		}
	}
	return nil
```

## Snippet 3

Context: `plugin/evm/vm_test.go:4093` (changes signature or replay validation logic)

Before
```go
}

func TestMinFeeSetAtEUpgrade(t *testing.T) {
	require := require.New(t)
```
After
```go
}

func TestNoBlobsAllowed(t *testing.T) {
	ctx := context.Background()
	require := require.New(t)

	gspec := new(core.Genesis)
	err := json.Unmarshal([]byte(genesisJSONCancun), gspec)
```

## Snippet 4

Context: `core/state_processor_test.go:118` (changes signature or replay validation logic)

Before
```go
GasLimit: params.CortinaGasLimit,
			}
			blockchain, _  = NewBlockChain(db, DefaultCacheConfig, gspec, dummy.NewCoinbaseFaker(), vm.Config{}, common.Hash{}, false)
			tooBigInitCode = [params.MaxInitCodeSize + 1]byte{}
		)
```
After
```go
GasLimit: params.CortinaGasLimit,
			}
			// FullFaker used to skip header verification that enforces no blobs.
			blockchain, _  = NewBlockChain(db, DefaultCacheConfig, gspec, dummy.NewFullFaker(), vm.Config{}, common.Hash{}, false)
			tooBigInitCode = [params.MaxInitCodeSize + 1]byte{}
		)
```

# Fix Pattern

Add explicit protocol-invariant checks at header validation boundaries after Cancun/EIP-4844 field-shape validation.

## How It Was Fixed

The EVM block validator now requires BlobGasUsed to be non-nil during Cancun and rejects positive values. The dummy consensus engine now rejects positive BlobGasUsed after VerifyEIP4844Header. Tests were updated to exercise blob-block rejection and to bypass normal header verification where unrelated state-processor tests need to construct otherwise-invalid headers.

# Why It Matters

1. Prevents acceptance of headers that violate Avalanche's no-blobs rule.

2. Keeps Cancun header validation aligned with local network rules, not just generic EIP-4844 structure.

3. Adds regression coverage for blob transaction rejection.

4. Evidence does not support claims of panic, replay, storage corruption, or proven remote exploitability.

# Evidence Notes

Grounded evidence is the added BlobGasUsed checks in plugin/evm/block_verification.go and consensus/dummy/consensus.go, plus tests documenting that normal header verification now enforces no blobs. The evidence supports a header-validity enforcement gap. It does not support the heuristic baseline's claims about transaction decoding, panic-prone conversions, liveness failure, cryptographic logic, replay, or state/storage handling. Protocol security invariant: For Cancun-era Avalanche EVM headers, Cancun blob-related fields may be required by header shape, but blobs are not enabled on Avalanche networks, so BlobGasUsed must be present and equal to zero. Non-Cancun headers must not carry blob fields. Verification notes: The patch does not prove a node crash or panic condition. The patch does not prove remote exploitability or network-wide consensus failure by itself. The patch does not show that blob transaction execution or blob data availability was enabled. The patch evidence supports invalid-header acceptance prevention, not a state storage or replay bug. Primary code evidence is in block syntactic verification and consensus header verification. Test evidence constructs a Cancun block with a blob transaction and expects rejection. The security classification is likely rather than confirmed because the provided evidence establishes invalid-header acceptance prevention, but not an independently demonstrated exploit scenario or network impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `invalid-header-validation`
Final impact type: `consensus-integrity`
Final confidence: `medium`
Final tags: `consensus, header-validation, eip-4844, blob-gas, protocol-invariant, security-hardening`

The patch clearly tightens consensus/block header validation by enforcing Avalanche's no-blobs rule after Cancun/EIP-4844 support: Cancun headers must have BlobGasUsed present and must reject positive blob gas. This is security-relevant hardening of protocol validation, but the supplied evidence does not prove an exploitable liveness failure, replay issue, state corruption, or concrete network attack, so the original security-fix and high-confidence liveness framing is too strong.

## Security Evidence

1. Block syntactic verification now rejects Cancun headers with nil BlobGasUsed or BlobGasUsed greater than zero.
2. Dummy consensus header verification now rejects positive BlobGasUsed after EIP-4844 header validation.
3. Error text explicitly states blobs are not enabled on Avalanche networks, indicating enforcement of a local protocol invariant.
4. Tests were added/updated to construct blob-related Cancun behavior and account for header verification rejecting blobs.

## Missing Evidence

1. No evidence shows that such headers were accepted by production consensus end to end before the patch.
2. No demonstrated exploit path, remote attacker capability, or chain split/liveness failure is shown.
3. No evidence supports replay, cryptographic, storage corruption, or transaction decoding claims.
4. No impact analysis proves that positive BlobGasUsed could alter state execution or availability assumptions.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. The validated issue is limited to missing no-blobs header invariant enforcement.
3. Do not claim proven liveness failure or network-wide consensus failure from this patch alone.
4. Do not claim blob transaction execution, data availability bypass, replay, or storage impact without additional evidence.
