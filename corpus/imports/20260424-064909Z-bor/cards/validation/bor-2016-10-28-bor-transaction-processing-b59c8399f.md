# Validation Card

## Metadata

- ID: `bor-2016-10-28-bor-transaction-processing-b59c8399f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `message-signing-domain-separation`

## What Confirmed The Issue

- Commit metadata states eth_sign was changed to prefix and hash messages before signing.
- crypto.Sign is newly documented as unsafe for adversary-chosen inputs, indicating a security-sensitive risk in raw signing.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: integrity
- Expected severity band: high

## False-Positive Cautions

- No direct diff excerpt is provided for the RPC handler that performs the prefix-and-hash step.
- No proof that the prior behavior enabled a concrete exploit in practice.
