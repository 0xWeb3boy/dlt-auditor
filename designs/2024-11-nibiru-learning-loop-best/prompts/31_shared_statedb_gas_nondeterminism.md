# Prompt: Shared StateDB Gas Nondeterminism

Use this focused pass to find read-only execution residue that can affect later consensus gas or branch behavior through shared keeper state.

## Objective

Find candidates where `EthCall`, `EstimateGas`, trace/debug, query, simulation, or other read-only execution installs or mutates a process-local `StateDB`/keeper/cache pointer, and a later live consensus transaction consumes different gas on nodes depending on whether they served the read-only call.

## Search Instructions

1. Locate every shared mutable field that can hold EVM/native execution state:
   - bank keeper `StateDB` pointers,
   - active `StateDB` or cache context pointers saved/restored by precompiles,
   - warmed account/balance/code/storage caches,
   - dirty-object maps or mirror-sync helper state.
2. Trace every read-only entry point that can assign or warm those fields:
   - JSON-RPC `eth_call`, `eth_estimateGas`, debug/trace calls,
   - gRPC query paths,
   - simulation paths,
   - internal helper calls with `commit=false`.
3. For each path, answer:
   - Does it use the same singleton keeper object as live consensus execution?
   - Does it clear or restore the shared field on every success, error, panic, and early return?
   - Does it warm caches or dirty maps that live consensus checks before charging gas?
4. Build a two-node timeline:
   - Node A serves the read-only call before block execution.
   - Node B does not.
   - Both execute the same later block transaction.
   - Compare branch choices, cache hits, mirror-sync calls, SDK gas meter usage, EVM gas, block gas, and final state.
5. Treat "no state commit" as insufficient. The sink is deterministic gas/resource accounting in consensus execution, not persisted state from the read-only call.
6. Kill the candidate only with evidence that every shared field is restored or irrelevant and that the later live transaction consumes identical gas in both timelines.

## Output Format

For each candidate:
- Title:
- Entry point:
- Shared mutable object:
- Later consensus sink:
- Two-node timeline:
- Gas/branch divergence hypothesis:
- Key files/functions:
- Attacker preconditions:
- Impact hypothesis:
- What would confirm it:
- What would kill it:

End with a table of all read-only execution paths checked and whether they leave any shared residue.
