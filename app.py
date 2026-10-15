import calendar
import os
from datetime import date, timedelta, datetime
from typing import Optional, List, Dict, Any, Tuple
import html
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import db
import health_engine
import chat_assistant

# ---------------------------------------------------------
# Page Configuration & Relax Branding
# ---------------------------------------------------------
st.set_page_config(
    page_title="Relax | Menstrual Health & Wellness",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize persistent SQLite database
db.init_db()

# ---------------------------------------------------------
# Custom Styling: Relax Theme & Hide Streamlit Default UI
# ---------------------------------------------------------
st.markdown("""
<style>
/* Hide default Streamlit menu and footer for clean app feel */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background: transparent !important;
    z-index: 1 !important;
}

/* Safe page padding: ensures top header data and cards are fully visible below mobile notch & Streamlit top bar */
.block-container {
    padding-top: 4.5rem !important;
    padding-bottom: 95px !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 5.2rem !important; /* safe clearance under phone notch and browser top bar */
        padding-left: 0.9rem !important;
        padding-right: 0.9rem !important;
    }
}

/* Compact KPI Metric Cards */
[data-testid="stMetricValue"] {
    font-size: 1.18rem !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

/* Relax Hero & Status Badges Row - Clean Neutral, No Green Header Card */
.hero-card {
    background: transparent !important;
    border: none !important;
    padding: 2px 0px 6px 0px !important;
    margin-top: 4px !important;
    margin-bottom: 8px !important;
    box-shadow: none !important;
    font-size: 8pt !important;
}
.hero-title {
    font-size: 8.5pt !important;
    font-weight: 700 !important;
    color: #1e293b !important;
    margin-bottom: 3px !important;
    line-height: 1.3 !important;
}
.hero-subtitle {
    font-size: 8pt !important;
    color: #475569 !important;
    margin-bottom: 6px !important;
    line-height: 1.3 !important;
}
.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}
.hero-badge {
    display: inline-block;
    padding: 1px 6px;
    border-radius: 6px;
    font-size: 7.5pt !important;
    font-weight: 600;
}
.badge-phase { background: #fce7f3; color: #be185d; border: 1px solid #fbcfe8; }
.badge-countdown { background: #ede9fe; color: #6d28d9; border: 1px solid #ddd6fe; }
.badge-fertile { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.badge-fluctuation { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.badge-health { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
.health-chip {
    display: inline-block;
    background: #f8fafc;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 1px 5px;
    font-size: 7.5pt !important;
    font-weight: 600;
    margin-right: 4px;
    margin-bottom: 2px;
}

/* Person Face Account Button: No circle, transparent background, translucent man color */
[data-testid="stPopover"] {
    display: flex !important;
    justify-content: flex-end !important;
}
[data-testid="stPopover"] > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
[data-testid="stPopover"] button,
[data-testid="stPopover"] button:focus,
[data-testid="stPopover"] button:active,
[data-testid="stPopover"] button:focus-visible {
    border-radius: 8px !important;
    border: none !important;
    outline: none !important;
    background: transparent !important;
    background-color: transparent !important;
    box-shadow: none !important;
    -webkit-box-shadow: none !important;
    padding: 2px 8px !important;
    height: auto !important;
    min-height: 28px !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 6px !important;
    color: #334155 !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
}
[data-testid="stPopover"] button:hover {
    background: rgba(15, 118, 110, 0.08) !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    color: #0f766e !important;
}
[data-testid="stPopover"] button span[data-testid="stIconMaterial"],
[data-testid="stPopover"] button span.material-symbols-rounded,
[data-testid="stPopover"] button .material-symbols-rounded,
[data-testid="stPopover"] button svg {
    color: rgba(15, 118, 110, 0.40) !important; /* translucent / transparent man icon color */
    fill: rgba(15, 118, 110, 0.40) !important;
    opacity: 0.60 !important;
    font-size: 1.25rem !important;
}


/* Fixed Non-Movable Bottom Mobile Navigation Bar */
.st-key-bottom_nav_bar {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100vw !important;
    background: rgba(255, 255, 255, 0.98) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    border-top: 1px solid #e2e8f0 !important;
    padding: 6px 8px 8px 8px !important;
    z-index: 999999 !important;
    box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.08) !important;
    display: flex !important;
    justify-content: center !important;
}

/* Force side-by-side horizontal row on ALL screens, especially mobile phones */
.st-key-bottom_nav_bar [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    justify-content: space-between !important;
    align-items: center !important;
    gap: 8px !important;
    width: 100% !important;
    max-width: 400px !important;
    margin: 0 auto !important;
}

.st-key-bottom_nav_bar [data-testid="stColumn"],
.st-key-bottom_nav_bar [data-testid="column"] {
    width: auto !important;
    min-width: 0 !important;
    flex: 1 1 0 !important;
    display: flex !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
}

.st-key-bottom_nav_bar [data-testid="stButton"] {
    width: 100% !important;
    margin: 0 !important;
}

/* Base style: Small, light orange and yellow button */
.st-key-bottom_nav_bar [data-testid="stButton"] button {
    font-size: 1.05rem !important;
    padding: 2px 0 !important;
    min-height: 34px !important;
    height: 34px !important;
    border-radius: 10px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    background: linear-gradient(135deg, #fed7aa 0%, #fef08a 100%) !important;
    border: 1px solid #fde047 !important;
    color: #451a03 !important;
    box-shadow: 0 1px 3px rgba(245, 158, 11, 0.15) !important;
}

.st-key-bottom_nav_bar [data-testid="stButton"] button p {
    font-size: 1.05rem !important;
    line-height: 1 !important;
    margin: 0 !important;
}

/* Highlight selected button to GREEN */
.st-key-bottom_nav_bar [data-testid="stButton"] button[kind="primary"],
.st-key-bottom_nav_bar [data-testid="stButton"] button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #86efac 0%, #22c55e 100%) !important;
    border: 2px solid #16a34a !important;
    color: #ffffff !important;
    box-shadow: 0 2px 8px rgba(34, 197, 94, 0.45) !important;
    transform: translateY(-2px) !important;
}

/* Compact In-Page Buttons (Previous/Next Month, Actions) */
div[data-testid="stButton"]:not(.st-key-bottom_nav_bar [data-testid="stButton"]) button {
    padding: 2px 8px !important;
    min-height: 28px !important;
    height: 28px !important;
    font-size: 0.78rem !important;
    border-radius: 6px !important;
    line-height: 1 !important;
}
div[data-testid="stButton"]:not(.st-key-bottom_nav_bar [data-testid="stButton"]) button p {
    font-size: 0.78rem !important;
    line-height: 1 !important;
    margin: 0 !important;
}

/* Compact Symptom & Mood Selection Tiles (Small, Horizontally Placed) */
div[data-testid="stButtonGroup"],
.stButtonGroup {
    display: flex !important;
    flex-wrap: wrap !important;
    flex-direction: row !important;
    gap: 6px !important;
    row-gap: 7px !important;
    align-items: center !important;
    margin-top: 3px !important;
    margin-bottom: 8px !important;
}

div[data-testid="stButtonGroup"] button,
.stButtonGroup button,
div[data-testid="stButtonGroup"] [data-testid="stBaseButton-pills"],
div[data-testid="stButtonGroup"] [role="button"],
div[data-testid="stButtonGroup"] [role="radio"],
div[data-testid="stButtonGroup"] [role="checkbox"] {
    font-size: 0.82rem !important;
    padding: 4px 10px !important;
    min-height: 29px !important;
    height: auto !important;
    border-radius: 14px !important;
    font-weight: 500 !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #334155 !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

div[data-testid="stButtonGroup"] button p,
.stButtonGroup button p {
    font-size: 0.82rem !important;
    line-height: 1.2 !important;
    margin: 0 !important;
}

div[data-testid="stButtonGroup"] button:hover,
.stButtonGroup button:hover {
    border-color: #0f766e !important;
    background: #f0fdf4 !important;
    color: #0f766e !important;
    transform: translateY(-1px) !important;
}

/* Active / Selected Tile Highlight */
div[data-testid="stButtonGroup"] button[data-selected="true"],
div[data-testid="stButtonGroup"] button[data-selected],
.stButtonGroup button[data-selected="true"],
.stButtonGroup button[data-selected],
div[data-testid="stButtonGroup"] [data-selected="true"],
div[data-testid="stButtonGroup"] [data-selected],
div[data-testid="stButtonGroup"] button[aria-checked="true"],
div[data-testid="stButtonGroup"] [aria-checked="true"] {
    background: #dcfce7 !important;
    border: 1.5px solid #16a34a !important;
    color: #15803d !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 5px rgba(22, 163, 74, 0.22) !important;
}

div[data-testid="stButtonGroup"] button[data-selected="true"] p,
div[data-testid="stButtonGroup"] button[data-selected] p,
.stButtonGroup button[data-selected="true"] p,
.stButtonGroup button[data-selected] p {
    color: #15803d !important;
    font-weight: 600 !important;
}

/* Horizontal Smooth Scrolling Calendar Container (3 Months View, Scroll Right for Previous Months) */
.calendar-scroll-wrapper {
    position: relative !important;
    display: flex !important;
    flex-direction: row !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    gap: 14px !important;
    padding: 6px 2px 14px 2px !important;
    scroll-behavior: auto !important;
    -webkit-overflow-scrolling: touch !important;
    scroll-snap-type: x proximity !important;
}
.calendar-scroll-wrapper::-webkit-scrollbar {
    height: 8px !important;
}
.calendar-scroll-wrapper::-webkit-scrollbar-track {
    background: #f1f5f9 !important;
    border-radius: 8px !important;
}
.calendar-scroll-wrapper::-webkit-scrollbar-thumb {
    background: #94a3b8 !important;
    border-radius: 8px !important;
}
.calendar-scroll-wrapper::-webkit-scrollbar-thumb:hover {
    background: #64748b !important;
}
.calendar-scroll-item {
    flex: 0 0 calc((100% - 28px) / 3) !important;
    min-width: 295px !important;
    box-sizing: border-box !important;
    scroll-snap-align: start !important;
}
@media (max-width: 950px) {
    .calendar-scroll-item {
        flex: 0 0 calc((100% - 14px) / 2) !important;
        min-width: 280px !important;
    }
}
@media (max-width: 600px) {
    .calendar-scroll-item {
        flex: 0 0 88% !important;
        min-width: 260px !important;
    }
}

/* Relax Calendar Table */
.calendar {
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 0px !important;
    background: #ffffff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    height: 100%;
    box-sizing: border-box;
}
.calendar h3 {
    margin-top: 0;
    margin-bottom: 8px;
    font-size: 1.02rem;
    color: #1e293b;
    font-weight: 600;
}
.calendar table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
}
.calendar th {
    font-size: .75rem;
    padding: 6px;
    border-bottom: 1px solid #cbd5e1;
    color: #64748b;
    text-align: center;
    font-weight: 600;
}
.calendar td {
    height: 62px;
    vertical-align: top;
    padding: 0px !important;
    border: 1px solid #f1f5f9;
    font-size: .85rem;
    transition: all 0.15s ease-in-out;
    cursor: pointer;
    position: relative;
}
.calendar td a.cal-day-cell-link {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    justify-content: flex-start !important;
    width: 100% !important;
    height: 100% !important;
    padding: 4px !important;
    color: inherit !important;
    text-decoration: none !important;
    box-sizing: border-box !important;
}
.calendar td:hover:not(.empty) {
    transform: scale(1.06);
    z-index: 10;
    box-shadow: 0 6px 16px rgba(14, 116, 144, 0.22);
    border: 2px solid #0f766e;
}
.calendar td.empty { background: #f8fafc; cursor: default; }
.calendar td.bleeding { background: #fee2e2; }
.calendar td.estimated { background: #fff1f2; border: 1.5px dashed #f43f5e; }
.calendar td.fertile { background: transparent; }
.calendar td.ovulation { background: #f3e8ff; border: 2px solid #a855f7; }
.calendar td.pms { background: transparent; }
.calendar td.forecast { border: 2px dashed #94a3b8; }
.calendar td.today { box-shadow: inset 0 0 0 2px #2563eb; }
.calendar td.logged { border-bottom: 3px solid #ec4899; }
.cal-marker-symbol {
    font-size: 0.55rem !important;
    line-height: 1 !important;
    vertical-align: middle !important;
    margin-top: 1px !important;
    display: inline-block !important;
}

/* Year Selector Pills: Smooth Horizontal Scrolling & Compact Design */
.st-key-cal_pills_year [data-testid="stPills"] {
    display: flex !important;
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    gap: 4px !important;
    padding-bottom: 3px !important;
    scrollbar-width: thin !important;
}
.st-key-cal_pills_year [data-testid="stPills"] button {
    font-size: 0.78rem !important;
    padding: 2px 10px !important;
    white-space: nowrap !important;
    flex-shrink: 0 !important;
}

/* Sleek, Small & Designed Navigation Buttons (Left, Today, Right) */
.st-key-cal_nav_buttons_container {
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
}
.st-key-cal_nav_buttons_container [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 5px !important;
}
.st-key-cal_nav_buttons_container [data-testid="stColumn"] {
    width: auto !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
}
.st-key-cal_nav_buttons_container button {
    height: 28px !important;
    min-height: 28px !important;
    border-radius: 14px !important;
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    padding: 0 10px !important;
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    color: #334155 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
}
.st-key-cal_nav_buttons_container button:hover {
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08) !important;
    transform: translateY(-1px) !important;
}
.st-key-cal_nav_buttons_container button:active {
    transform: translateY(0px) !important;
}
.calendar td.selected-cal-day {
    box-shadow: inset 0 0 0 2.5px #0f766e, 0 0 12px rgba(15, 118, 110, 0.45) !important;
    background-color: #f0fdfa !important;
    border: 2px solid #0f766e !important;
    z-index: 11 !important;
}

/* Image 3 Pill Badge Styling for Date Selector Popover */
.st-key-cal_pill_container {
    margin-top: 4px !important;
    margin-bottom: 8px !important;
}
.st-key-cal_pill_container [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 10px !important;
}
.st-key-cal_pill_container [data-testid="stColumn"] {
    width: auto !important;
    min-width: 0 !important;
    display: flex !important;
    align-items: center !important;
}

/* Previous Image 1 Date Pill Button Styling */
.st-key-cal_pill_date [data-testid="stPopover"] button {
    background: #f8fafc !important;
    background-color: #f8fafc !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 20px !important;
    padding: 0 14px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #334155 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04) !important;
    height: 32px !important;
    min-height: 32px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
}
.st-key-cal_pill_date [data-testid="stPopover"] button:hover {
    background: #f1f5f9 !important;
    border-color: #94a3b8 !important;
}
.st-key-cal_pill_date [data-testid="stPopover"] button svg {
    display: inline-block !important;
    color: #64748b !important;
    width: 14px !important;
    height: 14px !important;
}

/* Top Bar Actions Row (Diet & Account tightly grouped with NO big gap) */
.st-key-top_actions_bar {
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
    width: 100% !important;
}
.st-key-top_actions_bar [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    justify-content: flex-end !important;
    align-items: center !important;
    gap: 8px !important;
    width: auto !important;
}
.st-key-top_actions_bar [data-testid="stColumn"] {
    width: auto !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
    display: flex !important;
    align-items: center !important;
}
.st-key-top_actions_bar [data-testid="stColumn"]:last-child [data-testid="stPopover"] button,
.st-key-top_actions_bar [data-testid="stPopover"]:last-child button {
    border-radius: 6px !important;
    height: 32px !important;
    min-height: 32px !important;
    width: 32px !important;
    min-width: 32px !important;
    padding: 0 !important;
    font-size: 1.15rem !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    color: #334155 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: none !important;
    cursor: pointer !important;
    transition: all 0.15s ease-in-out !important;
}
.st-key-top_actions_bar [data-testid="stColumn"]:last-child [data-testid="stPopover"] button:hover,
.st-key-top_actions_bar [data-testid="stPopover"]:last-child button:hover {
    background: rgba(0, 0, 0, 0.04) !important;
    border: none !important;
    box-shadow: none !important;
    color: #0f172a !important;
    transform: scale(1.15) !important;
}
/* Hide the chevron dropdown arrow so only the account icon is shown */
.st-key-top_actions_bar [data-testid="stColumn"]:last-child [data-testid="stPopover"] button svg:not([data-testid="stIconMaterial"]),
.st-key-top_actions_bar [data-testid="stPopover"]:last-child button svg:not([data-testid="stIconMaterial"]),
.st-key-top_actions_bar [data-testid="stColumn"]:last-child [data-testid="stPopover"] button svg[data-testid="stPopoverChevron"],
.st-key-top_actions_bar [data-testid="stPopover"]:last-child button svg[data-testid="stPopoverChevron"] {
    display: none !important;
}
.st-key-top_actions_bar [data-testid="stColumn"]:last-child [data-testid="stPopover"] button svg[data-testid="stIconMaterial"],
.st-key-top_actions_bar [data-testid="stPopover"]:last-child button svg[data-testid="stIconMaterial"] {
    display: inline-block !important;
    width: 22px !important;
    height: 22px !important;
    color: #334155 !important;
}
.st-key-top_actions_bar [data-testid="stColumn"]:last-child [data-testid="stPopover"] button:hover svg[data-testid="stIconMaterial"],
.st-key-top_actions_bar [data-testid="stPopover"]:last-child button:hover svg[data-testid="stIconMaterial"] {
    color: #0f172a !important;
}

/* Diet Notification Icon Styling (Circle Removed) */
.diet-notif-btn [data-testid="stPopover"] button,
div.diet-notif-btn button,
.st-key-diet_notif_top [data-testid="stPopover"] button,
.st-key-diet_notif_sel [data-testid="stPopover"] button,
.st-key-diet_notif_sym [data-testid="stPopover"] button {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
    padding: 0 !important;
    font-size: 1.25rem !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    box-shadow: none !important;
    transition: all 0.15s ease-in-out !important;
}
.diet-notif-btn [data-testid="stPopover"] button:hover,
div.diet-notif-btn button:hover,
.st-key-diet_notif_top [data-testid="stPopover"] button:hover,
.st-key-diet_notif_sel [data-testid="stPopover"] button:hover,
.st-key-diet_notif_sym [data-testid="stPopover"] button:hover {
    background: rgba(0, 0, 0, 0.04) !important;
    border: none !important;
    box-shadow: none !important;
    transform: scale(1.15) !important;
}
.diet-notif-btn [data-testid="stPopover"] button svg,
div.diet-notif-btn button svg,
.st-key-diet_notif_top [data-testid="stPopover"] button svg,
.st-key-diet_notif_sel [data-testid="stPopover"] button svg,
.st-key-diet_notif_sym [data-testid="stPopover"] button svg {
    display: none !important;
}

.st-key-cal_pill_container [data-testid="stCheckbox"] {
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
}
.st-key-cal_pill_container [data-testid="stCheckbox"] label {
    margin-bottom: 0 !important;
    padding-top: 0 !important;
}

/* Image 4 Responsive Small Button for Daily Log */
.st-key-log_action_buttons {
    margin-top: 10px !important;
    margin-bottom: 8px !important;
}
.st-key-log_action_buttons [data-testid="stHorizontalBlock"] {
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    gap: 10px !important;
}
.st-key-log_action_buttons [data-testid="stColumn"] {
    width: auto !important;
    min-width: 0 !important;
    flex: 0 0 auto !important;
}
.st-key-log_action_buttons div[data-testid="stButton"] {
    width: auto !important;
    margin: 0 !important;
}
.st-key-log_action_buttons button {
    height: 34px !important;
    min-height: 34px !important;
    padding: 4px 18px !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    width: auto !important;
    min-width: 120px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1.2 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    transition: all 0.15s ease-in-out !important;
}
.st-key-log_action_buttons button p {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    line-height: 1.2 !important;
}
@media (max-width: 600px) {
    .st-key-log_action_buttons [data-testid="stColumn"] {
        flex: 1 1 45% !important;
    }
    .st-key-log_action_buttons button {
        width: 100% !important;
        min-width: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Core Helper & Calculation Functions
# ---------------------------------------------------------
def add_days(d: date, n: int) -> date:
    return d + timedelta(days=n)

def cycle_dates(start: date, cycle_length: int, period_length: int) -> dict:
    next_period = add_days(start, cycle_length)
    ovulation = add_days(next_period, -14)
    return {
        "start": start,
        "bleeding_end": add_days(start, period_length - 1),
        "ovulation": ovulation,
        "fertile_start": add_days(ovulation, -5),
        "fertile_end": ovulation,
        "next_period": next_period,
    }

def build_cycles(start: date, cycle_length: int, period_length: int, future_cycles: int = 28, fluctuation_margin: int = 2) -> pd.DataFrame:
    today = date.today()
    rows = []
    current = start
    cycle_idx = 1
    max_loops = 150  # Cap supporting up to 10 years of projections
    
    remaining_future = future_cycles
    while max_loops > 0:
        max_loops -= 1
        c = cycle_dates(current, cycle_length, period_length)
        is_current = (c["start"] <= today <= c["next_period"])
        is_past = (c["next_period"] < today)
        is_future = (c["start"] > today)
        
        status = "Current" if is_current else ("Past" if is_past else "Future")
        
        _, _, window_str = health_engine.get_fluctuation_window(c["next_period"], fluctuation_margin)
        
        rows.append({
            "Cycle": cycle_idx,
            "Status": status,
            "Start": c["start"],
            "Bleeding end": c["bleeding_end"],
            "Ovulation estimate": c["ovulation"],
            "Next period": c["next_period"],
            "Expected Window (± Margin)": window_str,
            "is_current": is_current,
        })
        current = c["next_period"]
        cycle_idx += 1
        
        if c["start"] >= today:
            remaining_future -= 1
            if remaining_future <= 0:
                break
                
    return pd.DataFrame(rows)

def build_calendar_events(
    cycles: pd.DataFrame,
    user_symptoms: dict = None,
    phase_advisories: dict = None,
    user_logs: list = None,
    period_length: int = 5,
    cycle_length: int = 28
) -> dict:
    if user_symptoms is None:
        user_symptoms = {}
    if phase_advisories is None:
        phase_advisories = {}
    if user_logs is None:
        user_logs = []
    events = {}

    # 1. Populate all historical periods logged in user_logs
    sorted_logs = sorted(user_logs)
    for i, log_d in enumerate(sorted_logs):
        # Mark bleeding days for this confirmed historical period
        for day_idx in range(period_length):
            b_date = log_d + timedelta(days=day_idx)
            events[b_date] = {
                "classes": ["bleeding", "logged"],
                "marker": "",
                "phase": "Confirmed Historical Period 🩸",
                "mood": "Logged menstrual bleeding",
                "physical": "Confirmed period entry from your cycle history",
                "tip": "Rest with a warm heating pad and replenish iron.",
                "advisories": phase_advisories.get("menstrual", [])
            }

        # If there is a subsequent confirmed logged period, map the full biological cycle between them!
        if i < len(sorted_logs) - 1:
            next_log_d = sorted_logs[i + 1]
            interval = (next_log_d - log_d).days
            if 20 <= interval <= 48:
                hist_ov = next_log_d - timedelta(days=14)
                hist_fertile_start = hist_ov - timedelta(days=5)
                hist_pms_start = next_log_d - timedelta(days=6)

                # Follicular phase
                d = log_d + timedelta(days=period_length)
                while d < hist_fertile_start:
                    if d not in events:
                        events[d] = {
                            "classes": ["follicular"],
                            "marker": "",
                            "phase": "Follicular Phase 🌿",
                            "mood": "Rising stamina, clear focus, renewed energy",
                            "physical": "Skin brightening, rising estrogen levels",
                            "tip": "Great time for cardio workouts and starting new tasks.",
                            "advisories": phase_advisories.get("follicular", [])
                        }
                    d += timedelta(days=1)

                # Fertile window
                d = hist_fertile_start
                while d < hist_ov:
                    if d not in events:
                        events[d] = {
                            "classes": ["fertile"],
                            "marker": "",
                            "phase": "High Fertility Window 🌱",
                            "mood": "Confident, vibrant, energetic",
                            "physical": "Clear stretchy cervical mucus",
                            "tip": "Peak fertility days.",
                            "advisories": phase_advisories.get("ovulation", [])
                        }
                    d += timedelta(days=1)

                # Ovulation peak
                if hist_ov not in events:
                    events[hist_ov] = {
                        "classes": ["ovulation", "fertile"],
                        "marker": "",
                        "phase": "Ovulation Peak 🟣",
                        "mood": "Peak vitality and communicative energy",
                        "physical": "Mild one-sided pelvic twinge (mittelschmerz)",
                        "tip": "Highest fertility day of this cycle.",
                        "advisories": phase_advisories.get("ovulation", [])
                    }

                # Mid-Luteal phase
                d = hist_ov + timedelta(days=1)
                while d < hist_pms_start:
                    if d not in events:
                        events[d] = {
                            "classes": ["luteal"],
                            "marker": "",
                            "phase": "Mid-Luteal Phase 🌼",
                            "mood": "Calm, organized, steady focus",
                            "physical": "Progesterone rising, steady core temperature",
                            "tip": "Focus on complex carbs and consistent sleep routines.",
                            "advisories": phase_advisories.get("luteal", [])
                        }
                    d += timedelta(days=1)

                # PMS window
                d = hist_pms_start
                while d < next_log_d:
                    if d not in events:
                        events[d] = {
                            "classes": ["pms"],
                            "marker": "",
                            "phase": "Pre-Menstrual Phase (PMS Window) ✨",
                            "mood": "Mood swings, irritability, sensitive cues",
                            "physical": "Mild bloating, breast tenderness, cravings",
                            "tip": "Prioritize magnesium, chamomile tea, and self-care.",
                            "advisories": phase_advisories.get("pms", [])
                        }
                    d += timedelta(days=1)
            elif interval > 48:
                # Interpolate estimated cycles for unlogged gap months (e.g. June and July)
                curr_est = log_d + timedelta(days=cycle_length)
                while curr_est + timedelta(days=period_length) < next_log_d:
                    est_bleed_end = curr_est + timedelta(days=period_length - 1)
                    est_ov = curr_est + timedelta(days=cycle_length - 14)
                    est_fertile_start = est_ov - timedelta(days=5)
                    est_pms_start = curr_est + timedelta(days=cycle_length - 6)
                    est_next = curr_est + timedelta(days=cycle_length)

                    # Bleeding days for estimated unlogged cycle
                    d = curr_est
                    while d <= est_bleed_end:
                        if d not in events:
                            events[d] = {
                                "classes": ["bleeding", "estimated"],
                                "marker": "",
                                "phase": "Estimated Period (Unlogged Month) 🩸",
                                "mood": "Estimated menstrual cycle",
                                "physical": f"Calculated based on your typical {cycle_length}-day cycle",
                                "tip": "Rest with a warm heating pad and replenish iron.",
                                "advisories": phase_advisories.get("menstrual", [])
                            }
                        d += timedelta(days=1)

                    # Follicular phase
                    d = est_bleed_end + timedelta(days=1)
                    while d < est_fertile_start and d < next_log_d:
                        if d not in events:
                            events[d] = {
                                "classes": ["follicular"],
                                "marker": "",
                                "phase": "Follicular Phase 🌿 (Estimated)",
                                "mood": "Rising energy and focus",
                                "physical": "Skin brightening, rising stamina",
                                "tip": "Great time for workouts and self-care.",
                                "advisories": phase_advisories.get("follicular", [])
                            }
                        d += timedelta(days=1)

                    # Fertile window
                    d = est_fertile_start
                    while d < est_ov and d < next_log_d:
                        if d not in events:
                            events[d] = {
                                "classes": ["fertile"],
                                "marker": "",
                                "phase": "High Fertility Window 🌱 (Estimated)",
                                "mood": "Confident, upbeat, energetic",
                                "physical": "Clear stretchy cervical mucus",
                                "tip": "Peak fertility days.",
                                "advisories": phase_advisories.get("ovulation", [])
                            }
                        d += timedelta(days=1)

                    # Ovulation
                    if est_ov not in events and est_ov < next_log_d:
                        events[est_ov] = {
                            "classes": ["ovulation", "fertile"],
                            "marker": "",
                            "phase": "Ovulation Peak 🟣 (Estimated)",
                            "mood": "Peak vitality and communication",
                            "physical": "Estimated ovulation peak",
                            "tip": "Antioxidant nourishment.",
                            "advisories": phase_advisories.get("ovulation", [])
                        }

                    # Mid-Luteal phase
                    d = est_ov + timedelta(days=1)
                    while d < est_pms_start and d < next_log_d:
                        if d not in events:
                            events[d] = {
                                "classes": ["luteal"],
                                "marker": "",
                                "phase": "Mid-Luteal Phase 🌼 (Estimated)",
                                "mood": "Calm, organized, steady focus",
                                "physical": "Progesterone rising",
                                "tip": "Focus on complex carbs and consistent sleep.",
                                "advisories": phase_advisories.get("luteal", [])
                            }
                        d += timedelta(days=1)

                    # PMS window
                    d = est_pms_start
                    while d < min(est_next, next_log_d):
                        if d not in events:
                            events[d] = {
                                "classes": ["pms"],
                                "marker": "",
                                "phase": "PMS Window ✨ (Estimated)",
                                "mood": "Emotional sensitivity, irritability cues",
                                "physical": "Mild bloating, breast tenderness",
                                "tip": "Magnesium and gentle rest.",
                                "advisories": phase_advisories.get("pms", [])
                            }
                        d += timedelta(days=1)

                    curr_est += timedelta(days=cycle_length)

        # 1b. Project historical baseline for unlogged months before earliest logged period (up to 90 cycles / 7 years back)
    if sorted_logs:
        earliest_log = sorted_logs[0]
        curr_back = earliest_log - timedelta(days=cycle_length)
        for _ in range(90):
            back_bleed_end = curr_back + timedelta(days=period_length - 1)
            back_ov = curr_back + timedelta(days=cycle_length - 14)
            back_fertile_start = back_ov - timedelta(days=5)
            back_pms_start = curr_back + timedelta(days=cycle_length - 6)
            back_next = curr_back + timedelta(days=cycle_length)

            # Bleeding days
            d = curr_back
            while d <= back_bleed_end:
                if d not in events:
                    events[d] = {
                        "classes": ["bleeding", "estimated"],
                        "marker": "",
                        "phase": "Estimated Period (Historical Baseline) 🩸",
                        "mood": "Estimated menstrual cycle",
                        "physical": f"Calculated based on your typical {cycle_length}-day cycle",
                        "tip": "Rest with a warm heating pad and replenish iron.",
                        "advisories": phase_advisories.get("menstrual", [])
                    }
                d += timedelta(days=1)

            # Follicular phase
            d = back_bleed_end + timedelta(days=1)
            while d < back_fertile_start:
                if d not in events:
                    events[d] = {
                        "classes": ["follicular"],
                        "marker": "",
                        "phase": "Follicular Phase 🌿 (Estimated)",
                        "mood": "Rising energy and stamina",
                        "physical": "Skin brightening, rising estrogen",
                        "tip": "Great time for workouts.",
                        "advisories": phase_advisories.get("follicular", [])
                    }
                d += timedelta(days=1)

            # Fertile window
            d = back_fertile_start
            while d < back_ov:
                if d not in events:
                    events[d] = {
                        "classes": ["fertile"],
                        "marker": "",
                        "phase": "High Fertility Window 🌱 (Estimated)",
                        "mood": "Confident and upbeat",
                        "physical": "Cervical mucus shifts",
                        "tip": "Peak fertility days.",
                        "advisories": phase_advisories.get("ovulation", [])
                    }
                d += timedelta(days=1)

            # Ovulation
            if back_ov not in events:
                events[back_ov] = {
                    "classes": ["ovulation", "fertile"],
                    "marker": "",
                    "phase": "Ovulation Peak 🟣 (Estimated)",
                    "mood": "Peak vitality",
                    "physical": "Estimated ovulation",
                    "tip": "Antioxidants and healthy nourishment.",
                    "advisories": phase_advisories.get("ovulation", [])
                }

            # Mid-Luteal
            d = back_ov + timedelta(days=1)
            while d < back_pms_start:
                if d not in events:
                    events[d] = {
                        "classes": ["luteal"],
                        "marker": "",
                        "phase": "Mid-Luteal Phase 🌼 (Estimated)",
                        "mood": "Calm focus",
                        "physical": "Progesterone rising",
                        "tip": "Complex carbs and sleep.",
                        "advisories": phase_advisories.get("luteal", [])
                    }
                d += timedelta(days=1)

            # PMS
            d = back_pms_start
            while d < back_next:
                if d not in events:
                    events[d] = {
                        "classes": ["pms"],
                        "marker": "",
                        "phase": "PMS Window ✨ (Estimated)",
                        "mood": "Sensitive cues, irritability",
                        "physical": "Mild bloating",
                        "tip": "Self-care and rest.",
                        "advisories": phase_advisories.get("pms", [])
                    }
                d += timedelta(days=1)

            curr_back -= timedelta(days=cycle_length)

    # 2. Populate cycles from forecast dataframe
    for _, row in cycles.iterrows():
        start = row["Start"]
        bleed_end = row["Bleeding end"]
        ov = row["Ovulation estimate"]
        next_p = row["Next period"]
        window_str = row.get("Expected Window (± Margin)", "")
        fertile_start = add_days(ov, -5)
        pms_start = add_days(next_p, -6)

        # Menstrual phase (Bleeding days)
        d = start
        while d <= bleed_end:
            if d not in events:
                events[d] = {
                    "classes": ["bleeding"],
                    "marker": "",
                    "phase": "Menstrual Phase (Period) 🩸",
                    "mood": "Low energy, reflective, introspection, quiet focus",
                    "physical": "Uterine cramps, fatigue, lower back ache, pelvic fullness",
                    "tip": "Rest with a warm heating pad, sip warm chamomile tea, and eat iron-rich foods.",
                    "advisories": phase_advisories.get("menstrual", [])
                }
            d += timedelta(days=1)

        # Follicular phase (post-period to fertile window)
        d = add_days(bleed_end, 1)
        while d < fertile_start:
            if d not in events:
                events[d] = {
                    "classes": ["follicular"],
                    "marker": "",
                    "phase": "Follicular Phase 🌿",
                    "mood": "Rising energy, mental clarity, optimism, motivated & creative",
                    "physical": "Skin brightening, increased stamina, renewed vitality",
                    "tip": "Great time for cardio workouts, strategic planning, and starting new projects.",
                    "advisories": phase_advisories.get("follicular", [])
                }
            d += timedelta(days=1)

        # Fertile window (days leading up to ovulation)
        d = fertile_start
        while d < ov:
            if d not in events:
                events[d] = {
                    "classes": ["fertile"],
                    "marker": "",
                    "phase": "High Fertility Window 🌱",
                    "mood": "Confident, vibrant, outgoing, elevated libido, charismatic",
                    "physical": "Clear stretchy cervical mucus, heightened sensory perception",
                    "tip": "Peak conception window if trying to conceive; stay active and well-hydrated.",
                    "advisories": phase_advisories.get("ovulation", [])
                }
            d += timedelta(days=1)

        # Ovulation peak day
        if ov not in events:
            events[ov] = {
                "classes": ["ovulation", "fertile"],
                "marker": "",
                "phase": "Ovulation Peak 🟣",
                "mood": "Peak vitality, assertive, sensual, upbeat, highly communicative",
                "physical": "Mild one-sided pelvic twinge (mittelschmerz), peak conception chance",
                "tip": "Highest fertility day; nourish with antioxidants and balanced meals.",
                "advisories": phase_advisories.get("ovulation", [])
            }

        # Mid-Luteal phase
        d = add_days(ov, 1)
        while d < pms_start:
            if d not in events:
                events[d] = {
                    "classes": ["luteal"],
                    "marker": "",
                    "phase": "Mid-Luteal Phase 🌼",
                    "mood": "Calm, organized, detail-oriented, nesting mindset, steady focus",
                    "physical": "Progesterone rising, elevated core temperature, steady appetite",
                    "tip": "Focus on complex carbs, magnesium-rich foods, and consistent sleep routines.",
                    "advisories": phase_advisories.get("luteal", [])
                }
            d += timedelta(days=1)

        # Pre-Menstrual / PMS phase
        d = pms_start
        while d < next_p:
            if d not in events:
                events[d] = {
                    "classes": ["pms"],
                    "marker": "",
                    "phase": "Pre-Menstrual Phase (PMS Window) ✨",
                    "mood": "Mood swings, irritability, emotional sensitivity, anxiety, lower patience",
                    "physical": "Bloating, breast tenderness, food cravings (sweets/salty), mild headache",
                    "tip": "Reduce caffeine & sodium, take magnesium/B6, gentle walks, prioritize self-care.",
                    "advisories": phase_advisories.get("pms", [])
                }
            d += timedelta(days=1)

        # Forecasted next period
        if next_p not in events:
            events[next_p] = {
                "classes": ["forecast", "bleeding"],
                "marker": "",
                "phase": "Forecasted Next Period 🔮",
                "mood": "Readiness to slow down, cycle transition and reset",
                "physical": f"Anticipated bleeding onset. Expected window: {window_str if window_str else 'On schedule'}",
                "tip": "Have supplies ready, stay cozy, and plan a relaxing evening.",
                "advisories": phase_advisories.get("menstrual", [])
            }
    
    # 3. Merge custom user daily symptoms
    for log_date, symptom_data in user_symptoms.items():
        if log_date in events:
            events[log_date]["user_log"] = symptom_data
            events[log_date]["classes"].append("logged")
        else:
            events[log_date] = {
                "classes": ["logged"],
                "marker": " 📝",
                "phase": "Custom User Log 📝",
                "mood": symptom_data.get("mood", "Normal"),
                "physical": symptom_data.get("symptoms", "None noted"),
                "tip": "Keep listening to your body's daily cues.",
                "user_log": symptom_data
            }
            
    return events

def calendar_html(year: int, month: int, events: dict, selected_date: Optional[date] = None) -> str:
    cal = calendar.Calendar(firstweekday=0)
    today = date.today()
    tag_html = ""
    if year == today.year and month == today.month:
        tag_html = " <span style='font-size: 7pt; font-weight: 600; background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 6px; vertical-align: middle;'>Current</span>"
    html_code = f"<div class='calendar'><h3>{calendar.month_name[month]} {year}{tag_html}</h3><table>"
    html_code += "<tr>" + "".join(f"<th>{x}</th>" for x in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]) + "</tr>"
    for week in cal.monthdayscalendar(year, month):
        html_code += "<tr>"
        for day_num in week:
            if day_num == 0:
                html_code += "<td class='empty'></td>"
                continue
            d = date(year, month, day_num)
            info = events.get(d)
            classes = []
            markers = ""
            if d == today:
                classes.append("today")
            if selected_date and d == selected_date:
                classes.append("selected-cal-day")

            if info:
                classes.extend(info.get("classes", []))
                raw_markers = info.get("marker", "")
                # Strip old bleeding and decorative symbols, preserve phase indicator symbols
                for sym in ["🩸", "🌿", "🔮", "🌼"]:
                    raw_markers = raw_markers.replace(sym, "")
                markers = raw_markers.strip()

                # Phase symbols (smaller than day number):
                # 1. Ovulation peak shows 🟣
                if "ovulation" in classes and "🟣" not in markers:
                    markers = (markers + " 🟣").strip()
                # 2. Fertile window shows 🌱 (fertility symbol)
                elif "fertile" in classes and "🌱" not in markers:
                    markers = (markers + " 🌱").strip()
                # 3. PMS window shows 🌙 (pre-menstrual moon symbol)
                elif "pms" in classes and "🌙" not in markers:
                    markers = (markers + " 🌙").strip()

                clean_phase = info.get('phase', 'Normal')
                for sym in ["🩸", "🌿", "🔮", "🌼"]:
                    clean_phase = clean_phase.replace(sym, "").strip()
                if "ovulation" in classes and "🟣" not in clean_phase:
                    clean_phase = f"{clean_phase} 🟣"
                elif "fertile" in classes and "🌱" not in clean_phase:
                    clean_phase = f"{clean_phase} 🌱"
                elif "pms" in classes and "🌙" not in clean_phase:
                    clean_phase = f"{clean_phase} 🌙"
                
                tooltip_parts = [
                    f"📅 {d.strftime('%a, %d %b %Y')}",
                    f"📍 Phase: {clean_phase}",
                ]
                
                # If user logged custom entry for this day
                if "user_log" in info:
                    u_log = info["user_log"]
                    tooltip_parts.append(
                        f"\n📝 Your Log: Flow: {u_log.get('flow', 'None')} | Mood: {u_log.get('mood', 'N/A')} | Energy: {u_log.get('energy', 'Normal')}"
                    )
                    if u_log.get('symptoms'):
                        tooltip_parts.append(f"🩺 Logged Symptoms: {u_log.get('symptoms')}")
                    if u_log.get('notes'):
                        tooltip_parts.append(f"💭 Note: {u_log.get('notes')}")
                
                tooltip_parts.extend([
                    f"\n🧠 Expected Mood: {info.get('mood', 'Balanced')}",
                    f"🩺 Expected Physical: {info.get('physical', 'Stable')}",
                    f"💡 Care Tip: {info.get('tip', 'Stay hydrated and rested.')}"
                ])

                # Append personalized condition advisories if available
                if info.get("advisories"):
                    tooltip_parts.append("\n🩺 Health & Hormonal Advisories:")
                    for adv in info["advisories"]:
                        tooltip_parts.append(f"• {adv}")

                tooltip_text = "\n".join(tooltip_parts)
            else:
                tooltip_text = f"📅 {d.strftime('%a, %d %b %Y')}\nNormal baseline day"

            escaped_tooltip = html.escape(tooltip_text, quote=True).replace("\n", "&#10;")
            class_text = " ".join(set(classes))
            date_link = f"?cal_date={d.isoformat()}"
            marker_html = f"<span class='cal-marker-symbol'>{markers}</span>" if markers else ""
            html_code += f"<td class='{class_text}' title='{escaped_tooltip}'><a href='{date_link}' target='_self' class='cal-day-cell-link'><b>{day_num}</b>{marker_html}</a></td>"
        html_code += "</tr>"
    return html_code + "</table></div>"

def generate_ics(
    cycles: pd.DataFrame,
    username: str,
    include_period: bool = True,
    period_label: str = "🌸 Rest Time",
    include_ovulation: bool = True,
    ovulation_label: str = "🟣 Ovulation Peak",
    include_fertile: bool = True,
    fertile_label: str = "🌱 High Fertility Window",
    include_pms: bool = False,
    pms_label: str = "✨ Cozy Care Window"
) -> str:
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//Relax//Cycle Forecast for {username}//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    for _, row in cycles.iterrows():
        # 1. Bleeding / Period / Rest Time
        if include_period:
            start_str = row["Start"].strftime("%Y%m%d")
            end_str = (row["Bleeding end"] + timedelta(days=1)).strftime("%Y%m%d")
            window_note = row.get("Expected Window (± Margin)", "Regular cycle")
            summary_name = period_label if period_label.strip() else f"Rest Time ({username})"
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"SUMMARY:{summary_name}",
                f"DTSTART;VALUE=DATE:{start_str}",
                f"DTEND;VALUE=DATE:{end_str}",
                f"DESCRIPTION:Relax sync. Expected window: {window_note}",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])

        # 2. Ovulation Peak
        if include_ovulation:
            ov_str = row["Ovulation estimate"].strftime("%Y%m%d")
            ov_end = (row["Ovulation estimate"] + timedelta(days=1)).strftime("%Y%m%d")
            summary_name = ovulation_label if ovulation_label.strip() else f"Ovulation ({username})"
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"SUMMARY:{summary_name}",
                f"DTSTART;VALUE=DATE:{ov_str}",
                f"DTEND;VALUE=DATE:{ov_end}",
                f"DESCRIPTION:Estimated peak ovulation day.",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])

        # 3. Fertile Window
        if include_fertile:
            f_start = row["Ovulation estimate"] - timedelta(days=5)
            f_end = row["Ovulation estimate"] + timedelta(days=1)
            f_start_str = f_start.strftime("%Y%m%d")
            f_end_str = f_end.strftime("%Y%m%d")
            summary_name = fertile_label if fertile_label.strip() else f"Fertile Window ({username})"
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"SUMMARY:{summary_name}",
                f"DTSTART;VALUE=DATE:{f_start_str}",
                f"DTEND;VALUE=DATE:{f_end_str}",
                f"DESCRIPTION:Estimated high fertility window.",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])

        # 4. PMS Window
        if include_pms:
            pms_start = row["Next period"] - timedelta(days=6)
            pms_end = row["Next period"]
            pms_start_str = pms_start.strftime("%Y%m%d")
            pms_end_str = pms_end.strftime("%Y%m%d")
            summary_name = pms_label if pms_label.strip() else f"PMS Window ({username})"
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"SUMMARY:{summary_name}",
                f"DTSTART;VALUE=DATE:{pms_start_str}",
                f"DTEND;VALUE=DATE:{pms_end_str}",
                f"DESCRIPTION:Pre-menstrual gentle self-care window.",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])

    ics_lines.append("END:VCALENDAR")
    return "\r\n".join(ics_lines)

# ---------------------------------------------------------
# User Account & Database Profile Setup
# ---------------------------------------------------------
all_users = db.get_all_users()
user_names = [u["username"] for u in all_users]
db_stats = db.get_database_stats()

# Retrieve active user from session state or default to Krishna
if "selected_username" not in st.session_state:
    st.session_state["selected_username"] = "Krishna" if "Krishna" in user_names else (user_names[0] if user_names else "Krishna")

matched_users = [u for u in all_users if u["username"] == st.session_state["selected_username"]]
if matched_users:
    current_user = matched_users[0]
else:
    current_user = all_users[0] if all_users else db.get_or_create_user("Krishna")
    st.session_state["selected_username"] = current_user["username"]

user_id = current_user["id"]
username = current_user["username"]

# Security check: If user account has a PIN set, require PIN unlock
user_has_pin = bool(current_user.get("pin_hash"))
auth_session_key = f"auth_unlocked_{user_id}"

if user_has_pin and not st.session_state.get(auth_session_key, False):
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    lk_c1, lk_c2, lk_c3 = st.columns([1.3, 1.4, 1.3])
    with lk_c2:
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px 16px; box-shadow: 0 2px 10px rgba(0,0,0,0.04); text-align: center;">
            <div style="font-size: 1.4rem; margin-bottom: 2px;">🌸</div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #1e293b;">Relax &bull; Private Health Log</div>
            <div style="font-size: 0.80rem; color: #64748b; margin-top: 2px;">Profile <b>{username}</b> is protected by a PIN.</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        entered_pin = st.text_input("Enter PIN to unlock", type="password", key=f"pin_unlock_input_{user_id}", label_visibility="collapsed", placeholder="Enter PIN to unlock")
        if st.button("🔓 Unlock Account", type="primary", use_container_width=True, key=f"btn_unlock_{user_id}"):
            success, msg, _ = db.verify_user_login(username, entered_pin)
            if success:
                st.session_state[auth_session_key] = True
                st.rerun()
            else:
                st.error(msg)
                
        # Password / PIN Recovery when user forgets on the lock screen
        sec_info = db.get_user_security_info(user_id)
        saved_q = sec_info.get("recovery_question") or "What is your favorite comfort food?"
        with st.expander("❓ Forgot PIN?", expanded=False):
            st.caption(f"**Security Question:** {saved_q}")
            rec_ans = st.text_input("Security Answer", type="password", key=f"lk_rec_ans_{user_id}", placeholder="Answer to question")
            lr1, lr2 = st.columns(2)
            with lr1:
                new_p1 = st.text_input("New PIN", type="password", key=f"lk_new_p1_{user_id}", placeholder="New PIN")
            with lr2:
                new_p2 = st.text_input("Confirm PIN", type="password", key=f"lk_new_p2_{user_id}", placeholder="Confirm PIN")
            if st.button("🔑 Reset PIN & Unlock", key=f"btn_lk_reset_{user_id}", use_container_width=True):
                if not new_p1 or not new_p2:
                    st.error("Please enter and confirm your new PIN.")
                elif new_p1 != new_p2:
                    st.error("New PINs do not match.")
                else:
                    ok, r_msg = db.reset_user_pin_with_recovery(user_id, rec_ans.strip(), new_p1)
                    if ok:
                        st.session_state[auth_session_key] = True
                        st.success(f"✅ {r_msg}")
                        st.rerun()
                    else:
                        st.error(r_msg)
    st.stop()

# Fetch historical cycle dates for this user
user_logs = db.get_user_cycle_logs(user_id)

# ---------------------------------------------------------
# Sidebar: Typical Cycle Baseline Defaults
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Typical Cycle Baseline")
st.sidebar.caption("Set baseline length & duration. *(Note: You can log new period dates and daily symptoms directly using the Calendar!)*")

# Default latest start date
if user_logs:
    default_start_date = user_logs[-1]
else:
    default_start_date = date(date.today().year, 9, 21)

start_date = st.sidebar.date_input(
    "Latest period start date",
    value=default_start_date
)

cycle_length = st.sidebar.number_input(
    "Typical cycle length (days)",
    min_value=21, max_value=45,
    value=int(current_user["typical_cycle_length"]),
    step=1
)

period_length = st.sidebar.number_input(
    "Typical bleeding duration (days)",
    min_value=1, max_value=10,
    value=int(current_user["typical_period_length"]),
    step=1
)

if st.sidebar.button("💾 Save as My Defaults"):
    db.update_user_preferences(user_id, cycle_length, period_length)
    db.add_cycle_log(user_id, start_date, "Logged via settings")
    st.sidebar.success("Saved to database!")
    st.rerun()

# ---------------------------------------------------------
# Sidebar: Period History Management
# ---------------------------------------------------------
with st.sidebar.expander("📅 Log Historical Periods", expanded=False):
    new_log_date = st.date_input("Add period date", value=date.today())
    if st.button("➕ Add Date to History"):
        db.add_cycle_log(user_id, new_log_date)
        st.success(f"Added {new_log_date.strftime('%d %b %Y')}!")
        st.rerun()
    
    if user_logs:
        st.caption("Your logged periods:")
        for log_d in reversed(user_logs):
            c_del1, c_del2 = st.columns([3, 1])
            c_del1.write(f"• {log_d.strftime('%d %b %Y')}")
            if c_del2.button("🗑️", key=f"del_{log_d}"):
                db.delete_cycle_log(user_id, log_d)
                st.rerun()

# Determine effective cycle length
cycle_length_used = cycle_length
regularity_msg = "Manual setting"
if len(user_logs) >= 2:
    intervals = [(user_logs[i] - user_logs[i-1]).days for i in range(1, len(user_logs))]
    valid_intervals = [x for x in intervals if 21 <= x <= 45]
    if valid_intervals:
        avg_interval = round(sum(valid_intervals) / len(valid_intervals))
        cycle_length_used = avg_interval
        regularity_msg = f"Average of {len(valid_intervals)} past cycles ({avg_interval} days)"

# ---------------------------------------------------------
# Sidebar: Medications & Health Factors
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 💊 Medications")
st.sidebar.caption("Track medications, thyroid treatment, hormonal supplements & factors altering period timing.")

user_thyroid = current_user.get("thyroid_status") or "None / Normal Thyroid"
if user_thyroid == "None":
    user_thyroid = "None / Normal Thyroid"

raw_conds = current_user.get("health_conditions") or ""
user_conditions = [c.strip() for c in raw_conds.split(",") if c.strip()]

user_stress = current_user.get("stress_level") or "Low / Managed"
if user_stress == "Normal":
    user_stress = "Low / Managed"

thyroid_options = [
    "None / Normal Thyroid",
    "Hypothyroidism (Underactive)",
    "Hyperthyroidism (Overactive)",
    "Hashimoto's Thyroiditis"
]
curr_thyroid_idx = thyroid_options.index(user_thyroid) if user_thyroid in thyroid_options else 0

selected_thyroid = st.sidebar.selectbox(
    "Thyroid Condition / Medication",
    options=thyroid_options,
    index=curr_thyroid_idx,
    help="Underactive or overactive thyroid significantly alters TRH, prolactin, and ovulation timing."
)

condition_choices = [
    "PCOS / PCOD",
    "Endometriosis",
    "Uterine Fibroids",
    "Perimenopause",
    "Hormonal Birth Control"
]
valid_user_conds = [c for c in user_conditions if c in condition_choices]

selected_conditions = st.sidebar.multiselect(
    "Other Health Issues / Hormonal Rx",
    options=condition_choices,
    default=valid_user_conds,
    help="Select any diagnosed or suspected conditions affecting your cycle."
)

stress_options = ["Low / Managed", "Moderate", "High / Chronic Stress / Burnout"]
curr_stress_idx = stress_options.index(user_stress) if user_stress in stress_options else 0

selected_stress = st.sidebar.selectbox(
    "Stress Level",
    options=stress_options,
    index=curr_stress_idx,
    help="Cortisol suppresses GnRH pulsatility and can postpone ovulation."
)

if st.sidebar.button("💾 Save Medications Profile"):
    conds_str = ", ".join(selected_conditions)
    db.update_user_health_profile(user_id, selected_thyroid, conds_str, selected_stress)
    st.sidebar.success("Medications & health factors updated! Period fluctuations recalculated.")
    st.rerun()

# ---------------------------------------------------------
# Health & Period Fluctuation Engine Calculation
# ---------------------------------------------------------
health_res = health_engine.calculate_health_fluctuations(
    thyroid_status=selected_thyroid,
    health_conditions=selected_conditions,
    stress_level=selected_stress,
    base_cycle_length=cycle_length_used,
    base_period_length=period_length
)
fluctuation_margin = health_res["fluctuation_margin"]

# ---------------------------------------------------------
# Compute All Cycles & Phase Determination (Globally Available)
# ---------------------------------------------------------
# Compute All Cycles from start_date forward through today and into the future for 10+ years (140 cycles)
cycles = build_cycles(start_date, cycle_length_used, period_length, future_cycles=140, fluctuation_margin=fluctuation_margin)

# Fetch custom daily symptom logs
user_symptoms = db.get_daily_symptoms(user_id)

# Identify active cycle currently in progress for today
today = date.today()
current_rows = cycles[cycles["is_current"]]
if len(current_rows) > 0:
    active_cycle = current_rows.iloc[0]
else:
    future_rows = cycles[cycles["Start"] > today]
    if len(future_rows) > 0:
        active_cycle = future_rows.iloc[0]
    else:
        active_cycle = cycles.iloc[-1]

active_start = active_cycle["Start"]
active_cycle_dates = cycle_dates(active_start, cycle_length_used, period_length)
cycle_day = (today - active_start).days + 1
days_to_next_period = (active_cycle["Next period"] - today).days

earliest_next, latest_next, active_window_str = health_engine.get_fluctuation_window(
    active_cycle["Next period"],
    fluctuation_margin
)

if cycle_day <= 0:
    phase_name = "Upcoming Cycle"
    phase_badge = "badge-phase"
elif cycle_day <= period_length:
    phase_name = "Menstrual Phase (Period) 🩸"
    phase_badge = "badge-phase"
elif today < active_cycle_dates["fertile_start"]:
    phase_name = "Follicular Phase 🌿"
    phase_badge = "badge-fertile"
elif today <= active_cycle_dates["fertile_end"]:
    if today == active_cycle_dates["ovulation"]:
        phase_name = "Ovulation Peak Day 🟣"
    else:
        phase_name = "High Fertility Window 🌱"
    phase_badge = "badge-fertile"
elif today < add_days(active_cycle["Next period"], -6):
    phase_name = "Mid-Luteal Phase 🌼"
    phase_badge = "badge-countdown"
else:
    phase_name = "Pre-Menstrual Phase (PMS Window) ✨"
    phase_badge = "badge-countdown"

# Build calendar events globally so all views and popovers can inspect dates
events = build_calendar_events(
    cycles=cycles,
    user_symptoms=user_symptoms,
    phase_advisories=health_res["phase_advisories"],
    user_logs=user_logs,
    period_length=period_length,
    cycle_length=cycle_length_used
)

def render_diet_notif_popover(phase_val: str, tooltip_hint: str = "Diet", container_key: str = "diet_notif"):
    """Renders a sleek, cycle-synced diet notification icon popover."""
    diet_info = health_engine.get_diet_suggestions(phase_val)
    with st.container(key=container_key):
        with st.popover("🥗", help="Diet"):
            st.markdown(f"<div style='font-weight:700; font-size:1.05rem; color:#15803d; margin-bottom:2px;'>🥗 Diet</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.83rem; font-weight:600; color:#334155; margin-bottom:2px;'>{diet_info['name']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.78rem; color:#64748b; font-style:italic; margin-bottom:6px;'>{diet_info['tagline']}</div>", unsafe_allow_html=True)
            
            # Food image preview for this phase
            p_img_key = diet_info.get("key", "luteal")
            img_file = f"assets/{p_img_key}_diet.jpg"
            if os.path.exists(img_file):
                st.image(img_file, use_container_width=True)
                
            st.markdown(f"<div style='background:#f0fdf4; border-left:3px solid #22c55e; padding:5px 8px; border-radius:6px; font-size:0.78rem; color:#166534; margin-bottom:8px;'>🧬 <b>Biology:</b> {diet_info['biology']}</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='font-weight:600; font-size:0.82rem; color:#1e293b; margin-bottom:2px;'>🌟 Recommended Superfoods:</div>", unsafe_allow_html=True)
            for title, desc in diet_info["superfoods"][:3]:
                st.markdown(f"<div style='font-size:0.78rem; margin-bottom:2px;'>• <b>{title}:</b> <span style='color:#475569;'>{desc}</span></div>", unsafe_allow_html=True)
                
            st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='font-weight:600; font-size:0.82rem; color:#991b1b; margin-bottom:2px;'>🚫 Foods to Minimize:</div>", unsafe_allow_html=True)
            for avoid_item in diet_info["foods_to_avoid"][:2]:
                st.markdown(f"<div style='font-size:0.78rem; color:#64748b; margin-bottom:2px;'>• {avoid_item}</div>", unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)
            st.caption("✨ Full 4-phase nutrition guide available in 💡 Insights tab.")

# ---------------------------------------------------------
# Main App Header & Relax Branding
# ---------------------------------------------------------
top_bar_col1, top_bar_col2 = st.columns([2.5, 1.5])

with top_bar_col1:
    st.markdown("""
    <div style="margin-top: 2px; margin-bottom: 4px; display: flex; align-items: center; height: 100%;">
        <span style="font-size: 1.25rem; font-weight: 700; color: #1e293b;">🌸 Relax</span>
    </div>
    """, unsafe_allow_html=True)

with top_bar_col2:
    with st.container(key="top_actions_bar"):
        diet_col, acc_col = st.columns([1, 1], gap="small")
        with diet_col:
            render_diet_notif_popover(phase_name, "Diet", container_key="diet_notif_top")
        with acc_col:
            with st.popover("", icon=":material/person:", help="Account"):
                st.markdown(f"<div style='font-size:1.15rem; font-weight:700; color:#1e293b; margin-bottom:2px;'>👤 {username}</div>", unsafe_allow_html=True)
                st.caption(f"Profile: **{username}** &bull; {len(user_logs)} cycles logged")
                st.markdown("---")
            
                # Security & PIN info
                sec_info = db.get_user_security_info(user_id)
                has_pin = sec_info["has_pin"]
                saved_q = sec_info["recovery_question"] or "What is your favorite comfort food?"
                
                q_options = [
                    "What is your favorite comfort food?",
                    "What is the name of your first pet?",
                    "What city were you born in?",
                    "What was your childhood nickname?",
                    "What is your secret safe word or lucky charm?"
                ]
                if saved_q and saved_q not in q_options:
                    q_options.insert(0, saved_q)

                # 1. Set PIN / PIN Security Section
                pin_label = "🔒 Set PIN" if not has_pin else "🔑 PIN Security"
                with st.expander(pin_label, expanded=False):
                    if not has_pin:
                        st.caption("Protect private records by setting a PIN:")
                        new_p1 = st.text_input("New PIN", type="password", key="acc_set_new_p1", placeholder="Enter new PIN")
                        new_p2 = st.text_input("Confirm PIN", type="password", key="acc_set_new_p2", placeholder="Confirm new PIN")
                        sel_q = st.selectbox("Security Question", q_options, key="acc_set_sel_q")
                        rec_ans = st.text_input("Recovery Answer", type="password", key="acc_set_rec_ans", placeholder="Answer used for PIN recovery")
                        if st.button("🔒 Save PIN", key="acc_btn_save_pin", use_container_width=True):
                            if not new_p1 or not new_p2:
                                st.error("Please enter and confirm your PIN.")
                            elif new_p1 != new_p2:
                                st.error("PINs do not match.")
                            elif not rec_ans.strip():
                                st.error("Please provide a recovery answer.")
                            else:
                                db.set_user_security(user_id, new_p1, sel_q, rec_ans.strip())
                                st.session_state[f"auth_unlocked_{user_id}"] = True
                                st.success("✅ PIN activated!")
                                st.rerun()
                    else:
                        st.markdown("<div style='background:#dcfce7; border: 1px solid #86efac; border-radius:6px; padding:4px 8px; font-size:0.78rem; color:#15803d; font-weight:600; margin-bottom:6px;'>🔒 PIN Protection Active</div>", unsafe_allow_html=True)
                        sec_action = st.radio(
                            "Security Action",
                            ["Change PIN", "Forgot PIN", "Remove PIN"],
                            horizontal=True,
                            label_visibility="collapsed",
                            key="acc_sec_radio_action"
                        )
                        
                        if sec_action == "Change PIN":
                            chg_old = st.text_input("Current PIN", type="password", key="acc_chg_old", placeholder="Current PIN")
                            c_p1, c_p2 = st.columns(2)
                            with c_p1:
                                chg_p1 = st.text_input("New PIN", type="password", key="acc_chg_p1", placeholder="New PIN")
                            with c_p2:
                                chg_p2 = st.text_input("Confirm PIN", type="password", key="acc_chg_p2", placeholder="Confirm PIN")
                            chg_q = st.selectbox("Security Question", q_options, index=q_options.index(saved_q) if saved_q in q_options else 0, key="acc_chg_q")
                            chg_ans = st.text_input("New Recovery Answer (optional)", type="password", key="acc_chg_ans", placeholder="Optional new answer")
                            if st.button("🔄 Update PIN", key="acc_btn_update_pin", use_container_width=True):
                                ok, _, _ = db.verify_user_login(username, chg_old)
                                if not ok:
                                    st.error("Current PIN is incorrect.")
                                elif not chg_p1 or not chg_p2:
                                    st.error("New PIN cannot be empty.")
                                elif chg_p1 != chg_p2:
                                    st.error("New PINs do not match.")
                                else:
                                    if chg_ans.strip():
                                        db.set_user_security(user_id, chg_p1, chg_q, chg_ans.strip())
                                    else:
                                        db.set_user_pin(user_id, chg_p1)
                                    st.success("✅ PIN updated!")
                                    st.rerun()
                        elif sec_action == "Forgot PIN":
                            st.caption(f"**Security Question:** {saved_q}")
                            rec_in_ans = st.text_input("Answer to Security Question", type="password", key="acc_rec_in_ans", placeholder="Enter answer")
                            r1, r2 = st.columns(2)
                            with r1:
                                reset_p1 = st.text_input("New PIN", type="password", key="acc_reset_p1", placeholder="New PIN")
                            with r2:
                                reset_p2 = st.text_input("Confirm PIN", type="password", key="acc_reset_p2", placeholder="Confirm PIN")
                            if st.button("🔑 Reset PIN", key="acc_btn_rec_reset", use_container_width=True):
                                if not reset_p1 or reset_p1 != reset_p2:
                                    st.error("Please enter matching new PINs.")
                                else:
                                    ok, r_msg = db.reset_user_pin_with_recovery(user_id, rec_in_ans.strip(), reset_p1)
                                    if ok:
                                        st.session_state[f"auth_unlocked_{user_id}"] = True
                                        st.success(f"✅ {r_msg}")
                                        st.rerun()
                                    else:
                                        st.error(r_msg)
                        elif sec_action == "Remove PIN":
                            rm1, rm2 = st.columns([1.5, 1])
                            with rm1:
                                rem_pin = st.text_input("Enter PIN", type="password", key="acc_rem_pin", label_visibility="collapsed", placeholder="Enter PIN")
                            with rm2:
                                if st.button("Disable PIN", key="acc_btn_rem_pin", use_container_width=True):
                                    ok, _, _ = db.verify_user_login(username, rem_pin)
                                    if ok:
                                        db.remove_user_pin(user_id)
                                        st.info("PIN disabled.")
                                        st.rerun()
                                    else:
                                        st.error("Incorrect PIN.")

                # 2. Settings Section
                with st.expander("⚙️ Setting", expanded=False):
                    st.markdown(f"• **Typical Cycle Length:** `{current_user['typical_cycle_length']} days`")
                    st.markdown(f"• **Period Duration:** `{current_user['typical_period_length']} days`")
                    st.markdown(f"• **Recorded Cycles:** `{len(user_logs)} logs in database`")
                    st.markdown(f"• **Predictability:** `{health_res['predictability_rating']}`")
                    st.markdown(f"• **Thyroid Status:** `{selected_thyroid}`")
                    st.markdown(f"• **Health Conditions:** `{', '.join(selected_conditions) if selected_conditions else 'None'}`")
                    st.markdown(f"• **Stress Level:** `{selected_stress}`")
                    st.caption("💡 Tip: Use the left sidebar to edit cycle duration, thyroid, or health conditions anytime.")

tracked_note = ""
if (today - start_date).days > 45:
    tracked_note = f" &bull; <i>Calculated from {start_date.strftime('%d %b %Y')} (Cycle #{int(active_cycle['Cycle'])})</i>"

health_chip_html = ""
if health_res["active_factors_summary"]:
    chip_items = "".join(f"<span class='health-chip'>🩺 {f}</span>" for f in health_res["active_factors_summary"])
    health_chip_html = f"<div style='margin-top: 4px; font-size: 8pt;'><b>Active Health Factors:</b> {chip_items}</div>"

st.markdown(f"""
<div class="hero-card">
    <div class="hero-badges">
        <span class="hero-badge {phase_badge}">Current Phase: {phase_name}</span>
        <span class="hero-badge badge-countdown">Next Period: {f'In {days_to_next_period} days' if days_to_next_period > 0 else 'Due today' if days_to_next_period == 0 else 'Overdue'} ({active_cycle['Next period'].strftime('%d %b')})</span>
        <span class="hero-badge {health_res['badge_class']}">Predictability: {health_res['predictability_score']}% ({health_res['predictability_rating']})</span>
    </div>
    {health_chip_html}
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Fixed Bottom Mobile Navigation Bar (Non-movable, Icons only, Text on hover)
# ---------------------------------------------------------
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "📅"

with st.container(key="bottom_nav_bar"):
    nav_c1, nav_c2, nav_c3, nav_c4 = st.columns(4)

    with nav_c1:
        is_sel = st.session_state["active_nav"] in ["📅", "📅 Calendar"]
        if st.button("📅", key="nav_btn_cal", use_container_width=True, help="Calendar", type="primary" if is_sel else "secondary"):
            st.session_state["active_nav"] = "📅"
            st.rerun()

    with nav_c2:
        is_sel = st.session_state["active_nav"] in ["💬", "💬 Chat"]
        if st.button("💬", key="nav_btn_chat", use_container_width=True, help="Chat Assistant", type="primary" if is_sel else "secondary"):
            st.session_state["active_nav"] = "💬"
            st.rerun()

    with nav_c3:
        is_sel = st.session_state["active_nav"] in ["💡", "💡 Insights"]
        if st.button("💡", key="nav_btn_ins", use_container_width=True, help="Insights & Trends", type="primary" if is_sel else "secondary"):
            st.session_state["active_nav"] = "💡"
            st.rerun()

    with nav_c4:
        is_sel = st.session_state["active_nav"] in ["📝", "📝 Symptoms Update"]
        if st.button("📝", key="nav_btn_sym", use_container_width=True, help="Symptoms Update", type="primary" if is_sel else "secondary"):
            st.session_state["active_nav"] = "📝"
            st.rerun()

# =========================================================
# VIEW 1: 📅 Calendar (Flo-Style 3-Month View & Export)
# =========================================================
if st.session_state["active_nav"] in ["📅", "📅 Calendar"]:
    # 1. Build calendar events with ALL user history logs and future cycles
    events = build_calendar_events(
        cycles=cycles,
        user_symptoms=user_symptoms,
        phase_advisories=health_res["phase_advisories"],
        user_logs=user_logs,
        period_length=period_length,
        cycle_length=cycle_length_used
    )

    # Parse date if passed via query params (e.g. from calendar day link click)
    if "cal_date" in st.query_params:
        try:
            q_date = date.fromisoformat(st.query_params["cal_date"])
            st.session_state["cal_selected_date"] = q_date
            st.session_state["cal_center_year"] = q_date.year
            st.session_state["cal_center_month"] = q_date.month
        except (ValueError, TypeError):
            pass
        st.query_params.clear()

    if "cal_center_year" not in st.session_state:
        st.session_state["cal_center_year"] = today.year
    if "cal_center_month" not in st.session_state:
        st.session_state["cal_center_month"] = today.month
    if "cal_selected_date" not in st.session_state:
        st.session_state["cal_selected_date"] = today

    selected_date_cal = st.session_state["cal_selected_date"]
    center_y = int(st.session_state["cal_center_year"])
    center_m = int(st.session_state["cal_center_month"])

    # Year Selector Pills & Quick Month Navigation (2020 to 2035)
    nav_c1, nav_c2 = st.columns([3.5, 1.5])
    with nav_c1:
        years_list = list(range(2020, 2036))
        picked_year = st.pills(
            "Year",
            options=years_list,
            default=center_y if center_y in years_list else today.year,
            selection_mode="single",
            label_visibility="collapsed",
            key="cal_pills_year"
        )
        if picked_year and picked_year != center_y:
            st.session_state["cal_center_year"] = picked_year
            st.rerun()

    with nav_c2:
        with st.container(key="cal_nav_buttons_container"):
            prev_c, today_c, next_c = st.columns([0.8, 1.4, 0.8], gap="small")
            with prev_c:
                if st.button("◀", key="btn_cal_prev", help="Previous Month", use_container_width=True):
                    nm = center_m - 1
                    ny = center_y
                    if nm < 1:
                        nm = 12
                        ny -= 1
                    st.session_state["cal_center_month"] = nm
                    st.session_state["cal_center_year"] = max(years_list[0], ny)
                    st.rerun()
            with today_c:
                if st.button("📍 Today", key="btn_cal_today", help="Jump to Current Month", use_container_width=True):
                    st.session_state["cal_center_year"] = today.year
                    st.session_state["cal_center_month"] = today.month
                    st.session_state["cal_selected_date"] = today
                    st.rerun()
            with next_c:
                if st.button("▶", key="btn_cal_next", help="Next Month", use_container_width=True):
                    nm = center_m + 1
                    ny = center_y
                    if nm > 12:
                        nm = 1
                        ny += 1
                    st.session_state["cal_center_month"] = nm
                    st.session_state["cal_center_year"] = min(years_list[-1], ny)
                    st.rerun()

    # Calculate continuous 3-month window centered on active month
    prev_m = center_m - 1
    prev_y = center_y
    if prev_m < 1:
        prev_m = 12
        prev_y -= 1

    next_m = center_m + 1
    next_y = center_y
    if next_m > 12:
        next_m = 1
        next_y += 1

    scroll_months = [(prev_y, prev_m), (center_y, center_m), (next_y, next_m)]

    # Render months inside a smooth horizontally scrollable container (3 months: Past, Current/Selected, Future)
    month_cards_html = []
    for year, month in scroll_months:
        card_html = calendar_html(year, month, events, selected_date=selected_date_cal)
        is_cur = (year == center_y and month == center_m)
        item_id = "id='cal-current-month'" if is_cur else ""
        month_cards_html.append(f"<div class='calendar-scroll-item' {item_id}>{card_html}</div>")

    combined_scroll_html = f"<div class='calendar-scroll-wrapper' id='cal-scroll-wrapper'>{''.join(month_cards_html)}</div>"
    st.markdown(combined_scroll_html, unsafe_allow_html=True)

    # 3. Interactive Calendar Date Log & Cycle Update (Always shown for selected date)
    st.markdown("<div id='log-update-section' style='padding-top: 14px;'></div>", unsafe_allow_html=True)
    is_period_logged = selected_date_cal in user_logs
    period_marked = False

    with st.container(key="cal_pill_container"):
        date_ctrl_c1, diet_icon_c, date_ctrl_c2 = st.columns([1.1, 0.35, 2.3])
        with date_ctrl_c1:
            with st.container(key="cal_pill_date"):
                with st.popover(f"📅 {selected_date_cal.strftime('%d %b %Y')}", help="Select Date"):
                    st.markdown("<p style='font-size:0.85rem; font-weight:600; margin-bottom:4px; color:#1e293b;'>Select Date:</p>", unsafe_allow_html=True)
                    new_cal_date = st.date_input(
                        "Select Date",
                        value=selected_date_cal,
                        label_visibility="collapsed",
                        key=f"cal_picker_{selected_date_cal.isoformat()}"
                    )
                    if new_cal_date != selected_date_cal:
                        st.session_state["cal_selected_date"] = new_cal_date
                        st.session_state["cal_center_year"] = new_cal_date.year
                        st.session_state["cal_center_month"] = new_cal_date.month
                        st.rerun()

        with diet_icon_c:
            sel_ev = events.get(selected_date_cal, {})
            sel_phase = sel_ev.get("phase", phase_name)
            render_diet_notif_popover(sel_phase, "Diet", container_key="diet_notif_sel")

        with date_ctrl_c2:
            if is_period_logged:
                p_col1, p_col2 = st.columns([2, 1.2])
                with p_col1:
                    st.markdown("<div style='background: #fee2e2; border: 1px solid #fca5a5; color: #991b1b; padding: 4px 10px; border-radius: 8px; font-size: 0.82rem; font-weight: 600; display: inline-flex; align-items: center;'>🩸 Period Start Logged (Day 1)</div>", unsafe_allow_html=True)
                with p_col2:
                    if st.button("❌ Remove Marker", key=f"btn_del_period_{selected_date_cal.isoformat()}", use_container_width=True):
                        db.delete_cycle_log(user_id, selected_date_cal)
                        st.success(f"Period start marker removed for {selected_date_cal.strftime('%d %b %Y')}")
                        st.rerun()
                period_marked = True
            else:
                period_marked = st.checkbox(
                    "🩸 Mark this date as Period Start Date (Day 1)",
                    value=False,
                    key=f"chk_period_start_{selected_date_cal.isoformat()}",
                    help="Check this box if your bleeding started on this date to update cycle predictions."
                )

    # Directly show the log update tiles (Flow, Energy, Mood, Physical Symptoms, Reflections)
    existing_sym = user_symptoms.get(selected_date_cal, {})
    cal_date_str = selected_date_cal.isoformat()
    
    flow_choices = ["None", "Spotting", "Light", "Medium", "Heavy"]
    def_flow = existing_sym.get("flow", "None")
    f_default = def_flow if def_flow in flow_choices else "None"
    
    energy_choices = ["High ⚡", "Moderate 🌿", "Low / Fatigued 😴"]
    def_energy = existing_sym.get("energy", "Moderate 🌿")
    e_default = def_energy if def_energy in energy_choices else "Moderate 🌿"
    
    all_mood_choices = ["Happy 😊", "Calm 🧘", "Energetic ⚡", "Confident ✨", "Sensitive 🥺", "Irritable 😤", "Anxious 😟", "Brain Fog 🌫️", "Low Mood 🌧️"]
    raw_m = existing_sym.get("mood", "")
    def_moods = [m.strip() for m in raw_m.split(",") if m.strip() and m.strip() in all_mood_choices]
    
    all_sym_choices = ["Cramps 💥", "Bloating 🎈", "Headache 🤕", "Tender Breasts 🌸", "Acne 💧", "Lower Back Pain 🦴", "Cravings 🍫", "Insomnia 🌙"]
    raw_s = existing_sym.get("symptoms", "")
    def_syms = [s.strip() for s in raw_s.split(",") if s.strip() in all_sym_choices]

    st.markdown("<p style='font-size:0.88rem; font-weight:600; margin-top:8px; margin-bottom:2px; color:#334155;'>🩸 Flow Intensity</p>", unsafe_allow_html=True)
    q_flow_sel = st.pills("Flow Intensity", flow_choices, default=f_default, selection_mode="single", label_visibility="collapsed", key=f"quick_flow_{cal_date_str}")
    q_flow = q_flow_sel or "None"

    st.markdown("<p style='font-size:0.88rem; font-weight:600; margin-top:8px; margin-bottom:2px; color:#334155;'>⚡ Energy Level</p>", unsafe_allow_html=True)
    q_energy_sel = st.pills("Energy Level", energy_choices, default=e_default, selection_mode="single", label_visibility="collapsed", key=f"quick_energy_{cal_date_str}")
    q_energy = q_energy_sel or "Moderate 🌿"

    st.markdown("<p style='font-size:0.88rem; font-weight:600; margin-top:8px; margin-bottom:2px; color:#334155;'>🧘 Mood & Emotions (Select all that apply)</p>", unsafe_allow_html=True)
    q_mood = st.pills("Mood & Emotions", all_mood_choices, default=def_moods, selection_mode="multi", label_visibility="collapsed", key=f"quick_mood_{cal_date_str}") or []

    st.markdown("<p style='font-size:0.88rem; font-weight:600; margin-top:8px; margin-bottom:2px; color:#334155;'>🌸 Physical Symptoms (Select all that apply)</p>", unsafe_allow_html=True)
    q_syms = st.pills("Physical Symptoms", all_sym_choices, default=def_syms, selection_mode="multi", label_visibility="collapsed", key=f"quick_syms_{cal_date_str}") or []

    q_notes = st.text_area("Personal Notes & Self-Care Reflections", value=existing_sym.get("notes", ""), placeholder="E.g., chamomile tea helped cramps, slept 8 hours...", key=f"quick_notes_{cal_date_str}")
    
    with st.container(key="log_action_buttons"):
        if existing_sym:
            s_c1, s_c2, _ = st.columns([1, 1, 3])
            with s_c1:
                if st.button("💾 Save Log", type="primary", use_container_width=True, key=f"btn_quick_save_sym_{cal_date_str}"):
                    mood_str = ", ".join(q_mood)
                    sym_str = ", ".join(q_syms)
                    db.save_daily_symptom(user_id, selected_date_cal, q_flow, mood_str, sym_str, q_energy, q_notes)
                    if not is_period_logged and period_marked:
                        db.add_cycle_log(user_id, selected_date_cal, "Logged via calendar")
                    st.success(f"✅ Daily log saved for {selected_date_cal.strftime('%d %B %Y')}!")
                    st.rerun()
            with s_c2:
                if st.button("🗑️ Delete Entry", key=f"btn_quick_del_sym_{cal_date_str}", use_container_width=True):
                    db.delete_daily_symptom(user_id, selected_date_cal)
                    st.info(f"Deleted daily log for {selected_date_cal.strftime('%d %b %Y')}")
                    st.rerun()
        else:
            s_c1, _ = st.columns([1, 4])
            with s_c1:
                if st.button("💾 Save Log", type="primary", use_container_width=True, key=f"btn_quick_save_sym_{cal_date_str}"):
                    mood_str = ", ".join(q_mood)
                    sym_str = ", ".join(q_syms)
                    db.save_daily_symptom(user_id, selected_date_cal, q_flow, mood_str, sym_str, q_energy, q_notes)
                    if not is_period_logged and period_marked:
                        db.add_cycle_log(user_id, selected_date_cal, "Logged via calendar")
                    st.success(f"✅ Daily log saved for {selected_date_cal.strftime('%d %B %Y')}!")
                    st.rerun()

    # Phase Diet & Nutrition Suggestions (tailored to active phase: Fertility, Ovulation, Period, or Luteal/PMS)
    sel_event = events.get(selected_date_cal, {})
    sel_phase_title = sel_event.get("phase", phase_name)
    diet_info = health_engine.get_diet_suggestions(sel_phase_title)
    
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    with st.expander(f"🥗 Phase Diet & Nutrition Suggestions &bull; {diet_info['name']}", expanded=False):
        st.markdown(f"**Focus:** *{diet_info['tagline']}*")
        st.caption(diet_info["biology"])
        
        diet_c1, diet_c2 = st.columns(2)
        with diet_c1:
            st.markdown("##### 🌟 Recommended Superfoods")
            for sf_title, sf_desc in diet_info["superfoods"]:
                st.markdown(f"**{sf_title}**")
                st.caption(sf_desc)
        with diet_c2:
            st.markdown("##### 🚫 Foods to Minimize")
            for f_bad in diet_info["foods_to_avoid"]:
                st.markdown(f"• {f_bad}")
            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
            st.markdown("##### 🍽️ Sample Meal Inspiration")
            for meal_name, meal_desc in diet_info["sample_meals"].items():
                st.markdown(f"• **{meal_name}:** {meal_desc}")

    # Personalized Calendar Sync with Custom Events & Custom Names
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    with st.expander("📲 Sync to Phone Calendar (Custom Event Selection & Private Names)", expanded=False):
        st.write("Select which events to sync and customize their names for personal privacy (e.g. use **'🌸 Rest Time'** instead of *'Period'*):")
        
        sync_c1, sync_c2 = st.columns(2)
        with sync_c1:
            sync_period = st.checkbox("🩸 Bleeding / Period Dates", value=True, key="sync_chk_period")
            custom_period_label = st.text_input(
                "Custom Name for Bleeding Dates",
                value="🌸 Rest Time",
                key="sync_lbl_period",
                help="E.g. 'Rest Time', 'Self-Care Days', 'Moon Time'"
            )
            
            sync_ovulation = st.checkbox("🟣 Ovulation Peak Day", value=True, key="sync_chk_ov")
            custom_ovulation_label = st.text_input(
                "Custom Name for Ovulation Peak",
                value="🟣 Ovulation Peak",
                key="sync_lbl_ov",
                help="E.g. 'Ovulation Day', 'Energy Peak'"
            )

        with sync_c2:
            sync_fertile = st.checkbox("🌱 High Fertility Window", value=True, key="sync_chk_fertile")
            custom_fertile_label = st.text_input(
                "Custom Name for Fertile Window",
                value="🌱 High Fertility Window",
                key="sync_lbl_fertile",
                help="E.g. 'Conception Window', 'Vitality Window'"
            )
            
            sync_pms = st.checkbox("✨ Pre-Menstrual (PMS) Window", value=False, key="sync_chk_pms")
            custom_pms_label = st.text_input(
                "Custom Name for PMS Window",
                value="✨ Cozy Care Window",
                key="sync_lbl_pms",
                help="E.g. 'Gentle Care Days', 'Rest & Relax'"
            )

        custom_ics_content = generate_ics(
            cycles=cycles,
            username=username,
            include_period=sync_period,
            period_label=custom_period_label,
            include_ovulation=sync_ovulation,
            ovulation_label=custom_ovulation_label,
            include_fertile=sync_fertile,
            fertile_label=custom_fertile_label,
            include_pms=sync_pms,
            pms_label=custom_pms_label
        )
        
        st.download_button(
            label="📅 Download Customized Calendar (.ics)",
            data=custom_ics_content,
            file_name=f"Relax_Sync_{username}.ics",
            mime="text/calendar",
            type="primary",
            use_container_width=True
        )
        st.caption("Compatible with Apple Calendar (iPhone/Mac), Google Calendar (Android), and Microsoft Outlook.")

# =========================================================
# VIEW 2: 💬 Chat (AI Cycle & Menstrual Wellness Assistant)
# =========================================================
elif st.session_state["active_nav"] in ["💬", "💬 Chat"]:
    st.markdown("### 💬 Relax Wellness & Cycle Assistant")
    st.caption("Your personalized cycle guide for phase nutrition, natural symptom relief, thyroid/stress effects, and countdown forecasts.")

    chat_ctx = {
        "username": username,
        "phase_name": phase_name,
        "cycle_day": cycle_day,
        "days_to_next_period": days_to_next_period,
        "next_period_str": active_cycle["Next period"].strftime("%d %B %Y"),
        "cycle_length_used": cycle_length_used,
        "period_length": period_length,
        "fertile_str": f"{active_cycle_dates['fertile_start'].strftime('%d %b')} – {active_cycle_dates['fertile_end'].strftime('%d %b')}",
        "ovulation_str": active_cycle_dates['ovulation'].strftime('%d %b %Y'),
        "health_factors": health_res["active_factors_summary"],
        "care_tips": health_res["care_tips"],
        "insights": health_res["insights"],
        "predictability_score": health_res["predictability_score"]
    }

    session_chat_key = f"chat_history_{user_id}"
    if session_chat_key not in st.session_state:
        st.session_state[session_chat_key] = [
            {
                "role": "assistant",
                "content": f"Hello {username}! 🌸 I'm your Relax Cycle & Wellness Assistant.\n\nToday you are on **Cycle Day {cycle_day}** in your **{phase_name}**. How can I support your wellbeing today? You can choose a quick topic below or type your question!"
            }
        ]

    st.markdown("##### 💡 Suggested Questions:")
    chip_cols = st.columns(5)
    chip_items = [
        ("🥗 Foods for My Phase", f"What should I eat during my current phase ({phase_name})?"),
        ("🩸 Next Period Forecast", "When is my next period expected and what should I expect?"),
        ("💥 Relief for Cramps", "How can I naturally ease cramps, back pain, and bloating?"),
        ("🦋 Thyroid & Hormones", "How does my thyroid condition or stress level affect my cycle length?"),
        ("🌱 Fertile & Ovulation", "When is my fertile window and what are signs of ovulation?")
    ]
    
    queued_prompt = None
    for idx, (chip_title, chip_query) in enumerate(chip_items):
        with chip_cols[idx]:
            if st.button(chip_title, key=f"chip_btn_{idx}", use_container_width=True):
                queued_prompt = chip_query

    # Display chat message history
    for msg in st.session_state[session_chat_key]:
        with st.chat_message(msg["role"], avatar="🌸" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Ask Relax anything about your cycle, cramps, nutrition, or hormones...")
    prompt_to_process = queued_prompt or user_input

    if prompt_to_process:
        st.session_state[session_chat_key].append({"role": "user", "content": prompt_to_process})
        reply = chat_assistant.generate_chat_reply(prompt_to_process, chat_ctx)
        st.session_state[session_chat_key].append({"role": "assistant", "content": reply})
        st.rerun()

# =========================================================
# VIEW 3: 💡 Insights (Trends Chart, Health Protocol & Forecast)
# =========================================================
elif st.session_state["active_nav"] in ["💡", "💡 Insights"]:
    st.markdown("### 💡 Cycle Insights & Health Protocols")
    st.caption("Visualizing your cycle duration trends, biological health protocol, and complete forecast schedule.")

    # 1. Trend & Projection Chart
    st.subheader("📈 Cycle Trend & Period Projection")
    st.caption("Visualizing your average cycle benchmark, actual happened periods, and future expected dates.")
    
    hist_x = []
    hist_y = []
    hist_hover = []
    
    if len(user_logs) >= 2:
        for i in range(1, len(user_logs)):
            prev_d = user_logs[i-1]
            curr_d = user_logs[i]
            dur = (curr_d - prev_d).days
            diff = dur - cycle_length_used
            diff_str = f"+{diff}d" if diff > 0 else (f"{diff}d" if diff < 0 else "on target")
            
            x_label = f"{curr_d.strftime('%d %b %Y')}<br><b>(Happened)</b>"
            hist_x.append(x_label)
            hist_y.append(dur)
            hist_hover.append(
                f"<b>🩸 Confirmed Period (Happened)</b><br>"
                f"• <b>Happened Date:</b> {curr_d.strftime('%a, %d %b %Y')}<br>"
                f"• <b>Cycle Started:</b> {prev_d.strftime('%a, %d %b %Y')}<br>"
                f"• <b>Actual Cycle Duration:</b> {dur} days<br>"
                f"• <b>Baseline Average:</b> {cycle_length_used} days ({diff_str})<br>"
                f"• <i>Logged in cycle history</i>"
            )

    fut_x = []
    fut_y = []
    fut_hover = []
    
    for _, r in cycles.head(12).iterrows():
        p_date = r["Next period"]
        dur = (p_date - r["Start"]).days
        w_note = r.get("Expected Window (± Margin)", "Regular")
        diff = dur - cycle_length_used
        diff_str = f"+{diff}d" if diff > 0 else (f"{diff}d" if diff < 0 else "on target")
        
        x_label = f"{p_date.strftime('%d %b %Y')}<br><b>(Expected)</b>"
        fut_x.append(x_label)
        fut_y.append(dur)
        fut_hover.append(
            f"<b>🔮 Forecasted Cycle #{int(r['Cycle'])} (Expected)</b><br>"
            f"• <b>Expected Period Date:</b> {p_date.strftime('%a, %d %b %Y')}<br>"
            f"• <b>Fluctuation Window:</b> {w_note}<br>"
            f"• <b>Cycle Starts:</b> {r['Start'].strftime('%a, %d %b %Y')}<br>"
            f"• <b>Projected Cycle Length:</b> {dur} days<br>"
            f"• <b>Average Benchmark:</b> {cycle_length_used} days ({diff_str})<br>"
            f"• <b>Predictability:</b> {health_res['predictability_score']}% ({health_res['predictability_rating']})"
        )

    all_x = hist_x + fut_x
    all_y = hist_y + fut_y
    if not all_y:
        all_y = [cycle_length_used]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=all_x,
        y=[cycle_length_used] * len(all_x),
        mode="lines",
        name=f"Average Length ({cycle_length_used}d)",
        line=dict(color="#64748b", width=2, dash="dash"),
        hoverinfo="text",
        hovertext=[f"<b>Average Cycle Length:</b> {cycle_length_used} days<br><i>Derived from: {regularity_msg}</i>"] * len(all_x)
    ))

    if hist_x:
        fig.add_trace(go.Scatter(
            x=hist_x,
            y=hist_y,
            mode="lines+markers",
            name="Happened Period (Logged)",
            line=dict(color="#be185d", width=3),
            marker=dict(size=11, color="#be185d", symbol="circle", line=dict(color="#ffffff", width=2)),
            hoverinfo="text",
            hovertext=hist_hover
        ))

    if hist_x and fut_x:
        fig.add_trace(go.Scatter(
            x=[hist_x[-1], fut_x[0]],
            y=[hist_y[-1], fut_y[0]],
            mode="lines",
            name="Transition",
            showlegend=False,
            line=dict(color="#c084fc", width=2, dash="dot"),
            hoverinfo="skip"
        ))

    if fut_x:
        fig.add_trace(go.Scatter(
            x=fut_x,
            y=fut_y,
            mode="lines+markers",
            name="Expected Period (Forecast)",
            line=dict(color="#9333ea", width=2.5, dash="dash"),
            marker=dict(size=10, color="#9333ea", symbol="diamond", line=dict(color="#ffffff", width=2)),
            hoverinfo="text",
            hovertext=fut_hover
        ))

    y_min = max(18, min(all_y + [cycle_length_used]) - 4)
    y_max = min(50, max(all_y + [cycle_length_used]) + 5)

    fig.update_layout(
        height=320,
        xaxis_title="Cycle Timeline (Happened Period Dates → Expected Period Dates)",
        yaxis_title="Cycle Length (Days)",
        yaxis=dict(range=[y_min, y_max], dtick=2),
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="sans-serif")
    )
    st.plotly_chart(fig, width="stretch")

    latest_happened = user_logs[-1].strftime('%d %b %Y') if user_logs else start_date.strftime('%d %b %Y')
    next_expected = active_cycle['Next period'].strftime('%d %b %Y')
    st.caption(
        f"📊 **Average Length:** `{cycle_length_used} days` ({regularity_msg}) &nbsp;|&nbsp; "
        f"🩸 **Latest Happened Date:** `{latest_happened}` &nbsp;|&nbsp; "
        f"🔮 **Next Expected Date:** `{next_expected}` (Window: `{active_window_str}`)"
    )

    # 2. Biological Health & Nutrition Protocol Expander
    st.markdown("---")
    st.subheader("🩺 Biological Health & Nutrition Protocol")
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.markdown("#### 🧬 Endocrine & Health Insights")
        for ins in health_res["insights"]:
            st.markdown(f"**{ins['title']}**")
            st.write(ins["mechanism"])
            st.caption(f"📌 *Clinical Impact:* {ins['impact']}")
            st.markdown("---")
            
    with c_col2:
        st.markdown("#### 🥗 Personalized Nutrition & Self-Care Protocol")
        for tip in health_res["care_tips"]:
            st.info(f"💡 {tip}")
        
        if health_res["period_shift"] > 0:
            st.warning(f"🩸 **Bleeding Duration Advisory:** Your health profile suggests periods may run ~{health_res['period_shift']} day(s) longer with heavier flow. Prioritize iron-rich foods, vitamin C, and restful recovery.")
        elif health_res["period_shift"] < 0:
            st.warning(f"🩸 **Bleeding Duration Advisory:** Your health profile indicates a tendency toward lighter or shorter bleeding (-{abs(health_res['period_shift'])} day).")

    # 2b. Interactive Cycle-Synced Diet & Nutrition Guide
    st.markdown("---")
    st.subheader("🥗 Cycle-Synced Diet & Nutrition Guide")
    st.caption("Personalized nourishment strategies tailored to your metabolic shifts during menstruation, fertility, ovulation, and PMS.")
    
    all_diet_protocols = health_engine.get_all_cycle_diet_guides()
    phase_keys = ["menstrual", "follicular", "ovulation", "luteal"]
    phase_labels = {
        "menstrual": "🩸 Period (Menstrual)",
        "follicular": "🌱 Follicular & Fertility",
        "ovulation": "🟣 Ovulation Peak Day",
        "luteal": "✨ Luteal Phase (PMS)"
    }
    
    diet_tabs = st.tabs([phase_labels[k] for k in phase_keys])
    for idx, p_key in enumerate(phase_keys):
        with diet_tabs[idx]:
            p_diet = all_diet_protocols[p_key]
            st.markdown(f"#### {p_diet['name']}")
            st.markdown(f"*{p_diet['tagline']}*")
            st.info(f"🧬 **Biological Rationale:** {p_diet['biology']}")
            
            img_c, info_c1, info_c2 = st.columns([1.1, 1.3, 1.3])
            with img_c:
                img_path = f"assets/{p_key}_diet.jpg"
                if os.path.exists(img_path):
                    st.image(img_path, caption=f"🍽️ {p_diet['name']} Superfood Plate", use_container_width=True)
            with info_c1:
                st.markdown("##### 🌟 Recommended Superfoods")
                for s_title, s_desc in p_diet["superfoods"]:
                    st.markdown(f"**{s_title}**")
                    st.caption(s_desc)
            with info_c2:
                st.markdown("##### 🚫 Foods to Minimize")
                for avoid_item in p_diet["foods_to_avoid"]:
                    st.markdown(f"• {avoid_item}")
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                st.markdown("##### 🍽️ Daily Meal Blueprint")
                for m_t, m_d in p_diet["sample_meals"].items():
                    st.markdown(f"• **{m_t}:** {m_d}")

    # 3. Forecast Table
    st.markdown("---")
    tbl_h_col, tbl_f_col = st.columns([3, 1])
    with tbl_h_col:
        st.subheader("🗓️ Complete Cycle Forecast Table")
        st.caption("🔴 **Past dates** &nbsp;|&nbsp; 🟡 **Today** &nbsp;|&nbsp; 🟢 **Future forecast**")
    with tbl_f_col:
        if len(cycles) > 7:
            table_filter = st.selectbox("Show Cycles", ["Current & Upcoming (Next 12 Cycles)", f"Next 2 Years ({len(cycles)} Cycles total)"])
        else:
            table_filter = "All Cycles"

    if "Next 12" in table_filter:
        active_idx = int(active_cycle["Cycle"])
        display_df = cycles[cycles["Cycle"] >= active_idx].head(12).copy()
    elif "Next 2 Years" in table_filter:
        active_idx = int(active_cycle["Cycle"])
        display_df = cycles[cycles["Cycle"] >= active_idx].copy()
    else:
        display_df = cycles.copy()

    clean_cols = [c for c in display_df.columns if c not in ["is_current", "Status"]]
    display_df = display_df[clean_cols]

    def style_cell(val):
        if isinstance(val, date):
            if val < today:
                return "background-color: #fee2e2; color: #991b1b; font-weight: 500;"
            elif val == today:
                return "background-color: #fef3c7; color: #92400e; font-weight: 600;"
            else:
                return "background-color: #dcfce7; color: #166534;"
        return ""

    date_cols = ["Start", "Bleeding end", "Ovulation estimate", "Next period"]
    format_dict = {col: lambda d: d.strftime("%d %b %Y") for col in date_cols if col in display_df.columns}

    styler = display_df.style.map(style_cell).format(format_dict)
    st.dataframe(styler, width="stretch", hide_index=True)

