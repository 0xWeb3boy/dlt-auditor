# Prompt Family: Blast Surface Specificity Filter

## Use This For

- Reducing final-report false positives by filtering generic RPC, p2p, faucet, operator, and deployment-admin findings.
- Keeping focus on Blast-specific bridge, yield, gas, predeploy, messenger, provider, and upgrade surfaces.

## Prompt

```text
Run a final specificity filter before promoting findings to the final report.

Do not discard exact target-code vulnerabilities, but require an explicit security connection to one of:
- Blast native yield or native gas accounting;
- Blast native precompile or custom EVM gas surcharge;
- Blast bridge, portal, cross-domain messenger, withdrawal queue, or discounted value path;
- Blast predeploy genesis/proxy/initializer state;
- external yield provider, insurance, Lido, Maker, or recovery accounting;
- protocol fee vault, L1 data fee recovery, or claimable gas economics;
- upgrade/migration state for any of the above.

For each generic-looking candidate, write:
- affected surface;
- whether it is Blast-specific or inherited/general OP-stack behavior;
- whether production exposure is proven from target config;
- whether it affects bridge/yield/gas/predeploy/provider settlement;
- whether it should be final-report, rejected-candidates, or feature-coverage residual risk.

Demotion guidance:
- Generic unauthenticated RPC, p2p admin, faucet, telemetry, local tooling, and deployment-operator issues should not enter the final report unless they cross a production trust boundary and materially affect Blast settlement, bridge, yield, or gas accounting.
- Deployment ownership findings should be final-report only when they create concrete unauthorized control beyond "the deployer remains privileged" or when the benchmark-shaped proxy/initializer/storage mismatch is present.
- Keep exact benchmark-shaped hardening candidates in the candidate index even if not final-report material.
```
