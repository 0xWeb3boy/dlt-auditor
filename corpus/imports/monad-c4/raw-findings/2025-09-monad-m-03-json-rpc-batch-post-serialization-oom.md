---
id: monad-c4-2025-09-m-03
source: Code4rena 2025-09 Monad report
source_report: /testing/learning/2025-09-monad-report.md
report_date: 2026-02-26
audit_start_date: 2025-09-16
severity: medium
---

## [[M-03] Remote process crash (OOM) via post‑serialization size check and large batch aggregation in JSON‑RPC](https://code4rena.com/audits/2025-09-monad/submissions/F-722)

*Submitted by [RadiantLabs](https://code4rena.com/audits/2025-09-monad/submissions/S-227), also found by [Almanax](https://code4rena.com/audits/2025-09-monad/submissions/S-302) and [johnyfwesh](https://code4rena.com/audits/2025-09-monad/submissions/S-767)*

- `bft/monad-rpc/src/handlers/mod.rs`[#L129-L151](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/handlers/mod.rs#L129-L151)
- `bft/monad-rpc/src/handlers/mod.rs`[#L154-L169](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/handlers/mod.rs#L154-L169)
- `bft/monad-rpc/src/handlers/eth/txn.rs`[#L154-L181](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/handlers/eth/txn.rs#L154-L181)
- `bft/monad-rpc/src/handlers/eth/gas.rs`[#L402-L466](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/handlers/eth/gas.rs#L402-L466)
- `bft/monad-rpc/src/cli.rs`[#L63-L73](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/cli.rs#L63-L73)

The JSON‑RPC server fully materializes and serializes responses before enforcing the response size cap, and it aggregates entire batches into memory before a final serialization pass. This creates a multiplicative memory footprint that an unauthenticated client can exploit to exhaust memory and crash the process under default settings.

- Batch aggregation: [`rpc_handler()`](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/handlers/mod.rs#L129-L151) runs each request concurrently via `futures::future::join_all(...)`, collects `(id, Result<Box<RawValue>, JsonRpcError>)` pairs, and converts them into a `Vec<Response>`. Each `Response` already contains a pre-serialized `Box<RawValue>` for the per‑item result.
- Post‑serialization size check: After the batch is fully constructed, the server calls `serde_json::value::to_raw_value(&response)` to serialize the entire `ResponseWrapper` into a second large `RawValue`, and only then checks its size: see `response_raw_value` and the subsequent length check in [`rpc_handler()`](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/handlers/mod.rs#L154-L169). This duplicates memory usage at the worst possible time (the entire batch), so the size cap rejects only after the peak allocation.
- Amplification surface: `eth_getLogs` produces large outputs and lacks per‑endpoint concurrency gating. The RPC wrapper simply fetches and returns `Vec<MonadLog>` in [`monad_eth_getLogs()`](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/handlers/eth/txn.rs#L154-L181). While `eth_call`/`eth_estimateGas` have a permit‑based limiter, there is no equivalent guard for `eth_getLogs` in the `eth_getLogs` wrapper.
- Defaults exacerbate the issue: the CLI defaults permit very large batches and a relatively high response size cap (`batch_request_limit = 5000`, `max_response_size = 25_000_000`) in [`Cli`](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/cli.rs#L63-L73). With N=5000 and per‑item results of even ~200 KB, the batch holds ~1 GB of per‑item `RawValue` buffers before creating the final batch `RawValue`. With ~1.5 MB per item (wide `eth_getLogs` filters), this easily reaches many GB, resulting in OOM or severe swapping/CPU thrash before the size cap is applied.

The same late size check also applies to `ResponseWrapper::Single`. Combined with costly response builders like [`monad_eth_feeHistory()`](https://github.com/code-423n4/2025-09-monad/blob/c412a785a696286e5b054d76719d1da012e598ed/bft/monad-rpc/src/handlers/eth/gas.rs#L402-L466), a single request can allocate very large structures (e.g., reward matrices sized by `block_count × len(reward_percentiles)`) and only then be rejected after serialization.

Worst‑case outcome: A single crafted request or one batch forces the server to build large in‑memory results and then serialize the entire wrapper. Memory balloons and the process is terminated by the OOM killer or becomes unresponsive, denying service to honest users. This is an implementation‑specific weakness, not a generic network flood, and is exploitable on default config.

### Recommended mitigation steps

Option A (preferred): stream responses with budgeting

- Replace final `serde_json::value::to_raw_value(&response)` with a streaming JSON encoder for `ResponseWrapper` that writes to the HTTP body while tracking a byte budget.
- Abort emission early with an error once the per‑request or aggregate batch budget is exceeded.
- This avoids constructing a second massive `RawValue`.

Option B (quick hardening/defense in depth): cap batch and pre‑reject oversized batches

[View detailed Proof of Concept](https://code4rena.com/audits/2025-09-monad/submissions/F-722)

---
