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

## Reth Calibration Addendum

These mappings were derived from `/testing/reth/validated-findings/kept` after phase 4 validation. They are retained as provenance for prompt-pack refinement and should not be used as runtime instructions.

| Finding | Bug class | Primary prompt | Impact focus | Suggested baseline severity |
| --- | --- | --- | --- | --- |
| 2022-12-02-reth-p2p-networking-debc87177 | protocol-input-validation | `13_input_validation_and_invariant_enforcement.md` | p2p parser hardening, availability | Medium |
| 2022-12-15-reth-transaction-processing-9208f2fd9 | fork-selection-logic | `19_consensus_fork_and_payload_rule_validation.md` | consensus execution rule integrity | Medium |
| 2023-01-13-reth-p2p-networking-5c80bc912 | insufficient-peer-validation | `13_input_validation_and_invariant_enforcement.md` | peer admission hardening | Medium |
| 2023-01-20-reth-p2p-networking-eb11da8ad | p2p-handshake-state-inconsistency | `18_authoritative_state_and_boundary_enforcement.md` | handshake artifact binding | Medium |
| 2023-01-30-reth-storage-0e24093b0 | protocol-state-invariant | `19_consensus_fork_and_payload_rule_validation.md` | fork-specific state integrity | Medium |
| 2023-02-11-reth-transaction-processing-eba63b8f7 | consensus-transition-check | `19_consensus_fork_and_payload_rule_validation.md` | hardfork transition integrity | Medium |
| 2023-03-28-reth-rpc-client-api-b55b2d618 | peer-penalty-misclassification | `15_state_machine_and_lifecycle_consistency.md` | peer penalty accuracy | Medium |
| 2023-04-11-reth-transaction-processing-e0e449d5f | signature-input-validation | `11_signature_binding_and_signer_scope.md` | canonical signature validation | Medium |
| 2023-04-12-reth-consensus-e87960ea8 | forkchoice-input-validation | `19_consensus_fork_and_payload_rule_validation.md` | forkchoice state integrity | Medium |
| 2023-05-02-reth-storage-949b3639c | invalid-ancestor-handling | `19_consensus_fork_and_payload_rule_validation.md` | invalid ancestry handling | Medium |
| 2023-05-02-reth-storage-be87dcc68 | checkpoint-target-mismatch | `20_authenticated_state_proof_and_persistence_integrity.md` | trie rebuild checkpoint binding | Medium |
| 2023-05-04-reth-consensus-010b600f3 | insufficient-consensus-validation | `19_consensus_fork_and_payload_rule_validation.md` | parent identity validation | Medium |
| 2023-05-18-reth-consensus-460bf13b6 | consensus-validation | `19_consensus_fork_and_payload_rule_validation.md` | canonical state recognition | Medium |
| 2023-06-06-reth-storage-c0fb169da | consensus-error-handling | `19_consensus_fork_and_payload_rule_validation.md` | invalid block error classification | Medium |
| 2023-07-03-reth-transaction-processing-64554dd0f | body-validation-hardening | `13_input_validation_and_invariant_enforcement.md` | peer-supplied block body validation | Medium |
| 2023-07-12-reth-storage-99240906a | insufficient-state-validation | `19_consensus_fork_and_payload_rule_validation.md` | forkchoice consistency | Medium |
| 2023-08-02-reth-p2p-networking-94dfeb3ad | insufficient-input-validation | `13_input_validation_and_invariant_enforcement.md` | peer header range validation | Medium |
| 2023-08-03-reth-transaction-processing-3f63a0887 | policy-enforcement | `15_state_machine_and_lifecycle_consistency.md` | transaction propagation policy | Medium |
| 2023-08-29-reth-p2p-networking-03afe376b | listener-filter-bypass | `15_state_machine_and_lifecycle_consistency.md` | listener policy preservation | Medium |
| 2023-09-21-reth-transaction-processing-6a601755c | numeric-range-validation | `13_input_validation_and_invariant_enforcement.md` | RPC transaction bounds | Medium |
| 2023-09-26-reth-storage-eb6dc5197 | consensus-rule-validation | `19_consensus_fork_and_payload_rule_validation.md` | fork-gated blob transaction rejection | Medium |
| 2023-11-16-reth-transaction-processing-2b4eb8438 | incomplete-blob-transaction-validation-context | `13_input_validation_and_invariant_enforcement.md` | revalidation sidecar context | Medium |
| 2023-11-29-reth-transaction-processing-2c5a748c5 | signature-malleability | `11_signature_binding_and_signer_scope.md` | canonical signature recovery | Medium |
| 2023-12-23-reth-transaction-processing-8fb6ed9cc | incorrect-fork-gating | `19_consensus_fork_and_payload_rule_validation.md` | transaction fork gate correctness | Medium |
| 2024-02-02-reth-transaction-processing-72b7caa4c | resource-limit-enforcement | `14_resource_accounting_and_limits.md` | txpool count and size limits | Medium |
| 2024-02-03-reth-transaction-processing-d4dffa2ee | improper-resource-limit-enforcement | `14_resource_accounting_and_limits.md` | blobpool count and size limits | Medium |
| 2024-02-15-reth-transaction-processing-945031900 | missing-protocol-validation | `13_input_validation_and_invariant_enforcement.md` | cryptographic commitment binding | Medium |
| 2024-03-18-reth-storage-9962c3949 | ignored-error-result | `19_consensus_fork_and_payload_rule_validation.md` | canonicalization error surfacing | Medium |
| 2024-03-19-reth-p2p-networking-1ad50d148 | missing-handshake-timeout | `14_resource_accounting_and_limits.md` | p2p handshake resource bounding | Medium |
| 2024-04-16-reth-storage-33b195af3 | fork-hash-reconstruction | `20_authenticated_state_proof_and_persistence_integrity.md` | fork-local hash reconstruction | Medium |
| 2024-04-25-reth-rpc-client-api-33e7e0208 | insufficient-bad-peer-penalization | `15_state_machine_and_lifecycle_consistency.md` | bad-peer feedback loop | Medium |
| 2024-05-21-reth-transaction-processing-5100ddd28 | input-validation | `13_input_validation_and_invariant_enforcement.md` | type-specific transaction form rejection | Medium |
| 2024-08-05-reth-storage-08158e444 | insufficient-parent-header-validation | `19_consensus_fork_and_payload_rule_validation.md` | parent header validation | Medium |
| 2024-09-02-reth-consensus-d59854f1d | missing-runtime-bound-check | `15_state_machine_and_lifecycle_consistency.md` | pruning runtime bound enforcement | Medium |
| 2024-12-04-reth-transaction-processing-d298fb1b8 | consensus-validation | `19_consensus_fork_and_payload_rule_validation.md` | chain-variant header validation | Medium |
| 2025-04-19-reth-core-logic-6ef19f403 | missing-upper-bound-check | `19_consensus_fork_and_payload_rule_validation.md` | consensus gas-limit bound | Medium |
| 2025-04-25-reth-transaction-processing-82d650594 | improper-consensus-validation | `19_consensus_fork_and_payload_rule_validation.md` | post-merge header validation | Medium |
| 2025-05-28-reth-storage-1cfe50998 | state-integrity-hardening | `20_authenticated_state_proof_and_persistence_integrity.md` | missing trie updates before persistence | Medium |
| 2025-09-25-reth-rpc-client-api-aa192c255 | improper-auth-header-parsing | `13_input_validation_and_invariant_enforcement.md` | auth header syntax hardening | Medium |
| 2025-10-29-reth-transaction-processing-77ef028ac | consensus-validation | `19_consensus_fork_and_payload_rule_validation.md` | chain-variant blob-gas validation | Medium |
| 2026-01-29-reth-core-logic-bc5e23ddd | state-integrity-hardening | `20_authenticated_state_proof_and_persistence_integrity.md` | trie mutation atomicity | Medium |
| 2026-01-29-reth-storage-edf75de4d | atomicity-violation | `20_authenticated_state_proof_and_persistence_integrity.md` | trie rollback correctness | Medium |
| 2026-02-03-reth-storage-4b9244c7d | incomplete-trie-proof-generation | `20_authenticated_state_proof_and_persistence_integrity.md` | empty-root proof evidence | Medium |
| 2026-02-04-reth-transaction-processing-7671838c6 | gas-semantics-validation | `19_consensus_fork_and_payload_rule_validation.md` | fork-specific gas accounting semantics | Medium |
| 2026-03-04-reth-storage-d8de8afa9 | memory-bound-hardening | `14_resource_accounting_and_limits.md` | hashing-stage memory bound | Medium |
| 2026-03-06-reth-storage-a1600ef0c | proof-integrity | `20_authenticated_state_proof_and_persistence_integrity.md` | trie proof structure integrity | Medium |
| 2026-03-09-reth-transaction-processing-9c33fb5d4 | cache-state-isolation | `15_state_machine_and_lifecycle_consistency.md` | fork-aware cache isolation | Medium |
| 2026-03-21-reth-transaction-processing-b78f74f52 | validation-bypass | `19_consensus_fork_and_payload_rule_validation.md` | special-case payload validation narrowing | Medium |
| 2026-04-01-reth-storage-7c1a43bac | gas-accounting-state-reuse | `14_resource_accounting_and_limits.md` | cache-hit gas accounting isolation | Medium |
| 2026-04-01-reth-transaction-processing-c4517d4c3 | gas-accounting-corruption | `14_resource_accounting_and_limits.md` | cache-hit gas accounting isolation | Medium |
| 2026-04-20-reth-storage-d577814eb | protocol-validation | `19_consensus_fork_and_payload_rule_validation.md` | Engine API method-version validation | Medium |
| 2026-04-21-reth-storage-d92ad5aa3 | improper-state-binding | `20_authenticated_state_proof_and_persistence_integrity.md` | fork-aware state overlay binding | Medium |

