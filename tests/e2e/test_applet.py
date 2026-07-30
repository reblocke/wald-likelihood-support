from __future__ import annotations

import struct
from pathlib import Path

from playwright.sync_api import Page, expect


def _ready(page: Page, app_url: str) -> None:
    page.goto(app_url)
    expect(page.locator("#runtime-status")).to_have_attribute(
        "data-state",
        "ready",
        timeout=120_000,
    )


def _png_dimensions(path: Path) -> tuple[int, int]:
    contents = path.read_bytes()
    assert contents.startswith(b"\x89PNG\r\n\x1a\n")
    return struct.unpack(">II", contents[16:24])


def _assert_plot_titles_contained(page: Page) -> None:
    title_bounds = page.locator("#plot").evaluate(
        """
        (plot) => {
          const plotBounds = plot.getBoundingClientRect();
          return Array.from(plot.querySelectorAll(".gtitle")).map((title) => {
            const bounds = title.getBoundingClientRect();
            return {
              left: bounds.left,
              right: bounds.right,
              plotLeft: plotBounds.left,
              plotRight: plotBounds.right,
              viewportWidth: window.innerWidth,
            };
          });
        }
        """
    )
    assert title_bounds
    for bounds in title_bounds:
        assert bounds["left"] >= bounds["plotLeft"] - 1
        assert bounds["right"] <= bounds["plotRight"] + 1
        assert bounds["left"] >= -1
        assert bounds["right"] <= bounds["viewportWidth"] + 1


def test_worker_loads_and_calculates(page: Page, app_url: str) -> None:
    _ready(page, app_url)

    page.locator("#thresholds").fill("1.25")
    page.get_by_text("Optional candidate A versus candidate B").click()
    page.locator("#candidate-a").fill("1.25")
    page.locator("#candidate-b").fill("1")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
    expect(page.locator("#result-summary")).to_contain_text(
        "normalized relative likelihood 0.0176602"
    )
    expect(page.locator("#support-interval-summary")).to_contain_text("1.1901022")
    expect(page.locator("#support-interval-summary")).to_contain_text("2.7224553")
    expect(page.locator("#reference-table tbody tr")).to_have_count(2)
    expect(page.locator("#reference-table tbody tr").nth(1)).to_contain_text("0.2115185")
    expect(page.locator("#reference-table tbody tr").nth(1)).to_contain_text("11.977128")
    expect(page.locator("#pairwise-table tbody tr")).to_have_count(1)
    expect(page.locator("#pairwise-sentence")).to_have_text(
        "Candidate A is more supported than candidate B; the reported order is L(A)/L(B)."
    )
    expect(page.locator("#plot .plot-container")).to_be_visible()
    for label in [
        "CI-implied estimate",
        "Null",
        "Reference 1",
        "Candidate A",
        "Candidate B",
        "S−2 / exp(2):1 support interval",
    ]:
        expect(page.locator("#plot .annotation-text").filter(has_text=label)).to_be_visible()
    expect(page.locator("#reconstruction-summary")).to_contain_text("1.8")
    expect(page.locator("#runtime-versions")).to_contain_text("wald-likelihood-support 0.1.2")
    expect(page.locator("#runtime-versions")).to_contain_text("wald-inference 0.4.1")
    expect(page.locator("#core-version")).to_have_text("wald-inference core 0.4.1")


