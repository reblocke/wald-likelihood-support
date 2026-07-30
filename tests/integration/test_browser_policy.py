from __future__ import annotations

import re
from pathlib import Path

from wald_inference import EFFECT_SPECS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WEB_ROOT = PROJECT_ROOT / "web"


def test_worker_is_manifest_driven_and_verifies_before_import() -> None:
    worker = (WEB_ROOT / "pyodide_worker.js").read_text(encoding="utf-8")

    assert "manifest.packages" in worker
    assert "fileRecord.path" in worker
    assert "PACKAGE_FILES" not in worker
    assert "fetchVerifiedBundle()" in worker
    assert worker.index("await fetchVerifiedBundle()") < worker.index("importScripts(")
    assert worker.index("failed integrity verification") < worker.index("loadPyodide(")
    assert "if (bundle.manifest.pyodide_packages.length > 0)" in worker


def test_production_web_code_has_no_persistence_telemetry_or_input_urls() -> None:
    production = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(WEB_ROOT.rglob("*"))
        if path.is_file() and "assets/py" not in path.as_posix()
    )

    forbidden_fragments = [
        "localStorage",
        "sessionStorage",
        "indexedDB",
        "document.cookie",
        "location.search",
        "location.hash",
        "sendBeacon",
        "gtag(",
        "analytics",
        "console.log",
    ]
    assert not [fragment for fragment in forbidden_fragments if fragment in production]
    assert "new URL(path" not in production
    for argument in re.findall(r"fetch\(([^,)]+)", production):
        assert "input" not in argument.lower()


def test_ui_contains_accessibility_scope_and_text_alternatives() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
    css = (WEB_ROOT / "styles.css").read_text(encoding="utf-8")

    assert 'aria-live="polite"' in html
    assert 'role="alert"' in html
    for control_id in [
        "effect-type",
        "estimate",
        "ci-lower",
        "ci-upper",
        "null-value",
        "thresholds",
        "support-criterion",
        "candidate-a",
        "candidate-b",
    ]:
        assert re.search(rf'<label for="{control_id}"', html)
    assert "<details>" in html and "<summary>" in html
    assert 'class="skip-link"' in html
    assert 'aria-describedby="plot-description"' in html
    assert 'id="reconstruction-summary"' in html
    assert 'id="support-interval-summary"' in html
    assert 'id="reference-table"' in html
    assert ":focus-visible" in css
    assert "not the original fitted-model profile likelihood" in html
    assert re.search(r"not\s+a posterior probability", html)
    assert re.search(r"clinical\s+decision support", html)


def test_browser_effect_options_match_the_released_core_registry() -> None:
    config = (WEB_ROOT / "js" / "config.js").read_text(encoding="utf-8")
    configured = re.findall(r'key: "([a-z_]+)"', config)

    assert configured == list(EFFECT_SPECS)
    for key, spec in EFFECT_SPECS.items():
        section = config.split(f'key: "{key}"', maxsplit=1)[1].split("},", maxsplit=1)[0]
        assert f'label: "{spec.label}"' in section
        assert f'family: "{spec.family}"' in section
        assert f"defaultNull: {spec.default_null:g}" in section


def test_exports_use_exact_focused_columns_and_separate_png_hooks() -> None:
    exports = (WEB_ROOT / "js" / "exports.js").read_text(encoding="utf-8")
    keys = re.findall(r'\{ key: "([^"]+)", label:', exports)

    assert keys == [
        "effect_display",
        "effect_working",
        "standardized_distance",
        "relative_likelihood",
        "log_relative_likelihood",
    ]
    assert "exportDashboardPng" in exports
    assert "exportManuscriptPng" in exports
    assert "height: 1000" in exports
    assert "width: 1400" in exports
    assert "scale: 2" in exports
    assert "copyCaption" in exports
    assert "filenameSlug" in exports
    assert not {
        "compatibility",
        "power",
        "critical_effect",
        "type_s",
        "type_m",
        "information_multiplier",
        "precision",
    } & set(keys)


def test_likelihood_ui_has_no_compatibility_or_design_controls() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")

    for forbidden_control in [
        "show-guides",
        "alpha",
        "power",
        "selection-rule",
        "type-s",
        "type-m",
        "information-multiplier",
        "precision-target",
    ]:
        assert f'id="{forbidden_control}"' not in html
    assert "log L(A)/L(B)" in html
    assert "S−2" in html
    assert "2:1 interval is a different" in html


def test_external_source_links_are_safe_and_related_routes_are_static() -> None:
    html = (WEB_ROOT / "index.html").read_text(encoding="utf-8")

    assert 'href="https://academic.oup.com/ajrccm/article/211/9/1610/8300617"' in html
    source_section = html.split("academic.oup.com", maxsplit=1)[1].split(">", maxsplit=1)[0]
    assert 'target="_blank"' in source_section
    assert 'rel="noopener noreferrer"' in source_section
    for repository in [
        "compatibility-curve",
        "critical-effect-size",
        "type-s-m-calibrator",
        "precision-guardrail-planner",
        "conf_curve_likelihood",
    ]:
        assert repository in html
    assert "fetch(" not in html
