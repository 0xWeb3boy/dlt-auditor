# Prompt Family: Constructor Only Proxy Intent And Upgrade Safety

## Use This For

- Blast/Gas/native predeploys and other system contracts that use constructor-only state or intentionally lack upgrade-safe initializers.
- Proxy deployment of contracts whose implementation design assumes direct deployment.
- Future upgrade/reinitializer safety, not just initial genesis storage parity.

## Prompt

```text
Hunt for constructor-only or intentionally non-upgradeable system contracts placed behind proxy machinery.

Build a proxy-intent table:
- system/predeploy contract name
- proxy address and proxy admin/upgrade authority
- implementation constructor arguments and immutable assumptions
- initializer presence or absence
- storage fields expected to be set by constructor versus by proxy storage
- whether future implementation upgrades can reproduce constructor validation and state
- whether the contract was designed to be non-upgradeable even though the deployment path exposes upgrade semantics

Search patterns:
- a contract has meaningful constructor-only validation/state but is installed behind a proxy
- a contract has no initializer, no reinitializer, or an initializer that cannot reproduce constructor postconditions
- current genesis storage is sufficient, but a future proxy upgrade would skip constructor-only safety checks or leave proxy storage incompatible
- ProxyAdmin can upgrade a system/predeploy whose implementation design assumes immutability/non-upgradeability
- storage layout, constants, immutable-like assumptions, or constructor-validated parameter bounds cannot be enforced through proxy upgrade
- the audit kills the issue because today's genesis works, without assessing future upgrade safety and non-upgradeable intent

Questions to answer:
1. Is the contract meant to be upgradeable or direct-deployed?
2. If proxied, where are constructor postconditions represented in proxy storage?
3. Can an upgrade replace the implementation with one that assumes constructor-initialized state that proxy storage lacks?
4. Is there an initializer/reinitializer that validates the same invariants as the constructor?
5. Could proxy upgrade authority accidentally or maliciously bypass constructor-only checks for gas/yield accounting?

Severity guidance:
- Medium if proxy upgrade semantics can bypass constructor-only invariants for live gas/yield/accounting predeploys.
- Low if this is deployment hygiene with no realistic upgrade or accounting impact.
- Informational if the contract is direct-deployed or has a complete upgrade-safe initializer.
```
