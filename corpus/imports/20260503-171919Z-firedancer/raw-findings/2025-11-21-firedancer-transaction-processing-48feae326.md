---
case_id: case_20251121_48feae326
project: firedancer
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2025-11-21
source_refs:
  - git:48feae326263be3f73fcbbac5e11bbadb00a7d4b
  - "src/discof/restore/fd_snapin_tile.c:520"
  - "src/disco/gui/fd_gui_config_parse.h:7"
  - "src/disco/gui/fd_gui_config_parse.c:67"
  - "src/app/firedancer/topology.c:429"
bug_class: out-of-bounds-read
impact_type:
  - memory-safety
tags:
  - gui
  - config-parser
  - cjson
  - bounds-check
  - out-of-bounds-read
  - memory-safety
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a memory-safety overread in Firedancer's GUI validator-info config parser. The strongest evidence is the parser changing its bounds check from json_str_sz to json_str_sz+1 before calling cJSON_ParseWithLengthOpts, with a comment that this cJSON API requires a byte after the JSON payload. A supporting topology change increases the snapin_gui link size to a WITH_NULL variant so the extra byte is available at the inter-tile buffer boundary.

## Observed Patch Facts

1. In `src/discof/restore/fd_snapin_tile.c`, the patch replaces `FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ, since this the the` with `FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ, since this the size`.

2. In `src/disco/gui/fd_gui_config_parse.h`, the patch replaces `#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_NAME_SZ ( 80UL) /* +1UL for NULL terminato...` with `#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_NAME_SZ ( 80UL) /* +1UL for NULL terminato...`.

3. In `src/disco/gui/fd_gui_config_parse.c`, the patch replaces `CHECK_LEFT( json_str_sz );` with `CHECK_LEFT( json_str_sz+1UL ); /* cJSON_ParseWithLengthOpts requires having byte afte...`.

4. In `src/app/firedancer/topology.c`, the patch replaces `/**/ fd_topob_link( topo, "snapin_gui", "snapin_gui", 128UL, FD_GUI_CONFIG_PARSE_MAX_...` with `/**/ fd_topob_link( topo, "snapin_gui", "snapin_gui", 128UL, FD_GUI_CONFIG_PARSE_MAX_...`.

## Project Context

