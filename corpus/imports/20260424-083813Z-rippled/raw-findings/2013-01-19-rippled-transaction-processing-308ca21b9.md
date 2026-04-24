---
case_id: case_20130119_308ca21b9
project: rippled
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2013-01-19
source_refs:
  - git:308ca21b977b6be5d548e91b11c41d9103c70527
  - "src/cpp/ripple/WalletAddTransactor.cpp:39"
  - "src/cpp/ripple/TransactionErr.cpp:20"
  - "src/cpp/ripple/PaymentTransactor.cpp:162"
  - "src/cpp/ripple/OfferCreateTransactor.cpp:341"
bug_class: reserve-enforcement-bypass
impact_type:
  - state-accounting
  - economic-policy-bypass
confidence: medium
tags:
  - transaction-processing
  - walletadd
  - reserve-enforcement
  - xrp-balance-check
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The grounded substantive fix is in WalletAdd: it changes an account-creation XRP send from a simple balance-versus-amount check to a reserve-aware funding check. The other shown changes mostly split generic tecUNFUNDED into path-specific result codes for WalletAdd, Payment, and OfferCreate.

## Observed Patch Facts

1. In `src/cpp/ripple/WalletAddTransactor.cpp`, the patch replaces `STAmount saAmount = mTxn.getFieldAmount(sfAmount);` with `// Direct XRP payment.`.

2. In `src/cpp/ripple/TransactionErr.cpp`, the patch replaces `{ tecUNFUNDED, "tecUNFUNDED", "Source account had insufficient balance for transactio...` with `{ tecUNFUNDED, "tecUNFUNDED", "One of _ADD, _OFFER, or _SEND. Deprecated." },`.

3. In `src/cpp/ripple/PaymentTransactor.cpp`, the patch replaces `terResult = tecUNFUNDED;` with `terResult = tecUNFUNDED_PAYMENT;`.

4. In `src/cpp/ripple/OfferCreateTransactor.cpp`, the patch replaces `terResult = tecUNFUNDED;` with `terResult = tecUNFUNDED_OFFER;`.

## Project Context

The changed code sits primarily in `src/cpp/ripple`, `src/cpp`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `src/cpp/ripple/TrustSetTransactor.cpp`, `src/cpp/ripple/Transactor.cpp` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/cpp/ripple/TrustSetTransactor.cpp`, `src/cpp/ripple/Transactor.cpp`. The strongest project-level identifiers around this patch are `tecUNFUNDED`, `STAmount`, `getFieldAmount`, and `balance`. Nearby tests or test-like files include `src/cpp/websocketpp/websocketpp.xcodeproj/xcuserdata/jcar.xcuserdatad/xcschemes/fuzzing_server.xcscheme`, `src/cpp/websocketpp/websocketpp.xcodeproj/xcuserdata/jcar.xcuserdatad/xcschemes/fuzzing_client.xcscheme`.

## Before/After Behavior

Before, WalletAdd rejected only when the source balance was less than the destination amount. After, it computes the source account's owner reserve and rejects when source balance plus the already paid fee is less than destination amount plus reserve. Payment and offer paths now return more specific unfunded result codes, and TransactionErr maps those codes.

# Root Cause

WalletAdd enforced an incomplete funding check: it considered whether the source could cover the XRP amount, but not whether the source would retain its required reserve after the send, apart from the allowed fee handling.

## Walkthrough

1. WalletAdd reaches its apply path after checking that the destination account does not already exist.

2. The old code loaded sfAmount and sfBalance and rejected only on saSrcBalance < saAmount.

3. That condition could allow the source account to fund the destination amount while falling below its required reserve.

4. The patched code loads the destination amount, source balance, source owner count, and ledger reserve.

5. It then accounts for the transaction fee already paid and checks saSrcBalance + saPaid against saDstAmount + uReserve.

6. Payment and offer paths receive more specific tecUNFUNDED_* result codes, which appear diagnostic/API-facing based on the provided evidence.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/cpp/ripple/WalletAddTransactor.cpp | 39 | Primary fix path; enforces source XRP balance plus paid fee against destination amount plus required reserve for WalletAdd/account-creation payment. |
| src/cpp/ripple/PaymentTransactor.cpp | 162 | Existing direct XRP payment funding failure now returns the more specific tecUNFUNDED_PAYMENT result. |
| src/cpp/ripple/OfferCreateTransactor.cpp | 341 | Offer funding failure now returns the more specific tecUNFUNDED_OFFER result. |
| src/cpp/ripple/TransactionErr.cpp | 20 | Transaction result mapping adds specific unfunded error tokens and deprecates the generic tecUNFUNDED meaning. |

## Code Snippets

## Snippet 1

Context: `src/cpp/ripple/WalletAddTransactor.cpp:39` (updates aggregate accounting or lifecycle state)

Before
```cpp
}

	STAmount			saAmount		= mTxn.getFieldAmount(sfAmount);
	STAmount			saSrcBalance	= mTxnAccount->getFieldAmount(sfBalance);

	if (saSrcBalance < saAmount)
	{
		std::cerr
```
After
```cpp
}

	// Direct XRP payment.

	STAmount		saDstAmount		= mTxn.getFieldAmount(sfAmount);
	const STAmount	saSrcBalance	= mTxnAccount->getFieldAmount(sfBalance);
	const uint32	uOwnerCount		= mTxnAccount->getFieldU32(sfOwnerCount);
	const uint64	uReserve		= mEngine->getLedger()->getReserve(uOwnerCount);
