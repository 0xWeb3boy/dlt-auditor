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

## Solana Calibration Addendum

These mappings were derived from `/testing/solana/validated-findings/kept` through the corpus import at `/testing/dlt-ai-audit-system/corpus/imports/20260509-161152Z-solana`. They are retained as provenance for prompt-pack refinement and should not be used as runtime instructions.

Family counts from the imported manifest: `13_input_validation_and_invariant_enforcement.md` 97, `10_authz_and_role_gates.md` 14, `11_signature_binding_and_signer_scope.md` 9, `12_attestation_trust_and_freshness.md` 5, `17_checked_arithmetic_and_parameter_bounds.md` 5, `14_resource_accounting_and_limits.md` 4, `16_staking_registry_and_accountability.md` 3, `15_state_machine_and_lifecycle_consistency.md` 2.

| Finding | Bug class | Primary prompt | Impact focus | Suggested baseline severity |
| --- | --- | --- | --- | --- |
| 2018-03-02-solana-cryptography-36bb1f989d | double-spend-stale-accounting | `15_state_machine_and_lifecycle_consistency.md` | lifecycle-cleanup | High |
| 2018-04-05-solana-transaction-processing-c960e8d351 | freshness-anchor-validation | `12_attestation_trust_and_freshness.md` | freshness | Low/Medium |
| 2018-07-08-solana-cryptography-71f05cb23e | timestamp-source-authorization | `10_authz_and_role_gates.md` | authorization | Low/Medium |
| 2018-10-26-solana-transaction-processing-cda9ad8565 | incomplete-signature-verification | `11_signature_binding_and_signer_scope.md` | signer-authorization | Low/Medium |
| 2018-12-01-solana-cryptography-34c3a0cc1f | gossip-signature-verification-hardening | `11_signature_binding_and_signer_scope.md` | signer-authorization | Low/Medium |
| 2019-02-15-solana-core-logic-132c664e18 | cross-program-state-mutation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2019-02-22-solana-transaction-processing-66891d9d4e | access-control | `10_authz_and_role_gates.md` | authorization | Low/Medium |
| 2019-02-28-solana-staking-20e4edec61 | vote-account-binding-confusion | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2019-03-01-solana-staking-db825b6e26 | missing-signature-check | `11_signature_binding_and_signer_scope.md` | signer-authorization | High |
| 2019-03-08-solana-p2p-networking-c8c85ff93b | gossip-signature-integrity | `11_signature_binding_and_signer_scope.md` | signer-authorization | Medium |
| 2019-03-18-solana-staking-61a4b998fa | consensus-vote-safety-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2019-03-18-solana-staking-89c42ecd3f | consensus-vote-safety-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2019-05-20-solana-transaction-processing-ead15d294e | panic-prone-input-parsing | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2019-06-10-solana-consensus-807c69d97c | account-permission-invariant-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2019-06-20-solana-cryptography-aacb38864c | invalid-fork-replay-handling | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2019-07-31-solana-staking-1a0003fbcc | stake-withdrawal-epoch-accounting-hardening | `16_staking_registry_and_accountability.md` | accountability-enforcement | Low/Medium |
| 2019-07-31-solana-staking-9278201198 | missing-withdrawal-state-guard | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2019-08-21-solana-storage-e2d6f01ad3 | missing-genesis-blockhash-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2019-09-12-solana-staking-5dceeec1ca | improper-authorization | `10_authz_and_role_gates.md` | authorization | Low/Medium |
| 2019-09-25-solana-staking-43795193c4 | authorization-hardening | `10_authz_and_role_gates.md` | authorization | Low/Medium |
| 2019-09-26-solana-staking-61930c0dd3 | authorization-check-hardening | `10_authz_and_role_gates.md` | authorization | Low/Medium |
| 2019-10-15-solana-storage-78d5c1de9a | account-data-size-boundary-enforcement | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2019-10-29-solana-staking-a587d05098 | stake-redelegation-invariant-hardening | `16_staking_registry_and_accountability.md` | accountability-enforcement | Low/Medium |
| 2019-10-31-solana-cryptography-e8e5ddc55d | consensus-ledger-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2019-11-03-solana-consensus-d9a9d6547f | signature-identity-binding | `11_signature_binding_and_signer_scope.md` | signer-authorization | Low/Medium |
| 2019-12-20-solana-cryptography-3c361eb759 | snapshot-integrity-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-01-15-solana-cryptography-b16c30b4c6 | state-hash-alignment-bug | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-02-07-solana-staking-fa00803fbf | gossip-freshness-validation | `12_attestation_trust_and_freshness.md` | freshness | Low/Medium |
| 2020-02-14-solana-staking-535ee281e8 | peer-gossip-freshness-validation | `12_attestation_trust_and_freshness.md` | freshness | Low/Medium |
| 2020-02-26-solana-consensus-242afa7e6b | untrusted-bootstrap-data-validation | `12_attestation_trust_and_freshness.md` | freshness | High |
| 2020-02-26-solana-consensus-87cfac12dd | bootstrap-trust-validation | `12_attestation_trust_and_freshness.md` | freshness | High |
| 2020-03-16-solana-cryptography-1cc66f0cd7 | validator-state-consistency-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2020-03-16-solana-cryptography-dc347dd3d7 | validator-state-consistency-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2020-04-02-solana-consensus-0139236464 | consensus-vote-guard-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2020-04-02-solana-consensus-4649378f95 | consensus-vote-gating | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-04-16-solana-consensus-66abe45ea1 | state-consistency-monitoring | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-04-27-solana-consensus-e46026f1fb | missing-deserialization-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-04-27-solana-cryptography-8ef097bf6f | missing-input-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-04-27-solana-cryptography-9c6f613f8c | protocol-input-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-05-02-solana-cryptography-f37f83fd12 | transaction-sanitization-ordering | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-05-02-solana-transaction-processing-fa254ff18f | malformed-transaction-validation-ordering | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-05-08-solana-cryptography-f98bfda6f9 | disabled-signature-verification-path | `11_signature_binding_and_signer_scope.md` | signer-authorization | Low/Medium |
| 2020-05-21-solana-transaction-processing-ee1f218e76 | rpc-input-validation-panic-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-05-26-solana-storage-03abd3ddd7 | missing-privilege-check | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2020-05-26-solana-storage-8c8e2c4b2b | cross-program-invocation-privilege-escalation | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2020-05-28-solana-rpc-client-api-bc86ee8d13 | repair-response-gating-bypass | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-05-28-solana-staking-0c68f27ac3 | denial-of-service | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-05-28-solana-staking-e68621b8bb | denial-of-service | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-06-30-solana-cryptography-88eeb817e4 | validator-restart-precondition-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-07-21-solana-staking-e07c00710a | reward-accounting-invariant | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2020-07-31-solana-cryptography-e33f9ea6b5 | authorization-role-confusion | `10_authz_and_role_gates.md` | authorization | High |
| 2020-07-31-solana-staking-61d9d219f9 | authorization-role-confusion | `10_authz_and_role_gates.md` | authorization | Medium |
| 2020-08-05-solana-transaction-processing-7b8e5a9f47 | missing-transaction-sanitization | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-08-06-solana-cryptography-5c4b8153c6 | missing-off-curve-address-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-08-17-solana-staking-d9ae092637 | rent-exemption-recheck-bypass | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-08-25-solana-core-logic-f162c6d1d0 | pointer-alignment-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2020-09-15-solana-core-logic-b5c7ad3a9b | validator-network-exposure-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-10-01-solana-staking-e3773d919c | integer-overflow | `17_checked_arithmetic_and_parameter_bounds.md` | arithmetic-bounds | High |
| 2020-10-02-solana-storage-29af9d1a36 | integer-overflow-accounting | `17_checked_arithmetic_and_parameter_bounds.md` | arithmetic-bounds | Low/Medium |
| 2020-10-12-solana-storage-9797c93db3 | panic-on-invalid-native-loader-input | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-10-20-solana-consensus-25078d46ba | gossip-stale-peer-fanout | `15_state_machine_and_lifecycle_consistency.md` | lifecycle-cleanup | Medium |
| 2020-10-28-solana-cryptography-ae91270961 | udp-amplification-via-source-spoofing | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-10-28-solana-cryptography-f19778b7d9 | udp-reflection-amplification | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-10-29-solana-cryptography-06067dd823 | udp-amplification-missing-endpoint-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-11-13-solana-transaction-processing-5a61827702 | integer-overflow | `17_checked_arithmetic_and_parameter_bounds.md` | arithmetic-bounds | Low/Medium |
| 2020-11-13-solana-transaction-processing-f6b65b033e | arithmetic-overflow-in-validation-counter | `17_checked_arithmetic_and_parameter_bounds.md` | arithmetic-bounds | Low/Medium |
| 2020-11-16-solana-staking-e12cb457fb | account-owner-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-11-19-solana-storage-a8c29505f0 | panic-dos | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-11-20-solana-storage-0ad7b64961 | missing-input-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-11-20-solana-storage-ff38a46af6 | remote-denial-of-service | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2020-11-24-solana-transaction-processing-db3f154b3f | durable-nonce-failed-transaction-state-persistence | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-12-15-solana-consensus-75e9e321de | consensus-state-publication-race | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-12-15-solana-consensus-db339cb925 | consensus-state-ordering-race | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2020-12-15-solana-consensus-ef9f54b3d4 | consensus-state-race | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2020-12-17-solana-cryptography-ff728e5e56 | rent-exemption-undercheck | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-01-09-solana-staking-4470afceaa | authority-model-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-01-19-solana-cryptography-540e23c987 | account-locking-invariant | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2021-01-20-solana-transaction-processing-2783aee483 | input-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-01-21-solana-transaction-processing-9dd5d4407b | input-bound-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-01-22-solana-cryptography-77572a7c53 | cpi-writable-privilege-tracking | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-01-23-solana-cryptography-480a35d678 | improper-privilege-propagation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-01-29-solana-transaction-processing-07cef5a557 | authorization-invariant-enforcement | `10_authz_and_role_gates.md` | authorization | Medium |
| 2021-01-29-solana-transaction-processing-08bda35fd6 | access-control | `10_authz_and_role_gates.md` | authorization | Medium |
| 2021-01-29-solana-transaction-processing-893cc76472 | authorization-invariant-bypass | `10_authz_and_role_gates.md` | authorization | Low/Medium |
| 2021-02-13-solana-transaction-processing-99012f022e | input-size-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-03-11-solana-core-logic-cc38ae72e7 | writable-account-boundary-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-03-16-solana-staking-999f81c56d | missing-resource-metering | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-04-06-solana-transaction-processing-03d3ae1cb9 | resource-control-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-04-06-solana-transaction-processing-f6780d72b1 | faucet-rate-limit-scope | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-05-28-solana-consensus-2f7f243022 | read-only-account-modification-bypass | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-05-28-solana-consensus-a3240aebde | read-only-account-mutation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-06-01-solana-cryptography-b000d490ce | resource-exhaustion-mitigation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-06-06-solana-transaction-processing-8f5e773caf | missing-authorization | `10_authz_and_role_gates.md` | authorization | Low/Medium |
| 2021-06-06-solana-transaction-processing-e5ea16fad8 | authorization-check-bypass | `10_authz_and_role_gates.md` | authorization | High |
| 2021-06-07-solana-transaction-processing-b777bbf7db | missing-authorization-check | `10_authz_and_role_gates.md` | authorization | High |
| 2021-07-01-solana-cryptography-03d213d764 | transaction-signature-length-validation | `11_signature_binding_and_signer_scope.md` | signer-authorization | Low/Medium |
| 2021-07-01-solana-cryptography-d5961e9d9f | transaction-signature-length-validation | `11_signature_binding_and_signer_scope.md` | signer-authorization | Low/Medium |
| 2021-07-13-solana-cryptography-350baece21 | panic-on-invalid-transaction-index | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-08-18-solana-transaction-processing-6f31882260 | bpf-syscall-memory-overlap-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2021-08-20-solana-transaction-processing-967746abbf | unbounded-serialization | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-09-02-solana-validator-ops-afb87a386a | unsafe-key-reuse | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-09-02-solana-validator-ops-e288459cf2 | unsafe-authority-default | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-09-08-solana-transaction-processing-38bbb77989 | account-mutability-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-09-09-solana-transaction-processing-3eee222667 | improper-writable-account-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-09-09-solana-transaction-processing-b9a0156a93 | improper-writable-account-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-10-06-solana-cryptography-1dd6dc3709 | resource-accounting-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-10-06-solana-cryptography-db85d659b9 | resource-accounting-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-10-15-solana-consensus-44ff30b65b | consensus-repair-retry-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2021-10-26-solana-staking-4fe3354c8f | unchecked-sysvar-account-input | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-12-06-solana-consensus-e123883b26 | missing-rent-exemption-check | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-12-07-solana-consensus-83e01442a7 | rent-exemption-invariant-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2021-12-07-solana-consensus-89d2f34a03 | protocol-invariant-enforcement | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-01-28-solana-validator-ops-a71f05f86c | cpi-duplicate-account-privilege-escalation | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2022-02-17-solana-transaction-processing-2120ef5808 | precompile-lifecycle-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-02-24-solana-storage-97d40ba3da | rent-state-validation-bypass | `10_authz_and_role_gates.md` | authorization | High |
| 2022-02-24-solana-transaction-processing-3bee925967 | rent-resource-accounting-invariant | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-05-07-solana-cryptography-10f6845071 | improper-transaction-sanitization | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-05-25-solana-cryptography-880684565c | packet-payload-boundary-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-06-02-solana-cryptography-1c2ae470c5 | network-admission-control-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2022-06-02-solana-cryptography-a781cff386 | quic-stake-admission-control | `16_staking_registry_and_accountability.md` | accountability-enforcement | Medium |
| 2022-06-03-solana-transaction-processing-5dbf7d8f91 | improper-packet-bounds-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2022-06-03-solana-transaction-processing-5ee157f43d | replay-domain-collision | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2022-06-08-solana-cryptography-165ee12ed4 | nonce-authority-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-06-16-solana-transaction-processing-7a4d64a5e3 | missing-resource-limit-enforcement | `14_resource_accounting_and_limits.md` | resource-accounting | High |
| 2022-06-20-solana-cryptography-529b856998 | packet-buffer-read-boundary-hardening | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-06-20-solana-cryptography-e71f56c3f2 | unchecked-packet-slice-access | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2022-06-22-solana-consensus-5b864ef97d | quic-ingress-resource-limiting | `14_resource_accounting_and_limits.md` | resource-accounting | Medium |
| 2022-06-28-solana-cryptography-348fe9ebe2 | late-network-input-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2022-08-25-solana-consensus-1de5ddf748 | arithmetic-overflow-hardening | `17_checked_arithmetic_and_parameter_bounds.md` | arithmetic-bounds | High |
| 2022-08-26-solana-transaction-processing-c846221bb8 | missing-snapshot-validation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-09-22-solana-transaction-processing-565aacc23a | missing-account-mutability-check | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2022-09-29-solana-cryptography-82e65593ee | invalid-transaction-forwarding | `13_input_validation_and_invariant_enforcement.md` | input-validation | Medium |
| 2022-12-02-solana-cryptography-87d939b319 | incorrect-cryptographic-key-derivation | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2023-01-31-solana-cryptography-a5af54669a | missing-resource-limit | `14_resource_accounting_and_limits.md` | resource-accounting | Medium |
| 2023-02-01-solana-cryptography-8270f29b0c | missing-resource-limit | `14_resource_accounting_and_limits.md` | resource-accounting | Medium |
| 2023-02-15-solana-cryptography-cf0a149add | signature-commitment-hardening | `11_signature_binding_and_signer_scope.md` | signer-authorization | Low/Medium |
| 2023-05-25-solana-transaction-processing-9d6c921b5f | underconstrained-transaction-classification | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
| 2023-06-20-solana-consensus-20a7cdd43d | consensus-state-exposure | `13_input_validation_and_invariant_enforcement.md` | input-validation | High |
| 2023-09-05-solana-consensus-a8e83c8720 | consensus-duplicate-slot-state-recovery | `13_input_validation_and_invariant_enforcement.md` | input-validation | Low/Medium |
