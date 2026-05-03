---
case_id: case_20240117_df9ddc2d1
project: firedancer
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2024-01-17
source_refs:
  - git:df9ddc2d10eba3fee308805904ba98fc28a90ef0
  - "src/app/fdctl/run/tiles/fd_shred.c:696"
  - "src/app/fdctl/topology.h:172"
  - "src/app/fdctl/run/tiles/sign.seccomppolicy:1"
  - "src/disco/keyguard/fd_keyguard_match.c:248"
bug_class: signing-isolation-hardening
impact_type:
  - privilege-reduction
  - signing-boundary-hardening
confidence: medium
tags:
  - validator-ops
  - remote-signing
  - shred-signing
  - keyguard
  - payload-authorization
  - seccomp
  - privilege-separation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is plausibly security-relevant because it adds an explicit remote signing path for shreds, a signing tile seccomp policy, and role-based keyguard payload authorization for leader shred signing. However, the provided evidence does not establish a concrete pre-patch vulnerability, attacker reachability, arbitrary signing primitive, key disclosure, forged shred impact, or consensus impact. Treat this as unclear security relevance rather than a validated vulnerability fix.

## Observed Patch Facts

1. In `src/app/fdctl/run/tiles/fd_shred.c`, the patch replaces `if( FD_UNLIKELY( tile->in_cnt != 4 ||` with `if( FD_UNLIKELY( tile->in_cnt != 5 ||`.

2. In `src/app/fdctl/topology.h`, the patch adds `int in_link_poll[ 16 ]; /* If each link that this tile reads from should be polled by...`.

3. In `src/app/fdctl/run/tiles/sign.seccomppolicy`, the patch adds `# logfile_fd: It can be disabled by configuration, but typically tiles`.

4. In `src/disco/keyguard/fd_keyguard_match.c`, the patch adds `FD_FN_PURE int`.

## Project Context

