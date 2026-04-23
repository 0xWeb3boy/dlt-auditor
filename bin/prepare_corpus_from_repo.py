#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/testing/dlt-ai-audit-system")
DEFAULT_OUTPUT_ROOT = ROOT / "corpus" / "imports"


@dataclass
class Finding:
    source_path: Path
    slug: str
    title: str
    project: str
    date: str
    subsystem: str
    bug_class: str
    security_verdict: str
    validated_as: str
    summary: str
    bug_family: str
    confidence_tier: str
    missing_property: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare structured corpus artifacts from a repo's validated-findings/kept folder."
    )
    parser.add_argument("repo", help="Path to the target repository.")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Directory where the prepared import bundle should be created.",
    )
    parser.add_argument(
        "--no-copy-raw",
        action="store_true",
        help="Do not copy the raw finding markdown files into the import bundle.",
    )
    return parser.parse_args()


def parse_frontmatter_and_summary(text: str) -> tuple[dict[str, str], str]:
    fields: dict[str, str] = {}
    summary = ""

    if text.startswith("---\n"):
        parts = text.split("\n---\n", 1)
        if len(parts) == 2:
            frontmatter, body = parts
            for line in frontmatter.splitlines()[1:]:
                if not line or line.startswith("  - ") or ":" not in line:
                    continue
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip().strip('"')

            body_lines = body.splitlines()
            in_summary = False
            collected: list[str] = []
            for line in body_lines:
                if line.strip() == "# Summary":
                    in_summary = True
                    continue
                if in_summary:
                    if line.startswith("#"):
                        break
                    if line.strip():
                        collected.append(line.strip())
                        if len(collected) >= 2:
                            break
            summary = " ".join(collected).strip()

    return fields, summary


def infer_bug_family(bug_class: str) -> str:
    bc = bug_class.lower()
    if any(
        token in bc
        for token in [
            "authentication",
            "authorization",
            "access-control",
            "role",
            "update-validation",
            "validation-bypass",
        ]
    ):
        return "authz_and_role_gates"
    if any(
        token in bc
        for token in [
            "signature",
            "signer",
            "query-verification",
            "state-verification",
            "domain-separation",
            "signed-message",
        ]
    ):
        return "signature_binding_and_signer_scope"
    if any(
        token in bc
        for token in [
            "trust",
            "freshness",
            "quote",
            "peer-identity",
            "credential-acceptance",
            "key-scope",
        ]
    ):
        return "attestation_trust_and_freshness"
    if any(
        token in bc
        for token in [
            "input-validation",
            "identity-validation",
            "panic-on-malformed-input",
            "unsafe-debug",
            "untrusted-secret",
            "predictable-beacon-entropy",
            "insufficient-validation",
        ]
    ):
        return "input_validation_and_invariant_enforcement"
    if any(
        token in bc
        for token in [
            "gas",
            "resource-limit",
            "resource-limits",
            "validator-set-minimum-check",
        ]
    ):
        return "resource_accounting_and_limits"
    if any(
        token in bc
        for token in [
            "stale",
            "protocol-state-confusion",
            "state-integrity-hardening",
            "consensus-role-accounting",
            "role-scoped-enforcement",
        ]
    ):
        return "state_machine_and_lifecycle_consistency"
    if any(
        token in bc
        for token in [
            "slash",
            "stake",
            "voting-power",
            "validator-selection",
            "reserved-address",
            "proposer-liveness",
        ]
    ):
        return "staking_registry_and_accountability"
    if "overflow" in bc or "underflow" in bc or "arithmetic" in bc:
        return "checked_arithmetic_and_parameter_bounds"
    return "input_validation_and_invariant_enforcement"


def infer_confidence_tier(security_verdict: str, validated_as: str) -> str:
    verdict = security_verdict.lower()
    validated = validated_as.lower()
    if verdict == "confirmed":
        return "tier_a_confirmed"
    if verdict == "likely" and validated in {"security-fix", "security-hardening"}:
        return "tier_b_likely"
    return "tier_c_provenance_only"


def infer_missing_property(bug_class: str, family: str) -> str:
    bc = bug_class.lower()
    explicit_map = {
        "missing-authentication": "authentication",
        "improper-authorization-check": "authorization",
        "access-control": "authorization",
        "missing-signer-authorization": "signer-authorization",
        "missing-signer-authorization-check": "signer-authorization",
        "insufficient-signature-domain-separation": "domain-separation",
        "insufficient-signature-verification": "signer-authorization",
        "missing-query-verification": "query-verification",
        "state-verification-gap": "query-verification",
        "freshness-verification": "freshness",
        "trust-root-verification": "freshness",
        "quote-policy-synchronization": "policy-gating",
        "non-production-credential-acceptance": "policy-gating",
        "missing-gas-accounting": "resource-accounting",
        "insufficient-resource-limits": "resource-accounting",
        "improper-resource-limit-enforcement": "resource-accounting",
        "stale-timeout-state": "lifecycle-cleanup",
        "stale-session-state": "lifecycle-cleanup",
        "protocol-state-confusion": "state-coordinate-consistency",
        "integer-overflow": "arithmetic-bounds",
    }
    if bug_class in explicit_map:
        return explicit_map[bug_class]

    family_defaults = {
        "authz_and_role_gates": "authorization",
        "signature_binding_and_signer_scope": "signer-authorization",
        "attestation_trust_and_freshness": "freshness",
        "input_validation_and_invariant_enforcement": "input-validation",
        "resource_accounting_and_limits": "resource-accounting",
        "state_machine_and_lifecycle_consistency": "lifecycle-cleanup",
        "staking_registry_and_accountability": "accountability-enforcement",
        "checked_arithmetic_and_parameter_bounds": "arithmetic-bounds",
    }
    return family_defaults[family]