The changed code sits primarily in `src/discof/restore`, `src/discof`, `src/disco/gui`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/discof/restore/fd_snapla_tile.c`, `src/discof/restore/fd_snapin_tile_vinyl.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/discof/restore/fd_snapla_tile.c`, `src/discof/restore/utils/fd_ssparse.h`. The strongest project-level identifiers around this patch are `define`, `result`, `account_data`, and `size`. Nearby tests or test-like files include `src/disco/gui/fuzz_config_parser.c`, `src/app/firedancer-dev/commands/send_test/send_test.c`.

## Before/After Behavior

Before the patch, fd_gui_config_parse_validator_info_check verified only that json_str_sz payload bytes remained before calling cJSON_ParseWithLengthOpts. The snapin_gui link was sized to FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ, matching the maximum accepted account-data size but not the extra byte required by the parser. After the patch, the parser requires json_str_sz+1 bytes and the snapin_gui link uses FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ_WITH_NULL.

# Root Cause

The parser bounds check did not account for cJSON_ParseWithLengthOpts reading or requiring one byte past the declared JSON payload. The upstream snapin_gui buffer sizing also did not reserve that extra byte for maximum-sized inputs.

## Walkthrough

1. Snapshot account-data handling in fd_snapin_tile.c filters ConfigProgram-owned account data for GUI handling when GUI output is enabled and the data matches the expected validator-info shape and size limit.

2. That data can be published over the snapin_gui path toward GUI parsing.

3. Before the fix, topology.c sized the snapin_gui link using FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ.

4. The parser loaded json_str_sz and checked only CHECK_LEFT(json_str_sz) before calling cJSON_ParseWithLengthOpts.

5. The patch changes the parser check to CHECK_LEFT(json_str_sz+1UL), explicitly requiring a byte after the JSON payload.

6. The patch also changes the snapin_gui link size to FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ_WITH_NULL, aligning buffer capacity with the parser requirement.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/disco/gui/fd_gui_config_parse.c | 67 | validator-info config account parser; enforces payload-plus-one-byte availability before calling cJSON_ParseWithLengthOpts |
| src/app/firedancer/topology.c | 429 | snapin_gui topology link sizing; allocates buffer capacity for max config account data plus the extra byte required by the parser |
| src/discof/restore/fd_snapin_tile.c | 520 | snapshot account-data path that filters ConfigProgram validator-info accounts and publishes them toward GUI parsing |
| src/disco/gui/fd_gui_config_parse.h | 7 | shared GUI config parser size constants defining validator-info and maximum valid account sizes |

## Code Snippets

## Snippet 1

Context: `src/discof/restore/fd_snapin_tile.c:520` (changes bounds, limits, or capacity handling)

Before
```c
/* We exepect ConfigKeys Vec to be length 2.  We expect the size
           of ConfigProgram-owned accounts to be
           FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ, since this the the
           size that the solana CLI allocates for them.  Although the
           Config program itself does not enforce this limit, the vast
           majority of accounts (with a tiny number of excpetions on
           devnet) are maintained with the solana cli. */
        if( FD_UNLIKELY( ctx->gui_out.idx!=ULONG_MAX && !memcmp( result->account_data.owner, fd_solana_config_program_id.key, sizeof(fd_hash_t) ) && result->account_data.data_sz && *(uchar *)result->account_data.data==2UL && result->account_data.data_sz<=FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ ) ) {
```
After
```c
/* We exepect ConfigKeys Vec to be length 2.  We expect the size
           of ConfigProgram-owned accounts to be
           FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ, since this the size
           that the solana CLI allocates for them.  Although the Config
           program itself does not enforce this limit, the vast majority
           of accounts (with a tiny number of excpetions on devnet) are
           maintained with the solana cli. */
        if( FD_UNLIKELY( ctx->gui_out.idx!=ULONG_MAX && !memcmp( result->account_data.owner, fd_solana_config_program_id.key, sizeof(fd_hash_t) ) && result->account_data.data_sz && *(uchar *)result->account_data.data==2UL && result->account_data.data_sz<=FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ ) ) {
```

## Snippet 2

Context: `src/disco/gui/fd_gui_config_parse.h:7` (changes a sensitive control or state-update path)

Before
```c
/* https://github.com/anza-xyz/agave/blob/master/account-decoder/src/validator_info.rs */
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_NAME_SZ     (  80UL) /* +1UL for NULL terminator */
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_WEBSITE_SZ  (  80UL)
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_DETAILS_SZ  ( 300UL)
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_ICON_URI_SZ (  80UL)
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_KEYBASE_USERNAME_SZ (80UL)
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_MAX_SZ      ( 576UL) /* does not include size of ConfigKeys */
```
After
```c
/* https://github.com/anza-xyz/agave/blob/master/account-decoder/src/validator_info.rs */
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_NAME_SZ             (  80UL) /* +1UL for NULL terminator */
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_WEBSITE_SZ          (  80UL)
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_DETAILS_SZ          ( 300UL)
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_ICON_URI_SZ         (  80UL)
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_KEYBASE_USERNAME_SZ (  80UL)
#define FD_GUI_CONFIG_PARSE_VALIDATOR_INFO_MAX_SZ              ( 576UL) /* does not include size of ConfigKeys */
```

## Snippet 3

Context: `src/disco/gui/fd_gui_config_parse.c:67` (changes a sensitive control or state-update path)

Before
```c
CHECK_LEFT( sizeof(ulong) ); ulong json_str_sz = FD_LOAD( ulong, data+i ); i += sizeof(ulong);

  CHECK_LEFT( json_str_sz );
  cJSON * json = cJSON_ParseWithLengthOpts( (char *)(data+i), json_str_sz, NULL, 0 );
  if( FD_UNLIKELY( !json ) ) return 0;
```
After
```c
CHECK_LEFT( sizeof(ulong) ); ulong json_str_sz = FD_LOAD( ulong, data+i ); i += sizeof(ulong);

  CHECK_LEFT( json_str_sz+1UL ); /* cJSON_ParseWithLengthOpts requires having byte after the JSON payload */
  cJSON * json = cJSON_ParseWithLengthOpts( (char *)(data+i), json_str_sz, NULL, 0 );
  if( FD_UNLIKELY( !json ) ) return 0;
```

## Snippet 4

Context: `src/app/firedancer/topology.c:429` (changes a sensitive control or state-update path)

Before
```c
if( FD_LIKELY( config->tiles.gui.enabled ) ) {
      /**/             fd_topob_link( topo, "snapct_gui",   "snapct_gui",   128UL,                                    sizeof(fd_snapct_update_t),    1UL );
      /**/             fd_topob_link( topo, "snapin_gui",   "snapin_gui",   128UL,                                    FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ, 1UL );
    }
    if( vinyl_enabled ) {
```
After
```c
if( FD_LIKELY( config->tiles.gui.enabled ) ) {
      /**/             fd_topob_link( topo, "snapct_gui",   "snapct_gui",   128UL,                                    sizeof(fd_snapct_update_t),    1UL );
      /**/             fd_topob_link( topo, "snapin_gui",   "snapin_gui",   128UL,                                    FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ_WITH_NULL, 1UL );
    }
    if( vinyl_enabled ) {
```

# Fix Pattern

Enforce the third-party parser's buffer contract at the call site and align upstream buffer sizing with the same payload-plus-sentinel requirement.

## How It Was Fixed

The parser check in src/disco/gui/fd_gui_config_parse.c was tightened from CHECK_LEFT(json_str_sz) to CHECK_LEFT(json_str_sz+1UL). The snapin_gui topology link in src/app/firedancer/topology.c was changed from FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ to FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ_WITH_NULL.

# Why It Matters

1. Prevents cJSON from accessing past the parser-visible account-data buffer.

2. Keeps parser bounds checks and inter-tile buffer sizing consistent.

3. Applies to GUI parsing of snapshot-derived ConfigProgram validator-info account data.

4. Evidence supports a bounded memory-safety overread claim, not consensus impact, RCE, or data exfiltration.

# Evidence Notes

The core evidence is the src/disco/gui/fd_gui_config_parse.c hunk changing CHECK_LEFT(json_str_sz) to CHECK_LEFT(json_str_sz+1UL) with the explanatory comment about cJSON_ParseWithLengthOpts. The topology hunk at src/app/firedancer/topology.c supports the same invariant by using FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ_WITH_NULL. The fd_snapin_tile.c evidence grounds the path that forwards filtered ConfigProgram account data toward GUI handling. The provided evidence does not prove exploitability beyond an overread condition, does not establish consensus-critical impact, and does not establish impact when the GUI path is disabled. Protocol security invariant: The GUI config parser must only pass buffers to cJSON_ParseWithLengthOpts when the declared JSON payload length and the parser-required following byte are both accessible. The snapin_gui transport buffer must preserve the same payload-plus-one-byte capacity invariant for maximum-sized validator-info account data. Verification notes: The patch does not show a consensus-critical state transition bug. The patch does not prove remote code execution or data exfiltration. The patch does not show that arbitrary accounts bypass the ConfigProgram owner and size filters. The patch does not establish impact when the GUI tile is disabled. The evidence supports an out-of-bounds read/overrun prevention claim, not state corruption. No PoC, crash trace, sanitizer output, or test result is included in the provided evidence. The claim is limited to likely buffer overread prevention in the GUI config parser path. Confidence is medium because the code change directly supports the overread thesis, but exploitability and full input control are not demonstrated. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `out-of-bounds-read`
Final impact type: `memory-safety`
Final tags: `gui, config-parser, cjson, bounds-check, out-of-bounds-read, memory-safety`

The supplied patch evidence supports retaining this as security hardening: the parser now requires one additional accessible byte before calling cJSON_ParseWithLengthOpts, and the topology buffer size is increased to provide that byte for maximum-sized GUI config inputs. This directly addresses a potential parser overrun/overread condition, but the evidence does not prove exploitability, consensus impact, state corruption, or a concrete security incident, so security-fix and the original state-integrity framing are too strong.

## Security Evidence

1. Commit subject explicitly says "gui: fix cJSON_Parse overrun".
2. Parser bounds check changes from CHECK_LEFT(json_str_sz) to CHECK_LEFT(json_str_sz+1UL).
3. Inline comment states cJSON_ParseWithLengthOpts requires a byte after the JSON payload.
4. snapin_gui link size changes from FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ to FD_GUI_CONFIG_PARSE_MAX_VALID_ACCT_SZ_WITH_NULL.
5. Input appears to come from snapshot ConfigProgram account data forwarded to GUI parsing.

## Missing Evidence

1. No crash trace, sanitizer report, PoC, or exploit scenario is provided.
2. No evidence that the overread crosses a sensitive boundary or leaks data.
3. No evidence of consensus-critical state corruption or transaction-processing impact.
4. No proof of impact when the GUI path is disabled.
5. No test output showing the previous behavior was externally triggerable.

## Claim Boundaries

1. Validated only as GUI config parser memory-safety hardening.
2. Do not claim state corruption, replay compromise, or state-integrity impact from this evidence.
3. Do not claim RCE, data exfiltration, or consensus failure.
4. The supported issue is a potential out-of-bounds read/overrun due to a third-party parser buffer contract.
5. The finding should be scoped to parser bounds and inter-tile buffer sizing consistency.