# =========================================================
# VIEW 4: 📝 Symptoms Update (Daily Logger & History)
# =========================================================
elif st.session_state["active_nav"] in ["📝", "📝 Symptoms Update"]:
    st.markdown("### 📝 Daily Symptoms, Mood & Health Update")
    st.caption(f"Log your daily cues for **{username}** to track physical patterns, energy shifts, and emotions across your cycle.")

    sym_form_col, sym_hist_col = st.columns([1.2, 1])

    with sym_form_col:
        st.markdown("#### ✍️ Log Symptoms for a Date")
        v4_d_col, v4_diet_col = st.columns([1.5, 0.35])
        with v4_d_col:
            log_date = st.date_input("Select Date", value=today, max_value=today + timedelta(days=7), key="symptom_log_date")
        with v4_diet_col:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            v4_ev = events.get(log_date, {})
            v4_phase = v4_ev.get("phase", phase_name)
            render_diet_notif_popover(v4_phase, "Diet", container_key="diet_notif_sym")
        
        existing_v4 = user_symptoms.get(log_date, {})
        v4_str = log_date.isoformat()

        flow_choices = ["None", "Spotting", "Light", "Medium", "Heavy"]
        def_v4_flow = existing_v4.get("flow", "None")
        v4_flow_default = def_v4_flow if def_v4_flow in flow_choices else "None"

        energy_choices = ["High ⚡", "Moderate 🌿", "Low / Fatigued 😴"]
        def_v4_energy = existing_v4.get("energy", "Moderate 🌿")
        v4_energy_default = def_v4_energy if def_v4_energy in energy_choices else "Moderate 🌿"

        all_mood_choices = ["Happy 😊", "Calm 🧘", "Energetic ⚡", "Confident ✨", "Sensitive 🥺", "Irritable 😤", "Anxious 😟", "Brain Fog 🌫️", "Low Mood 🌧️"]
        raw_v4_m = existing_v4.get("mood", "")
        def_v4_moods = [m.strip() for m in raw_v4_m.split(",") if m.strip() and m.strip() in all_mood_choices]

        all_symptom_choices = ["Cramps 💥", "Bloating 🎈", "Headache 🤕", "Tender Breasts 🌸", "Acne 💧", "Lower Back Pain 🦴", "Cravings 🍫", "Insomnia 🌙"]
        raw_v4_s = existing_v4.get("symptoms", "")
        def_v4_syms = [s.strip() for s in raw_v4_s.split(",") if s.strip() in all_symptom_choices]

        st.markdown("<p style='font-size:0.88rem; font-weight:600; margin-top:8px; margin-bottom:2px; color:#334155;'>🩸 Flow Intensity</p>", unsafe_allow_html=True)
        flow_option_sel = st.pills("Flow Intensity", flow_choices, default=v4_flow_default, selection_mode="single", label_visibility="collapsed", key=f"sym_flow_{v4_str}")
        flow_option = flow_option_sel or "None"

        st.markdown("<p style='font-size:0.88rem; font-weight:600; margin-top:8px; margin-bottom:2px; color:#334155;'>⚡ Energy Level</p>", unsafe_allow_html=True)
        energy_option_sel = st.pills("Energy Level", energy_choices, default=v4_energy_default, selection_mode="single", label_visibility="collapsed", key=f"sym_energy_{v4_str}")
        energy_option = energy_option_sel or "Moderate 🌿"

        st.markdown("<p style='font-size:0.88rem; font-weight:600; margin-top:8px; margin-bottom:2px; color:#334155;'>🧘 Mood & Emotions (Select all that apply)</p>", unsafe_allow_html=True)
        mood_options = st.pills("Mood & Emotions", all_mood_choices, default=def_v4_moods, selection_mode="multi", label_visibility="collapsed", key=f"sym_mood_{v4_str}") or []

        st.markdown("<p style='font-size:0.88rem; font-weight:600; margin-top:8px; margin-bottom:2px; color:#334155;'>🌸 Physical Symptoms (Select all that apply)</p>", unsafe_allow_html=True)
        symptom_options = st.pills("Physical Symptoms", all_symptom_choices, default=def_v4_syms, selection_mode="multi", label_visibility="collapsed", key=f"sym_phys_{v4_str}") or []

        note_text = st.text_area("Personal Notes & Self-Care Reflections", value=existing_v4.get("notes", ""), placeholder="E.g., chamomile tea helped cramps, slept 8 hours...", key=f"sym_notes_{v4_str}")
        
        if st.button("💾 Save Daily Log", type="primary", use_container_width=True, key="btn_save_sym"):
            mood_str = ", ".join(mood_options)
            symptom_str = ", ".join(symptom_options)
            db.save_daily_symptom(user_id, log_date, flow_option, mood_str, symptom_str, energy_option, note_text)
            st.success(f"✅ Daily log saved for {log_date.strftime('%d %B %Y')}!")
            st.rerun()

    with sym_hist_col:
        st.markdown("#### 📋 Logged Symptoms History")
        if not user_symptoms:
            st.info("No symptoms logged yet. Use the form on the left to record your daily flow, mood, and symptoms!")
        else:
            sorted_dates = sorted(user_symptoms.keys(), reverse=True)
            st.caption(f"Showing **{len(sorted_dates)}** recorded log entries:")
            for s_date in sorted_dates:
                s_data = user_symptoms[s_date]
                flow_badge = f"🩸 {s_data.get('flow', 'None')}" if s_data.get('flow', 'None') != 'None' else "✨ No Flow"
                energy_val = s_data.get('energy', 'Moderate')
                mood_val = s_data.get('mood', '') or 'None noted'
                sym_val = s_data.get('symptoms', '') or 'None noted'
                note_val = s_data.get('notes', '')
                
                with st.expander(f"📅 {s_date.strftime('%a, %d %b %Y')} &bull; {flow_badge}", expanded=False):
                    st.write(f"**Energy:** {energy_val}")
                    st.write(f"**Mood:** {mood_val}")
                    st.write(f"**Physical Symptoms:** {sym_val}")
                    if note_val:
                        st.write(f"**Notes:** *{note_val}*")
                    if st.button(f"🗑️ Delete Entry ({s_date.strftime('%d %b')})", key=f"del_sym_{s_date.isoformat()}"):
                        db.delete_daily_symptom(user_id, s_date)
                        st.success(f"Deleted entry for {s_date.strftime('%d %b %Y')}")
                        st.rerun()

