---
id: monad-c4-2025-09-m-07
source: Code4rena 2025-09 Monad report
source_report: /testing/learning/2025-09-monad-report.md
report_date: 2026-02-26
audit_start_date: 2025-09-16
severity: medium
---

## [[M-07] Consensus validator accepts blocks with mismatched basefee and execution `basefeepergas`](https://code4rena.com/audits/2025-09-monad/submissions/F-806)

*Submitted by [lian886](https://code4rena.com/audits/2025-09-monad/submissions/S-211), also found by [0xAsen](https://code4rena.com/audits/2025-09-monad/submissions/S-192), [fromeo_016](https://code4rena.com/audits/2025-09-monad/submissions/S-815), [Jorgect](https://code4rena.com/audits/2025-09-monad/submissions/S-543), and [QuestceQuecest](https://code4rena.com/audits/2025-09-monad/submissions/S-679)*

- `bft/monad-eth-block-validator/src/lib.rs`[#L182](https://github.com/code-423n4/2025-09-monad/tree/main/bft/monad-eth-block-validator/src/lib.rs#L182)
- `bft/monad-eth-block-validator/src/lib.rs`[#L405](https://github.com/code-423n4/2025-09-monad/tree/main/bft/monad-eth-block-validator/src/lib.rs#L405)
- `bft/monad-eth-txpool/src/pool/mod.rs`[#L357](https://github.com/code-423n4/2025-09-monad/tree/main/bft/monad-eth-txpool/src/pool/mod.rs#L357)
- `bft/monad-updaters/src/txpool.rs`[#L320](https://github.com/code-423n4/2025-09-monad/tree/main/bft/monad-updaters/src/txpool.rs#L320)
- `bft/monad-state/src/consensus.rs`[#L360](https://github.com/code-423n4/2025-09-monad/tree/main/bft/monad-state/src/consensus.rs#L360)
- `monad/category/execution/monad/validate_monad_block.cpp`[#L40](https://github.com/code-423n4/2025-09-monad/tree/main/monad/category/execution/monad/validate_monad_block.cpp#L40)

`validate_block_header` only re-validates ancillary `ProposedEthHeader` fields (transaction tree, mix hash, timestamp, etc.) and never ensures that the execution header’s `base_fee_per_gas` matches the consensus header’s `base_fee`. During block validation the subsequent fee checks inside `validate_block_body` (bft/monad-eth-block-validator/src/lib.rs:405) therefore rely solely on `header.base_fee.unwrap_or(monad_tfm::base_fee::PRE_TFM_BASE_FEE)`, ignoring the actual execution base fee.

Because the txpool builds the execution header and consensus header via independent data paths—`EthTxPool::create_proposal` fixes `base_fee_per_gas` when constructing the `ProposedEthHeader` (bft/monad-eth-txpool/src/pool/mod.rs:357), while the consensus side writes independently supplied `base_fee`/trend/moment values into the `ConsensusBlockHeader` (bft/monad-updaters/src/txpool.rs:320 → bft/monad-state/src/consensus.rs:360)—a malicious proposer can deliberately diverge these numbers. The validator will still accept the block so long as `header.base_fee` is low enough for the static per-transaction fee checks.

Once the block reaches execution, the engine relies on `execution_inputs.base_fee_per_gas` and will detect the inconsistency only after consensus acceptance: `static_validate_consensus_header` for `MonadConsensusBlockHeaderV2` raises `BaseFeeMismatch` when the consensus `base_fee` differs from the execution header’s `base_fee_per_gas` (monad/category/execution/monad/validate*monad*block.cpp:40). This late rejection causes a consensus/execution split: consensus finalizes a block that execution cannot run, and all max-fee transactions chosen between the forged `base_fee` and the true `base_fee_per_gas` will fail to cover gas, guaranteeing execution failure and divergence. For pre-TFM rounds, the validator even permits `base_fee == None`, silently substituting the `PRE_TFM_BASE_FEE` constant while execution still charges the high `base_fee_per_gas`, making the exploit possible regardless of TFM activation.

On a live network every replica would receive the same finalized header and hit the identical BaseFeeMismatch, so executors everywhere halt while consensus has already voted the block in. That leaves the ledger stuck(or nodes cycling if restarted), producing a persistent consensus/exec split until operators intervene—explaining why enforcing the match during Rust-side validation is critical.

### Recommended mitigation steps

Add an explicit consistency check inside `validate_block_header`: when `header.base_fee` is `Some`, require equality with `execution_inputs.base_fee_per_gas`. When it is `None`, enforce that `execution_inputs.base_fee_per_gas` equals `monad_tfm::base_fee::PRE_TFM_BASE_FEE`. Reject any block where these fields diverge so the validator shares execution’s invariant before the block is accepted.

[View detailed Proof of Concept](https://code4rena.com/audits/2025-09-monad/submissions/F-806)

---
