# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-nonupgradeable-predeploys-proxied`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `constructor-only-contract-behind-proxy`

## Code Shape Summary

- Predeploy proxy rules include Blast and Gas even though their security-relevant setup is constructor-oriented and not expressed as upgradeable Initializable storage.

## Search Motifs

- IsProxied default true
- Gas constructor
- Blast constructor
- no Initializable
- ProxyAdmin can upgrade predeploy

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Mark constructor-only predeploys as non-proxied, or convert them to explicit upgradeable contracts with initializer parity and upgrade tests.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
