# Finding To Prompt Map

This table maps every file in `validated-findings/kept` to the prompt family most likely to rediscover it.

These are source-corpus examples derived from Oasis findings. The prompt families themselves are intended to work on any blockchain or DLT repo.

| Finding | Bug class | Primary prompt | Impact focus | Suggested baseline severity |
| --- | --- | --- | --- | --- |
| 2018-05-26-oasis-core-cryptography-19cd4a286 | signed-message-validation-consistency | `11_signature_binding_and_signer_scope.md` | request integrity | Medium |
| 2018-06-22-oasis-core-storage-821f88a81 | consensus-role-accounting | `15_state_machine_and_lifecycle_consistency.md` | consensus integrity, availability | Medium |
| 2019-01-10-oasis-core-storage-686bc266d | improper-authorization-check | `10_authz_and_role_gates.md` | unauthorized message processing | High |
| 2019-05-06-oasis-core-cryptography-bf949bbb0 | insufficient-input-validation | `12_attestation_trust_and_freshness.md` | TEE capability validation | Medium |
| 2019-05-07-oasis-core-rpc-client-api-e55738ce6 | key-scope-isolation | `12_attestation_trust_and_freshness.md` | cross-scope data access | High |
| 2019-06-03-oasis-core-rpc-client-api-3f0716ecd | non-production-credential-acceptance | `12_attestation_trust_and_freshness.md` | policy bypass | Medium |
| 2019-06-27-oasis-core-cryptography-ee21c841e | predictable-beacon-entropy | `13_input_validation_and_invariant_enforcement.md` | predictable randomness | Medium |
| 2019-07-22-oasis-core-cryptography-079912fe5 | missing-signer-authorization-check | `11_signature_binding_and_signer_scope.md` | unauthorized signature acceptance | High |
| 2019-07-24-oasis-core-cryptography-64cb06901 | missing-signer-authorization | `11_signature_binding_and_signer_scope.md` | unauthorized consensus message acceptance | High |
| 2019-08-15-oasis-core-cryptography-4c642baa8 | insufficient-input-validation | `13_input_validation_and_invariant_enforcement.md` | invalid state acceptance | Medium |
| 2019-08-23-oasis-core-rpc-client-api-4333549d8 | missing-authentication | `10_authz_and_role_gates.md` | unauthorized request processing | High |
| 2019-10-11-oasis-core-storage-82a0d8ee2 | state-integrity-hardening | `15_state_machine_and_lifecycle_consistency.md` | state integrity | Medium |
| 2019-10-28-oasis-core-staking-a34ab1924 | slashability-bypass | `16_staking_registry_and_accountability.md` | slashing bypass | High |
| 2019-11-08-oasis-core-transaction-processing-ba88a37cf | missing-validator-set-minimum-check | `14_resource_accounting_and_limits.md` | validator set safety floor | Medium |
| 2019-11-11-oasis-core-rpc-client-api-7816e47dd | validator-selection-policy | `16_staking_registry_and_accountability.md` | validator selection integrity | Medium |
| 2019-11-13-oasis-core-rpc-client-api-75e2e189e | panic-on-malformed-input | `13_input_validation_and_invariant_enforcement.md` | denial of service | Medium |
| 2019-11-21-oasis-core-transaction-processing-e2d134a5a | missing-gas-accounting | `14_resource_accounting_and_limits.md` | DoS, fee bypass | Medium |
| 2019-11-25-oasis-core-cryptography-d123ab1b1 | insufficient-identity-validation | `13_input_validation_and_invariant_enforcement.md` | descriptor integrity | Medium |
| 2019-11-27-oasis-core-validator-ops-a74913bae | unsafe-debug-configuration | `13_input_validation_and_invariant_enforcement.md` | unsafe local security posture | Low |
| 2020-01-23-oasis-core-cryptography-d5cc58f88 | insufficient-signature-verification | `11_signature_binding_and_signer_scope.md` | unauthorized registration | High |
| 2020-01-29-oasis-core-cryptography-f8809788d | input-validation | `13_input_validation_and_invariant_enforcement.md` | descriptor admission hardening | Medium |
| 2020-01-31-oasis-core-staking-956168c04 | integer-overflow | `17_checked_arithmetic_and_parameter_bounds.md` | freeze/slashing state integrity | Medium |
| 2020-02-06-oasis-core-staking-635fcfd29 | missing-stake-enforcement | `16_staking_registry_and_accountability.md` | policy bypass, improper runtime admission | Medium |
| 2020-04-22-oasis-core-staking-d477a90f7 | incorrect-validator-voting-power | `16_staking_registry_and_accountability.md` | consensus integrity | Medium |
| 2020-06-23-oasis-core-staking-0f89673a0 | missing-update-validation | `10_authz_and_role_gates.md` | unauthorized state modification | High |
| 2020-08-25-oasis-core-cryptography-a7c5872e3 | stale-timeout-state | `15_state_machine_and_lifecycle_consistency.md` | liveness disruption | Medium |
| 2020-12-01-oasis-core-storage-af0555775 | validation-bypass | `10_authz_and_role_gates.md` | mempool validation bypass | Medium |
| 2021-01-21-oasis-core-staking-253376f8d | insufficient-validator-slashing-enforcement | `16_staking_registry_and_accountability.md` | accountability integrity | Medium |
| 2021-02-15-oasis-core-cryptography-a0ac508da | insufficient-signature-domain-separation | `11_signature_binding_and_signer_scope.md` | signature replay or misbinding | High |
| 2021-05-24-oasis-core-transaction-processing-25f10e879 | improper-resource-limit-enforcement | `14_resource_accounting_and_limits.md` | resource exhaustion | Medium |
| 2022-04-13-oasis-core-consensus-8381b14d1 | insufficient-resource-limits | `14_resource_accounting_and_limits.md` | txpool DoS | Medium |
| 2022-04-20-oasis-core-rpc-client-api-40afd4203 | trust-root-verification | `12_attestation_trust_and_freshness.md` | premature readiness | Medium |
| 2022-04-20-oasis-core-rpc-client-api-a02e1e95f | improper-trust-verification-gating | `12_attestation_trust_and_freshness.md` | trust-state exposure | Medium |
| 2022-05-23-oasis-core-staking-07f5399b5 | reserved-address-invariant-enforcement | `16_staking_registry_and_accountability.md` | state integrity | Medium |
| 2022-06-29-oasis-core-cryptography-57692e8f7 | missing-query-verification | `11_signature_binding_and_signer_scope.md` | query integrity | Medium |
| 2022-09-05-oasis-core-rpc-client-api-fa52dea46 | freshness-verification | `12_attestation_trust_and_freshness.md` | stale attestation acceptance | Medium |
| 2022-12-08-oasis-core-rpc-client-api-52536d293 | quote-policy-synchronization | `12_attestation_trust_and_freshness.md` | stale security policy | Medium |
| 2023-01-26-oasis-core-cryptography-8ffc81e94 | insufficient-peer-identity-verification | `12_attestation_trust_and_freshness.md` | identity misbinding | Medium |
| 2023-02-01-oasis-core-rpc-client-api-8eabf0d47 | insufficient-validation | `13_input_validation_and_invariant_enforcement.md` | committee construction integrity | Medium |
| 2023-04-12-oasis-core-cryptography-97f265501 | untrusted-secret-validation | `13_input_validation_and_invariant_enforcement.md` | secret rotation integrity | High |
| 2023-06-29-oasis-core-rpc-client-api-95923572b | state-verification-gap | `11_signature_binding_and_signer_scope.md` | verification freshness and integrity | Medium |
| 2023-07-31-oasis-core-staking-67711fa42 | proposer-liveness-accounting-gap | `16_staking_registry_and_accountability.md` | availability, penalty bypass | Medium |
| 2023-10-02-oasis-core-consensus-87f19bb1e | improper-role-scoped-enforcement | `15_state_machine_and_lifecycle_consistency.md` | integrity, availability | Medium |
| 2024-03-16-oasis-core-storage-68133d1f3 | protocol-state-confusion | `15_state_machine_and_lifecycle_consistency.md` | protocol state integrity | Medium |
| 2024-04-05-oasis-core-transaction-processing-7d649f96d | missing-gas-accounting | `14_resource_accounting_and_limits.md` | resource exhaustion, DoS | Medium |
| 2024-05-11-oasis-core-core-logic-ddf51345a | integer-overflow | `17_checked_arithmetic_and_parameter_bounds.md` | protocol parameter integrity | Medium |
| 2024-07-04-oasis-core-cryptography-8e2f08bb2 | access-control | `10_authz_and_role_gates.md` | privilege misuse | High |
| 2024-10-03-oasis-core-cryptography-0d2f546b2 | stale-session-state | `15_state_machine_and_lifecycle_consistency.md` | stale trust policy, session confusion | Medium |
