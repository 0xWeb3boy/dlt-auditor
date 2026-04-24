# Prompt Family: Attestation, Trust, And Freshness

## Use This For

- TEE capability validation gaps.
- Trust-root sync or registration gating bugs.
- Freshness or policy synchronization bugs.
- Acceptance of test credentials in production paths.
- Peer identity misbinding in privileged RPC or session setup.

If the repo does not use TEEs or attestation, reuse this prompt for the nearest equivalent trust-establishment layer:

- light-client trust roots,
- bridge validator sets,
- checkpoint verification,
- signer-set rotation,
- node identity bootstrapping,
- remote prover verification,
- HSM-backed workers or coprocessors.

## Prompt

```text
Hunt for bugs where a blockchain or DLT system trusts attestation, trust roots, signer sets, remote proofs, or peer identity state too early, too broadly, or for too long.

Focus on:
- attestation reports, trust roots, signer sets, remote proofs, and capability handling
- trust-root synchronization and readiness gating
- privileged RPC or session setup
- trust-policy propagation
- freshness proofs
- production-vs-test credential acceptance

Search patterns:
- availability or registration paths that do not wait for trust sync
- capability, quote, or proof objects consumed before local Verify calls
- policy state cached in one component without refresh on epoch, redeploy, upgrade, signer-set rotation, or policy update
- peer or session APIs that select a target identity but do not bind that identity into verification
- code paths that accept well-formed test keys because they verify cryptographically
- signer or policy interfaces shared across scopes without explicit domain binding
- external consensus-client, bridge-client, checkpoint, milestone, or oracle reads that feed local consensus should be pinned to one deterministic snapshot boundary. Check whether time-based, latest, retry, or fallback queries are converted into an explicit height, hash, epoch, finalized checkpoint, or signer-set identity before the data affects block validity, finalization, or state derivation

Questions to answer:
1. What trust decision is being made here?
2. What data is that trust decision based on?
3. How fresh must that data be?
4. What event should invalidate or refresh the trust state?
5. Is the identity or policy bound to the specific chain, runtime, peer, bridge domain, prover, or session that uses it?

Severity guidance:
- High if the issue can bypass privileged trust policy, expose privileged key material or bridge behavior, or confuse peer identity.
- Medium for stale trust policy, premature readiness, or acceptance of non-production credentials.
```