# ---------------------------------------------------------
# Database Management, Data Portability & Cloud Sync
# ---------------------------------------------------------
st.markdown("---")
st.subheader("💾 My Database & Data Backups")
st.caption(f"All cycle history, personal health conditions, and daily symptoms for **{username}** are persistently saved in the database.")

db_stats = db.get_database_stats()
db_col1, db_col2, db_col3, db_col4 = st.columns(4)
db_col1.metric("Database File", db_stats["database_file"], help="Persistent SQLite database file stored on disk.")
db_col2.metric("Cycles Saved", f"{len(user_logs)} cycles", help="Number of period start dates saved in database for this account.")
db_col3.metric("Symptoms Logged", f"{len(user_symptoms)} records", help="Daily symptoms, moods, and energy logs saved in database.")
db_col4.metric("Database Status", "Connected 🟢", help="All changes auto-save automatically in real-time.")

with st.expander("📦 Data Portability: Download Backup or Restore Data", expanded=False):
    exp_col, imp_col = st.columns(2)
    with exp_col:
        st.markdown("#### 📥 Export My Complete Health Record")
        st.write("Download all your historical cycle dates, daily symptoms, moods, and health conditions as a JSON file.")
        user_backup = db.export_user_data(user_id)
        backup_json_str = json.dumps(user_backup, indent=2)
        st.download_button(
            label="💾 Download Backup (.json)",
            data=backup_json_str,
            file_name=f"Relax_Backup_{username}_{date.today().strftime('%Y%m%d')}.json",
            mime="application/json",
            type="primary"
        )
        st.caption("You can save this file as a personal backup or import it onto another computer.")

    with imp_col:
        st.markdown("#### 📤 Restore / Import Backup")
        st.write("Upload a previously downloaded Relax backup file to restore all your cycles and symptom records.")
        uploaded_backup = st.file_uploader("Choose Relax backup JSON file", type=["json"], key="backup_uploader")
        if uploaded_backup is not None:
            try:
                backup_data = json.load(uploaded_backup)
                if st.button("🔄 Confirm & Import to Database"):
                    success, msg = db.import_user_data(user_id, backup_data)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            except Exception as e:
                st.error(f"Error reading backup file: {e}")

