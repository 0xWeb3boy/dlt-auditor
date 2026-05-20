# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-m06-tracetx-unbounded-predecessors`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-rpc-simulation-work`

## Code Shape Summary

- TraceTx iterated over caller-supplied predecessor transactions and simulated each before tracing the target message without an explicit global bound.

## Search Motifs

- for i, tx := range req.Predecessors
- TraceTx predecessor simulation
- NewInfiniteGasMeterWithLimit(msg.Gas()) in query
- trace endpoint no timeout

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Add predecessor count limits, total simulation gas caps, and timeout enforcement around the whole TraceTx predecessor simulation path.

## False Match Warnings

- No issue if the endpoint is authenticated or operator-local only.
- No issue if request size, predecessor count, total gas, and timeout are already bounded.
- No chain-wide issue unless validators expose the endpoint in a way that affects consensus.
