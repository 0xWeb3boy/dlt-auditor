# Root-Cause Card

## Metadata

- ID: `rippled-2019-08-05-rippled-p2p-networking-9213c49ca`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `tls-client-config-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `trust-root-and-freshness-validation`

## Violated Invariant

- Invariant: Externally supplied trust material must be fetched, redirected, cached, and accepted only under the configured trust roots and transport policy.

## Trust Boundary

- Boundary: remote peer message -> local node networking/resource manager

## Attack Surface

- Entrypoint type: p2p-message-handler
- Sensitive sink: peer session state, fetch scheduling, handshake slots, or local resource accounting

## Impact Pattern

- Primary impact: outbound-tls-verification-hardening
- Secondary impact: Primarily node-local resource, liveness, or peer-trust impact with possible network-level amplification.

## Short Reusable Lesson

- The patch is likely security-relevant because it changes ValidatorSite and SSLHTTPDownloader outbound HTTPS paths to use a shared HTTPClientSSLContext and adds explicit pre-connect and post-connect verification calls.
