# Root-Cause Card

## Metadata

- ID: `fuel-core-2025-03-11-fuel-core-transaction-processing-8b3eb35018`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `missing-signature-verification`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `signer-authorization`

## Violated Invariant

- A signed status or preconfirmation update must be authenticated against the authorized signer before it mutates client-visible transaction status.

## Trust Boundary

- Boundary: `p2p-message->status-manager`
- Entrypoint type: `p2p-message-handler`
- Sensitive sink: `transaction preconfirmation status updates`

## Attack Surface

- Send or relay a sealed preconfirmation message containing chosen status updates.
- Reach the status manager through the network-facing preconfirmation path.

## Exploit Preconditions

- The handler destructures sealed content before verifying the seal.
- Clients or services trust preconfirmation status as meaningful authority output.

## Impact Pattern

- Primary impact: `unauthorized-action`
- Secondary impact: `request-forgery-or-replay`
- Blast radius: `node-local`
- Severity guess: `high`

## Short Reusable Lesson

- Do not destructure or act on sealed authority messages until the seal has been verified in the same trust domain.
