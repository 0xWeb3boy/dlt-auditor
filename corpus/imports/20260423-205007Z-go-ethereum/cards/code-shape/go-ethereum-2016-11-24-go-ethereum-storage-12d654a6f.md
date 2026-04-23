# Code-Shape Card

## Metadata

- ID: `go-ethereum-2016-11-24-go-ethereum-storage-12d654a6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-revert-bug`

## Code Shape Summary

- Touching an account was consensus-relevant under the shown EIP158 empty-account clearing path, but the pre-fix behavior did not represent that touch as an independently journaled and revertible state transition. Snapshot/Revert could therefore leave account existence or dirty-state inconsistent with the intended state transition behavior.

## Search Motifs

- Motif 1: p2p message missing exact checks for consensus state revert bug
- Motif 2: security-sensitive path reaches consensus-visible state transition or journal replay before rejecting malformed or unauthorized input
- Motif 3: Model implicit consensus-relevant state as an explicit journal entry, mutate it through one helper, and implement undo logic so snapshot rollback restores account tracking consistently

## Typical Asymmetry

- A remote peer or spoofed sender can trigger more local work, state change, or outbound traffic than the cost of the crafted message.

## Patch Pattern

- Model implicit consensus-relevant state as an explicit journal entry, mutate it through one helper, and implement undo logic so snapshot rollback restores account tracking consistently.

## False Match Warnings

- Valid claim: consensus-relevant state handling for touched empty accounts was corrected or made client-compatible.
- Valid claim: Snapshot/Revert behavior for touch state became explicitly journaled and reversible.
