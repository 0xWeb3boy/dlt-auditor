# Code-Shape Card

## Metadata

- ID: `geth-arb-2022-04-17-go-ethereum-transaction-processing-f990e534ab`
- Bug family: `authz_and_role_gates`
- Bug class: `container-least-privilege-hardening`

## Code Shape Summary

- The node distribution image ran as root and was hardened by switching the runtime user to a non-root account.

## Search Motifs

- production node container defaults to root user
- Dockerfile lacks USER for runtime stage
- service process has unnecessary write or root privileges
- authorization predicate combines boolean result and error handling unsafely
- policy warning is advisory where fail-closed behavior is expected
- privileged sink accepts caller-controlled authority or destination parameter

## Typical Asymmetry

- The vulnerable asymmetry is fail-open authorization: policy, role, or trusted-parameter state was weaker at the entrypoint than at the privileged sink process privileges inside the production container.

## Patch Pattern

- Create/select an unprivileged user in the image and set it as the default runtime identity.

## False Match Warnings

- a separate mandatory role check guards the sink
- errors fail closed before privilege is granted
- the changed path only affects local diagnostics and not authorization or privilege
- the patch only improves diagnostics, naming, generated bindings, or tests without changing runtime acceptance or rejection
- the input is not attacker-influenced in the deployed threat model
