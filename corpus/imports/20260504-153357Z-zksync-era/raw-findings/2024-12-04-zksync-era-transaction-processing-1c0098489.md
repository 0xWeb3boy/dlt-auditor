---
case_id: case_20241204_1c0098489
project: zksync-era
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-12-04
source_refs:
  - git:1c0098489d82aa3d88b055d73e74bb3dc150d94e
  - "core/node/genesis/src/lib.rs:322"
  - "core/lib/eth_client/src/types.rs:125"
  - "prover/crates/bin/prover_cli/src/commands/status/l1.rs:80"
  - "core/node/eth_watch/src/client.rs:322"
bug_class: cryptographic-configuration-validation
impact_type:
  - configuration-integrity
  - correctness-or-hardening
confidence: medium
tags:
  - blockchain-core
  - genesis-validation
  - verifier-key-hash
  - abi-overload
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes FFLONK verifier verification-key-hash reads by explicitly selecting the overloaded `verificationKeyHash` ABI entry and adds a genesis-time comparison against `fflonk_snark_wrapper_vk_hash`. This is plausibly security relevant because verification key hashes are cryptographic configuration, but the supplied evidence does not establish attacker control, exploitability, invalid proof acceptance, consensus divergence, or fund loss.

## Observed Patch Facts

1. In `core/node/genesis/src/lib.rs`, the patch replaces `Ok(())` with `if Some(fflonk_verification_key_hash) != genesis_params.config().fflonk_snark_wrapper...`.

2. In `core/lib/eth_client/src/types.rs`, the patch adds `pub async fn call_with_function<Res: Detokenize>(`.

3. In `prover/crates/bin/prover_cli/src/commands/status/l1.rs`, the patch replaces `CallFunctionArgs::new("verificationKeyHash", U256::from(FFLONK_VERIFIER_TYPE))` with `let function = helper::verifier_contract()`.

4. In `core/node/eth_watch/src/client.rs`, the patch replaces `.for_contract(verifier_address, &self.verifier_contract_abi)` with `let function = self`.

## Project Context

The changed code sits primarily in `core/node/genesis/src`, `core/node/genesis`, `core/lib/eth_client/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/lib/eth_client/src/lib.rs`, `prover/crates/bin/prover_cli/src/commands/status/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/lib/eth_client/src/clients/mock.rs`, `core/lib/eth_client/src/clients/http/signing.rs`. The strongest project-level identifiers around this patch are `ContractCallError::Function`, `function`, `ContractCallError`, and `CallFunctionArgs::new`. Nearby tests or test-like files include `core/node/eth_watch/src/tests/client.rs`, `core/node/eth_watch/src/tests/mod.rs`.

## Before/After Behavior

Before the patch, FFLONK hash reads used the generic `CallFunctionArgs::new("verificationKeyHash", U256::from(...)).call(...)` path, while `validate_genesis_params` visibly checked protocol version and the non-FFLONK verification key hash but did not show a FFLONK mismatch rejection. After the patch, callers select `functions_by_name("verificationKeyHash")?[1].clone()` and pass it to `call_with_function`, and genesis validation rejects when the fetched FFLONK hash differs from configured `fflonk_snark_wrapper_vk_hash`.

# Root Cause

The grounded issue is that FFLONK verifier hash retrieval for an overloaded contract function was not explicit enough in the previous call path, and genesis validation lacked the visible FFLONK hash mismatch check. A stronger root-cause claim about exploitable security failure is not supported by the provided evidence.

## Walkthrough

1. `validate_genesis_params` reads the protocol version and rejects mismatches against genesis parameters.

2. It reads the regular verifier `verificationKeyHash` and compares it to `snark_wrapper_vk_hash`.

3. The patch adds explicit retrieval of the overloaded FFLONK `verificationKeyHash` ABI function using `functions_by_name(...)?[1].clone()`.

4. `ContractCall::call_with_function` lets callers encode and decode using a caller-supplied `ethabi::Function` instead of resolving only by name internally.

5. Genesis validation now compares `Some(fflonk_verification_key_hash)` with `fflonk_snark_wrapper_vk_hash` and returns an error on mismatch.

6. The eth watcher and prover CLI L1 status paths are updated to use the same explicit overloaded-function selection for FFLONK hash reads.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/node/genesis/src/lib.rs | 275 | validates L1 protocol version and verifier key hashes against genesis configuration |
| core/node/genesis/src/lib.rs | 322 | newly rejects mismatched FFLONK verification key hash |
| core/lib/eth_client/src/types.rs | 125 | adds explicit ABI function call helper for overloaded contract functions |
| core/node/eth_watch/src/client.rs | 319 | queries FFLONK scheduler verification key hash using the selected overloaded ABI function |
| prover/crates/bin/prover_cli/src/commands/status/l1.rs | 80 | reports L1 FFLONK verification key hash using the selected overloaded ABI function |

## Code Snippets

## Snippet 1

Context: `core/node/genesis/src/lib.rs:322` (changes signature or replay validation logic)

Before
```rust
}

    Ok(())
}
```
After
```rust
}

    if Some(fflonk_verification_key_hash) != genesis_params.config().fflonk_snark_wrapper_vk_hash {
        return Err(anyhow::anyhow!(
            "Verification key hash mismatch: {fflonk_verification_key_hash:?} on contract, {:?} in config",
            genesis_params.config().fflonk_snark_wrapper_vk_hash
        ));
    }
```

## Snippet 2