The changed code sits primarily in `src/app/fdctl/run/tiles`, `src/app/fdctl/run`, `src/app/fdctl`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/app/fdctl/topology.c`, `src/app/fdctl/run/tiles/tiles.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/app/fdctl/topology.c`, `src/app/fdctl/run/tiles/fd_verify.c`. The strongest project-level identifiers around this patch are `tile`, `links`, `topo`, and `kind`. Nearby tests or test-like files include `src/app/fddev/tests/test_single_txn.sh`, `src/app/fddev/tests/test_single_transfer.sh`.

## Before/After Behavior

Before the change, the shred tile topology check shown in the evidence expected four inputs and one output, with no visible SIGN_TO_SHRED input or SHRED_TO_SIGN output. After the change, the shred tile requires those sign links. The patch also adds in_link_poll topology metadata, introduces a sign tile seccomp policy, and adds fd_keyguard_payload_authorize, mapping FD_KEYGUARD_ROLE_LEADER to fd_keyguard_payload_matches_shred(data, sz).

# Root Cause

The evidence supports only that the previous architecture did not show an explicit sign tile/keyguard path for shred signing in the cited topology checks. It does not prove that the old architecture allowed unauthorized signing or that this was a vulnerability rather than an architectural migration to remote signing.

## Walkthrough

1. The shred tile previously validated four input links and one network output in the provided fd_shred.c evidence.

2. The patch changes that validation to require a SIGN_TO_SHRED input and SHRED_TO_SIGN output.

3. The topology structure gains in_link_poll metadata for inputs that may be handled manually rather than by generic polling.

4. A new sign.seccomppolicy constrains the signing tile process, including write targets visible in the provided snippet.

5. fd_keyguard_payload_authorize adds role-based dispatch, including LEADER role authorization through shred payload matching.

6. These changes are consistent with signing isolation or hardening, but the evidence does not show attacker-controlled access to the old path or a concrete exploit condition.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/app/fdctl/run/tiles/fd_shred.c | 696 | Requires the shred tile to be wired to the sign tile via explicit sign input/output links before running. |
| src/disco/keyguard/fd_keyguard_match.c | 248 | Adds centralized role-based payload authorization, including LEADER role authorization through shred payload matching. |
| src/app/fdctl/run/tiles/sign.seccomppolicy | 1 | Defines syscall/file-descriptor restrictions for the new signing tile process. |
| src/app/fdctl/topology.h | 172 | Adds topology metadata controlling whether tile inputs are polled by infrastructure, supporting manual handling of signing links. |

## Code Snippets

## Snippet 1

Context: `src/app/fdctl/run/tiles/fd_shred.c:696` (changes a sensitive control or state-update path)

Before
```c
fd_topo_tile_t * tile,
                   void *           scratch ) {
  if( FD_UNLIKELY( tile->in_cnt != 4 ||
                   topo->links[ tile->in_link_id[ NET_IN_IDX     ] ].kind != FD_TOPO_LINK_KIND_NETMUX_TO_OUT    ||
                   topo->links[ tile->in_link_id[ POH_IN_IDX     ] ].kind != FD_TOPO_LINK_KIND_POH_TO_SHRED     ||
                   topo->links[ tile->in_link_id[ STAKE_IN_IDX   ] ].kind != FD_TOPO_LINK_KIND_STAKE_TO_OUT     ||
                   topo->links[ tile->in_link_id[ CONTACT_IN_IDX ] ].kind != FD_TOPO_LINK_KIND_CRDS_TO_SHRED ) )
    FD_LOG_ERR(( "shred tile has none or unexpected input links %lu %lu %lu",
```
After
```c
fd_topo_tile_t * tile,
                   void *           scratch ) {
  if( FD_UNLIKELY( tile->in_cnt != 5 ||
                   topo->links[ tile->in_link_id[ NET_IN_IDX     ] ].kind != FD_TOPO_LINK_KIND_NETMUX_TO_OUT    ||
                   topo->links[ tile->in_link_id[ POH_IN_IDX     ] ].kind != FD_TOPO_LINK_KIND_POH_TO_SHRED     ||
                   topo->links[ tile->in_link_id[ STAKE_IN_IDX   ] ].kind != FD_TOPO_LINK_KIND_STAKE_TO_OUT     ||
                   topo->links[ tile->in_link_id[ CONTACT_IN_IDX ] ].kind != FD_TOPO_LINK_KIND_CRDS_TO_SHRED    ||
                   topo->links[ tile->in_link_id[ SIGN_IN_IDX    ] ].kind != FD_TOPO_LINK_KIND_SIGN_TO_SHRED ) )
```

## Snippet 2

Context: `src/app/fdctl/topology.h:172` (changes a sensitive control or state-update path)

Before
```c
ulong in_link_id[ 16 ];       /* The link_id of each link that this tile reads from, indexed in [0, in_cnt). */
  int   in_link_reliable[ 16 ]; /* If each link that this tile reads from is a reliable or unreliable consumer, indexed in [0, in_cnt). */

  ulong out_link_id_primary;    /* The link_id of the primary link that this tile writes to.  A value of ULONG_MAX means there is no primary output link. */
```
After
```c
ulong in_link_id[ 16 ];       /* The link_id of each link that this tile reads from, indexed in [0, in_cnt). */
  int   in_link_reliable[ 16 ]; /* If each link that this tile reads from is a reliable or unreliable consumer, indexed in [0, in_cnt). */
  int   in_link_poll[ 16 ];     /* If each link that this tile reads from should be polled by the tile infrastructure, indexed in [0, in_cnt).
                                   If the link is not polled, the tile will not receive frags for it and the tile writer is responsible for
                                   reading from the link.  The link must be marked as unreliable as it is not flow controlled. */

  ulong out_link_id_primary;    /* The link_id of the primary link that this tile writes to.  A value of ULONG_MAX means there is no primary output link. */
```

## Snippet 3

Context: `src/app/fdctl/run/tiles/sign.seccomppolicy:1` (changes a sensitive control or state-update path)

Before
```text
(no before snippet captured)
```
After
```text
# logfile_fd: It can be disabled by configuration, but typically tiles
#             will open a log file on boot and write all messages there.
unsigned int logfile_fd

# logging: all log messages are written to a file and/or pipe
#
# 'WARNING' and above are written to the STDERR pipe, while all messages
# are always written to the log file.
```

## Snippet 4

Context: `src/disco/keyguard/fd_keyguard_match.c:248` (changes an authorization or privilege gate)

Before
```c
return 1;
}
```
After
```c
return 1;
}

FD_FN_PURE int
fd_keyguard_payload_authorize( uchar const * data,
                               ulong         sz,
                               int           role ) {
  switch( role ) {
```

# Fix Pattern

Introduce an explicit signing service path and role-based payload validation around leader shred signing, with process-level restrictions for the signing tile.

## How It Was Fixed

The patch wires the shred tile to a sign tile through explicit topology links, adds topology support for selective input polling, creates a seccomp policy for the sign tile, and centralizes keyguard payload authorization so leader-role payloads are checked with fd_keyguard_payload_matches_shred.

# Why It Matters

1. May reduce implicit signing authority in the shred tile path.

2. Adds an explicit boundary for leader shred signing requests and responses.

3. Adds role-specific validation for leader signing payloads.

4. Does not prove arbitrary signing, key compromise, or forged shred impact.

# Evidence Notes

Grounded evidence comes from src/app/fdctl/run/tiles/fd_shred.c line 696, src/disco/keyguard/fd_keyguard_match.c line 248, src/app/fdctl/run/tiles/sign.seccomppolicy line 1, and src/app/fdctl/topology.h line 172. The commit subject uses security language, but the supplied snippets do not establish vulnerability conditions or exploitability. Protocol security invariant: Leader shred signing should be constrained to intended shred payloads and, if remote signing is used, should pass through explicit sign/keyguard topology links with role-specific authorization. Verification notes: Does not prove that pre-patch code allowed arbitrary signing requests. Does not prove private key disclosure or direct key compromise. Does not prove consensus failure, forged shreds, or network-wide exploitability. Does not show attacker-controlled access to the shred tile signing path. Does not establish that the previous direct signing behavior was unintended rather than an architectural baseline. No evidence proves attacker reachability to pre-patch signing behavior. No evidence proves arbitrary payload signing was possible before the patch. No evidence proves private key disclosure or direct key compromise. No evidence proves forged shreds or consensus failure. Classify as unclear rather than a confirmed or likely vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signing-isolation-hardening`
Final impact type: `privilege-reduction, signing-boundary-hardening`
Final confidence: `medium`
Final tags: `validator-ops, remote-signing, shred-signing, keyguard, payload-authorization, seccomp, privilege-separation`

The supplied patch evidence does not prove a concrete pre-patch vulnerability, arbitrary signing primitive, key disclosure, or consensus exploit, so it should not be retained as a security-fix. However, the commit clearly adds a security-sensitive remote signing path for shreds, introduces role-based keyguard payload authorization, wires shred signing through explicit sign links, and adds a seccomp policy for the signing tile. That supports keeping it conservatively as security hardening.

## Security Evidence

1. Commit subject explicitly says security: add remote signing tile for shreds.
2. Shred tile topology is changed to require SIGN_TO_SHRED input and SHRED_TO_SIGN output links.
3. fd_keyguard_payload_authorize adds role-based authorization and maps leader signing to shred payload matching.
4. A dedicated sign.seccomppolicy is added for the signing tile, indicating syscall/file-descriptor restriction of a sensitive process.
5. The changes separate signing behavior into an explicit sign/keyguard path rather than leaving it implicit in the shred path.

## Missing Evidence

1. No evidence that the previous shred signing path accepted attacker-controlled signing requests.
2. No evidence of arbitrary payload signing before the patch.
3. No evidence of private key disclosure or direct key compromise.
4. No evidence of forged shreds, consensus failure, or network-wide exploitability.
5. No evidence that the old behavior was unintended rather than an architectural baseline.

## Claim Boundaries

1. Classify as security hardening, not a confirmed vulnerability fix.
2. Do not claim exploitable access control bypass from the supplied snippets alone.
3. Do not claim key compromise, arbitrary signing, forged shreds, or consensus impact.
4. The strongest supported claim is improved signing isolation and role-specific payload authorization for shred signing.
