---
case_id: case_20240612_8b8649322
project: firedancer
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: access-control
source_quality: high
date: 2024-06-12
source_refs:
  - git:8b864932211b894ff713ac41926684d95c0ab7ee
  - "src/disco/keyguard/fd_keyload.h:42"
  - "src/util/sandbox/test_sandbox.c:1"
  - "src/disco/keyguard/fd_keyload.c:105"
  - "src/app/fdctl/run/run.c:397"
bug_class: secret-memory-hardening
impact_type:
  - secret-exposure-reduction
  - sandbox-hardening
confidence: medium
tags:
  - key-management
  - memory-protection
  - sandbox
  - defense-in-depth
  - landlock
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to harden Firedancer's sandbox/keyguard area by adding a protected-page allocation API for key material and by warning when the optional Landlock sandbox layer is unavailable. The evidence supports security-relevant defense-in-depth work, but not a confirmed or likely vulnerability fix: no prior exploit path, remote input path, concrete key exposure, sandbox bypass, resource-exhaustion condition, or consensus impact is shown.

## Observed Patch Facts

1. In `src/disco/keyguard/fd_keyload.h`, the patch replaces `#endif /* HEADER_fd_src_disco_keyguard_fd_keyload_h */` with `/* fd_keyload_alloc_protected_pages allocates 'page_cnt' regular (4 kB)`.

2. In `src/util/sandbox/test_sandbox.c`, the patch removes `#if !defined(__linux__)`.

3. In `src/disco/keyguard/fd_keyload.c`, the patch adds `void * FD_FN_SENSITIVE`.

4. In `src/app/fdctl/run/run.c`, the patch replaces `if( FD_UNLIKELY( close( 0 ) ) ) FD_LOG_ERR(( "close(0) failed (%i-%s)", errno, fd_io_...` with `#if defined(__x86_64__)`.

## Project Context

The changed code sits primarily in `src/disco/keyguard`, `src/disco`, `src/util/sandbox`, which anchors the finding in the `access-control` area of the project. Historical context from `src/util/sandbox/fd_sandbox.c`, `src/disco/keyguard/test_keyload.c` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/util/wksp/fd_wksp_ctl.c`, `src/util/shmem/fd_shmem_admin.c`. The strongest project-level identifiers around this patch are `errno`, `pages`, `page_cnt`, and `include`. Nearby tests or test-like files include `src/util/sanitize/fd_fuzz_stub.c`, `src/util/net/fuzz_pcap.c`.

## Before/After Behavior

Before the patch, the provided evidence does not show a documented reusable protected-page allocation API for keyguard memory, and the visible startup path proceeded from topology logging to file descriptor handling. After the patch, `fd_keyload_alloc_protected_pages` is documented and implemented to allocate usable pages surrounded by guard pages, with documented OS-level protections against swap, core dumps, and fork inheritance. The startup path also probes Landlock support and logs a warning if the kernel lacks it, describing Landlock as an additional sandbox layer that is not required.

# Root Cause

No proven vulnerability root cause is established. The grounded interpretation is that prior code lacked the newly documented protected-memory helper and Landlock availability warning shown in the patch evidence. The evidence does not prove that key material was previously exposed, that missing Landlock allowed a bypass, or that an attacker could trigger unsafe behavior.

## Walkthrough

1. The keyguard header now documents `fd_keyload_alloc_protected_pages` as allocating usable 4 kB pages with unreadable and unwritable guard pages on both sides.

2. The documented contract says the usable pages are configured to avoid swap, core-dump inclusion, and fork inheritance.

3. The keyguard implementation adds `fd_keyload_alloc_protected_pages`, allocates the combined guard-plus-usable region with `mmap`, computes the usable middle region, and begins applying `mprotect` to guard pages.

4. The Firedancer startup path now checks Landlock ABI support with `SYS_landlock_create_ruleset`.

5. If Landlock is unsupported, the runtime logs a warning that Landlock is an additional sandbox layer and is not required.

6. The sandbox test changes indicate supporting test reorganization, but the provided snippets do not show a specific prior failing security case.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/disco/keyguard/fd_keyload.c | 105 | implements protected memory allocation for sensitive key material using mmap-backed pages and guard-page protections |
| src/disco/keyguard/fd_keyload.h | 42 | declares and documents the protected-pages keyload memory contract, including no swap, no core dump, and fork wiping behavior |
| src/app/fdctl/run/run.c | 397 | runtime firedancer startup path checks Landlock availability as part of sandbox hardening |
| src/util/sandbox/test_sandbox.c | 1 | sandbox test coverage adjusted around Linux/seccomp sandbox behavior |

## Code Snippets

## Snippet 1

Context: `src/disco/keyguard/fd_keyload.h:42` (changes a consensus- or validator-sensitive branch)

Before
```c
int           public_key_only );

