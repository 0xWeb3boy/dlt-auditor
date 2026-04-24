# Validation Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-858c6ae6d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit-enforcement`

## What Confirmed The Issue

- GetLogs now calls checkBlockRangeLimit(begin, end, head, api.sys.cfg.RangeLimit) before constructing a range filter.
- GetFilterLogs adds the same range-limit enforcement for replayed/saved filter criteria.

## What Could Have Invalidated It

- Do not flag if the value is produced only by trusted local code and cannot be influenced across a protocol, RPC, or persistence boundary.
- Do not treat as exploitable if an earlier mandatory validation step rejects the malformed input before the sensitive sink.

## Severity Guidance

- Expected impact band: availability
- Expected severity band: medium

## False-Positive Cautions

- No supplied hunk shows a demonstrated exploit, benchmark, or incident tied to oversized RPC range queries.
- The evidence does not show whether these RPC methods were exposed to untrusted callers in affected deployments.
