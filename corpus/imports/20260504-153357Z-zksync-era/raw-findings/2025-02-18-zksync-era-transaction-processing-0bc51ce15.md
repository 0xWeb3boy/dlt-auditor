---
case_id: case_20250218_0bc51ce15
project: zksync-era
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2025-02-18
source_refs:
  - git:0bc51ce15a5dd5230055c4b7224a5452b2b3f5ed
  - "core/node/eth_watch/src/lib.rs:260"
  - "core/node/eth_sender/src/eth_tx_aggregator.rs:854"
  - "core/node/eth_sender/src/eth_tx_aggregator.rs:558"
  - "core/node/eth_watch/src/lib.rs:195"
bug_class: migration-state-guard
impact_type:
  - protocol-state-consistency
  - unsafe-operation-during-migration
confidence: medium
tags:
  - blockchain-core
  - gateway-migration
  - eth-watch
  - eth-sender
  - event-routing
  - operation-gating
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes gateway migration handling in EthWatch and EthTxAggregator. EthWatch now refreshes gateway_status and routes EventsSource::SL through L1 or settlement-layer clients depending on migration state. EthTxAggregator now reads gateway migration state and blocks commit aggregation while GatewayMigrationState::Started. This may be security relevant because it affects a protocol transition path, but the provided evidence does not prove an exploitable vulnerability, consensus failure, invalid commit, fund loss, or cryptographic bypass.

## Observed Patch Facts

1. In `core/node/eth_watch/src/lib.rs`, the patch adds `self.gateway_status = gateway_status(storage, self.l1_client.as_ref()).await?;`.

2. In `core/node/eth_sender/src/eth_tx_aggregator.rs`, the patch adds `async fn query_no_params_method(`.

3. In `core/node/eth_sender/src/eth_tx_aggregator.rs`, the patch replaces `let mut op_restrictions = OperationSkippingRestrictions {` with `let commit_restriction = if self.gateway_migration_state == GatewayMigrationState::St...`.

4. In `core/node/eth_watch/src/lib.rs`, the patch replaces `EventsSource::SL => self.sl_client.as_ref(),` with `EventsSource::SL => match &self.gateway_status {`.

## Project Context

The changed code sits primarily in `core/node/eth_watch/src`, `core/node/eth_watch`, `core/node/eth_sender/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/node/eth_watch/src/client.rs`, `core/node/eth_sender/src/tests.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/node/eth_watch/src/event_processors/decentralized_upgrades.rs`, `core/node/eth_watch/src/client.rs`. The strongest project-level identifiers around this patch are `l1_client`, `GatewayMigrationState::Started`, `EventsSource::SL`, and `as_ref`. Nearby tests or test-like files include `core/node/eth_watch/src/tests/mod.rs`, `core/node/eth_watch/src/tests/client.rs`.

## Before/After Behavior

Before the patch, the visible EthWatch code selected self.sl_client.as_ref() unconditionally for EventsSource::SL and did not show gateway_status refresh at the end of the loop. After the patch, EventsSource::SL uses self.l1_client.as_ref() while GatewayMigrationState::Not and self.sl_client.as_ref() once migration is Started or Finalized, and EthWatch refreshes self.gateway_status after processing. Before the patch, EthTxAggregator commit_restriction was controlled by tx_aggregation_only_prove_and_execute. After the patch, loop_iteration loads gateway migration state and sets commit_restriction to Some("Gateway migration started") when the state is Started.

# Root Cause

The grounded issue is incomplete or inconsistent use of GatewayMigrationState in the visible gateway migration paths. The evidence supports a behavior change that ties event routing and commit eligibility to migration state, but it does not prove that the prior behavior caused a security vulnerability.

## Walkthrough

1. EthWatch processes event ranges for configured processors.

2. Previously, EventsSource::SL selected the settlement-layer client unconditionally in the visible code.

3. After the patch, EventsSource::SL selects the L1 client before migration and the settlement-layer client once migration is Started or Finalized.

4. EthWatch now refreshes self.gateway_status by calling gateway_status after processing event ranges.

5. EthTxAggregator now loads self.gateway_migration_state at the start of loop_iteration.

6. When gateway migration state is Started, EthTxAggregator applies a commit restriction.

7. When migration is not Started, the existing tx_aggregation_only_prove_and_execute restriction remains the fallback.

8. The helper query_no_params_method appears to support no-argument contract reads and should be treated as support code, not the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/node/eth_watch/src/lib.rs | 190 | Selects the event source client for settlement-layer event processors based on current gateway migration status. |
| core/node/eth_watch/src/lib.rs | 260 | Refreshes EthWatch gateway_status after processing event ranges so later iterations use current migration state. |
| core/node/eth_sender/src/eth_tx_aggregator.rs | 524 | Loads gateway migration state before aggregating L1 batch operations. |
| core/node/eth_sender/src/eth_tx_aggregator.rs | 558 | Adds a commit restriction while GatewayMigrationState is Started, preventing commit operation aggregation during migration. |
| core/node/eth_sender/src/eth_tx_aggregator.rs | 854 | Adds helper for querying no-parameter contract methods, apparently supporting migration/status reads from the bound Ethereum interface. |

## Code Snippets

## Snippet 1

