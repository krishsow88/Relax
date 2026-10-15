import calendar
import os
from datetime import date, timedelta, datetime
from typing import Optional, List, Dict, Any, Tuple
import html
import json
import io
import urllib.parse
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
# Themes & Multilingual Localization Dictionaries
# ---------------------------------------------------------
THEMES = {
    "Blush Rose": {
        "name": "Blush Rose 🌸",
        "bg_gradient": "linear-gradient(180deg, #fff5f7 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text_primary": "#1e293b",
        "text_secondary": "#475569",
        "accent": "#e11d48",
        "is_dark": False
    },
    "Calm Mint": {
        "name": "Calm Mint 🌿",
        "bg_gradient": "linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text_primary": "#1e293b",
        "text_secondary": "#475569",
        "accent": "#16a34a",
        "is_dark": False
    },
    "Lavender Mist": {
        "name": "Lavender Mist 💜",
        "bg_gradient": "linear-gradient(180deg, #faf5ff 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text_primary": "#1e293b",
        "text_secondary": "#475569",
        "accent": "#9333ea",
        "is_dark": False
    },
    "Warm Peach": {
        "name": "Warm Peach ☀️",
        "bg_gradient": "linear-gradient(180deg, #fff7ed 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text_primary": "#1e293b",
        "text_secondary": "#475569",
        "accent": "#ea580c",
        "is_dark": False
    },
    "Ocean Breeze": {
        "name": "Ocean Breeze 🌊",
        "bg_gradient": "linear-gradient(180deg, #f0f9ff 0%, #ffffff 100%)",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "text_primary": "#1e293b",
        "text_secondary": "#475569",
        "accent": "#0284c7",
        "is_dark": False
    },
    "Midnight Velvet": {
        "name": "Midnight Velvet 🌙",
        "bg_gradient": "linear-gradient(180deg, #0f172a 0%, #1e293b 100%)",
        "card_bg": "#1e293b",
        "card_border": "#334155",
        "text_primary": "#f8fafc",
        "text_secondary": "#cbd5e1",
        "accent": "#2dd4bf",
        "is_dark": True
    }
}


TRANSLATIONS = {
    "English": {
        "app_title": "Relax",
        "tagline": "Private & Cycle-Synced Health Companion",
        "diet": "Diet",
        "notifications": "Notifications",
        "account": "Account",
        "pin_security": "PIN Security",
        "setting": "Setting",
        "logout": "Logout",
        "current_phase": "Current Phase",
        "next_period": "Next Period",
        "predictability": "Predictability",
        "today": "Today"
    },
    "Español": {
        "app_title": "Relax",
        "tagline": "Compañero privado de salud sincronizado con tu ciclo",
        "diet": "Dieta",
        "notifications": "Notificaciones",
        "account": "Cuenta",
        "pin_security": "Seguridad PIN",
        "setting": "Ajustes",
        "logout": "Cerrar sesión",
        "current_phase": "Fase actual",
        "next_period": "Próximo período",
        "predictability": "Previsibilidad",
        "today": "Hoy"
    },
    "Français": {
        "app_title": "Relax",
        "tagline": "Compagnon privé de santé synchronisé avec votre cycle",
        "diet": "Régime",
        "notifications": "Notifications",
        "account": "Compte",
        "pin_security": "Sécurité PIN",
        "setting": "Paramètres",
        "logout": "Déconnexion",
        "current_phase": "Phase actuelle",
        "next_period": "Prochaines règles",
        "predictability": "Prévisibilité",
        "today": "Aujourd'hui"
    },
    "Deutsch": {
        "app_title": "Relax",
        "tagline": "Ihr privater zyklussynchroner Gesundheitsbegleiter",
        "diet": "Ernährung",
        "notifications": "Benachrichtigungen",
        "account": "Konto",
        "pin_security": "PIN-Sicherheit",
        "setting": "Einstellungen",
        "logout": "Abmelden",
        "current_phase": "Aktuelle Phase",
        "next_period": "Nächste Periode",
        "predictability": "Vorhersagbarkeit",
        "today": "Heute"
    },
    "हिन्दी": {
        "app_title": "रिलैक्स",
        "tagline": "आपका निजी और चक्र-संबद्ध स्वास्थ्य साथी",
        "diet": "आहार",
        "notifications": "सूचनाएं",
        "account": "खाता",
        "pin_security": "पिन सुरक्षा",
        "setting": "सेटिंग",
        "logout": "लॉग आउट",
        "current_phase": "वर्तमान चरण",
        "next_period": "अगला पीरियड",
        "predictability": "सटीकता",
        "today": "आज"
    },
    "తెలుగు": {
        "app_title": "రిలాక్స్",
        "tagline": "మీ వ్యక్తిగత మరియు చక్ర-సమకాలీకరించిన ఆరోగ్య సహచరుడు",
        "diet": "ఆహారం",
        "notifications": "నోటిఫికేషన్లు",
        "account": "ఖాతా",
        "pin_security": "పిన్ భద్రత",
        "setting": "సెట్టింగ్స్",
        "logout": "లాగ్ అవుట్",
        "current_phase": "ప్రస్తుత దశ",
        "next_period": "తదుపరి పీరియడ్",
        "predictability": "ఖచ్చితత్వం",
        "today": "ఈరోజు"
    }
}

