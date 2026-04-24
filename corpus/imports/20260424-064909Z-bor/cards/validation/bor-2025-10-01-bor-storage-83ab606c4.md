# Validation Card

## Metadata

- ID: `bor-2025-10-01-bor-storage-83ab606c4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- receiveWitnessPage handles peer-supplied witness pages and now rejects page.Page >= page.TotalPages.
- The code no longer blindly overwrites witTotalPages[page.Hash]; it now rejects inconsistent TotalPages values for the same hash.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: hardening
- Expected severity band: low

## False-Positive Cautions

- No proof in the patch alone that the old behavior was exploitable in practice.
- No demonstrated impact such as crash, resource exhaustion, consensus fault, or state corruption.