```

## Snippet 2

Context: `src/cpp/ripple/TransactionErr.cpp:20` (updates aggregate accounting or lifecycle state)

Before
```cpp
{	tecPATH_PARTIAL,		"tecPATH_PARTIAL",			"Path could not send full amount."						},

		{	tecUNFUNDED,			"tecUNFUNDED",				"Source account had insufficient balance for transaction."	},

		{	tefFAILURE,				"tefFAILURE",				"Failed to apply."										},
```
After
```cpp
{	tecPATH_PARTIAL,		"tecPATH_PARTIAL",			"Path could not send full amount."						},

		{	tecUNFUNDED,			"tecUNFUNDED",				"One of _ADD, _OFFER, or _SEND. Deprecated."			},
		{	tecUNFUNDED_ADD,		"tecUNFUNDED_ADD",			"Insufficient XRP balance for WalletAdd."				},
		{	tecUNFUNDED_OFFER,		"tecUNFUNDED_OFFER",		"Insufficient balance to fund created offer."			},
		{	tecUNFUNDED_PAYMENT,	"tecUNFUNDED_PAYMENT",		"Insufficient XRP balance to send."						},

		{	tefFAILURE,				"tefFAILURE",				"Failed to apply."										},
```

## Snippet 3

Context: `src/cpp/ripple/PaymentTransactor.cpp:162` (updates aggregate accounting or lifecycle state)

Before
```cpp
% saSrcXRPBalance.getText() % (saDstAmount + uReserve).getText() % uReserve);

			terResult	= tecUNFUNDED;
		}
		else
```
After
```cpp
% saSrcXRPBalance.getText() % (saDstAmount + uReserve).getText() % uReserve);

			terResult	= tecUNFUNDED_PAYMENT;
		}
		else
```

## Snippet 4

Context: `src/cpp/ripple/OfferCreateTransactor.cpp:341` (updates aggregate accounting or lifecycle state)

Before
```cpp
cLog(lsWARNING) << "OfferCreate: delay: Offers must be at least partially funded.";

		terResult	= tecUNFUNDED;
	}
```
After
```cpp
cLog(lsWARNING) << "OfferCreate: delay: Offers must be at least partially funded.";

		terResult	= tecUNFUNDED_OFFER;
	}
