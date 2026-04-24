# Validation Card

## Metadata

- ID: `sui-2023-03-03-sui-storage-816b0144bc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-invariant-hardening`

## What Confirmed The Issue

- Commit subject states hardening for checking SUI conservation after charging gas.
- TemporaryStore output SUI calculation changes from get_total_sui(&self.store) to get_total_sui(&self), allowing checks to see temporary written state.
- TemporaryStore gains GetModule behavior that consults self.written before falling back to backing storage.
- The changed code is in transaction execution/storage accounting paths for SUI conservation.

## What Could Have Invalidated It

- No demonstrated attacker-controlled exploit path is shown.
- No evidence proves SUI could actually be minted, burned, or corrupted before the patch.
- The exact execution_engine call site is not included in the supplied patch evidence.
- A related storage-cost assertion is commented out with a deferred guard, limiting claims of complete invariant enforcement.

## Severity Guidance

- Expected impact band: state-integrity
- Expected severity band: medium
- Rationale: The affected property protects authorization, accounting, or signature trust; likely hardening is kept below high unless exploitability is proven.

## False-Positive Cautions

- Classify as hardening of a ledger/accounting invariant, not a confirmed vulnerability fix.
- Do not claim consensus compromise, validator compromise, or exploitable state corruption.
- Do not claim complete dynamic-field conservation coverage from this evidence.
- Supporting trait implementations should be treated as plumbing for the invariant check, not independent security fixes.