Context: `core/node/eth_watch/src/lib.rs:260` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
.map_err(DalError::generalize)?;
        }
        Ok(())
    }
}
```
After
```rust
.map_err(DalError::generalize)?;
        }

        self.gateway_status = gateway_status(storage, self.l1_client.as_ref()).await?;
        Ok(())
    }
}
```

## Snippet 2

Context: `core/node/eth_sender/src/eth_tx_aggregator.rs:854` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
}
}
```
After
```rust
}
}

async fn query_no_params_method(
    l1_client: &dyn BoundEthInterface,
    method_name: &str,
) -> Result<U256, EthSenderError> {
    let data = l1_client
```

## Snippet 3

Context: `core/node/eth_sender/src/eth_tx_aggregator.rs:558` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
};

        let mut op_restrictions = OperationSkippingRestrictions {
            commit_restriction: self
                .config
                .tx_aggregation_only_prove_and_execute
                .then_some("tx_aggregation_only_prove_and_execute=true"),
            prove_restriction: None,
```
After
```rust
};

        let commit_restriction = if self.gateway_migration_state == GatewayMigrationState::Started {
            Some("Gateway migration started")
        } else {
            self.config
                .tx_aggregation_only_prove_and_execute
                .then_some("tx_aggregation_only_prove_and_execute=true")
```

## Snippet 4

Context: `core/node/eth_watch/src/lib.rs:195` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
let client = match processor.event_source() {
                EventsSource::L1 => self.l1_client.as_ref(),
                EventsSource::SL => self.sl_client.as_ref(),
            };
            let chain_id = client.chain_id().await?;
```
After
```rust
let client = match processor.event_source() {
                EventsSource::L1 => self.l1_client.as_ref(),
                EventsSource::SL => match &self.gateway_status {
                    GatewayMigrationState::Not => self.l1_client.as_ref(),
                    GatewayMigrationState::Started | GatewayMigrationState::Finalized => {
                        self.sl_client.as_ref()
                    }
                },
```

# Fix Pattern

Refresh migration state before dependent decisions, route event processing according to migration phase, and skip commit aggregation while gateway migration is Started.

## How It Was Fixed

The patch added gateway_status refresh in EthWatch, made settlement-layer event client selection depend on GatewayMigrationState, loaded gateway migration state in EthTxAggregator::loop_iteration, and added a commit restriction for GatewayMigrationState::Started.

# Why It Matters

1. Gateway migration is a sensitive protocol transition path.

2. Event routing should match the active migration phase.

3. Commit aggregation behavior now changes during the Started phase.

4. The evidence supports hardening or correctness work, not a confirmed vulnerability fix.

# Evidence Notes

Primary evidence is from core/node/eth_watch/src/lib.rs around client selection and gateway_status refresh, and core/node/eth_sender/src/eth_tx_aggregator.rs around gateway_migration_state loading and commit_restriction. The evidence does not support the earlier serialization/canonical-object framing. It also does not establish exploitability or concrete security impact. Protocol security invariant: During gateway migration, event-source routing and commit aggregation should be consistent with the current GatewayMigrationState. The supplied evidence shows the patch enforcing this behavior, but does not establish a concrete security violation in the prior behavior. Verification notes: The patch does not prove an externally exploitable vulnerability. The patch does not show that invalid batches could be committed, only that commits are now skipped during migration Started state. The patch does not demonstrate fund loss, consensus failure, or cryptographic verification bypass. The evidence does not support the heuristic claim that this is primarily a serialization or canonical object transfer fix. The CLI completion file changes are not security-relevant based on the provided evidence. No evidence shows invalid batches were committed before the patch. No evidence shows fund loss, consensus failure, or cryptographic verification bypass. CLI completion changes are not security-relevant based on the supplied evidence. Classified as unclear because the patch may be security relevant but the vulnerability thesis is not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `migration-state-guard`
Final impact type: `protocol-state-consistency, unsafe-operation-during-migration`
Final confidence: `medium`
Final tags: `blockchain-core, gateway-migration, eth-watch, eth-sender, event-routing, operation-gating`

The supplied patch evidence does not prove a concrete exploitable vulnerability, but it does show security-sensitive hardening in a blockchain protocol transition path. The code now refreshes gateway migration state, routes settlement-layer event processing according to that state, and blocks commit aggregation while migration is Started. That is stronger than ordinary cleanup, but should be represented conservatively as hardening rather than a confirmed security fix.

## Security Evidence

1. EthTxAggregator now loads gateway migration state before aggregation decisions.
2. Commit aggregation is explicitly restricted when GatewayMigrationState::Started.
3. EthWatch now refreshes gateway_status after processing event ranges.
4. EventsSource::SL routing now depends on migration state instead of always using the settlement-layer client.
5. The changed paths affect L1/settlement-layer event watching and batch commit aggregation, which are protocol-sensitive areas.

## Missing Evidence

1. No evidence that the previous behavior allowed invalid batches to be committed.
2. No evidence of fund loss, consensus failure, or cryptographic bypass.
3. No security advisory, CVE, incident report, or exploit scenario is provided.
4. No test excerpt proves a specific security regression was fixed.
5. The commit subject describes behavioral change, not an explicit vulnerability fix.

## Claim Boundaries

1. Do not classify this as a confirmed exploitable vulnerability.
2. Do not retain the original serialization-or-state-representation framing.
3. Do not claim signature, cryptographic, or replay protection impact from the supplied evidence.
4. The supported claim is limited to migration-state-based event routing and commit gating hardening.
5. CLI completion file changes are not security-relevant based on the supplied evidence.