```

# Fix Pattern

Replace a local amount-only funding check with a reserve-aware transaction validity check, and return path-specific unfunded errors for clearer failure attribution.

## How It Was Fixed

WalletAdd now derives the source account reserve from sfOwnerCount via getReserve and rejects insufficiently funded sends with tecUNFUNDED_ADD when the balance, amount, fee, and reserve relationship fails. Payment and OfferCreate now return tecUNFUNDED_PAYMENT and tecUNFUNDED_OFFER, and TransactionErr documents those codes.

# Why It Matters

1. Prevents WalletAdd from bypassing the reserve-aware funding invariant shown in the payment path.

2. Keeps account reserve enforcement consistent across native XRP send paths.

3. Specific error codes improve diagnosis but are not themselves the vulnerability fix.

4. The evidence does not establish theft, double spend, value creation, memory corruption, or consensus divergence.

# Evidence Notes

The reserve issue is directly supported by the WalletAdd diff: a simple saSrcBalance < saAmount check is replaced with saSrcBalance + saPaid < saDstAmount + uReserve using sfOwnerCount and getReserve. The PaymentTransactor excerpt shows the same reserve-aware condition for direct XRP payments, supporting the consistency argument. The OfferCreate, Payment, and TransactionErr changes support only error-code specialization, not an additional root cause. Protocol security invariant: Native XRP transaction paths should not permit a source account to spend below its required owner reserve, except for the explicitly allowed fee treatment. Verification notes: The patch does not prove theft, double spend, or value creation. The patch does not prove a remotely exploitable crash or memory safety issue. The evidence does not show consensus divergence across nodes. The tecUNFUNDED specialization appears diagnostic/API-facing unless consumers depend on exact result codes. Exploitability depends on whether WalletAdd transactions were accepted on live ledgers and how reserve violations affected later processing. No external exploit scenario is shown in the provided evidence. Tests are listed but their contents are not provided, so regression coverage cannot be evaluated. Confidence remains medium because the code supports a reserve-bypass fix, but operational impact is not fully established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `reserve-enforcement-bypass`
Final impact type: `state-accounting, economic-policy-bypass`
Final confidence: `medium`
Final tags: `transaction-processing, walletadd, reserve-enforcement, xrp-balance-check, security-hardening`

The patch evidence supports a security-hardening classification rather than a confirmed security-fix. WalletAdd changed from an amount-only source balance check to a reserve-aware check using owner count, ledger reserve, destination amount, and already-paid fee. In a ledger/payment system this clearly tightens a security-sensitive accounting invariant, but the provided evidence does not prove concrete exploitability, consensus failure, theft, value creation, or other specific security impact. The error-code changes are mostly diagnostic/API cleanup and should not carry the security claim.

## Security Evidence

1. WalletAdd previously rejected only when source balance was below the sent amount.
2. WalletAdd now also accounts for the source account reserve derived from owner count and ledger reserve.
3. The new condition prevents a WalletAdd send from leaving the source below required reserve, except for the explicit fee handling.
4. The same reserve-aware pattern appears in the PaymentTransactor context, supporting that reserve preservation is an intended transaction invariant.

## Missing Evidence

1. No exploit scenario or attacker-controlled sequence is shown.
2. No evidence shows theft, double spend, value creation, or consensus divergence.
3. No test contents are provided, so regression behavior cannot be independently confirmed.
4. The patch does not show whether WalletAdd was exposed or accepted on production ledgers in a way that made the bypass practically exploitable.

## Claim Boundaries

1. Treat the WalletAdd reserve check as the security-relevant change.
2. Do not treat the tecUNFUNDED_* result-code split as a vulnerability fix by itself.
3. Do not claim memory safety, remote code execution, denial of service, theft, double spend, or consensus divergence from this evidence.
4. Classify as reserve/accounting invariant hardening, not a fully demonstrated exploitable security bug.
