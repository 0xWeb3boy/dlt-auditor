# Validation Card

## Metadata

- ID: `optimism-2026-02-19-optimism-transaction-processing-543510ee9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- Commit body explicitly says unbounded zlib decompression was replaced with a limit-aware variant to prevent zip-bomb OOM.
- decompress_brotli now caps the initial output buffer by max_rlp_bytes_per_channel.
- The brotli decompression loop is documented and structured to stop/truncate at the configured limit instead of unbounded growth.
- The affected code is the channel decompression path before batch decoding, so it handles attacker-influenced compressed input.

## What Could Have Invalidated It

- No direct diff hunk shows the zlib API replacement at the call site.
- No proof of an observed exploit or demonstrated pre-fix OOM in a deployed node.
- No evidence here establishes a concrete remote attack path or real-world reachability.
- Part of the patch is also protocol/spec-correctness work, which dilutes a pure security-fix reading.

## Severity Guidance

- Expected impact band: availability-or-liveness
- Expected severity band: medium_or_low

## False-Positive Cautions

- No direct diff hunk shows the zlib API replacement at the call site.
- No proof of an observed exploit or demonstrated pre-fix OOM in a deployed node.
- No evidence here establishes a concrete remote attack path or real-world reachability.
