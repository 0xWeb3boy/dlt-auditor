# Prompt Family: Uninitialized Implementation Privileged Delegatecall Takeover

## Use This For

- Proxy implementations that can be initialized directly.
- Manager/provider/strategy contracts with owner/admin-only delegatecall hooks.
- Implementation-address bricking, code destruction, state corruption, or permanent operational failure after direct implementation initialization.

## Prompt

```text
Hunt for uninitialized implementation takeovers that become exploitable through implementation-local privileged calls.

For every proxy implementation and manager-like contract:
- identify the implementation address and proxy address
- check whether the implementation contract can be initialized directly
- record what owner/admin/governor/provider state is written in implementation storage
- enumerate every owner/admin/governor call that can be made on the implementation address after direct initialization
- especially enumerate delegatecall, plugin, provider, strategy, hook, migration, upgrade, or arbitrary-call sinks
- check whether a malicious provider/plugin can execute in the implementation contract context
- evaluate code-destruction/bricking under the active fork semantics, including whether direct implementation code availability or initialized implementation state is security-sensitive

Search patterns:
- implementation initializer is public and not disabled by constructor `_disableInitializers`
- attacker initializes implementation storage and becomes owner/admin/governor
- attacker configures a provider/plugin/strategy on the implementation address
- attacker calls an owner/admin function that delegatecalls the malicious provider/plugin
- malicious code can `selfdestruct`, corrupt critical implementation storage, exhaust future initialization, or otherwise brick the implementation/upgrade path
- validation rejects proxy-storage compromise too early and misses implementation-code availability or implementation-address bricking

Questions to answer:
1. Can anyone initialize the implementation address directly?
2. Which privileged functions become callable on the implementation after that direct initialization?
3. Can any privileged function execute attacker code via delegatecall or arbitrary external call?
4. Does code destruction, forced initialization, or implementation-address state corruption matter for the proxy, upgrade, or deployment system?
5. What fork semantics apply to `SELFDESTRUCT`, and is the implementation created in the same transaction or an older deployed account?

Severity guidance:
- High if an attacker can permanently destroy/brick an implementation used by a live proxy, seize a privileged upgrade/deployment path, or corrupt a shared implementation state that live flows depend on.
- Medium if the direct implementation takeover only creates a realistic operational denial or future-upgrade hazard.
- Low/Informational if proxy storage and implementation code availability are unaffected and no privileged implementation-only sink is reachable.
```
