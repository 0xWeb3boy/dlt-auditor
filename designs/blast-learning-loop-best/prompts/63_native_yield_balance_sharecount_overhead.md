# Prompt Family: Native Yield Balance Share-Count Overhead

## Use This For

- The native-yield half of broad resource-accounting issues.
- Balance, flags, share-count, claimable amount, and StateDB journaling paths that are not the gas-refund `AllocateDevGas` finalizer.

## Prompt

```text
Hunt specifically for Blast native-yield balance/share-count bookkeeping that is not directly metered by ordinary EVM opcode gas.

Keep this separate from:
- native precompile `RequiredGas`;
- invalid native precompile revert gas;
- high-frame custom CALL/CREATE surcharge;
- gas-refund/claimable-gas `AllocateDevGas` finalizer loops.

Build a native-yield budget table with one row per operation:
- `Balance`
- `GetBalance`
- `SetBalance`
- `AddBalance`
- `SubBalance`
- `SetFlags`
- `GetClaimableAmount`
- `SubClaimableAmount`
- `GetShares`
- `SetShares`
- `adjustShareCount`
- direct predeploy storage reads/writes
- StateDB journal entries
- automatic-yield value transfer
- claimable-yield claim
- gas buy/refund balance mutation
- selfdestruct beneficiary transfer
- contract creation with constructor value

For each row, record:
- attacker-controlled dimension: recipient count, value fanout, automatic-account set, repeated balance mutations, or claim targets;
- native work: storage read, storage write, big.Int arithmetic, share-price read, journal entry, account trie mutation, predeploy slot update;
- ordinary gas charged at the EVM opcode level;
- any Blast-specific extra gas charged;
- whether the work occurs inside EVM execution or after/beside it in StateDB/native code;
- whether refunds/rebates reduce effective paid gas;
- whether a victim/sponsor can pay for the transaction while attacker chooses targets.

Required exact checks:
1. Newly created empty accounts default to automatic yield unless explicitly disabled.
2. Automatic-yield balance changes convert fixed value to shares and can update global share-count storage.
3. Native balance mutations from transfers, gas buy/refund, withdrawals, precompile claims, and selfdestruct are not all equivalent to user-visible SSTOREs.
4. `SubClaimableAmount` / claim paths must account for flags, fixed, shares, remainder, share price, and journal rollback overhead.
5. A broad finding can be valid even if individual paths are bounded by ordinary CALL/new-account/value-transfer gas.

Reporting discipline:
- Promote a separate native-yield overhead candidate when source proves attacker-shaped native bookkeeping beyond `AllocateDevGas`.
- It may be Low/Medium or hardening, but do not let it vanish during canonicalization.
- The candidate should explicitly say whether it completes the broad native-yield/gas-refund overhead class together with the `AllocateDevGas` candidate.
```