#endif /* HEADER_fd_src_disco_keyguard_fd_keyload_h */
```
After
```c
int           public_key_only );

/* fd_keyload_alloc_protected_pages allocates `page_cnt` regular (4 kB)
   pages of memory protected by `guard_page_cnt` pages of unreadable and
   unwritable memory on each side.  Additionally the OS is configured so
   that the page_cnt pages in the middle will not be paged out to disk
   in a swap file, appear in core dumps, and will be wiped on fork so it
   is not readable by any child process forked off from this process.
```

## Snippet 2

Context: `src/util/sandbox/test_sandbox.c:1` (changes an authorization or privilege gate)

Before
```c
#if !defined(__linux__)
# error "Target operating system is unsupported by seccomp."
#endif

#if !FD_HAS_ASAN

#define _GNU_SOURCE
```
After
```c
#define _GNU_SOURCE
#include "fd_sandbox.h"
#include "fd_sandbox_private.h"

#include "../fd_util.h"
#include "generated/test_sandbox_seccomp.h"

#include <sys/file.h>
```

## Snippet 3

Context: `src/disco/keyguard/fd_keyload.c:105` (changes a consensus- or validator-sensitive branch)

Before
```c
FD_LOG_ERR(( "munmap failed (%i-%s)", errno, fd_io_strerror( errno ) ));
}
```
After
```c
FD_LOG_ERR(( "munmap failed (%i-%s)", errno, fd_io_strerror( errno ) ));
}

void * FD_FN_SENSITIVE
fd_keyload_alloc_protected_pages( ulong page_cnt,
                                  ulong guard_page_cnt ) {
#define PAGE_SZ (4096UL)
  void * pages = mmap( NULL, (2UL*guard_page_cnt+page_cnt)*PAGE_SZ, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0UL );
```

## Snippet 4

Context: `src/app/fdctl/run/run.c:397` (changes a sensitive control or state-update path)

Before
```c
fd_topo_print_log( 0, &config->topo );

  if( FD_UNLIKELY( close( 0 ) ) ) FD_LOG_ERR(( "close(0) failed (%i-%s)", errno, fd_io_strerror( errno ) ));
  if( FD_UNLIKELY( fd_log_private_logfile_fd()!=1 && close( 1 ) ) ) FD_LOG_ERR(( "close(1) failed (%i-%s)", errno, fd_io_strerror( errno ) ));
```
After
```c
fd_topo_print_log( 0, &config->topo );

#if defined(__x86_64__)
#define SYS_landlock_create_ruleset 444
#define LANDLOCK_CREATE_RULESET_VERSION (1U << 0)
#endif
  long abi = syscall( SYS_landlock_create_ruleset, NULL, 0, LANDLOCK_CREATE_RULESET_VERSION );
  if( -1L==abi && (errno==ENOSYS || errno==EOPNOTSUPP ) ) {
```

# Fix Pattern

Add defense-in-depth memory-protection and sandbox-awareness mechanisms without changing the evidence into a proven vulnerability claim.

## How It Was Fixed

The patch added and documented a keyguard protected-page allocator using `mmap` and guard-page protection, and added a runtime Landlock support probe with a warning when unavailable. Test and helper changes appear to support the sandbox/keyguard hardening work.

# Why It Matters

1. Private key memory receives stronger documented process-memory confinement.

2. Guard pages can turn adjacent out-of-bounds access into a fault.

3. No-swap and no-core-dump protections reduce accidental secret disclosure through OS artifacts.

4. Fork wiping limits key exposure to child processes.

5. Landlock probing improves operator visibility into an optional sandbox layer.

6. The evidence supports hardening, not a demonstrated exploitable bug.

# Evidence Notes

Primary evidence is limited to snippets from `src/disco/keyguard/fd_keyload.h`, `src/disco/keyguard/fd_keyload.c`, `src/app/fdctl/run/run.c`, and `src/util/sandbox/test_sandbox.c`. The header documents the intended protected-memory contract, and the implementation snippet shows allocation plus guard-page setup beginning. The Landlock hunk only shows detection and warning for an optional layer. Claims about resource exhaustion, consensus impact, direct sandbox bypass, remote exploitability, or actual prior key disclosure are unsupported by the provided evidence. Protocol security invariant: Validator runtime sandboxing should reduce process privilege and filesystem/syscall exposure, and private key material should be held in memory with protections against accidental disclosure through adjacent memory access, swap, core dumps, and fork inheritance. The evidence shows this invariant being strengthened, but does not establish a specific prior vulnerability or attacker-controlled exploit path. Verification notes: No concrete prior exploit path is proven by the provided patch evidence. No remote attacker input path is shown. No consensus safety violation is demonstrated. No resource-exhaustion bug is supported by the visible hunks. Landlock is described as an additional layer and not required, so lack of Landlock is not shown to be a direct vulnerability. The evidence supports hardening of private-key memory handling, not proof that keys were previously exposed in practice. Downgraded from likely security fix to unclear security verdict because no vulnerability thesis is established. Kept classification as security-hardening because the code and commit subject support defense-in-depth intent. Set `keep_in_security_corpus` to false under the instruction for security-relevant patches without an established vulnerability thesis. Removed unsupported resource-exhaustion and consensus claims. Treated test and helper changes as support code, not root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `secret-memory-hardening`
Final impact type: `secret-exposure-reduction, sandbox-hardening`
Final confidence: `medium`
Final tags: `key-management, memory-protection, sandbox, defense-in-depth, landlock`

The supplied patch evidence supports retaining this as security hardening, not as a concrete vulnerability fix. The keyguard changes add protected allocation for sensitive key material with guard pages and OS protections against swap, core dumps, and fork inheritance, and the runtime adds visibility for unavailable Landlock sandbox support. The original resource-exhaustion and remote-DoS framing is unsupported by the shown code.

## Security Evidence

1. Commit subject explicitly says sandbox hardening.
2. Keyload API documentation describes unreadable and unwritable guard pages around sensitive memory.
3. Keyload contract says protected pages are not swapped, excluded from core dumps, and wiped on fork.
4. Implementation adds fd_keyload_alloc_protected_pages using mmap and begins applying mprotect guard-page protections.
5. Runtime probes Landlock support and warns when the optional sandbox access-control layer is unavailable.

## Missing Evidence

1. No concrete prior vulnerability or exploit path is shown.
2. No attacker-controlled input path is connected to the changed code.
3. No evidence supports remote denial of service or resource exhaustion.
4. No evidence shows prior key disclosure in practice.
5. No evidence shows missing Landlock caused a sandbox bypass.

## Claim Boundaries

1. Classify as defense-in-depth hardening for key memory and sandbox visibility.
2. Do not claim a proven security bug or exploitable vulnerability.
3. Do not retain resource-exhaustion, remote-DoS, queue, or consensus-impact claims.
4. Landlock evidence shows warning and operator visibility, not enforcement of a newly required sandbox layer.
