# Validation Card

## Metadata

- ID: `thor-2026-04-20-thor-transaction-processing-0734dc66`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `chain-id-validation-hardening`

## What Confirmed The Issue

- Txpool rejects EthTyped1559 before INTERSTELLAR and rejects mismatched EthChainID after it.
- Consensus validation applies equivalent fork and chain-ID checks.
- Runtime CHAINID switches to the configured Ethereum chain ID after the fork.
- Phase 4 kept the finding as likely `security-hardening`, not as a confirmed vulnerability.

## What Could Have Invalidated It

- No path can submit or include EthTyped1559 before INTERSTELLAR.
- The typed transaction signature scheme is already checked against the configured chain ID before txpool/consensus validation.

## Severity Guidance

- Expected impact band: medium chain-wide domain-separation hardening
- Expected severity band: `medium_or_low`
- Rationale: Chain ID is signature domain-separation material in consensus transaction processing. The patch is likely hardening, but the validation notes do not prove a practical replay exploit.

## False-Positive Cautions

- No issue if typed transactions are impossible before the fork.
- No issue if signature recovery independently rejects mismatched chain IDs everywhere.
- Fork configuration changes without admission checks are not enough to establish a security case.
