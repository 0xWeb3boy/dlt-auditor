# Prompt Family: Code Identity Redeploy Proxy Upgrade

## Use This For

- Uninitialized implementations, delegatecall plugin/provider hooks, selfdestruct/code destruction, CREATE2 address reuse, durable per-address configuration, non-upgradeable logic behind proxies, and upgrade initializers.
- Cases where authorization or configuration is keyed by address but code identity can change.

## Prompt

```text
Hunt for code-identity, redeploy, proxy, and upgrade bugs.

Build an address-lifecycle table:
- how the address is created
- who can initialize its implementation and proxy storage
- which protocol config maps are keyed only by address
- what survives selfdestruct, redeploy, CREATE2, or upgrade
- whether any delegatecall/plugin/provider hook can execute arbitrary code in the implementation/proxy context

Search patterns:
- uninitialized implementation contracts can be initialized directly, then used to invoke privileged delegatecall or selfdestruct-sensitive code
- provider/plugin modules are delegatecalled by a manager and can destroy, corrupt, or seize implementation state if the implementation is initialized by an attacker
- durable per-address governor/config state can be preseeded for a future CREATE2 deployment or survive selfdestruct/redeploy with a new code identity
- contracts with constructor-only state or no initializer are deployed behind upgradeable proxies
- proxy/admin/deployment scripts install an implementation but omit initialization, or initialize implementation storage instead of proxy storage
- upgrade/reinitializer paths reset replay flags, authorization maps, balances, governors, or one-time initialization markers
- same-transaction selfdestruct/create and cross-transaction redeploy have different behavior for code, nonce, storage, and protocol config maps

Questions to answer:
1. Can anyone call `initialize` on the implementation address, not just the proxy?
2. After implementation initialization, are there owner-only functions that delegatecall user/provider code or can trigger code destruction?
3. Is any security-critical state keyed only by address while code identity/nonce/storage can change?
4. Do predeploys or system contracts behind proxies have initializer-safe storage, or only constructors?
5. Can an upgrade reset replay/finalization/claim/governor state used by pending operations?

Severity guidance:
- High if implementation code can be destroyed/bricked, privileged state seized, or bridge replay protection reset.
- Medium if future deployments can inherit attacker-preseeded governors/config or proxy semantics break constructor-only contracts.
- Low if only operator tooling can misconfigure without attacker timing or value movement.
```
