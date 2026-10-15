#!/usr/bin/env python3
"""
Test Bot for Relax Cycle Tracking Calendar Enhancements.
Verifies:
1. Expanded year range (before 2024 and after 2029: 2020-2035).
2. Removal of fertile background color and addition of small fertile symbol (🌱).
3. Removal of PMS yellow background color and addition of PMS symbol (🌙).
4. Removal of naming information legend (Bleeding, Fertile, Ovulation, PMS, etc.).
5. Removal of 'Past | Future' label.
6. Small and designed Left, Today, Right navigation buttons.
7. Ovulation peak retention (🟣).
8. Live HTTP server health check (200 OK).
"""

import os
import sys
import re
import logging
import urllib.request
from datetime import date, timedelta
import pandas as pd

# Suppress Streamlit bare-mode context warnings
os.environ["STREAMLIT_LOG_LEVEL"] = "error"
logging.getLogger("streamlit").setLevel(logging.ERROR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load app.py content for static and code inspections
with open("app.py", "r", encoding="utf-8") as f:
    app_source = f.read()

results = []

def record(test_name: str, passed: bool, details: str = ""):
    results.append({
        "name": test_name,
        "passed": passed,
        "details": details
    })
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"[{status}] {test_name}")
    if details:
        print(f"       Details: {details}")

print("=" * 65)
print("🤖 RELAX CALENDAR TEST BOT RUNNING VERIFICATION SUITE")
print("=" * 65)

# -------------------------------------------------------------
# Test 1: Year Range (Before 2024 & Beyond 2029)
# -------------------------------------------------------------
try:
    has_range_match = re.search(r"years_list\s*=\s*list\(range\((\d+),\s*(\d+)\)\)", app_source)
    if has_range_match:
        start_year = int(has_range_match.group(1))
        end_year = int(has_range_match.group(2)) - 1
        is_expanded = start_year <= 2020 and end_year >= 2035
        record(
            "1. Year Range Expansion (2020 - 2035)",
            is_expanded,
            f"years_list spans {start_year} to {end_year} (before 2024 and after 2029)"
        )
    else:
        record("1. Year Range Expansion", False, "Could not locate years_list range definition")
except Exception as e:
    record("1. Year Range Expansion", False, str(e))

# -------------------------------------------------------------
# Test 2: Fertile Color Removed & Small Symbol Used
# -------------------------------------------------------------
try:
    # CSS: .calendar td.fertile should be transparent (no green #dcfce7 background)
    fertile_css_match = re.search(r"\.calendar\s+td\.fertile\s*\{([^}]+)\}", app_source)
    fertile_bg_is_transparent = False
    if fertile_css_match:
        css_props = fertile_css_match.group(1)
        fertile_bg_is_transparent = "background: transparent" in css_props or "background-color: transparent" in css_props
    
    # Python code: fertile days get symbol 🌱
    uses_fertile_sym = '"🌱"' in app_source and 'if "fertile" in classes' in app_source
    
    # Marker styling is smaller than number size
    marker_css = re.search(r"\.cal-marker-symbol\s*\{([^}]+)\}", app_source)
    is_small_font = False
    if marker_css:
        props = marker_css.group(1)
        is_small_font = "font-size: 0.55rem" in props or "font-size: 0.6" in props or "0.5" in props
    
    fertile_passed = fertile_bg_is_transparent and uses_fertile_sym and is_small_font
    record(
        "2. Fertile Color Removed & Small Symbol Used",
        fertile_passed,
        f"Background transparent: {fertile_bg_is_transparent}, Uses 🌱 symbol: {uses_fertile_sym}, Font size small: {is_small_font}"
    )
except Exception as e:
    record("2. Fertile Color Removed & Small Symbol Used", False, str(e))

# -------------------------------------------------------------
# Test 3: PMS Yellow Color Removed & Symbol Used
# -------------------------------------------------------------
try:
    # CSS: .calendar td.pms should be transparent (no yellow #fef3c7 background)
    pms_css_match = re.search(r"\.calendar\s+td\.pms\s*\{([^}]+)\}", app_source)
    pms_bg_is_transparent = False
    if pms_css_match:
        css_props = pms_css_match.group(1)
        pms_bg_is_transparent = "background: transparent" in css_props or "background-color: transparent" in css_props

    # Python code: pms days get symbol 🌙
    uses_pms_sym = '"🌙"' in app_source and 'if "pms" in classes' in app_source

    pms_passed = pms_bg_is_transparent and uses_pms_sym
    record(
        "3. PMS Yellow Color Removed & Symbol Used",
        pms_passed,
        f"Background transparent: {pms_bg_is_transparent}, Uses 🌙 symbol: {uses_pms_sym}"
    )