with st.expander("🔒 Account Privacy & Security PIN", expanded=False):
    pin_col1, pin_col2 = st.columns(2)
    with pin_col1:
        st.write("Set or update a 4-digit PIN / password to lock your account on this device so nobody else can view your personal cycle and symptom logs.")
        new_pin_input = st.text_input("New PIN / Password", type="password", key="new_pin_field", placeholder="e.g. 1234")
        if st.button("🔒 Save Security PIN"):
            if new_pin_input.strip():
                db.set_user_pin(user_id, new_pin_input.strip())
                st.success("Security PIN saved! Your profile is now locked.")
                st.rerun()
            else:
                st.warning("Please enter a valid PIN.")
    with pin_col2:
        if user_has_pin:
            st.info(f"✅ Account **{username}** is protected by a PIN.")
            if st.button("🔓 Remove PIN Lock"):
                db.set_user_pin(user_id, "")
                st.success("PIN lock removed.")
                st.rerun()
        else:
            st.caption("No PIN currently set. Your account can be accessed directly from the profile selector.")

with st.expander("🌐 Cloud Database Deployment Guide (PostgreSQL / Supabase)", expanded=False):
    st.markdown("""
    #### How to Deploy Relax with a Permanent Cloud Database:
    When hosting Relax on **Streamlit Community Cloud** or any cloud container:
    1. **Local SQLite (`relax.db`)** works great locally on your computer.
    2. For a cloud deployment shared across multiple phones, you can link a **free PostgreSQL database** (such as [Supabase](https://supabase.com) or [Neon](https://neon.tech)):
       - Create a free project on Supabase or Neon.
       - Copy your database connection string: `postgresql://user:password@host/dbname`.
       - In Streamlit Cloud, add it under **Settings > Secrets**:
         ```toml
         DATABASE_URL = "postgresql://user:password@host:5432/postgres"
         ```
       - Relax will automatically persist all user accounts in the cloud without local ephemeral file wipes!
    """)

# ---------------------------------------------------------
# Health Note & Disclaimer
# ---------------------------------------------------------
st.warning(
    "⚕️ **Health Disclaimer:** Ovulation and cycle timing can fluctuate due to stress, illness, sleep, and lifestyle. "
    "Relax provides educational estimates based on calendar algorithms and should not be used as a medical diagnosis or contraceptive method."
)
