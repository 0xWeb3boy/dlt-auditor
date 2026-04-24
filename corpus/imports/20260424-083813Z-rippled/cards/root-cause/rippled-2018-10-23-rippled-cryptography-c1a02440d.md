# Root-Cause Card

## Metadata

- ID: `rippled-2018-10-23-rippled-cryptography-c1a02440d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-list-redirect-scheme-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `trust-root-and-freshness-validation`

## Violated Invariant

- Invariant: Externally supplied trust material must be fetched, redirected, cached, and accepted only under the configured trust roots and transport policy.

## Trust Boundary

- Boundary: signed object or key material -> local trust and verification decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: accepted signature, signer identity, manifest, or replay-sensitive object

## Impact Pattern

- Primary impact: validator-list-source-integrity
- Secondary impact: Potentially network-wide safety or trust impact for nodes that accept the affected state or trust decision.

## Short Reusable Lesson

- The draft correctly rejects the unsupported replay/signature-validation theory. The grounded change is that validator-site redirects now reject schemes other than http and https while the commit adds explicit configured file:// validator-list support.
