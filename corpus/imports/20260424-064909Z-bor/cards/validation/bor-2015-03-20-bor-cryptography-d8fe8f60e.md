# Validation Card

## Metadata

- ID: `bor-2015-03-20-bor-cryptography-d8fe8f60e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- ethash_get_datasize and ethash_get_cachesize now reject epochs >= 2048 instead of relying on assert before fixed-table indexing.
- ethash_compute_cache_nodes now returns failure when cache_size is misaligned instead of assuming the invariant holds.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: hardening
- Expected severity band: low

## False-Positive Cautions

- No proof that untrusted or remote input can drive invalid block_number, cache_size, or full_size values in the deployed product.
- No commit message, test, or advisory links the change to a reported security issue, exploit, or CVE.
