# Prompt Family: Async Channel Backpressure And Panic

## Use This For

- Bounded channels, task updaters, worker pools, actor mailboxes, broadcast/watch channels, and lag handlers.
- Availability bugs where attacker-influenced traffic fills a queue and the receiver, updater, or sender panics, aborts, or wedges.
- Cross-task ownership where one task validates input but another task owns the bounded send or error handling.

## Prompt

```text
Hunt for async backpressure and panic bugs in a blockchain or DLT codebase.

Focus on attacker-influenced RPC, p2p, txpool, consensus, sync, tracing, storage, and background-worker paths that enqueue work into bounded channels or task updaters.

Search patterns:
- `try_send`, `send`, `blocking_send`, `reserve`, `broadcast`, `watch`, `mpsc`, `oneshot`, `JoinSet`, `tokio::spawn`, `unbounded_channel`, `bounded`, `channel(`, `Lagged`, `Full`, `Closed`
- `unwrap`, `expect`, `panic`, or `assert` on channel send results, lag errors, queue-full errors, join errors, or worker completion status
- queue-full handling that crashes the process instead of dropping, disconnecting, penalizing, backpressuring, retrying with a cap, or returning a local error
- bounded channel capacity that is smaller than a valid peer/RPC burst, forwarded transaction batch, consensus fanout, state-sync chunk burst, or trace/log output stream
- background task updaters where "executor lagging", "receiver lagged", or "missed update" is considered impossible even though attackers can create update bursts
- multiple producers sharing one bounded queue without per-peer/per-client attribution or load shedding
- validation done before enqueue but not at dequeue, causing invalid work to occupy scarce slots
- closed-channel or shutdown races where a peer-triggered path can turn a normal receiver drop into a panic
- retry loops that keep re-enqueueing after `Full` or `Lagged` without changing attribution or reducing rate
- task output aggregation where a failed child task is unwrapped and can crash the parent service

Required matrix:
- Ingress source and attacker/faulty-peer control.
- Queue/channel type and capacity.
- Producer sites.
- Consumer sites.
- Error handling for full, closed, lagged, timeout, cancellation, and panic.
- Whether failure crashes process, drops one message, disconnects one peer, or only affects local task.
- Existing rate limits or per-peer attribution before enqueue.

Questions to answer:
1. Can an untrusted or semi-trusted peer/client cause the queue to fill or lag?
2. What happens on every send error variant: full, closed, lagged, timed out, cancelled?
3. Does any send/update path use `unwrap`, `expect`, `panic`, or `assert` on an attacker-influenced queue result?
4. Is the capacity sized for worst-case valid bursts, not just normal operation?
5. Are invalid, duplicate, timeout, or already-known inputs charged to the same backpressure budget as successful inputs?
6. Can one noisy peer consume global capacity and crash or starve unrelated protocol work?
7. Is the panic in a critical node process, a restartable worker, or a local/offline tool?

High-signal evidence:
- A bounded channel `try_send` failure panics in a path reachable from peer/RPC/txpool traffic.
- A lagged update handler treats lag as impossible while the input rate is attacker-controlled.
- A forwarded/batched message path validates after enqueue, so invalid messages consume bounded slots first.
- A worker-pool result or join error is unwrapped after attacker-triggered work can panic inside the worker.

False-positive filters:
- Do not report a panic in a test-only harness or offline tool unless production reuses it.
- Do not report closed-channel panics during intentional shutdown without external trigger.
- Do not report queue-full errors that cleanly drop the message, apply backpressure, or disconnect only the offending peer.

Severity guidance:
- High if a remote or economically cheap actor can crash validator/consensus-critical nodes or halt block production.
- Medium if the crash is realistic for public RPC, p2p, txpool forwarding, state sync, or validator support services.
- Low for local operator-only crashes or hardening without attacker-controlled fill.
```
