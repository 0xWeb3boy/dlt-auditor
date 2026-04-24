# Code-Shape Card

## Metadata

- ID: `sui-2023-04-21-sui-storage-b149ca0b9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `wallet-content-script-message-validation`

## Code Shape Summary

- Wallet-ext: test site-cs messaging (#9444) looks like a focused hardening change in the storage path of sui. The strongest evidence spans `apps/wallet/src/background/connections/ContentScriptConnection.ts` and `apps/wallet/playwright.config.ts`. The affected state likely includes `command`, `port`, and `process`.

## Search Motifs

- input-validation enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The storage sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- The fix pattern is to tighten the sensitive storage control path so the key invariant is enforced before downstream work continues.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