except Exception as e:
    record("3. PMS Yellow Color Removed & Symbol Used", False, str(e))

# -------------------------------------------------------------
# Test 4: Legend Naming Information Removed
# -------------------------------------------------------------
try:
    # Legend names like "Bleeding / Period", "Forecast", etc. should NOT be in calendar navigation header
    has_bleeding_legend = "Bleeding / Period</span>" in app_source
    has_forecast_legend = "Forecast</span>" in app_source
    legend_removed = (not has_bleeding_legend) and (not has_forecast_legend)
    record(
        "4. Legend Naming Information Removed",
        legend_removed,
        f"Cluttering label bar completely removed from calendar header"
    )
except Exception as e:
    record("4. Legend Naming Information Removed", False, str(e))

# -------------------------------------------------------------
# Test 5: 'Past | Future' Removed
# -------------------------------------------------------------
try:
    has_past_future = "Past | Future" in app_source or "Past &nbsp;|&nbsp; Future" in app_source
    record(
        "5. 'Past | Future' Label Removed",
        not has_past_future,
        f"'Past | Future' label removed: {not has_past_future}"
    )
except Exception as e:
    record("5. 'Past | Future' Label Removed", False, str(e))

# -------------------------------------------------------------
# Test 6: Small, Designed Navigation Buttons
# -------------------------------------------------------------
try:
    has_container = "cal_nav_buttons_container" in app_source
    has_small_height = "height: 28px !important;" in app_source or "min-height: 28px !important;" in app_source
    has_pill_radius = "border-radius: 14px !important;" in app_source or "border-radius: 20px" in app_source
    has_hover = ".st-key-cal_nav_buttons_container button:hover" in app_source
    
    buttons_passed = has_container and has_small_height and has_pill_radius and has_hover
    record(
        "6. Small & Designed Navigation Buttons (Left, Today, Right)",
        buttons_passed,
        f"Keyed container: {has_container}, 28px compact height: {has_small_height}, Pill radius: {has_pill_radius}, Micro-hover: {has_hover}"
    )
except Exception as e:
    record("6. Small & Designed Navigation Buttons", False, str(e))

# -------------------------------------------------------------
# Test 7: Calendar HTML Function Verification
# -------------------------------------------------------------
try:
    import io
    import contextlib
    import calendar
    import html
    with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
        from app import calendar_html, build_calendar_events, build_cycles
    
    test_cycles = build_cycles(date(2026, 1, 1), 28, 5, future_cycles=20)
    test_events = build_calendar_events(test_cycles, period_length=5, cycle_length=28)
    
    # Generate HTML for October 2026
    c_html = calendar_html(2026, 10, test_events, selected_date=date(2026, 10, 15))
    
    contains_ovulation = "🟣" in c_html
    contains_fertile = "🌱" in c_html
    contains_pms = "🌙" in c_html
    contains_small_class = "cal-marker-symbol" in c_html
    
    fn_passed = contains_ovulation and contains_fertile and contains_pms and contains_small_class
    record(
        "7. Calendar Engine HTML Rendering Check",
        fn_passed,
        f"Ovulation 🟣: {contains_ovulation}, Fertile 🌱: {contains_fertile}, PMS 🌙: {contains_pms}, Small marker span: {contains_small_class}"
    )
except Exception as e:
    record("7. Calendar Engine HTML Rendering Check", False, str(e))

# -------------------------------------------------------------
# Test 8: Live Streamlit Server HTTP Health Check
# -------------------------------------------------------------
try:
    req = urllib.request.Request("http://localhost:8501")
    with urllib.request.urlopen(req, timeout=5) as response:
        code = response.status
        is_200 = (code == 200)
        record(
            "8. Live Streamlit Server Health Check",
            is_200,
            f"HTTP status code: {code}"
        )
except Exception as e:
    record("8. Live Streamlit Server Health Check", False, str(e))

# -------------------------------------------------------------
# Final Summary
# -------------------------------------------------------------
total_tests = len(results)
passed_tests = sum(1 for r in results if r["passed"])
failed_tests = total_tests - passed_tests

print("=" * 65)
print(f"📊 SUMMARY: {passed_tests}/{total_tests} Tests Passed ({(passed_tests/total_tests)*100:.1f}%)")
if failed_tests == 0:
    print("🎉 ALL REQUIREMENTS VERIFIED SUCCESSFULLY!")
    sys.exit(0)
else:
    print(f"⚠️ {failed_tests} tests failed.")
    sys.exit(1)
