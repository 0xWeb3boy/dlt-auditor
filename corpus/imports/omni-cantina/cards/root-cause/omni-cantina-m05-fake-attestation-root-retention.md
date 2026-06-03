# Root-Cause Card

Record: `omni-cantina-m05-fake-attestation-root-retention`
Project: `omni-network`
Source finding: `Omni Cantina M-5`
Bug family: `attestation_trust_and_freshness`

## Core Failure

Attestation root admission and retention are not bounded tightly enough per validator or per consensus lifecycle cost.

## Why It Matters

Consensus modules without gas must bound attacker-created state that future EndBlock logic scans.

## Reusable Heuristic

Look for vote-extension or consensus-module inputs that create pending rows faster or longer than lifecycle cleanup can safely process.

## Patch Direction

Tighten root admission, lower/parameterize consensus trim lag, cap pending roots per validator/offset, and make lifecycle scans bounded or indexed by actionable work.
