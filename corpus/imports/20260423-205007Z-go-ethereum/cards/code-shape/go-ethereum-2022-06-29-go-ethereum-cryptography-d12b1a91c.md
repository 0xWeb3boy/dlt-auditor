# Code-Shape Card

## Metadata

- ID: `go-ethereum-2022-06-29-go-ethereum-cryptography-d12b1a91c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-terminal-block-validation-hardening`

## Code Shape Summary

- The transition verifier delegated the PoW side and PoS side to separate verification paths but lacked an explicit check that the PoW prefix did not cross terminal total difficulty before its final header. The result-merging logic also needed to avoid overwriting terminal-block validation errors with ordinary old-engine results.

## Search Motifs

- Motif 1: p2p message missing exact checks for consensus terminal block validation hardening
- Motif 2: security-sensitive path reaches canonical-chain selection or persistent chain-state update before rejecting malformed or unauthorized input
- Motif 3: Add an explicit consensus-boundary invariant check before merging asynchronous verifier results, mark all affected headers with a domain-specific error, and prevent later generic verifier output from overwriting that failure

## Typical Asymmetry

- A remote peer or spoofed sender can trigger more local work, state change, or outbound traffic than the cost of the crafted message.

## Patch Pattern

- Add an explicit consensus-boundary invariant check before merging asynchronous verifier results, mark all affected headers with a domain-specific error, and prevent later generic verifier output from overwriting that failure.

## False Match Warnings

- Classify as consensus validation hardening, not a proven exploitable vulnerability.
- Do not claim cryptographic primitive failure or signature-validation weakness.