## Go-Ethereum Calibration Addendum

These mappings were derived from `/testing/go-ethereum/validated-findings/kept` after phase 4 validation. They are retained as provenance for prompt-pack refinement and should not be used as runtime instructions.

| Finding | Bug class | Primary prompt | Impact focus | Suggested baseline severity |
| --- | --- | --- | --- | --- |
| 2015-03-25-go-ethereum-cryptography-de7af720d | udp-reflection-amplification | `13_input_validation_and_invariant_enforcement.md` | p2p transport abuse, reflection | Medium |
| 2015-05-14-go-ethereum-transaction-processing-a4246c2da | unknown-parent-sync-hardening | `21_peer_sync_progress_and_response_binding.md` | sync integrity, peer-driven work control | Medium |
| 2015-05-15-go-ethereum-core-logic-5c1a7b965 | p2p-sync-validation-bypass | `21_peer_sync_progress_and_response_binding.md` | sync integrity | High |
| 2015-05-15-go-ethereum-core-logic-cd2fb0905 | p2p-sync-no-progress-dos | `21_peer_sync_progress_and_response_binding.md` | peer-driven DoS, progress enforcement | Medium |
| 2015-05-21-go-ethereum-core-logic-52db6d8be | cross-check-validation-bypass | `21_peer_sync_progress_and_response_binding.md` | sync integrity | High |
| 2015-07-01-go-ethereum-p2p-networking-d6f2c0a76 | resource-exhaustion | `21_peer_sync_progress_and_response_binding.md` | sync queue exhaustion | Medium |
| 2015-04-29-go-ethereum-storage-4e0796771 | canonical-chain-reorg-invariant | `20_authenticated_state_proof_and_persistence_integrity.md` | canonical-chain integrity | Medium |
| 2016-10-28-go-ethereum-transaction-processing-b59c8399f | signature-domain-separation | `11_signature_binding_and_signer_scope.md` | signing-scope integrity | Medium |
| 2016-11-24-go-ethereum-storage-12d654a6f | consensus-state-revert-bug | `20_authenticated_state_proof_and_persistence_integrity.md` | revert and state-root integrity | High |
| 2016-11-24-go-ethereum-storage-db567eb01 | consensus-state-revert-mismatch | `20_authenticated_state_proof_and_persistence_integrity.md` | revert and state-root integrity | Medium |
| 2017-02-13-go-ethereum-storage-e23e86921 | missing-content-integrity-check | `13_input_validation_and_invariant_enforcement.md` | content-address integrity | Medium |
| 2017-05-12-go-ethereum-transaction-processing-a5f6a1cb7 | consensus-configuration-hardening | `19_consensus_fork_and_payload_rule_validation.md` | fork/config compatibility | Medium |
| 2017-06-22-go-ethereum-storage-0042f13d4 | resource-exhaustion | `21_peer_sync_progress_and_response_binding.md` | state-sync liveness, peer work bounding | Medium |
| 2017-08-25-go-ethereum-storage-08f27428b | contract-address-collision | `19_consensus_fork_and_payload_rule_validation.md` | protocol-rule enforcement | Medium |
| 2018-02-12-go-ethereum-p2p-networking-9123eceb0 | protocol-response-correlation | `21_peer_sync_progress_and_response_binding.md` | response binding, anti-spoofing | Medium |
| 2018-09-20-go-ethereum-storage-d6254f827 | fork-choice-tie-break-hardening | `19_consensus_fork_and_payload_rule_validation.md` | fork-choice policy integrity | Medium |
| 2018-09-25-go-ethereum-cryptography-d3441ebb5 | signer-policy-hardening | `10_authz_and_role_gates.md` | signer policy enforcement | Medium |
| 2020-12-04-go-ethereum-transaction-processing-15339cf1c | signed-vulnerability-advisory-check | `11_signature_binding_and_signer_scope.md` | signed metadata trust | Medium |
| 2020-12-08-go-ethereum-transaction-processing-ed0670cb1 | replay-protection | `11_signature_binding_and_signer_scope.md` | replay scope integrity | Medium |
| 2021-02-23-go-ethereum-transaction-processing-142fbcfd6 | missing-replay-protection-enforcement | `11_signature_binding_and_signer_scope.md` | transaction replay protection | Medium |
| 2021-07-22-go-ethereum-transaction-processing-97aacd9b3 | transaction-balance-validation | `19_consensus_fork_and_payload_rule_validation.md` | state-transition validity | Medium |
| 2022-06-29-go-ethereum-cryptography-d12b1a91c | consensus-terminal-block-validation-hardening | `19_consensus_fork_and_payload_rule_validation.md` | terminal block validation | Medium |
| 2022-12-20-go-ethereum-transaction-processing-b818e73ef | consensus-validation-hardening | `19_consensus_fork_and_payload_rule_validation.md` | Merge-boundary validation coverage | Medium |
| 2023-01-11-go-ethereum-transaction-processing-793f0f9ec | resource-accounting-hardening | `14_resource_accounting_and_limits.md` | protocol gas accounting | Medium |
| 2024-05-07-go-ethereum-transaction-processing-e4b8058d5 | unbounded-query-parameter | `14_resource_accounting_and_limits.md` | RPC fanout bounding | Medium |
| 2025-04-08-go-ethereum-transaction-processing-2e739fce5 | mempool-resource-exhaustion | `21_peer_sync_progress_and_response_binding.md` | shared reservation and queue isolation | Medium |
| 2025-12-11-go-ethereum-transaction-processing-56d201b0f | p2p-metadata-validation | `21_peer_sync_progress_and_response_binding.md` | metadata-driven fetch control | Medium |
| 2026-03-04-go-ethereum-storage-6d99759f0 | rpc-persistent-state-side-effect | `18_authoritative_state_and_boundary_enforcement.md` | read-only/write-sink separation | Medium |
| 2026-03-24-go-ethereum-transaction-processing-8327e870e | gas-accounting-ordering | `14_resource_accounting_and_limits.md` | gas accounting integrity | Medium |