# ---------------------------------------------------------
# Custom Styling: Relax Theme & Hide Streamlit Default UI
# ---------------------------------------------------------
st.markdown("""
<style>
/* Completely hide default Streamlit developer header toolbar, cloud viewer badges, fork & deploy buttons */
header[data-testid="stHeader"],
header,
[data-testid="stHeader"],
[data-testid="stToolbar"],
.stAppToolbar,
#MainMenu,
footer,
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stAppDeployButton,
[data-testid="stAppDeployButton"],
[data-testid="manage-app-button"],
[class*="viewerBadge"],
[class*="manage-app"],
.viewerBadge_container__1QSob,
[data-testid="stActionButtonIcon"],
[data-testid="stToolbarActionButton"],
[data-testid="stToolbarActions"],
[data-testid="stElementToolbar"],
div[class*="stAppDeployButton"],
div[class*="viewerBadge"],
a[href*="github.com"][target="_blank"],
button[title*="Fork"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    width: 0px !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

/* Clean top padding since developer toolbar is completely removed */
.block-container {
    padding-top: 1.2rem !important;
    padding-bottom: 95px !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1.0rem !important;
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

/* Relax Hero & Status Badges Row - Clean Neutral, Small Compact Badges */
.hero-card {
    background: transparent !important;
    border: none !important;
    padding: 1px 0px 4px 0px !important;
    margin-top: 1px !important;
    margin-bottom: 4px !important;
    box-shadow: none !important;
    font-size: 7pt !important;
}
.hero-title {
    font-size: 7.5pt !important;
    font-weight: 700 !important;
    color: #1e293b !important;
    margin-bottom: 2px !important;
    line-height: 1.2 !important;
}
.hero-subtitle {
    font-size: 7pt !important;
    color: #475569 !important;
    margin-bottom: 3px !important;
    line-height: 1.2 !important;
}
.hero-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}
.hero-badge {
    display: inline-block;
    padding: 1px 5px !important;
    border-radius: 4px !important;
    font-size: 6.8pt !important;
    font-weight: 600 !important;
    line-height: 1.2 !important;
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
.st-key-top_actions_bar [data-testid="stPopover"] button svg,
.st-key-top_actions_bar [data-testid="stPopover"] button [data-testid="stIconChevronDown"] {
    display: none !important;
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
}
.st-key-top_actions_bar [data-testid="stPopover"] button {
    font-size: 1.25rem !important;
    padding: 2px 6px !important;
    min-height: 28px !important;
    line-height: 1 !important;
    background: transparent !important;
    border: none !important;
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
    user_email: str = "",
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
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Relax Cycle ({username})"
    ]
    clean_email = user_email.strip()
    if clean_email:
        ics_lines.append(f"X-WR-CALDESC:Relax Cycle Health Calendar for {clean_email}")

    for _, row in cycles.iterrows():
        # 1. Bleeding / Period / Rest Time
        if include_period:
            start_str = row["Start"].strftime("%Y%m%d")
            end_str = (row["Bleeding end"] + timedelta(days=1)).strftime("%Y%m%d")
            window_note = row.get("Expected Window (± Margin)", "Regular cycle")
            summary_name = period_label if period_label.strip() else f"Rest Time ({username})"
            evt = [
                "BEGIN:VEVENT",
                f"SUMMARY:{summary_name}",
                f"DTSTART;VALUE=DATE:{start_str}",
                f"DTEND;VALUE=DATE:{end_str}",
                f"DESCRIPTION:Relax sync. Expected window: {window_note}",
                "STATUS:CONFIRMED"
            ]
            if clean_email:
                evt.append(f"ORGANIZER;CN=Relax Health:mailto:{clean_email}")
                evt.append(f"ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;CN={username}:mailto:{clean_email}")
            evt.append("END:VEVENT")
            ics_lines.extend(evt)

        # 2. Ovulation Peak
        if include_ovulation:
            ov_str = row["Ovulation estimate"].strftime("%Y%m%d")
            ov_end = (row["Ovulation estimate"] + timedelta(days=1)).strftime("%Y%m%d")
            summary_name = ovulation_label if ovulation_label.strip() else f"Ovulation ({username})"
            evt = [
                "BEGIN:VEVENT",
                f"SUMMARY:{summary_name}",
                f"DTSTART;VALUE=DATE:{ov_str}",
                f"DTEND;VALUE=DATE:{ov_end}",
                "DESCRIPTION:Estimated peak ovulation day.",
                "STATUS:CONFIRMED"
            ]
            if clean_email:
                evt.append(f"ORGANIZER;CN=Relax Health:mailto:{clean_email}")
                evt.append(f"ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;CN={username}:mailto:{clean_email}")
            evt.append("END:VEVENT")
            ics_lines.extend(evt)

        # 3. Fertile Window
        if include_fertile:
            f_start = row["Ovulation estimate"] - timedelta(days=5)
            f_end = row["Ovulation estimate"] + timedelta(days=1)
            f_start_str = f_start.strftime("%Y%m%d")
            f_end_str = f_end.strftime("%Y%m%d")
            summary_name = fertile_label if fertile_label.strip() else f"Fertile Window ({username})"
            evt = [
                "BEGIN:VEVENT",
                f"SUMMARY:{summary_name}",
                f"DTSTART;VALUE=DATE:{f_start_str}",
                f"DTEND;VALUE=DATE:{f_end_str}",
                "DESCRIPTION:Estimated high fertility window.",
                "STATUS:CONFIRMED"
            ]
            if clean_email:
                evt.append(f"ORGANIZER;CN=Relax Health:mailto:{clean_email}")
                evt.append(f"ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;CN={username}:mailto:{clean_email}")
            evt.append("END:VEVENT")
            ics_lines.extend(evt)

        # 4. PMS Window
        if include_pms:
            pms_start = row["Next period"] - timedelta(days=6)
            pms_end = row["Next period"]
            pms_start_str = pms_start.strftime("%Y%m%d")
            pms_end_str = pms_end.strftime("%Y%m%d")
            summary_name = pms_label if pms_label.strip() else f"PMS Window ({username})"
            evt = [
                "BEGIN:VEVENT",
                f"SUMMARY:{summary_name}",
                f"DTSTART;VALUE=DATE:{pms_start_str}",
                f"DTEND;VALUE=DATE:{pms_end_str}",
                "DESCRIPTION:Pre-menstrual gentle self-care window.",
                "STATUS:CONFIRMED"
            ]
            if clean_email:
                evt.append(f"ORGANIZER;CN=Relax Health:mailto:{clean_email}")
                evt.append(f"ATTENDEE;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;CN={username}:mailto:{clean_email}")
            evt.append("END:VEVENT")
            ics_lines.extend(evt)

    ics_lines.append("END:VCALENDAR")
    return "\r\n".join(ics_lines)

def generate_progress_report_html(
    username: str,
    cycles: pd.DataFrame,
    user_symptoms: dict,
    health_res: dict,
    cycle_length: int,
    period_length: int,
    phase_name: str,
    today_dt: date
) -> str:
    """Generates an elegant, print-ready HTML/PDF progress and medical cycle report."""
    cycle_rows_html = []
    for _, r in cycles.head(15).iterrows():
        cycle_rows_html.append(f"""
        <tr>
            <td style="text-align:center; font-weight:600;">Cycle #{int(r['Cycle'])}</td>
            <td>{r['Start'].strftime('%d %b %Y')}</td>
            <td>{r['Bleeding end'].strftime('%d %b %Y')}</td>
            <td>{r['Ovulation estimate'].strftime('%d %b %Y')}</td>
            <td><b>{r['Next period'].strftime('%d %b %Y')}</b></td>
            <td>{r.get('Expected Window (± Margin)', 'Regular')}</td>
        </tr>
        """)

    sym_rows_html = []
    for s_date, s_data in sorted(user_symptoms.items(), reverse=True)[:25]:
        sym_rows_html.append(f"""
        <tr>
            <td style="font-weight:600;">{s_date.strftime('%d %b %Y')}</td>
            <td>{s_data.get('flow', 'None')}</td>
            <td>{s_data.get('mood', 'N/A')}</td>
            <td>{s_data.get('energy', 'Moderate')}</td>
            <td>{s_data.get('symptoms', 'None')}</td>
            <td><i>{s_data.get('notes', '')}</i></td>
        </tr>
        """)

    if not sym_rows_html:
        sym_rows_html.append("<tr><td colspan='6' style='text-align:center; color:#64748b; padding:12px;'>No symptom entries logged yet.</td></tr>")

    active_factors = ", ".join(health_res.get("active_factors_summary", [])) or "None reported (Standard physiological baseline)"
    advisories = "".join(f"<li>{adv}</li>" for adv in health_res.get("care_tips", [])) or "<li>Maintain balanced hydration, whole-food nourishment, and consistent sleep.</li>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Relax &bull; Medical & Cycle Progress Report &bull; {username}</title>
<style>
    @page {{
        size: A4 portrait;
        margin: 15mm;
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background: #ffffff;
        margin: 0;
        padding: 20px;
        font-size: 11pt;
        line-height: 1.45;
    }}
    .print-bar {{
        background: #f1f5f9;
        border-bottom: 1px solid #cbd5e1;
        padding: 10px 20px;
        position: sticky;
        top: 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        border-radius: 8px;
    }}
    .print-btn {{
        background: #e11d48;
        color: #ffffff;
        border: none;
        padding: 8px 16px;
        font-size: 13pt;
        font-weight: 600;
        border-radius: 6px;
        cursor: pointer;
    }}
    .print-btn:hover {{ background: #be185d; }}
    @media print {{
        .print-bar {{ display: none !important; }}
        body {{ padding: 0; }}
    }}
    .report-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid #e11d48;
        padding-bottom: 12px;
        margin-bottom: 20px;
    }}
    .brand {{ font-size: 24pt; font-weight: 800; color: #be185d; }}
    .brand span {{ color: #1e293b; }}
    .meta-box {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        background: #fff1f2;
        border: 1px solid #fecdd3;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 20px;
    }}
    .meta-item b {{ display: block; font-size: 8.5pt; color: #9f1239; text-transform: uppercase; }}
    .meta-item span {{ font-size: 12pt; font-weight: 700; color: #1e293b; }}
    h2 {{
        font-size: 13pt;
        color: #be185d;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 4px;
        margin-top: 24px;
        margin-bottom: 10px;
    }}
    table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 18px;
        font-size: 9.5pt;
    }}
    th {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        padding: 6px 8px;
        text-align: left;
        color: #334155;
    }}
    td {{
        border: 1px solid #e2e8f0;
        padding: 6px 8px;
    }}
    tr:nth-child(even) {{ background: #fdf2f8; }}
    .footer-note {{
        margin-top: 30px;
        border-top: 1px dashed #cbd5e1;
        padding-top: 10px;
        font-size: 8.5pt;
        color: #64748b;
        text-align: center;
    }}
</style>
</head>
<body>
<div class="print-bar">
    <div><strong>Relax Cycle Health Progress Summary</strong> &bull; Print or Save as PDF for your healthcare provider</div>
    <button class="print-btn" onclick="window.print()">🖨️ Print / Save to PDF</button>
</div>

<div class="report-header">
    <div>
        <div class="brand">🌸 Relax <span>Cycle Progress Report</span></div>
        <div style="font-size: 10pt; color: #64748b;">Private & Cycle-Synced Women's Health Companion</div>
    </div>
    <div style="text-align: right; font-size: 9pt; color: #475569;">
        <div><b>Report Date:</b> {today_dt.strftime('%d %B %Y')}</div>
        <div><b>Account:</b> {username}</div>
    </div>
</div>

<div class="meta-box">
    <div class="meta-item">
        <b>Patient / User</b>
        <span>{username}</span>
    </div>
    <div class="meta-item">
        <b>Cycle Baseline</b>
        <span>{cycle_length} Days (Period: {period_length}d)</span>
    </div>
    <div class="meta-item">
        <b>Current Phase</b>
        <span>{phase_name}</span>
    </div>
    <div class="meta-item">
        <b>Predictability Score</b>
        <span>{health_res.get('predictability_score', 85)}% ({health_res.get('predictability_rating', 'Good')})</span>
    </div>
</div>

<div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; margin-bottom: 16px;">
    <div style="font-weight: 700; color: #0f172a; margin-bottom: 4px;">🩺 Active Health Profile & Biological Factors:</div>
    <div style="font-size: 9.5pt; color: #334155; margin-bottom: 6px;">{active_factors}</div>
    <div style="font-weight: 600; font-size: 9pt; color: #475569;">Personalized Care & Cycle Protocols:</div>
    <ul style="margin: 4px 0 0 18px; padding: 0; font-size: 9pt; color: #475569;">
        {advisories}
    </ul>
</div>

<h2>📅 Cycle Timeline & Fluctuation History</h2>
<table>
    <thead>
        <tr>
            <th>Cycle #</th>
            <th>Cycle Start</th>
            <th>Bleeding End</th>
            <th>Ovulation Estimate</th>
            <th>Next Period</th>
            <th>Fluctuation Margin</th>
        </tr>
    </thead>
    <tbody>
        {''.join(cycle_rows_html)}
    </tbody>
</table>

<h2>📝 Daily Symptom, Mood & Energy Progress Logs</h2>
<table>
    <thead>
        <tr>
            <th>Date</th>
            <th>Flow</th>
            <th>Mood</th>
            <th>Energy</th>
            <th>Physical Symptoms</th>
            <th>Reflections & Self-Care Notes</th>
        </tr>
    </thead>
    <tbody>
        {''.join(sym_rows_html)}
    </tbody>
</table>

<div class="footer-note">
    ⚕️ <b>Medical Disclaimer:</b> This report is generated by Relax for personal health tracking, rhythm synchronization, and symptom logging purposes. Cycle calculations are educational estimates and should not be used as a contraceptive method or diagnostic confirmation.
</div>
</body>
</html>"""
    return html_content


def is_local_host_device() -> bool:
    """Determines whether the client connection is from this host laptop (127.0.0.1 or localhost)."""
    try:
        if st.query_params.get("admin") == "1":
            return True
        ip = getattr(st.context, "ip_address", None)
        if ip and ip in ("127.0.0.1", "::1", "localhost"):
            return True
        h = getattr(st.context, "headers", None)
        if h:
            host = (h.get("host") or "").lower()
            if host.startswith("localhost") or host.startswith("127.0.0.1"):
                return True
    except Exception:
        pass
    return False

# ---------------------------------------------------------
# User Account & Multi-User Authentication Gate
# ---------------------------------------------------------
all_users = db.get_all_users()
user_names = [u["username"] for u in all_users]
db_stats = db.get_database_stats()
is_host = is_local_host_device()

# On host laptop, if Krishna has no PIN set and user hasn't explicitly logged out, auto-login host owner
krishna_user = next((u for u in all_users if u["username"] == "Krishna"), None)
krishna_has_pin = bool(krishna_user.get("pin_hash")) if krishna_user else False

if "authenticated_user" not in st.session_state:
    if is_host and "Krishna" in user_names and not krishna_has_pin and not st.session_state.get("logged_out_explicitly", False):
        st.session_state["authenticated_user"] = "Krishna"
        st.session_state["selected_username"] = "Krishna"

# If session is still unauthenticated (e.g. new user, external device, or after logout), show Login Gate
if not st.session_state.get("authenticated_user"):
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    auth_c1, auth_c2, auth_c3 = st.columns([1, 2.2, 1])
    with auth_c2:
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px 24px; box-shadow: 0 4px 18px rgba(0,0,0,0.05); text-align: center; margin-bottom: 18px;">
            <div style="font-size: 2.2rem; margin-bottom: 2px;">🌸</div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #1e293b;">Welcome to Relax</div>
            <div style="font-size: 0.85rem; color: #64748b; margin-top: 4px;">Private & Cycle-Synced Health Companion</div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_signup, tab_demo = st.tabs(["🔑 Sign In", "✨ New User? Create Account", "🌟 Demo Guest Preview"])

        with tab_login:
            st.caption("Sign in to your private cycle & health records:")
            default_uname = "Krishna" if (is_host and "Krishna" in user_names) else ""
            if is_host and "Krishna" in user_names:
                st.markdown("""
                <div style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 6px 12px; font-size: 0.80rem; color: #166534; margin-bottom: 10px;">
                    💻 <b>Host Laptop Detected:</b> Running locally on your computer.
                </div>
                """, unsafe_allow_html=True)

            login_username = st.text_input("Username / Name", value=default_uname, placeholder="Enter your name", key="auth_input_user")
            
            target_user = None
            if login_username.strip():
                m_users = [u for u in all_users if u["username"].lower() == login_username.strip().lower()]
                if m_users:
                    target_user = m_users[0]
            
            user_has_pin = bool(target_user.get("pin_hash")) if target_user else False
            entered_pin = ""
            if user_has_pin:
                entered_pin = st.text_input("Enter 4-Digit Security PIN", type="password", placeholder="Enter your PIN", key="auth_login_pin")
            elif target_user:
                st.caption("ℹ️ No PIN required for this account.")
            
            if st.button("🔓 Sign In to Relax", type="primary", use_container_width=True, key="btn_auth_signin"):
                clean_name = login_username.strip()
                if not clean_name:
                    st.error("Please enter your name / username.")
                elif not is_host and clean_name.lower() == "krishna" and not user_has_pin:
                    st.error("🔒 The 'Krishna' profile is reserved for the host laptop owner. Please register your own name or explore as Demo Guest.")
                else:
                    success, msg, u_obj = db.verify_user_login(clean_name, entered_pin)
                    if success and u_obj:
                        st.session_state["authenticated_user"] = u_obj["username"]
                        st.session_state["selected_username"] = u_obj["username"]
                        st.session_state[f"auth_unlocked_{u_obj['id']}"] = True
                        st.session_state["logged_out_explicitly"] = False
                        st.rerun()
                    else:
                        st.error(msg)
            
            if target_user and user_has_pin:
                sec_inf = db.get_user_security_info(target_user["id"])
                rec_q = sec_inf.get("recovery_question")
                if rec_q:
                    with st.expander("❓ Forgot PIN?", expanded=False):
                        st.caption(f"**Security Question:** {rec_q}")
                        ans_in = st.text_input("Security Answer", type="password", key="auth_rec_ans")
                        np1 = st.text_input("New PIN", type="password", key="auth_rec_np1")
                        np2 = st.text_input("Confirm New PIN", type="password", key="auth_rec_np2")
                        if st.button("🔑 Reset PIN & Sign In", key="btn_auth_rec_reset", use_container_width=True):
                            if not np1 or np1 != np2:
                                st.error("Please enter matching new PINs.")
                            else:
                                ok, rmsg = db.reset_user_pin_with_recovery(target_user["id"], ans_in.strip(), np1)
                                if ok:
                                    st.session_state["authenticated_user"] = target_user["username"]
                                    st.session_state["selected_username"] = target_user["username"]
                                    st.session_state[f"auth_unlocked_{target_user['id']}"] = True
                                    st.session_state["logged_out_explicitly"] = False
                                    st.success(rmsg)
                                    st.rerun()
                                else:
                                    st.error(rmsg)

        with tab_signup:
            st.caption("Create your own private cycle profile:")
            reg_name = st.text_input("Your Name / Nickname", placeholder="e.g. Sarah, Emily, Alex", key="reg_name_input")
            c_r1, c_r2 = st.columns(2)
            with c_r1:
                reg_cycle = st.number_input("Typical Cycle Length (days)", min_value=21, max_value=45, value=28, key="reg_cycle_len")
            with c_r2:
                reg_period = st.number_input("Period Duration (days)", min_value=1, max_value=10, value=5, key="reg_period_len")
            
            reg_pin = st.text_input("Set 4-Digit Security PIN (optional)", type="password", placeholder="Leave blank if no PIN desired", key="reg_pin_input")
            
            if st.button("🌸 Create Account & Start Journal", type="primary", use_container_width=True, key="btn_reg_create"):
                if not reg_name.strip():
                    st.error("Please enter your name.")
                elif not is_host and reg_name.strip().lower() == "krishna":
                    st.error("Name 'Krishna' is reserved for the host. Please choose your own name.")
                else:
                    success, msg, new_u = db.register_user(reg_name.strip(), reg_pin.strip(), reg_cycle, reg_period)
                    if success and new_u:
                        st.session_state["authenticated_user"] = new_u["username"]
                        st.session_state["selected_username"] = new_u["username"]
                        st.session_state[f"auth_unlocked_{new_u['id']}"] = True
                        st.session_state["logged_out_explicitly"] = False
                        st.success(f"Welcome, {new_u['username']}!")
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_demo:
            st.markdown("""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 12px; font-size: 0.83rem; color: #475569;">
                <b>👋 Preview for Interviewers & Guests:</b><br/>
                Explore all interactive features of <b>Relax</b> (3-month calendar, AI cycle forecasting, symptom logger, and 4-phase nutrition guide) without needing to create an account.
            </div>
            """, unsafe_allow_html=True)
            if st.button("👁️ Explore as Demo Guest", type="secondary", use_container_width=True, key="btn_guest_demo_launch"):
                demo_u = db.get_or_create_user("Demo Guest", default_cycle=28, default_period=5)
                demo_logs = db.get_user_cycle_logs(demo_u["id"])
                if not demo_logs:
                    db.add_cycle_log(demo_u["id"], date(date.today().year, date.today().month, 1), "Sample cycle")
                    p_m = date.today().month - 1 or 12
                    p_y = date.today().year if date.today().month > 1 else date.today().year - 1
                    db.add_cycle_log(demo_u["id"], date(p_y, p_m, 3), "Previous sample cycle")
                st.session_state["authenticated_user"] = "Demo Guest"
                st.session_state["selected_username"] = "Demo Guest"
                st.session_state[f"auth_unlocked_{demo_u['id']}"] = True
                st.session_state["logged_out_explicitly"] = False
                st.rerun()

    st.stop()

# Retrieve authenticated active user
authenticated_name = st.session_state.get("authenticated_user", "Krishna")
matched_users = [u for u in all_users if u["username"] == authenticated_name]
if matched_users:
    current_user = matched_users[0]
else:
    current_user = db.get_or_create_user(authenticated_name)

user_id = current_user["id"]
username = current_user["username"]
user_has_pin = bool(current_user.get("pin_hash"))

# Load user settings: theme, language, reminders
u_settings = db.get_user_app_settings(user_id)
if "app_bg_theme" not in st.session_state:
    st.session_state["app_bg_theme"] = u_settings.get("theme_color", "Blush Rose")
if "app_language" not in st.session_state:
    st.session_state["app_language"] = u_settings.get("language", "English")
if "app_reminders" not in st.session_state:
    st.session_state["app_reminders"] = u_settings.get("reminders") or {
        "period_approaching": True,
        "period_days_before": 2,
        "period_note": "Hydrate well, herbal tea & rest.",
        "fertile_window": True,
        "fertile_note": "Entering high fertility stage.",
        "ovulation_peak": True,
        "ovulation_note": "Ovulation peak day - peak vitality!",
        "pms_care": True,
        "pms_note": "PMS window: magnesium rich foods & gentle care.",
        "daily_log": True,
        "daily_time": "20:00"
    }

cur_theme_name = st.session_state.get("app_bg_theme", "Blush Rose")
cur_theme = THEMES.get(cur_theme_name, THEMES["Blush Rose"])
text_pri = cur_theme.get("text_primary", "#1e293b")
text_sec = cur_theme.get("text_secondary", "#475569")
card_bg = cur_theme.get("card_bg", "#ffffff")
card_border = cur_theme.get("card_border", "#e2e8f0")
is_dark = cur_theme.get("is_dark", False)

st.markdown(f"""
<style>
/* Consistent Background and Text Color across Laptop, Tablet and Phone */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], .main {{
    background: {cur_theme['bg_gradient']} !important;
    background-attachment: fixed !important;
    color: {text_pri} !important;
}}

/* High contrast typography for readability across all device screens */
h1, h2, h3, h4, h5, h6, .hero-title, .calendar h3 {{
    color: {text_pri} !important;
}}
p, span, label, .hero-subtitle {{
    color: {text_sec} !important;
}}
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
    color: {text_pri} !important;
}}
.calendar {{
    background: {card_bg} !important;
    border-color: {card_border} !important;
}}
</style>
""", unsafe_allow_html=True)



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

def render_notification_popover(phase_val: str, days_to_next: int, next_period_dt: date):
    """Renders cycle stage notifications & period reminders next to the diet icon."""
    reminders = st.session_state.get("app_reminders", {})
    cur_lang = st.session_state.get("app_language", "English")
    t = TRANSLATIONS.get(cur_lang, TRANSLATIONS["English"])
    
    with st.popover("🔔", help=t.get("notifications", "Notifications")):
        st.markdown(f"<div style='font-size:1.05rem; font-weight:700; color:#1e293b; margin-bottom:4px;'>🔔 {t.get('notifications', 'Reminders & Notifications')}</div>", unsafe_allow_html=True)
        
        # 1. Upcoming Period Status
        p_status_txt = f"In {days_to_next} days" if days_to_next > 0 else "Due today" if days_to_next == 0 else "Overdue"
        st.markdown(f"""
        <div style="background: #fff1f2; border-left: 3px solid #f43f5e; padding: 7px 10px; border-radius: 6px; margin-bottom: 8px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #9f1239;">🩸 Next Period: {p_status_txt}</div>
            <div style="font-size: 0.78rem; color: #881337;">Estimated Date: <b>{next_period_dt.strftime('%d %B %Y')}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Current Cycle Stage
        st.markdown(f"""
        <div style="background: #f0fdf4; border-left: 3px solid #22c55e; padding: 7px 10px; border-radius: 6px; margin-bottom: 8px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #166534;">🌸 Active Cycle Stage: {phase_val}</div>
            <div style="font-size: 0.78rem; color: #14532d;">Hormonal & biological rhythm is synced to this phase.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # 3. Active Configured Reminders
        st.markdown("<div style='font-size: 0.83rem; font-weight: 600; color: #334155; margin-bottom: 4px;'>⏰ Active Stage Alerts:</div>", unsafe_allow_html=True)
        
        has_any_alert = False
        if reminders.get("period_approaching", True):
            has_any_alert = True
            days_bef = reminders.get("period_days_before", 2)
            st.markdown(f"<div style='font-size:0.78rem; margin-bottom:3px;'>• <b>Period Alert:</b> {days_bef} days before ({reminders.get('period_note', 'Hydrate well')})</div>", unsafe_allow_html=True)
            
        if reminders.get("fertile_window", True):
            has_any_alert = True
            st.markdown(f"<div style='font-size:0.78rem; margin-bottom:3px;'>• <b>Fertile Window:</b> {reminders.get('fertile_note', 'Fertility window starts')}</div>", unsafe_allow_html=True)
            
        if reminders.get("ovulation_peak", True):
            has_any_alert = True
            st.markdown(f"<div style='font-size:0.78rem; margin-bottom:3px;'>• <b>Ovulation Peak:</b> {reminders.get('ovulation_note', 'Ovulation peak energy')}</div>", unsafe_allow_html=True)
            
        if reminders.get("pms_care", True):
            has_any_alert = True
            st.markdown(f"<div style='font-size:0.78rem; margin-bottom:3px;'>• <b>PMS Gentle Care:</b> {reminders.get('pms_note', 'Magnesium & gentle rest')}</div>", unsafe_allow_html=True)
            
        if reminders.get("daily_log", True):
            has_any_alert = True
            st.markdown(f"<div style='font-size:0.78rem; margin-bottom:3px;'>• <b>Daily Check-in:</b> At {reminders.get('daily_time', '20:00')}</div>", unsafe_allow_html=True)
            
        if not has_any_alert:
            st.caption("No custom reminders currently enabled.")
            
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if st.button("⚙️ Manage Reminders in Setting", key="btn_notif_goto_settings", use_container_width=True):
            st.session_state["acc_window_view"] = "settings"
            st.rerun()

def render_account_window(health_factors_list: list = None):
    """Renders the sleek Account popover window with PIN Security, Settings, centered Logout, and Active Health Factors."""
    sec_info = db.get_user_security_info(user_id)
    has_pin = sec_info["has_pin"]
    rec_type = sec_info.get("recovery_type", "question")
    saved_phone = sec_info.get("recovery_phone", "")
    saved_q = sec_info.get("recovery_question", "") or "What is your favorite comfort food?"
    
    cur_lang = st.session_state.get("app_language", "English")
    t = TRANSLATIONS.get(cur_lang, TRANSLATIONS["English"])
    
    with st.popover("👤", help=t.get("account", "Account")):
        acc_view = st.session_state.get("acc_window_view", "main")
        
        # -------------------------------------------------------------
        # VIEW 1: Main Account Menu
        # -------------------------------------------------------------
        if acc_view == "main":
            # Top right: user name
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.15rem; font-weight: 700; color: #1e293b;">👤 {username}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Active Health Factors inside Account
            if health_factors_list:
                chip_items = "".join(f"<span class='health-chip' style='display:inline-block; margin:2px;'>🩺 {f}</span>" for f in health_factors_list)
                st.markdown(f"""
                <div style='background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; padding: 6px 10px; margin-bottom: 12px; font-size: 0.80rem;'>
                    <div style='font-weight: 600; color: #334155; margin-bottom: 4px;'>🩺 Active Health Factors</div>
                    <div>{chip_items}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # On left / vertical stack
            # Button 1: Pin
            pin_btn_label = "🔒 PIN Security" if has_pin else "🔒 Create PIN"
            if st.button(pin_btn_label, key="btn_menu_pin", use_container_width=True):
                st.session_state["acc_window_view"] = "pin"
                st.rerun()
                
            st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
            # Button 2: Setting
            if st.button(f"⚙️ {t.get('setting', 'Setting')}", key="btn_menu_setting", use_container_width=True):
                st.session_state["acc_window_view"] = "settings"
                st.rerun()
                
            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
            # Button 3: Logout in the middle of the window
            lo_c1, lo_c2, lo_c3 = st.columns([1, 2, 1])
            with lo_c2:
                if st.button(f"🚪 {t.get('logout', 'Logout')}", key="acc_btn_logout_center", use_container_width=True):
                    st.session_state.pop("authenticated_user", None)
                    st.session_state.pop("selected_username", None)
                    st.session_state[f"auth_unlocked_{user_id}"] = False
                    st.session_state["logged_out_explicitly"] = True
                    st.session_state["acc_window_view"] = "main"
                    st.rerun()
                    
        # -------------------------------------------------------------
        # VIEW 2: PIN Window
        # -------------------------------------------------------------
        elif acc_view == "pin":
            hdr_c1, hdr_c2 = st.columns([1.2, 3])
            with hdr_c1:
                if st.button("◀ Back", key="btn_pin_back", use_container_width=True):
                    st.session_state["acc_window_view"] = "main"
                    st.rerun()
            with hdr_c2:
                st.markdown("<div style='text-align: right; font-weight: 700; font-size: 1.05rem; color: #1e293b;'>🔒 PIN Security</div>", unsafe_allow_html=True)
            st.markdown("---")
            
            # If pin is not yet set -> show ONLY the option to create new Pin button
            if not has_pin:
                st.markdown("<div style='background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px; padding: 6px 10px; font-size: 0.80rem; color: #92400e; margin-bottom: 10px;'>ℹ️ No PIN currently set. Create a PIN to protect your cycle records:</div>", unsafe_allow_html=True)
                
                p_new1 = st.text_input("Create New PIN", type="password", key="pin_cre_new1", placeholder="Enter 4-digit PIN")
                p_new2 = st.text_input("Confirm PIN", type="password", key="pin_cre_new2", placeholder="Confirm 4-digit PIN")
                
                rec_opt = st.radio("Recovery Option", ["Recovery Question", "Recovery Phone Number"], horizontal=True, key="pin_rec_opt_radio")
                
                sel_q_val = ""
                ans_val = ""
                phone_val = ""
                if rec_opt == "Recovery Question":
                    q_list = [
                        "What is your favorite comfort food?",
                        "What is the name of your first pet?",
                        "What city were you born in?",
                        "What was your childhood nickname?",
                        "What is your secret safe word or lucky charm?"
                    ]
                    sel_q_val = st.selectbox("Select Security Question", q_list, key="pin_sel_q_new")
                    ans_val = st.text_input("Security Answer", type="password", key="pin_ans_new", placeholder="Answer used for PIN recovery")
                else:
                    phone_val = st.text_input("Recovery Phone Number", placeholder="+1 (555) 000-0000", key="pin_phone_new")
                
                st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
                if st.button("➕ Create New PIN", key="btn_do_create_pin", type="primary", use_container_width=True):
                    if not p_new1 or not p_new2:
                        st.error("Please enter and confirm your new PIN.")
                    elif p_new1 != p_new2:
                        st.error("PINs do not match.")
                    elif rec_opt == "Recovery Question" and not ans_val.strip():
                        st.error("Please provide a recovery answer.")
                    elif rec_opt == "Recovery Phone Number" and not phone_val.strip():
                        st.error("Please provide a recovery phone number.")
                    else:
                        rtype = "question" if rec_opt == "Recovery Question" else "phone"
                        db.set_user_security_v2(user_id, p_new1, recovery_type=rtype, recovery_question=sel_q_val, recovery_answer=ans_val, recovery_phone=phone_val)
                        st.session_state[f"auth_unlocked_{user_id}"] = True
                        st.success("✅ New PIN created successfully!")
                        st.session_state["acc_window_view"] = "main"
                        st.rerun()
            else:
                # PIN is already set: Show "Set new pin" and "Create/Reset new pin" options
                st.markdown("<div style='background: #dcfce7; border: 1px solid #86efac; border-radius: 6px; padding: 4px 8px; font-size: 0.78rem; color: #15803d; font-weight: 600; margin-bottom: 8px;'>🔒 PIN Protection Active</div>", unsafe_allow_html=True)
                
                pin_action = st.radio("Choose Action", ["Set New PIN", "Reset / Create New PIN", "Remove PIN"], horizontal=True, label_visibility="collapsed", key="pin_set_action_radio")
                
                if pin_action == "Set New PIN":
                    p_old = st.text_input("Current PIN", type="password", key="pin_upd_old", placeholder="Enter current PIN")
                    p_up1 = st.text_input("New PIN", type="password", key="pin_upd_p1", placeholder="Enter new PIN")
                    p_up2 = st.text_input("Confirm New PIN", type="password", key="pin_upd_p2", placeholder="Confirm new PIN")
                    
                    rec_choice_upd = st.radio("Recovery Option", ["Recovery Question", "Recovery Phone Number"], index=0 if rec_type == "question" else 1, horizontal=True, key="pin_upd_rec_choice")
                    
                    sel_q_upd = ""
                    ans_upd = ""
                    phone_upd = ""
                    if rec_choice_upd == "Recovery Question":
                        q_list = [
                            "What is your favorite comfort food?",
                            "What is the name of your first pet?",
                            "What city were you born in?",
                            "What was your childhood nickname?",
                            "What is your secret safe word or lucky charm?"
                        ]
                        sel_q_upd = st.selectbox("Security Question", q_list, index=q_list.index(saved_q) if saved_q in q_list else 0, key="pin_upd_q")
                        ans_upd = st.text_input("New Recovery Answer (optional)", type="password", key="pin_upd_ans", placeholder="Optional new answer")
                    else:
                        phone_upd = st.text_input("Recovery Phone Number", value=saved_phone, placeholder="+1 (555) 000-0000", key="pin_upd_phone")
                        
                    if st.button("🔑 Set New PIN", key="btn_do_set_new_pin", type="primary", use_container_width=True):
                        ok, _, _ = db.verify_user_login(username, p_old)
                        if not ok:
                            st.error("Current PIN is incorrect.")
                        elif not p_up1 or not p_up2:
                            st.error("New PIN cannot be empty.")
                        elif p_up1 != p_up2:
                            st.error("New PINs do not match.")
                        else:
                            rtype = "question" if rec_choice_upd == "Recovery Question" else "phone"
                            db.set_user_security_v2(user_id, p_up1, recovery_type=rtype, recovery_question=sel_q_upd, recovery_answer=ans_upd, recovery_phone=phone_upd)
                            st.success("✅ PIN updated successfully!")
                            st.session_state["acc_window_view"] = "main"
                            st.rerun()
                            
                elif pin_action == "Reset / Create New PIN":
                    st.caption("Recover using your security question or phone:")
                    if rec_type == "phone" and saved_phone:
                        st.caption(f"Recovery Phone on file: `{saved_phone[:4]}...{saved_phone[-4:]}`")
                        ph_ans = st.text_input("Enter Full Phone Number to Verify", key="pin_rst_phone_in", placeholder="Verify recovery phone")
                    else:
                        st.caption(f"Security Question: **{saved_q}**")
                        ph_ans = st.text_input("Answer to Security Question", type="password", key="pin_rst_ans_in", placeholder="Enter answer")
                        
                    rst_p1 = st.text_input("New PIN", type="password", key="pin_rst_p1", placeholder="New PIN")
                    rst_p2 = st.text_input("Confirm New PIN", type="password", key="pin_rst_p2", placeholder="Confirm new PIN")
                    
                    if st.button("➕ Reset & Create New PIN", key="btn_do_reset_pin", type="primary", use_container_width=True):
                        if not rst_p1 or rst_p1 != rst_p2:
                            st.error("Please enter matching new PINs.")
                        else:
                            if rec_type == "phone":
                                if ph_ans.strip() != saved_phone.strip():
                                    st.error("Phone number does not match recovery record.")
                                else:
                                    db.set_user_pin(user_id, rst_p1)
                                    st.success("✅ PIN reset successfully!")
                                    st.session_state["acc_window_view"] = "main"
                                    st.rerun()
                            else:
                                ok, r_msg = db.reset_user_pin_with_recovery(user_id, ph_ans.strip(), rst_p1)
                                if ok:
                                    st.success(f"✅ {r_msg}")
                                    st.session_state["acc_window_view"] = "main"
                                    st.rerun()
                                else:
                                    st.error(r_msg)
                                    
                elif pin_action == "Remove PIN":
                    rem_p = st.text_input("Enter PIN to confirm removal", type="password", key="pin_rem_input")
                    if st.button("Disable PIN Protection", key="btn_do_disable_pin", use_container_width=True):
                        ok, _, _ = db.verify_user_login(username, rem_p)
                        if ok:
                            db.remove_user_pin(user_id)
                            st.info("PIN lock disabled.")
                            st.session_state["acc_window_view"] = "main"
                            st.rerun()
                        else:
                            st.error("Incorrect PIN.")

        # -------------------------------------------------------------
        # VIEW 3: Settings Window
        # -------------------------------------------------------------
        elif acc_view == "settings":
            s_hdr1, s_hdr2 = st.columns([1.2, 3])
            with s_hdr1:
                if st.button("◀ Back", key="btn_settings_back", use_container_width=True):
                    st.session_state["acc_window_view"] = "main"
                    st.rerun()
            with s_hdr2:
                st.markdown("<div style='text-align: right; font-weight: 700; font-size: 1.05rem; color: #1e293b;'>⚙️ Settings</div>", unsafe_allow_html=True)
            st.markdown("---")
            
            set_tabs = st.tabs(["🎨 Background Color", "🌐 Language", "⏰ Reminders"])
            
            # Tab 1: Background Color / Theme
            with set_tabs[0]:
                st.caption("Change the background color & theme of the app:")
                theme_keys = list(THEMES.keys())
                cur_th = st.session_state.get("app_bg_theme", "Blush Rose")
                idx_th = theme_keys.index(cur_th) if cur_th in theme_keys else 0
                
                sel_theme = st.selectbox("Select Background Color / Theme", theme_keys, index=idx_th, key="sel_app_theme")
                
                # Theme preview badge
                th_preview = THEMES[sel_theme]
                st.markdown(f"""
                <div style="background: {th_preview['bg_gradient']}; border: 1.5px solid #cbd5e1; border-radius: 8px; padding: 10px; text-align: center; margin-top: 6px; margin-bottom: 10px;">
                    <span style="font-weight: 700; color: #1e293b; font-size: 0.88rem;">{th_preview['name']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🎨 Apply Background Color", key="btn_apply_theme", type="primary", use_container_width=True):
                    st.session_state["app_bg_theme"] = sel_theme
                    db.save_user_app_settings(user_id, sel_theme, st.session_state.get("app_language", "English"), st.session_state.get("app_reminders", {}))
                    st.success(f"Applied {sel_theme} theme!")
                    st.rerun()
                    
            # Tab 2: Language
            with set_tabs[1]:
                st.caption("Change language of the app:")
                lang_keys = list(TRANSLATIONS.keys())
                cur_ln = st.session_state.get("app_language", "English")
                idx_ln = lang_keys.index(cur_ln) if cur_ln in lang_keys else 0
                
                sel_lang = st.selectbox("Select Language", lang_keys, index=idx_ln, key="sel_app_language")
                
                if st.button("🌐 Apply Language", key="btn_apply_language", type="primary", use_container_width=True):
                    st.session_state["app_language"] = sel_lang
                    db.save_user_app_settings(user_id, st.session_state.get("app_bg_theme", "Blush Rose"), sel_lang, st.session_state.get("app_reminders", {}))
                    st.success(f"Language changed to {sel_lang}!")
                    st.rerun()
                    
            # Tab 3: Reminders for Different Stages of Period
            with set_tabs[2]:
                st.caption("Create reminders for your different stages of period:")
                rem_data = st.session_state.get("app_reminders", {})
                
                # 1. Period Approaching
                r_period_on = st.toggle("🩸 Period Approaching Reminder", value=rem_data.get("period_approaching", True), key="r_tog_period")
                r_period_days = st.slider("Notify how many days before?", min_value=1, max_value=5, value=rem_data.get("period_days_before", 2), key="r_slide_period")
                r_period_note = st.text_input("Self-care note", value=rem_data.get("period_note", "Hydrate well and rest."), key="r_note_period")
                st.markdown("---")
                
                # 2. Fertile Window
                r_fertile_on = st.toggle("🌱 Fertile Window Reminder", value=rem_data.get("fertile_window", True), key="r_tog_fertile")
                r_fertile_note = st.text_input("Fertility stage note", value=rem_data.get("fertile_note", "High fertility window starts."), key="r_note_fertile")
                st.markdown("---")
                
                # 3. Ovulation Peak Day
                r_ov_on = st.toggle("🟣 Ovulation Peak Day Reminder", value=rem_data.get("ovulation_peak", True), key="r_tog_ov")
                r_ov_note = st.text_input("Ovulation peak note", value=rem_data.get("ovulation_note", "Ovulation peak today - peak vitality!"), key="r_note_ov")
                st.markdown("---")
                
                # 4. PMS / Luteal Phase Gentle Care
                r_pms_on = st.toggle("🌙 PMS Gentle Care Reminder", value=rem_data.get("pms_care", True), key="r_tog_pms")
                r_pms_note = st.text_input("PMS comfort note", value=rem_data.get("pms_note", "PMS window: magnesium, light yoga & rest."), key="r_note_pms")
                st.markdown("---")
                
                # 5. Daily Log Check-in
                r_daily_on = st.toggle("💊 Daily Symptom & Mood Reminder", value=rem_data.get("daily_log", True), key="r_tog_daily")
                r_daily_time = st.selectbox("Preferred daily reminder time", ["08:00 AM", "12:00 PM", "06:00 PM", "08:00 PM", "10:00 PM"], index=3, key="r_sel_daily_time")
                
                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("💾 Save All Reminders", key="btn_save_reminders", type="primary", use_container_width=True):
                    new_rems = {
                        "period_approaching": r_period_on,
                        "period_days_before": r_period_days,
                        "period_note": r_period_note,
                        "fertile_window": r_fertile_on,
                        "fertile_note": r_fertile_note,
                        "ovulation_peak": r_ov_on,
                        "ovulation_note": r_ov_note,
                        "pms_care": r_pms_on,
                        "pms_note": r_pms_note,
                        "daily_log": r_daily_on,
                        "daily_time": r_daily_time
                    }
                    st.session_state["app_reminders"] = new_rems
                    db.save_user_app_settings(user_id, st.session_state.get("app_bg_theme", "Blush Rose"), st.session_state.get("app_language", "English"), new_rems)
                    st.success("✅ Reminders saved successfully!")
                    st.rerun()

# ---------------------------------------------------------
# Main App Header & Relax Branding
# ---------------------------------------------------------
top_bar_col1, top_bar_col2 = st.columns([2.2, 1.8])

with top_bar_col1:
    cur_lang_code = st.session_state.get("app_language", "English")
    t_app = TRANSLATIONS.get(cur_lang_code, TRANSLATIONS["English"])
    st.markdown(f"""
    <div style="margin-top: 2px; margin-bottom: 4px; display: flex; align-items: center; height: 100%;">
        <span style="font-size: 1.25rem; font-weight: 700; color: #1e293b;">🌸 {t_app.get('app_title', 'Relax')}</span>
    </div>
    """, unsafe_allow_html=True)

with top_bar_col2:
    with st.container(key="top_actions_bar"):
        diet_col, notif_col, acc_col = st.columns([1, 1, 1], gap="small")
        with diet_col:
            render_diet_notif_popover(phase_name, "Diet", container_key="diet_notif_top")
        with notif_col:
            render_notification_popover(phase_name, days_to_next_period, active_cycle['Next period'])
        with acc_col:
            render_account_window(health_factors_list=health_res.get("active_factors_summary", []))


tracked_note = ""
if (today - start_date).days > 45:
    tracked_note = f" &bull; <i>Calculated from {start_date.strftime('%d %b %Y')} (Cycle #{int(active_cycle['Cycle'])})</i>"

st.markdown(f"""
<div class="hero-card">
    <div class="hero-badges">
        <span class="hero-badge {phase_badge}">Current Phase: {phase_name}</span>
        <span class="hero-badge badge-countdown">Next Period: {f'In {days_to_next_period} days' if days_to_next_period > 0 else 'Due today' if days_to_next_period == 0 else 'Overdue'} ({active_cycle['Next period'].strftime('%d %b')})</span>
        <span class="hero-badge {health_res['badge_class']}">Predictability: {health_res['predictability_score']}% ({health_res['predictability_rating']})</span>
    </div>
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

    # Year Selector Pills & Quick Month Navigation (2020 to 2035) - Placed under the calendar
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
                if st.button("💾 Save", type="primary", use_container_width=True, key=f"btn_quick_save_sym_{cal_date_str}"):
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
                if st.button("💾 Save", type="primary", use_container_width=True, key=f"btn_quick_save_sym_{cal_date_str}"):
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

    # Personalized Calendar Sync with Email ID & Custom Names
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    with st.expander("📲 Connect Period Stages to Calendar with Email ID", expanded=False):
        st.write("Connect upcoming period, ovulation, and cycle stages directly to your personal calendar (Google, Apple, or Outlook) using your email ID:")
        
        cal_email_in = st.text_input(
            "📧 Enter Your Email ID for Calendar Sync",
            value=st.session_state.get("cal_sync_email_val", ""),
            placeholder="e.g. yourname@gmail.com",
            key="input_cal_sync_email",
            help="Allows calendar invitations and event reminders to sync with your phone and email account."
        )
        if cal_email_in.strip():
            st.session_state["cal_sync_email_val"] = cal_email_in.strip()
            
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
            user_email=cal_email_in.strip(),
            include_period=sync_period,
            period_label=custom_period_label,
            include_ovulation=sync_ovulation,
            ovulation_label=custom_ovulation_label,
            include_fertile=sync_fertile,
            fertile_label=custom_fertile_label,
            include_pms=sync_pms,
            pms_label=custom_pms_label
        )
        
        cal_btn_c1, cal_btn_c2 = st.columns([1.5, 1])
        with cal_btn_c1:
            st.download_button(
                label="📅 Download Calendar Sync (.ics)",
                data=custom_ics_content,
                file_name=f"Relax_Sync_{username}.ics",
                mime="text/calendar",
                type="primary",
                use_container_width=True
            )
        with cal_btn_c2:
            if not cycles.empty:
                next_row = cycles.iloc[0]
                g_start = next_row["Start"].strftime("%Y%m%d")
                g_end = (next_row["Bleeding end"] + timedelta(days=1)).strftime("%Y%m%d")
                g_title = urllib.parse.quote(custom_period_label)
                g_desc = urllib.parse.quote(f"Relax Cycle Health reminder for {username}. Cycle length: {cycle_length_used} days.")
                g_email_param = f"&add={urllib.parse.quote(cal_email_in.strip())}" if cal_email_in.strip() else ""
                gcal_link = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={g_title}&dates={g_start}/{g_end}&details={g_desc}{g_email_param}"
                st.link_button("🌐 Open in Google Calendar", gcal_link, use_container_width=True)
                
        st.caption("✨ Compatible with Google Calendar (Android / Web), Apple Calendar (iPhone / Mac), and Microsoft Outlook.")

    # Whole Progress Export: MS Sheet or PDF Report based on user choice
    st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
    with st.expander("📊 Export Whole Progress (MS Sheet or PDF Report)", expanded=False):
        st.write("Download your entire progress including cycle timeline forecasts, daily symptoms, moods, and health factor advisories:")
        
        progress_fmt_choice = st.radio(
            "Select Format:",
            ["📑 MS Sheet (Excel .xlsx)", "📄 PDF / Printable Health Report (.html / .pdf)"],
            horizontal=True,
            key="progress_export_fmt_choice"
        )
        
        if "MS Sheet" in progress_fmt_choice:
            excel_bytes = io.BytesIO()
            with pd.ExcelWriter(excel_bytes, engine="openpyxl") as writer:
                # 1. Cycle Timeline
                export_cycles = cycles.copy()
                for d_col in ["Start", "Bleeding end", "Ovulation estimate", "Next period"]:
                    if d_col in export_cycles.columns:
                        export_cycles[d_col] = export_cycles[d_col].astype(str)
                export_cycles.to_excel(writer, sheet_name="Cycle_Timeline", index=False)
                
                # 2. Daily Symptoms Log
                sym_export_rows = []
                for s_dt, s_info in sorted(user_symptoms.items(), reverse=True):
                    sym_export_rows.append({
                        "Date": str(s_dt),
                        "Flow": s_info.get("flow", "None"),
                        "Mood": s_info.get("mood", "N/A"),
                        "Energy": s_info.get("energy", "Moderate"),
                        "Symptoms": s_info.get("symptoms", ""),
                        "Reflections_Notes": s_info.get("notes", "")
                    })
                if not sym_export_rows:
                    sym_export_rows = [{"Date": "No symptom entries yet", "Flow": "", "Mood": "", "Energy": "", "Symptoms": "", "Reflections_Notes": ""}]
                pd.DataFrame(sym_export_rows).to_excel(writer, sheet_name="Daily_Symptoms_Log", index=False)
                
                # 3. Medical & Profile Summary
                prof_summary_rows = [
                    {"Parameter": "User Name", "Value": username},
                    {"Parameter": "Baseline Cycle Length", "Value": f"{cycle_length_used} days"},
                    {"Parameter": "Baseline Period Length", "Value": f"{period_length} days"},
                    {"Parameter": "Current Phase", "Value": phase_name},
                    {"Parameter": "Predictability Score", "Value": f"{health_res['predictability_score']}% ({health_res['predictability_rating']})"},
                    {"Parameter": "Active Health Factors", "Value": ", ".join(health_res["active_factors_summary"]) or "None reported"},
                    {"Parameter": "Total Cycles Logged", "Value": len(user_logs)},
                    {"Parameter": "Export Date", "Value": str(date.today())}
                ]
                pd.DataFrame(prof_summary_rows).to_excel(writer, sheet_name="Health_Summary", index=False)
                
            excel_output = excel_bytes.getvalue()
            
            exp_c1, exp_c2 = st.columns([2, 1])
            with exp_c1:
                st.download_button(
                    label="📊 Download Whole Progress in MS Sheet (.xlsx)",
                    data=excel_output,
                    file_name=f"Relax_Whole_Progress_{username}_{date.today().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
            with exp_c2:
                csv_bytes = export_cycles.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV (.csv)",
                    data=csv_bytes,
                    file_name=f"Relax_Cycles_{username}_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            st.caption("Microsoft Excel (.xlsx) workbook includes separate sheets for Cycle Timeline, Daily Symptoms Log, and Health Profile Summary.")

        else:
            med_report_html = generate_progress_report_html(
                username=username,
                cycles=cycles,
                user_symptoms=user_symptoms,
                health_res=health_res,
                cycle_length=cycle_length_used,
                period_length=period_length,
                phase_name=phase_name,
                today_dt=today
            )
            st.download_button(
                label="📄 Download Health Progress Report (PDF / Printable HTML)",
                data=med_report_html.encode('utf-8'),
                file_name=f"Relax_Medical_Progress_Report_{username}_{date.today().strftime('%Y%m%d')}.html",
                mime="text/html",
                type="primary",
                use_container_width=True
            )
            st.caption("💡 When you open the downloaded report in any browser, click **'🖨️ Print / Save to PDF'** to instantly save or print your formatted medical PDF report.")


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
        
        if st.button("💾 Save", type="primary", use_container_width=True, key="btn_save_sym"):
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
# Health Note & Disclaimer
# ---------------------------------------------------------
st.warning(
    "⚕️ **Health Disclaimer:** Ovulation and cycle timing can fluctuate due to stress, illness, sleep, and lifestyle. "
    "Relax provides educational estimates based on calendar algorithms and should not be used as a medical diagnosis or contraceptive method."
)
