# Prompt Family: Deployment Initialization And Proxy Consistency

## Use This For

- Constructors, initializers, genesis allocs, or migration scripts that set security-sensitive state.
- Proxy, implementation, clone, registry, CREATE2, or predeploy wiring that can diverge from intended ownership or storage layout.
- Durable per-address configuration that survives redeploy, selfdestruct, upgrade, or chain genesis transitions.

## Prompt

```text
Hunt for deployment, initialization, and proxy-consistency bugs in a blockchain or DLT codebase.

Focus on code where a contract, predeploy, system account, registry entry, implementation, or chain-config object becomes trusted after construction, initialization, genesis import, migration, upgrade, or redeploy.

Search patterns:
- constructors and initializers that write different owners, admins, guardians, sequencers, bridge endpoints, vaults, strategies, gas parameters, fee recipients, or pause flags
- initializer guards that protect direct calls but not proxy upgrade, clone, factory, genesis, migration, or replay paths
- proxy storage layouts that can collide with implementation storage, inherited gaps, beacon slots, EIP-1967-like slots, or app-specific durable config
- implementation contracts that can be initialized directly and later used as an authority, template, or source of default config
- CREATE2, selfdestruct, redeploy, or predeploy paths where durable metadata is keyed only by address and not by code hash, implementation identity, fork, or initialization epoch
- genesis allocs, migration scripts, deployment manifests, or hardcoded addresses that disagree with runtime constructors or registry validation
- upgrade paths that change an implementation without rechecking storage layout, admin intent, version gates, initialization requirements, or compatibility with existing state
- deployment helpers that skip invariant checks because they run in tests, scripts, local dev, or genesis mode but feed artifacts used in production
- registry or resolver entries that are trusted by bridge, gas, yield, oracle, precompile, or system-contract code without verifying code identity and initialization state at the sink
- constructors that accept externally provided implementation, vault, provider, oracle, messenger, or fee recipient addresses and only check nonzero values

Questions to answer:
1. What state is security-sensitive immediately after deployment or genesis?
2. Which path first installs that state: constructor, initializer, proxy admin, factory, migration, or genesis allocation?
3. Can any equivalent path create the same trusted object without the same checks?
4. Is the runtime code identity compared with the intended implementation or manifest before downstream code trusts it?
5. Can selfdestruct, redeploy, upgrade, clone creation, or address reuse preserve stale trust while changing code or initialization semantics?
6. Are storage slots and inherited layouts stable across every implementation that can be installed?
7. Does a failed, partial, or repeated initialization leave privileged state usable?

Severity guidance:
- High if a public or weakly authorized path can seize ownership, redirect bridge/yield/gas value, bypass pause controls, or install a malicious implementation.
- Medium if a realistic migration, redeploy, or misconfiguration path can leave privileged state inconsistent with the deployed code or intended manifest.
- Low if the issue is deployment hygiene only and cannot affect already deployed or production-like configurations.
```