Context: `core/lib/eth_client/src/types.rs:125` (changes signature or replay validation logic)

Before
```rust
})
    }
}
```
After
```rust
})
    }

    pub async fn call_with_function<Res: Detokenize>(
        &self,
        client: &dyn EthInterface,
        function: ethabi::Function,
    ) -> Result<Res, ContractCallError> {
```

## Snippet 3

Context: `prover/crates/bin/prover_cli/src/commands/status/l1.rs:80` (changes a sensitive control or state-update path)

Before
```rust
.await?;

    let fflonk_verification_key_hash: H256 =
        CallFunctionArgs::new("verificationKeyHash", U256::from(FFLONK_VERIFIER_TYPE))
            .for_contract(contracts_config.verifier_addr, &helper::verifier_contract())
            .call(&query_client)
            .await?;
```
After
```rust
.await?;

    let function = helper::verifier_contract()
        .functions_by_name("verificationKeyHash")
        .map_err(|x| ContractCallError::Function(x))?[1]
        .clone();

    let fflonk_verification_key_hash: H256 =
```

## Snippet 4

Context: `core/node/eth_watch/src/client.rs:322` (changes a sensitive control or state-update path)

Before
```rust
) -> Result<H256, ContractCallError> {
        // New verifier returns the hash of the verification key.
        CallFunctionArgs::new("verificationKeyHash", U256::from(FFLONK_VERIFIER_TYPE))
            .for_contract(verifier_address, &self.verifier_contract_abi)
            .call(&self.client)
            .await
    }
```
After
```rust
) -> Result<H256, ContractCallError> {
        // New verifier returns the hash of the verification key.
        let function = self
            .verifier_contract_abi
            .functions_by_name("verificationKeyHash")
            .map_err(|x| ContractCallError::Function(x))?[1]
            .clone();
        CallFunctionArgs::new("verificationKeyHash", U256::from(FFLONK_VERIFIER_TYPE))
```

# Fix Pattern

For overloaded contract functions, pass the exact ABI function entry into the low-level call helper and enforce returned configuration values where they affect genesis validation.

## How It Was Fixed

The patch adds `call_with_function` to `ContractCall`, updates FFLONK `verificationKeyHash` callers to select the intended overload explicitly, and adds a genesis validation error when the on-chain FFLONK verification key hash does not match the configured hash.

# Why It Matters

1. Verification key hashes are important cryptographic configuration values.

2. Overloaded ABI functions can be called incorrectly if the intended function is not selected explicitly.

3. Genesis now fails on a FFLONK verification key hash mismatch.

4. The evidence supports a correctness and hardening fix, but not a confirmed vulnerability.

# Evidence Notes

Evidence is limited to the supplied diff excerpts and mapped context for commit `1c0098489` titled `fix calling contract`. The evidence supports the exact ABI selection change and the new FFLONK genesis mismatch check. It does not prove attacker influence over the verifier address, ABI, or configuration, nor does it prove invalid-proof acceptance or other concrete security impact. Protocol security invariant: Genesis and L1 verifier monitoring should read the intended verifier contract function for each proof-system variant and compare the resulting verification key hash against local configuration before relying on it. Verification notes: The patch does not show that invalid proofs could be accepted on-chain. The patch does not show attacker control over verifier contract address or ABI selection. The patch does not prove consensus divergence or fund loss. The CLI status change is diagnostic and is not itself an enforcement path. The exact behavior of the previous generic overloaded function lookup is inferred from the provided diff, not independently proven. No exploit path is established by the supplied evidence. Previous overloaded-function behavior is partly inferred from the shown generic `call` implementation and changed call sites. CLI status changes are diagnostic support, not enforcement. Treat as unclear security relevance rather than a confirmed or likely vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cryptographic-configuration-validation`
Final impact type: `configuration-integrity, correctness-or-hardening`
Final confidence: `medium`
Final tags: `blockchain-core, genesis-validation, verifier-key-hash, abi-overload, security-hardening`

The patch does not prove a concrete exploitable vulnerability, but it clearly tightens a security-sensitive invariant: genesis validation now rejects mismatched FFLONK verifier verification-key hashes, and callers explicitly select the intended overloaded ABI function when reading that hash. Because verifier key hashes are cryptographic configuration and the validation path gates acceptance of genesis parameters, this is best retained as security-hardening rather than a confirmed security fix.

## Security Evidence

1. Adds a genesis-time error when the on-chain FFLONK verification key hash differs from configured fflonk_snark_wrapper_vk_hash.
2. Changes FFLONK verificationKeyHash reads to select the intended overloaded ABI entry explicitly with functions_by_name(...)?[1].clone().
3. The affected values are verifier verification-key hashes, which are cryptographic configuration inputs.
4. The enforcement change is in validate_genesis_params, not only in diagnostic CLI code.

## Missing Evidence

1. No evidence shows attacker control over the verifier address, ABI, or genesis configuration.
2. No evidence proves invalid proof acceptance, consensus divergence, fund loss, or chain compromise.
3. The prior overloaded-function resolution behavior is only inferred from the patch context.
4. No tests or incident context are supplied to show the previous behavior caused a security failure.

## Claim Boundaries

1. Classify as security-hardening, not a confirmed vulnerability fix.
2. Do not claim exploitable invalid-proof acceptance from the supplied evidence.
3. Do not treat the CLI status update alone as security enforcement.
4. The supported claim is limited to stricter cryptographic configuration validation and safer ABI overload selection.
