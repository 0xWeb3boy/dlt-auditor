# Code-Shape Card

## Metadata

- ID: `go-ethereum-2015-03-25-go-ethereum-cryptography-de7af720d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-reflection-amplification`

## Code Shape Summary

- The findnode request path could generate a substantially larger neighbors response before verifying that the recovered sender NodeID had an existing bond. In a UDP protocol, the commit states this allowed spoofed-source findnode packets to reflect amplified traffic at a victim address.

## Search Motifs

- Motif 1: p2p message missing exact checks for udp reflection amplification
- Motif 2: security-sensitive path reaches network response generation and peer table mutation before rejecting malformed or unauthorized input
- Motif 3: Require a prior lightweight peer bond before performing an asymmetric UDP response

## Typical Asymmetry

- A remote peer or spoofed sender can trigger more local work, state change, or outbound traffic than the cost of the crafted message.

## Patch Pattern

- Require a prior lightweight peer bond before performing an asymmetric UDP response.

## False Match Warnings

- Applies to UDP discovery findnode handling and neighbors responses.
- Supports a DDoS reflection/amplification fix, not a general cryptography vulnerability.
