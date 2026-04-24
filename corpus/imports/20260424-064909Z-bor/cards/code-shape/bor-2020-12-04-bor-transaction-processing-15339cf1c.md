# Code-Shape Card

## Metadata

- ID: `bor-2020-12-04-bor-transaction-processing-15339cf1c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsigned-advisory-feed`

## Code Shape Summary

- The evidence supports that this commit adds a cmd/geth vulnerability/version check and includes signed advisory-feed handling with Minisign/Signify test material. It does not support a stronger claim that the commit fixes a proven exploitable vulnerability in existing code. The CorruptedDAG content in the JSON files is advisory data consumed by the checker, not the bug being fixed here. Root cause: Not established by the provided evidence. At most, the commit shows that advisory-feed authenticity was implemented or strengthened in the new checker. The evidence does not prove that older code accepted unauthenticated advisory data or that a concrete security bug existed before this commit.

## Search Motifs

- block/header/transaction validation has a special case that bypasses a consensus rule
- fork-choice or state-transition code derives canonical state before checking all protocol invariants
- reward, validator-set, timestamp, gas, or root validation differs across execution paths or fork eras

## Typical Asymmetry

- Attacker-controlled data crosses untrusted signed payload to verifier or signer boundary and reaches signer recovery, authorization, or replay-protection decision before the missing property is enforced.

## Patch Pattern

- Add signature verification and trusted-key material around externally supplied security metadata as part of an advisory-check feature, with tests and support code for signer/key handling.

## False Match Warnings

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.
- Consensus findings need evidence that different valid-looking inputs or node versions can reach divergent acceptance, state, or fork-choice behavior.
