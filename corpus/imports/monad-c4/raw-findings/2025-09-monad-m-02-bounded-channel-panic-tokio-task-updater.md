---
id: monad-c4-2025-09-m-02
source: Code4rena 2025-09 Monad report
source_report: /testing/learning/2025-09-monad-report.md
report_date: 2026-02-26
audit_start_date: 2025-09-16
severity: medium
---

## [[M-02] Bounded channel panic in TokioTaskUpdater causes node crash leading to realistic chain halt](https://code4rena.com/audits/2025-09-monad/submissions/F-322)

*Submitted by [dontonka](https://code4rena.com/audits/2025-09-monad/submissions/S-507)*

`bft/monad-updaters/src/lib.rs` [#L141-L161](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-updaters/src/lib.rs#L141-L161)

The [TokioTaskUpdater executor](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-updaters/src/lib.rs#L141-L161) uses a bounded channel with only [1024 slots](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-updaters/src/lib.rs#L58) for command batches. When an attacker sends `ForwardedTx` messages that exceed this capacity, the executor panics with “executor is lagging” instead of gracefully handling the overflow. An unauthenticated attacker can crash any validator by sending `ForwardedTx` messages with `batches_per_conn` × `num_connections` > 1024 (e.g., 500 batches × 5 connections = 2,500 batches). The vulnerability stems from using `.expect()` on `try_send()` rather than implementing proper backpressure or error handling.

```rust
#[cfg(feature = "tokio")]
impl<U, E> Executor for TokioTaskUpdater<U, E>
where
    U: Updater<E>,
    U::Command: Send + 'static,
    E: Send + 'static,
{
    type Command = U::Command;

    fn exec(&mut self, commands: Vec<Self::Command>) {
        self.verify_handle_liveness();

        self.command_tx
            .try_send(commands)
            .expect("executor is lagging")
    }

    fn metrics(&self) -> ExecutorMetricsChain {
        ExecutorMetricsChain::from(&self.metrics)
    }
}
```

### Impact

- **Crash the node**: crash any discoverable node in seconds.
- **Chain halt**: very realistic scenario by simply killing all the validator sets in the current epoch.

### Likelihood

- Anyone can trigger this attack (see PoC), no need to be an official node in the chain (validator, full node, etc.), it simply requires connection to the node port, which is required to be open as this is how peers communicate in Monad.
- There is no cost for this attack in terms of money, only very little resources are needed.

### Recommended mitigation steps

Implement proper backpressure or error handling such that it doesn’t crash.

[View detailed Proof of Concept](https://code4rena.com/audits/2025-09-monad/submissions/F-322)

---
