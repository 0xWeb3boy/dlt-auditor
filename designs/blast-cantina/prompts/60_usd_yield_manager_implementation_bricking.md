# Prompt Family: Uninitialized Implementation Bricking

## Use This For

- Uninitialized implementation contracts behind proxies.
- Implementation-local owner/admin takeover that can reach delegatecall, plugin, provider, selfdestruct, or code/state availability impacts.

## Prompt

```text
Hunt specifically for implementation-address takeover and bricking, not proxy-storage takeover.

For every upgradeable implementation that has a public initializer:
- compare constructor behavior with implementation initializer locking;
- call the initializer on the implementation address in the model, not through the proxy;
- determine implementation-local owner, admin, bridge, provider, plugin, and token-approval state after direct initialization;
- enumerate every privileged method now reachable on the implementation address;
- identify delegatecall, arbitrary-call, provider initialization, plugin, recovery, upgrade, or destructive hooks reachable from that implementation-local authority.

Required implementation-bricking matrix:
- implementation contract
- proxy contract using it
- constructor locks initializer? yes/no
- direct initializer arguments attacker can choose
- implementation-local privileged roles attacker gains
- delegatecall/arbitrary-call hook reachable
- malicious callee/provider preconditions
- active fork/EVM semantics for selfdestruct or code destruction
- impact on implementation code availability, proxy upgrade safety, monitoring, rescue scripts, accidental balances, or deployment pipelines
- evidence that proxy storage separation does or does not kill the reported impact

Questions to answer:
1. Can an attacker initialize the implementation directly before anyone else?
2. Can the attacker add or configure a malicious provider/plugin whose code executes by delegatecall in the implementation context?
3. Under the active fork semantics in the target, can that delegatecall destroy code, brick execution, poison implementation state, or otherwise break systems that rely on the implementation address?
4. If code destruction is not permanent, is there still a temporary availability, upgrade, deployment, rescue, or accidental-asset impact?
5. Which exact test or fork semantic would kill the bricking claim?

Reporting discipline:
- Do not reject the candidate solely because proxy storage is separate. Proxy storage separation only kills proxy takeover; it does not by itself kill implementation-address bricking.
- Preserve the implementation-local exploit sequence even if severity is conditional on fork semantics.
- Keep implementation-bricking separate from generic uninitialized implementation hardening and from provider-mutability findings.
```