def slugify_repo_name(path: Path) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", path.name).strip("-").lower()


def build_finding(path: Path) -> Finding:
    text = path.read_text()
    fields, summary = parse_frontmatter_and_summary(text)

    project = fields.get("project", path.parent.parent.name)
    date = fields.get("date", "")
    subsystem = fields.get("subsystem", "unknown")
    bug_class = fields.get("bug_class", "unknown")
    security_verdict = fields.get("security_verdict", "unclear")
    validated_as = fields.get("validated_as", "unclear")
    title = path.stem
    bug_family = infer_bug_family(bug_class)
    confidence_tier = infer_confidence_tier(security_verdict, validated_as)
    missing_property = infer_missing_property(bug_class, bug_family)

    return Finding(
        source_path=path,
        slug=path.stem,
        title=title,
        project=project,
        date=date,
        subsystem=subsystem,
        bug_class=bug_class,
        security_verdict=security_verdict,
        validated_as=validated_as,
        summary=summary,
        bug_family=bug_family,
        confidence_tier=confidence_tier,
        missing_property=missing_property,
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")


def create_record(repo_slug: str, finding: Finding) -> str:
    record_id = f"{repo_slug}-{finding.slug}"
    uses = {
        "tier_a_confirmed": ["retrieval_exemplar", "eval_positive", "taxonomy_refinement"],
        "tier_b_likely": ["retrieval_exemplar", "taxonomy_refinement"],
        "tier_c_provenance_only": ["provenance_only"],
    }[finding.confidence_tier]

    return f"""id: "{record_id}"
source_finding: "{finding.source_path.name}"
project: "{finding.project}"
date: "{finding.date}"
language_tags: []

bug_family: "{finding.bug_family}"
bug_class: "{finding.bug_class}"
subsystem: "{finding.subsystem}"
architecture_tags: []

confidence_tier: "{finding.confidence_tier}"
security_verdict: "{finding.security_verdict}"
validated_as: "{finding.validated_as}"
recommended_uses: {json.dumps(uses)}

missing_property: "{finding.missing_property}"
violated_invariant: "TODO: rewrite from the finding in plain, generic terms."
trust_boundary: "TODO: identify the trust boundary crossed."
entrypoint_type: "TODO: classify the entrypoint."
sensitive_sink: "TODO: name the privileged action or state reached."

attacker_capabilities: []
exploit_preconditions: []
blast_radius: ""

impact_types: []
severity_guess: ""
severity_rationale: "TODO: justify the expected severity band."

code_shape_summary: "{escape_yaml_scalar(finding.summary) if finding.summary else 'TODO: summarize the code shape.'}"
search_motifs: []
negative_signals: []
patch_pattern: "TODO: summarize the structural fix pattern."

source_refs: ["{finding.source_path}"]
notes:
  - "Prepared automatically from a raw finding. Needs enrichment."
"""


def escape_yaml_scalar(text: str) -> str:
    return text.replace('"', "'")


def create_root_cause_card(repo_slug: str, finding: Finding) -> str:
    return f"""# Root-Cause Card

## Metadata

- ID: `{repo_slug}-{finding.slug}`
- Bug family: `{finding.bug_family}`
- Bug class: `{finding.bug_class}`
- Confidence tier: `{finding.confidence_tier}`

## Missing Property

- Missing property: `{finding.missing_property}`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- {finding.summary or 'TODO: explain the reusable security lesson in one short paragraph.'}
"""


def create_code_shape_card(repo_slug: str, finding: Finding) -> str:
    return f"""# Code-Shape Card

## Metadata

- ID: `{repo_slug}-{finding.slug}`
- Bug family: `{finding.bug_family}`
- Bug class: `{finding.bug_class}`

## Code Shape Summary

- {finding.summary or 'TODO: describe what the buggy code looked like.'}

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
"""


def create_validation_card(repo_slug: str, finding: Finding) -> str:
    return f"""# Validation Card

## Metadata

- ID: `{repo_slug}-{finding.slug}`
- Bug family: `{finding.bug_family}`
- Bug class: `{finding.bug_class}`

## What Confirmed The Issue

- Evidence 1: TODO
- Evidence 2: TODO

## What Could Have Invalidated It

- Compensating control 1: TODO
- Compensating control 2: TODO

## Severity Guidance

- Expected impact band: TODO
- Expected severity band: TODO

## False-Positive Cautions

- Caution 1: TODO
- Caution 2: TODO
"""


def create_eval_record(repo_slug: str, finding: Finding) -> str:
    severity_band = {
        "tier_a_confirmed": "high_or_medium",
        "tier_b_likely": "medium_or_low",
        "tier_c_provenance_only": "low_or_informational",
    }[finding.confidence_tier]
    return f"""id: "{repo_slug}-{finding.slug}"
source_record: "{repo_slug}-{finding.slug}.yaml"
project: "{finding.project}"

expected_bug_family: "{finding.bug_family}"
expected_bug_class: "{finding.bug_class}"
expected_missing_property: "{finding.missing_property}"

expected_impact_band: "TODO"
expected_severity_band: "{severity_band}"

should_be_detected: true
should_be_flagged_as_security: true

false_positive_cautions:
  - "TODO: describe what could make a similar case non-security."
notes:
  - "Prepared automatically from a raw finding. Needs enrichment."
"""


def main() -> int:
    args = parse_args()

    repo = Path(args.repo).resolve()
    kept_dir = repo / "validated-findings" / "kept"
    if not kept_dir.is_dir():
        raise SystemExit(f"Expected kept findings at: {kept_dir}")

    findings_paths = sorted(kept_dir.glob("*.md"))
    if not findings_paths:
        raise SystemExit(f"No .md findings found in: {kept_dir}")

    repo_slug = slugify_repo_name(repo)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")
    bundle_root = Path(args.output_root).resolve() / f"{timestamp}-{repo_slug}"
    records_dir = bundle_root / "records"
    root_cause_dir = bundle_root / "cards" / "root-cause"
    code_shape_dir = bundle_root / "cards" / "code-shape"
    validation_dir = bundle_root / "cards" / "validation"
    evals_dir = bundle_root / "evals"
    raw_dir = bundle_root / "raw-findings"

    for directory in [records_dir, root_cause_dir, code_shape_dir, validation_dir, evals_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    if not args.no_copy_raw:
        raw_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, object] = {
        "repo": str(repo),
        "repo_slug": repo_slug,
        "kept_dir": str(kept_dir),
        "created_at_utc": timestamp,
        "finding_count": len(findings_paths),
        "findings": [],
    }

    findings = [build_finding(path) for path in findings_paths]
    for finding in findings:
        record_id = f"{repo_slug}-{finding.slug}"
        write_text(records_dir / f"{record_id}.yaml", create_record(repo_slug, finding))
        write_text(root_cause_dir / f"{record_id}.md", create_root_cause_card(repo_slug, finding))
        write_text(code_shape_dir / f"{record_id}.md", create_code_shape_card(repo_slug, finding))
        write_text(validation_dir / f"{record_id}.md", create_validation_card(repo_slug, finding))
        write_text(evals_dir / f"{record_id}.yaml", create_eval_record(repo_slug, finding))

        if not args.no_copy_raw:
            shutil.copy2(finding.source_path, raw_dir / finding.source_path.name)

        manifest["findings"].append(
            {
                "id": record_id,
                "source": str(finding.source_path),
                "bug_family": finding.bug_family,
                "bug_class": finding.bug_class,
                "subsystem": finding.subsystem,
                "confidence_tier": finding.confidence_tier,
                "missing_property": finding.missing_property,
            }
        )

    (bundle_root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    family_counts: dict[str, int] = {}
    tier_counts: dict[str, int] = {}
    for finding in findings:
        family_counts[finding.bug_family] = family_counts.get(finding.bug_family, 0) + 1
        tier_counts[finding.confidence_tier] = tier_counts.get(finding.confidence_tier, 0) + 1

    summary = [
        "# Corpus Import Summary",
        "",
        f"- Repo: `{repo}`",
        f"- Source findings: `{kept_dir}`",
        f"- Bundle root: `{bundle_root}`",
        f"- Finding count: `{len(findings)}`",
        "",
        "## Bug Family Counts",
        "",
    ]
    for family, count in sorted(family_counts.items()):
        summary.append(f"- `{family}`: `{count}`")
    summary.extend(["", "## Confidence Tier Counts", ""])
    for tier, count in sorted(tier_counts.items()):
        summary.append(f"- `{tier}`: `{count}`")
    summary.extend(
        [
            "",
            "## What Was Created",
            "",
            "- `records/`: normalized YAML stubs for each finding",
            "- `cards/root-cause/`: short root-cause retrieval cards",
            "- `cards/code-shape/`: short code-pattern retrieval cards",
            "- `cards/validation/`: validation and false-positive caution cards",
            "- `evals/`: eval record stubs",
            "- `manifest.json`: machine-readable import index",
            "",
            "## Next Step",
            "",
            "Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.",
        ]
    )
    write_text(bundle_root / "SUMMARY.md", "\n".join(summary))

    print(bundle_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
