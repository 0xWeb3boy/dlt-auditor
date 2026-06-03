# Code-Shape Card

Record: `omni-cantina-m03-signature-malleability-raw-duplicate`
Project: `omni-network`
Source finding: `Omni Cantina M-3`

## Search Shape

Signature verification uses semantic address recovery, while duplicate persistence treats raw byte differences for the same signer/root as a fatal bug.

## Motifs

- `k1util.Verify`
- `SigToPub`
- `S = -S and V toggle`
- `isDoubleSign`
- `bytes.Equal signature`
- `different signature for identical vote`
- `replayed vote`

## Negative Signals

- Verifier rejects non-canonical signatures before recovery.
- Signatures are normalized before storage.
- Identical signer/root duplicates ignore raw-byte differences.

## Likely Fix Shape

Canonicalize or reject malleable signatures before storage, and treat same signer/root duplicates as idempotent once the signature has verified.