def test_additive_case_and_effect_specific_controls(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#effect-type").select_option("mean_difference")
    expect(page.locator("#axis-spacing-group")).to_be_hidden()
    page.locator("#ci-lower").fill("0.11")
    page.locator("#ci-upper").fill("0.73")
    page.locator("#thresholds").fill("0.2")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
    expect(page.locator("#result-summary")).to_contain_text("0.02943215")
    expect(page.locator("#reconstruction-summary")).to_contain_text("0.15816617")
    expect(page.locator("#reference-table tbody tr").nth(1)).to_contain_text("0.3800851")
    expect(page.locator("#reference-table tbody tr").nth(1)).to_contain_text("Yes")


def test_support_criterion_and_log_view_are_explicit(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#support-criterion").select_option("custom")
    expect(page.locator("#custom-ratio-field")).to_be_visible()
    page.locator("#custom-support-ratio").fill("6.5")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
    expect(page.locator("#support-interval-summary")).to_contain_text("Custom 6.5:1")
    expect(page.locator("#support-interval-summary")).to_contain_text("6.5:1")
    summary = page.locator("#result-summary").inner_text()

    page.get_by_text("Advanced display controls").click()
    page.locator("#view-mode").select_option("log")
    expect(page.locator("#plot .gtitle")).to_contain_text("Log relative support")
    expect(page.locator("#plot .ytitle")).to_contain_text("Log relative support (0 at estimate)")
    assert page.locator("#result-summary").inner_text() == summary


def test_validation_error_and_worker_recovery(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#ci-lower").fill("-1")
    page.locator("#calculate").click()

    expect(page.locator("#error-summary")).to_contain_text("strictly positive")
    expect(page.locator("#runtime-status")).to_have_attribute("data-state", "error")
    expect(page.locator("#error-summary")).not_to_contain_text("Traceback")
    expect(page.locator("#error-summary")).not_to_contain_text("/Users/")

    page.locator("#ci-lower").fill("1.2")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
    expect(page.locator("#reconstruction-summary")).to_contain_text("1.8")


def test_extreme_unrepresentable_support_boundary_is_sanitized(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#effect-type").select_option("mean_difference")
    page.locator("#ci-lower").fill("9.999999999999998e307")
    page.locator("#ci-upper").fill("1.0000000000000002e308")
    page.locator("#null-value").fill("0")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_attribute("data-state", "error")
    expect(page.locator("#error-summary")).to_contain_text(
        "Lower support interval endpoint cannot represent the requested "
        "log-relative-likelihood cutoff at finite floating-point precision"
    )
    expect(page.locator("#error-summary")).not_to_contain_text("Traceback")
    expect(page.locator("#error-summary")).not_to_contain_text("/Users/")


def test_input_errors_link_to_controls(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#ci-lower").fill("")
    page.locator("#calculate").click()

    expect(page.locator("#error-summary")).to_be_visible()
    expect(page.locator("#error-summary a")).to_have_attribute("href", "#ci-lower")
    expect(page.locator("#ci-lower")).to_have_attribute("aria-invalid", "true")
    page.locator("#error-summary a").click()
    expect(page.locator("#ci-lower")).to_be_focused()

    page.locator("#ci-lower").fill("1.2")
    page.locator("#support-criterion").select_option("custom")
    page.locator("#custom-support-ratio").fill("1")
    page.locator("#calculate").click()
    expect(page.locator("#error-summary")).to_contain_text("greater than 1")
    expect(page.locator("#error-summary a")).to_have_attribute("href", "#custom-support-ratio")


def test_presentation_range_does_not_change_support_summaries(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    page.locator("#thresholds").fill("1.25")
    page.locator("#calculate").click()
    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
    reconstruction = page.locator("#reconstruction-summary").inner_text()
    interval = page.locator("#support-interval-summary").inner_text()
    references = page.locator("#reference-table").inner_text()

    page.locator("#display-range-lower").fill("0.9")
    page.locator("#display-range-upper").fill("1.1")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
    assert page.locator("#reconstruction-summary").inner_text() == reconstruction
    assert page.locator("#support-interval-summary").inner_text() == interval
    assert page.locator("#reference-table").inner_text() == references
    expect(page.locator("#warnings-list li")).to_have_count(5)
    expect(page.locator("#warnings-list")).to_contain_text("excludes the CI-implied estimate")
    expect(page.locator("#warnings-list")).to_contain_text("reference thresholds")
    expect(page.locator("#warnings-list")).to_contain_text("selected support interval")


def test_asymmetric_in_range_display_window_keeps_exact_normalized_peak(
    page: Page,
    app_url: str,
) -> None:
    _ready(page, app_url)
    page.locator("#effect-type").select_option("mean_difference")
    page.locator("#ci-lower").fill("-0.0001")
    page.locator("#ci-upper").fill("0.0001")
    page.locator("#null-value").fill("0")
    page.locator("#display-range-lower").fill("-1")
    page.locator("#display-range-upper").fill("0.9")
    page.get_by_text("Advanced display controls").click()
    page.locator("#grid-points").select_option("201")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
    trace = page.locator("#plot").evaluate(
        "(element) => ({x: element.data[0].x, y: element.data[0].y})"
    )
    estimate_index = trace["x"].index(0)
    assert estimate_index >= 0
    assert trace["y"][estimate_index] == 1
    assert max(trace["y"]) == 1


def test_overflow_uses_log_domain_status_in_browser(page: Page, app_url: str) -> None:
    _ready(page, app_url)
    page.locator("#effect-type").select_option("mean_difference")
    page.locator("#ci-lower").fill("-0.0001")
    page.locator("#ci-upper").fill("0.0001")
    page.locator("#null-value").fill("100")
    page.locator("#calculate").click()

    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
    expect(page.locator("#reference-table tbody tr").first).to_contain_text(
        "overflow (see log ratio)"
    )
    expect(page.locator("#reference-table tbody tr").first).to_contain_text("-1.92073e+12")
    expect(page.locator("#warnings-list")).to_contain_text("finite log ratio remains authoritative")


def test_csv_png_and_caption_exports(page: Page, app_url: str, tmp_path: Path) -> None:
    page.context.grant_permissions(
        ["clipboard-read", "clipboard-write"], origin=app_url.rstrip("/")
    )
    _ready(page, app_url)
    page.locator("#thresholds").fill("1.25")
    page.locator("#calculate").click()
    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")

    with page.expect_download() as csv_info:
        page.locator("#export-csv").click()
    csv_download = csv_info.value
    csv_path = tmp_path / csv_download.suggested_filename
    csv_download.save_as(csv_path)
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == (
        "effect_display,effect_working,standardized_distance,"
        "relative_likelihood,log_relative_likelihood"
    )
    assert len(lines) == 802
    assert csv_download.suggested_filename == "wald-likelihood-support.csv"

    for selector, suffix, dimensions in [
        ("#export-manuscript", "-manuscript.png", (2800, 2000)),
        ("#export-dashboard", "-dashboard.png", (1600, 1200)),
    ]:
        with page.expect_download(timeout=60_000) as png_info:
            page.locator(selector).click()
        download = png_info.value
        png_path = tmp_path / download.suggested_filename
        download.save_as(png_path)
        assert download.suggested_filename.endswith(suffix)
        assert _png_dimensions(png_path) == dimensions

    page.locator("#copy-caption").click()
    expect(page.locator("#runtime-status")).to_have_text("Caption copied.")
    clipboard = page.evaluate("navigator.clipboard.readText()")
    assert "reported 95% confidence interval (1.2 to 2.7)" in clipboard
    assert "normalized at the CI-implied estimate" in clipboard
    assert "S−2 / exp(2):1 support interval" in clipboard
    assert "not the original fitted-model likelihood or an exact profile likelihood" in clipboard
    assert "not posterior odds or probabilities" in clipboard


def test_mobile_keyboard_and_privacy_smoke(page: Page, app_url: str) -> None:
    requests: list[tuple[str, str | None]] = []
    page.context.on("request", lambda request: requests.append((request.url, request.post_data)))
    page.set_viewport_size({"width": 390, "height": 844})
    _ready(page, app_url)
    initial_url = page.url
    page.locator("#ci-lower").fill("1.234567891")
    page.locator("#effect-type").focus()
    page.keyboard.press("Tab")
    expect(page.locator("#estimate")).to_be_focused()
    page.keyboard.press("Tab")
    expect(page.locator("#ci-lower")).to_be_focused()
    page.locator("#calculate").click()
    expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")

    assert page.url == initial_url
    assert page.evaluate("localStorage.length") == 0
    assert page.evaluate("sessionStorage.length") == 0
    assert page.evaluate("document.cookie") == ""
    assert (
        page.evaluate("indexedDB.databases ? indexedDB.databases().then((rows) => rows.length) : 0")
        == 0
    )
    serialized_requests = "\n".join(f"{url}\n{body or ''}" for url, body in requests)
    assert "1.234567891" not in serialized_requests
    expect(page.locator(".controls")).to_be_visible()
    expect(page.locator(".results")).to_be_visible()
    assert page.evaluate(
        "document.documentElement.scrollWidth <= document.documentElement.clientWidth"
    )
    effect_options = page.locator("#effect-type option").evaluate_all(
        """
        (options) => options.map((option) => ({
          label: option.textContent.trim(),
          value: option.value,
        }))
        """
    )
    assert effect_options
    page.get_by_text("Advanced display controls").click()
    for option in effect_options:
        page.locator("#effect-type").select_option(str(option["value"]))
        page.locator("#calculate").click()
        expect(page.locator("#runtime-status")).to_have_text("Likelihood-support curve updated.")
        for view, title in [
            ("relative", "Normalized Wald relative likelihood"),
            ("log", "Log relative support"),
        ]:
            page.locator("#view-mode").select_option(view)
            plot_title = page.locator("#plot .gtitle")
            page.wait_for_function(
                """
                ([expectedView, expectedEffect]) => {
                  const raw = document.querySelector("#plot .gtitle")
                    ?.getAttribute("data-unformatted");
                  const normalized = raw
                    ?.replaceAll("<br>", " ")
                    .replace(/\\s+/g, " ")
                    .trim();
                  return normalized?.includes(expectedView) &&
                    normalized?.includes(expectedEffect);
                }
                """,
                arg=[title, str(option["label"]).lower()],
            )
            unformatted_title = plot_title.get_attribute("data-unformatted")
            assert unformatted_title is not None
            normalized_title = " ".join(unformatted_title.replace("<br>", " ").split())
            assert title in normalized_title
            _assert_plot_titles_contained(page)
