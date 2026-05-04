# Code-Shape Card

## Metadata

- ID: `stellar-core-2015-03-10-stellar-core-transaction-processing-6bd5130f1`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-verification-amplification`

## Code Shape Summary

- A nested signer/signature loop invoked expensive verification before checking decorated-signature hints, and extra signatures could remain unused on successful paths.

## Search Motifs

- verifySig inside nested loop over signatures and signers
- decorated signature hint ignored before verification
- unused signatures accepted after threshold reached
- signature usage vector added to transaction frame

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Filter signer candidates using cheap hint metadata, mark consumed signatures, and reject envelopes containing unused authentication material.

## False Match Warnings

- Do not claim signature forgery when the patch only reduces verification work.
- Batch verification or cached verification can change the amplification model.
- Hint mismatches are not a bug if they are rejected before expensive verification.
