---
id: monad-c4-2025-09-m-05
source: Code4rena 2025-09 Monad report
source_report: /testing/learning/2025-09-monad-report.md
report_date: 2026-02-26
audit_start_date: 2025-09-16
severity: medium
---

## [[M-05] Typed receipt encoding does not conform to standard Ethereum RPC format](https://code4rena.com/audits/2025-09-monad/submissions/F-776)

*Submitted by [Evo](https://code4rena.com/audits/2025-09-monad/submissions/S-421)*

`bft/monad-rpc/src/handlers/debug.rs` [#L126](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-rpc/src/handlers/debug.rs#L126)

### Root Cause

The `debug_getRawReceipts` RPC method in `bft/monad-rpc/src/handlers/debug.rs` violates the EIP-2718 specification by using incorrect encoding for typed transaction receipts. The method uses plain RLP encoding (`r.encode()`) instead of EIP-2718 encoding (`r.encode_2718()`), resulting in receipts that are missing their required transaction type prefix byte.

### Technical Details

**Current Implementation:**

[https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-rpc/src/handlers/debug.rs#L126](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-rpc/src/handlers/debug.rs#L126)

```rust
// In bft/monad-rpc/src/handlers/debug.rs, monad_debug_getRawReceipts function
let encode_receipts = |receipts: Vec<ReceiptEnvelope<alloy_primitives::Log>>| {
    let receipts = receipts
        .into_iter()
        .map(|r| {
            let mut res = Vec::new();
            r.encode(&mut res);  // ← ISSUE: Using plain RLP encoding
            hex::encode(&res)
        })
        .collect();
    Ok(MonadDebugGetRawReceiptsResult { receipts })
};
```

**Correct Implementation (as seen in `debug_getRawTransaction` in the same file L156):**

[https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-rpc/src/handlers/debug.rs#L156](https://github.com/code-423n4/2025-09-monad/blob/main/bft/monad-rpc/src/handlers/debug.rs#L156)

```rust
let mut res = Vec::new();
let tx: TxEnvelope = tx.into();
tx.encode_2718(&mut res);  // ← CORRECT: Using EIP-2718 encoding
```

**The EIP-2718 Violation**

According to the EIP-2718 specification:

> “Receipt is either TransactionType || ReceiptPayload or LegacyReceipt”

And critically:

> “The TransactionType of the receipt MUST match the TransactionType of the transaction with a matching Index.”

The specification defines that for typed transactions:

- `TransactionType` is a positive unsigned 8-bit number between 0 and 0x7f
- `ReceiptPayload` is an opaque byte array whose interpretation depends on the TransactionType
- The format MUST be: `TransactionType || ReceiptPayload` where `||` is the concatenation operator

**Example of the violation for an EIP-1559 transaction:**

| Component | Expected (EIP-2718 compliant) | Actual (Current Implementation) |
| --- | --- | --- |
| Transaction | `0x02 \\|\\| TransactionPayload` | `0x02 \\|\\| TransactionPayload` ✓ |
| Receipt | `0x02 \\|\\| ReceiptPayload` | `RLP([status, gas, bloom, logs])` ✗ |

The receipt is missing the critical `0x02` TransactionType byte prefix, violating the MUST requirement that “The TransactionType of the receipt MUST match the TransactionType of the transaction.”

**Dependency Context**

The project uses the `alloy-consensus` crate (v0.8.3) which provides the `ReceiptEnvelope` type. This type **correctly implements** the `Encodable2718` trait in `alloy-consensus-0.8.3/src/receipt/envelope.rs`:

```rust
// From alloy-consensus-0.8.3/src/receipt/envelope.rs
impl Encodable2718 for ReceiptEnvelope {
    fn encode_2718(&self, out: &mut dyn BufMut) {
        match self.type_flag() {
            None => {}                    // Legacy receipts - no prefix
            Some(ty) => out.put_u8(ty),  // Typed receipts - adds type byte
        }
        self.as_receipt_with_bloom().unwrap().encode(out);
    }
}
```

The `encode_2718()` method automatically handles all receipt types:

- Legacy (no prefix, remains as `rlp([status, cumulativeGasUsed, logsBloom, logs])`)
- EIP-2930 (0x01 prefix)
- EIP-1559 (0x02 prefix)
- EIP-4844 (0x03 prefix)
- EIP-7702 (0x04 prefix)

### Impact

- Malformed receipts could cause incorrect state verification or proof generation in systems relying on proper receipt encoding, and the tools and clients expecting EIP-2718 compliant receipts will fail to parse them correctly.
- Violates EIP-2718’s MUST requirements - the spec requires matching TransactionType between transactions and receipts, and the method documentation falsely claims to return “EIP-2718 binary-encoded receipts”, as external clients cannot differentiate receipt types as the first byte should be in range [0, 0x7f] for typed transactions but instead contains RLP data.

### Recommended mitigation steps

Replace the plain RLP encoding with EIP-2718 encoding in the `debug_getRawReceipts` function:

```rust
// In bft/monad-rpc/src/handlers/debug.rs, line ~49
let encode_receipts = |receipts: Vec<ReceiptEnvelope<alloy_primitives::Log>>| {
    let receipts = receipts
        .into_iter()
        .map(|r| {
            let mut res = Vec::new();
            r.encode_2718(&mut res);  // ← FIX: Use encode_2718 instead of encode
            hex::encode(&res)
        })
        .collect();
    Ok(MonadDebugGetRawReceiptsResult { receipts })
};
```

---
