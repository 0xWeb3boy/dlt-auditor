---
id: monad-c4-2025-09-m-04
source: Code4rena 2025-09 Monad report
source_report: /testing/learning/2025-09-monad-report.md
report_date: 2026-02-26
audit_start_date: 2025-09-16
severity: medium
---

## [[M-04] Incorrect Write Position in Block Device Trim Operation](https://code4rena.com/audits/2025-09-monad/submissions/F-747)

*Submitted by [inh3l](https://code4rena.com/audits/2025-09-monad/submissions/S-876)*

`monad/category/async/storage_pool.cpp` [#L258-L320](https://github.com/code-423n4/2025-09-monad/blob/5eb99e1c365d61b34a637db6c0a9b476bbaed5ee/monad/category/async/storage_pool.cpp#L258-L320)

The `chunk::try_trim_contents()` method for block devices contains a critical bug in handling partial page preservation during trim operations. When a trim boundary falls within a disk page (i.e., `remainder > 0`), the code:

1. Reads the partial page from the original offset (`range[0]`)
2. Advances `range[0]` by `DISK_PAGE_SIZE` to skip the partial page in the trim operation
3. But then incorrectly writes the modified buffer back to the advanced `range[0]` instead of the original offset

### Current Buggy Implementation

```cpp
if (remainder > 0) {
    range[0] += DISK_PAGE_SIZE;  // Advance for trim
    range[1] -= DISK_PAGE_SIZE;
}
// ... trim operation happens ...
if (remainder > 0) {
    // @audit Writing to advanced range[0] instead of original position
    MONAD_ASSERT_PRINTF(
        -1 != ::pwrite(
                  write_fd_,
                  buffer,
                  DISK_PAGE_SIZE,
                  static_cast<off_t>(range[0])),  // Wrong offset!
        "failed due to %s",
        strerror(errno));
}
```

This writes the preserved data fragment to the next disk page, corrupting whatever data was stored there.

### Recommended mitigation steps

Store the original offset before modification and use it for the write operation.

---
