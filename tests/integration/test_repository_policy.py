from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_makefile_exposes_required_commands() -> None:
    makefile = (PROJECT_ROOT / "Makefile").read_text(encoding="utf-8")

    for target in [
        "stage-web:",
        "fmt:",
        "fmt-check:",
        "lint:",
        "test:",
        "e2e:",
        "verify:",
        "serve:",
        "clean:",
    ]:
        assert target in makefile


def test_ci_and_pages_use_repository_targets() -> None:
    ci = (PROJECT_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    pages = (PROJECT_ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")

    assert "make fmt-check" in ci
    assert "make lint" in ci
    assert "make test" in ci
    assert "make e2e" in ci
    assert "make e2e-webkit-smoke" in ci
    assert "make stage-web" in pages
    assert "web" in pages


def test_generated_stage_is_ignored_and_not_tracked() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "web/assets/py/" in gitignore
    assert (
        subprocess.run(
            ["git", "check-ignore", "web/assets/py/manifest.json"],
            cwd=PROJECT_ROOT,
            check=False,
        ).returncode
        == 0
    )
    assert (
        subprocess.run(
            ["git", "ls-files", "web/assets/py"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        == ""
    )


def test_repository_has_exact_mit_identity_and_no_template_prompts() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    license_text = (PROJECT_ROOT / "LICENSE").read_text(encoding="utf-8")
    public_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            PROJECT_ROOT / "README.md",
            PROJECT_ROOT / "CITATION.cff",
            PROJECT_ROOT / "llms.txt",
            *sorted((PROJECT_ROOT / "docs").rglob("*.md")),
        ]
    )

    assert 'license = "MIT"' in pyproject
    assert '{ name = "Brian Locke" }' in pyproject
    assert "MIT License" in license_text
    assert "Copyright (c) 2026 Brian Locke" in license_text
    assert "AUTHOR ACTION REQUIRED" not in public_docs
    assert "Replace-me demonstration" not in public_docs


def test_scientific_dependency_is_release_url_only() -> None:
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    stage = (PROJECT_ROOT / "browser-stage.toml").read_text(encoding="utf-8")
    dependency_text = f"{pyproject}\n{stage}"

    assert "releases/download/v0.2.1/wald_inference-0.2.1-py3-none-any.whl" in dependency_text
    assert re.search(r"#sha256=[0-9a-f]{64}", pyproject)
    for forbidden in [
        "../wald-inference",
        "wald-inference-core.git@",
        "localhost",
        "127.0.0.1",
        "source = { path",
        "branch =",
    ]:
        assert forbidden not in dependency_text


def test_app_delegates_scientific_calculations_to_root_public_core_apis() -> None:
    contract = (PROJECT_ROOT / "src" / "wald_likelihood_support" / "contract.py").read_text(
        encoding="utf-8"
    )

    assert "from wald_inference import (" in contract
    assert "from wald_inference." not in contract
    for required_api in [
        "reconstruct_wald_from_95_ci",
        "standardized_distance",
        "relative_likelihood",
        "log_relative_likelihood",
        "log_support_ratio",
        "support_ratio",
        "support_interval",
        "support_interval_for_ratio",
    ]:
        assert required_api in contract
    for app_local_formula in [
        "np.exp(",
        "np.log(",
        "np.square(",
        "math.exp(",
        "math.log(",
        "math.sqrt(",
        "-0.5 *",
    ]:
        assert app_local_formula not in contract
