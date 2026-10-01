import calendar
from datetime import date, timedelta, datetime
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
    initial_sidebar_state="expanded"
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

/* Compact page padding */
.block-container {
    padding-top: 1.8rem !important;
    padding-bottom: 2rem !important;
}

/* Compact KPI Metric Cards */
[data-testid="stMetricValue"] {
    font-size: 1.18rem !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.8rem !important;
    font-weight: 600 !important;
}

/* Relax Hero & Status Cards (Small, Compact Font - Size 8) */
.hero-card {
    background: linear-gradient(135deg, #fff1f2 0%, #fdf2f8 50%, #f5f3ff 100%);
    border: 1px solid #fbcfe8;
    border-radius: 10px;
    padding: 6px 12px;
    margin-bottom: 8px;
    box-shadow: 0 1px 4px rgba(244, 114, 182, 0.05);
    font-size: 8pt !important;
}
.hero-title {
    font-size: 8pt !important;
    font-weight: 700;
    color: #9d174d;
    margin-bottom: 2px;
    line-height: 1.2;
}
.hero-subtitle {
    font-size: 8pt !important;
    color: #4b5563;
    margin-bottom: 5px;
    line-height: 1.2;
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
    background: #fdf2f8;
    color: #9d174d;
    border: 1px solid #fbcfe8;
    border-radius: 6px;
    padding: 1px 5px;
    font-size: 7.5pt !important;
    font-weight: 600;
    margin-right: 4px;
    margin-bottom: 2px;
}

/* Compact Buttons with small icons throughout the app */
div[data-testid="stButton"] button {
    padding: 2px 8px !important;
    min-height: 26px !important;
    height: 26px !important;
    font-size: 0.72rem !important;
    border-radius: 6px !important;
    line-height: 1 !important;
}
div[data-testid="stButton"] button p {
    font-size: 0.72rem !important;
    line-height: 1 !important;
    margin: 0 !important;
}

/* Relax Calendar Table */
.calendar {
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 14px;
    background: #ffffff;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
}
.calendar h3 {
    margin-top: 0;
    margin-bottom: 8px;
    font-size: 1.05rem;
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
    height: 65px;
    vertical-align: top;
    padding: 5px;
    border: 1px solid #f1f5f9;
    font-size: .85rem;
    transition: all 0.15s ease-in-out;
    cursor: pointer;
    position: relative;
}
.calendar td:hover:not(.empty) {
    transform: scale(1.06);
    z-index: 10;
    box-shadow: 0 6px 16px rgba(236, 72, 153, 0.22);
    border: 2px solid #ec4899;
}
.calendar td.empty { background: #f8fafc; cursor: default; }
.calendar td.bleeding { background: #fee2e2; }
.calendar td.estimated { background: #fff1f2; border: 1.5px dashed #f43f5e; }
.calendar td.fertile { background: #dcfce7; }
.calendar td.ovulation { background: #f3e8ff; border: 2px solid #a855f7; }
.calendar td.pms { background: #fef3c7; }
.calendar td.forecast { border: 2px dashed #94a3b8; }
.calendar td.today { box-shadow: inset 0 0 0 2px #2563eb; }
.calendar td.logged { border-bottom: 3px solid #ec4899; }
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
                "marker": " 🩸",
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
                            "marker": " 🌱",
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
                        "marker": " 🟣",
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
                            "marker": " ✨",
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
                                "marker": " 🩸",
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
                                "marker": " 🌱",
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
                            "marker": " 🟣",
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
                                "marker": " ✨",
                                "phase": "PMS Window ✨ (Estimated)",
                                "mood": "Emotional sensitivity, irritability cues",
                                "physical": "Mild bloating, breast tenderness",
                                "tip": "Magnesium and gentle rest.",
                                "advisories": phase_advisories.get("pms", [])
                            }
                        d += timedelta(days=1)

                    curr_est += timedelta(days=cycle_length)

    # 1b. Project historical baseline for unlogged months before earliest logged period (up to 12 cycles / 1 year back)
    if sorted_logs:
        earliest_log = sorted_logs[0]
        curr_back = earliest_log - timedelta(days=cycle_length)
        for _ in range(12):
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
                        "marker": " 🩸",
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
                        "marker": " 🌱",
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
                    "marker": " 🟣",
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
                        "marker": " ✨",
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
                    "marker": " 🩸",
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
                    "marker": " 🌱",
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
                "marker": " 🟣",
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
                    "marker": " ✨",
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
                "marker": " 🔮",
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

def calendar_html(year: int, month: int, events: dict) -> str:
    cal = calendar.Calendar(firstweekday=0)
    html_code = f"<div class='calendar'><h3>{calendar.month_name[month]} {year}</h3><table>"
    html_code += "<tr>" + "".join(f"<th>{x}</th>" for x in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]) + "</tr>"
    today = date.today()
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

            if info:
                classes.extend(info.get("classes", []))
                markers = info.get("marker", "")
                
                tooltip_parts = [
                    f"📅 {d.strftime('%a, %d %b %Y')}",
                    f"📍 Phase: {info.get('phase', 'Normal')}",
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
            html_code += f"<td class='{class_text}' title='{escaped_tooltip}'><b>{day_num}</b><span style='font-size: 0.72rem;'>{markers}</span></td>"
        html_code += "</tr>"
    return html_code + "</table></div>"

def generate_ics(cycles: pd.DataFrame, username: str) -> str:
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//Relax//Cycle Forecast for {username}//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH"
    ]
    for _, row in cycles.iterrows():
        # Period Window
        start_str = row["Start"].strftime("%Y%m%d")
        end_str = (row["Bleeding end"] + timedelta(days=1)).strftime("%Y%m%d")
        window_note = row.get("Expected Window (± Margin)", "Regular cycle")
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"SUMMARY:🩸 Period - Relax ({username})",
            f"DTSTART;VALUE=DATE:{start_str}",
            f"DTEND;VALUE=DATE:{end_str}",
            f"DESCRIPTION:Predicted menstrual period by Relax app. Fluctuation window: {window_note}",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])
        # Ovulation Peak
        ov_str = row["Ovulation estimate"].strftime("%Y%m%d")
        ov_end = (row["Ovulation estimate"] + timedelta(days=1)).strftime("%Y%m%d")
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"SUMMARY:🟣 Ovulation Peak - Relax ({username})",
            f"DTSTART;VALUE=DATE:{ov_str}",
            f"DTEND;VALUE=DATE:{ov_end}",
            f"DESCRIPTION:Estimated peak ovulation day by Relax app.",
            "STATUS:CONFIRMED",
            "END:VEVENT"
        ])
    ics_lines.append("END:VCALENDAR")
    return "\r\n".join(ics_lines)

# ---------------------------------------------------------
# Sidebar: User Account & Database Profile
# ---------------------------------------------------------
st.sidebar.markdown("### 🌸 User Account & Profile")

all_users = db.get_all_users()
user_names = [u["username"] for u in all_users]

db_stats = db.get_database_stats()
st.sidebar.caption(f"💾 **Database:** `{db_stats['database_file']}` (Auto-saved 🟢)")

selected_option = st.sidebar.selectbox(
    "Active Profile",
    options=user_names + ["➕ Register New Account"],
    index=user_names.index("Krishna") if "Krishna" in user_names else 0
)

if selected_option == "➕ Register New Account":
    new_username = st.sidebar.text_input("Enter your name / username", placeholder="e.g. Sarah, Maya")
    new_pin = st.sidebar.text_input("Security PIN / Password (optional)", type="password", placeholder="e.g. 1234", help="Protects your personal cycle and health data on this device.")
    col_reg1, col_reg2 = st.sidebar.columns(2)
    with col_reg1:
        if st.button("Register & Save", type="primary") and new_username.strip():
            success, msg, created_user = db.register_user(new_username.strip(), new_pin)
            if success:
                st.sidebar.success(msg)
                st.rerun()
            else:
                st.sidebar.error(msg)
    current_user = all_users[0] if all_users else db.get_or_create_user("Krishna")
else:
    current_user = [u for u in all_users if u["username"] == selected_option][0]

user_id = current_user["id"]
username = current_user["username"]

# Security check: If user account has a PIN set, require PIN unlock
user_has_pin = bool(current_user.get("pin_hash"))
auth_session_key = f"auth_unlocked_{user_id}"

if user_has_pin and not st.session_state.get(auth_session_key, False):
    st.sidebar.warning(f"🔒 Profile **{username}** is protected by a PIN.")
    entered_pin = st.sidebar.text_input("Enter PIN to unlock", type="password", key=f"pin_input_{user_id}")
    if st.sidebar.button("🔓 Unlock Account"):
        success, msg, _ = db.verify_user_login(username, entered_pin)
        if success:
            st.session_state[auth_session_key] = True
            st.sidebar.success("Account unlocked!")
            st.rerun()
        else:
            st.sidebar.error(msg)
            st.stop()
    else:
        st.stop()

# Fetch historical cycle dates for this user
user_logs = db.get_user_cycle_logs(user_id)

# ---------------------------------------------------------
# Sidebar: Cycle Parameters & Period Logger
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Cycle Settings")

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
# Sidebar: Personal Health & Thyroid Factors
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 🩺 Health & Thyroid Profile")
st.sidebar.caption("Log thyroid or personal health factors to calculate period fluctuations and uncertainty windows.")

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
    "Thyroid Condition",
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
    "Other Health Issues",
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

if st.sidebar.button("💾 Save Health Profile"):
    conds_str = ", ".join(selected_conditions)
    db.update_user_health_profile(user_id, selected_thyroid, conds_str, selected_stress)
    st.sidebar.success("Health profile updated! Period fluctuations recalculated.")
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
# Main App Header & Relax Branding
# ---------------------------------------------------------
st.markdown(f"""
<div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 6px;">
    <span style="font-size: 1rem; font-weight: 700; color: #9d174d;">🌸 Relax</span>
    <span style="font-size: 8pt; color: #64748b;">Personalized menstrual wellness & cycle tracking for <b>{username}</b></span>
</div>
""", unsafe_allow_html=True)

# Compute All Cycles from start_date forward through today and into the future for the next 2 full years (28 cycles)
cycles = build_cycles(start_date, cycle_length_used, period_length, future_cycles=28, fluctuation_margin=fluctuation_margin)

# Fetch custom daily symptom logs
user_symptoms = db.get_daily_symptoms(user_id)

# ---------------------------------------------------------
# Current Cycle Phase & Countdown (Hero Banner)
# ---------------------------------------------------------
today = date.today()

# Identify active cycle currently in progress for today
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

tracked_note = ""
if (today - start_date).days > 45:
    tracked_note = f" &bull; <i>Calculated from {start_date.strftime('%d %b %Y')} (Cycle #{int(active_cycle['Cycle'])})</i>"

health_chip_html = ""
if health_res["active_factors_summary"]:
    chip_items = "".join(f"<span class='health-chip'>🩺 {f}</span>" for f in health_res["active_factors_summary"])
    health_chip_html = f"<div style='margin-top: 4px; font-size: 8pt;'><b>Active Health Factors:</b> {chip_items}</div>"

st.markdown(f"""
<div class="hero-card">
    <div class="hero-title">Welcome back, {username}!</div>
    <div class="hero-subtitle">Today is <b>{today.strftime('%A, %d %B %Y')}</b> &bull; Cycle Day <b>{cycle_day if cycle_day > 0 else 'Upcoming'}</b>{tracked_note}</div>
    <div class="hero-badges">
        <span class="hero-badge {phase_badge}">Current Phase: {phase_name}</span>
        <span class="hero-badge badge-countdown">Next Period: {f'In {days_to_next_period} days' if days_to_next_period > 0 else 'Due today' if days_to_next_period == 0 else 'Overdue'} ({active_cycle['Next period'].strftime('%d %b')})</span>
        <span class="hero-badge {health_res['badge_class']}">Predictability: {health_res['predictability_score']}% ({health_res['predictability_rating']})</span>
    </div>
    {health_chip_html}
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Page Navigation (4 Compact Icon Views: Calendar, Chat, Insights, Symptoms Update)
# ---------------------------------------------------------
if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "📅 Calendar"

nav_c1, nav_c2, nav_c3, nav_c4, _ = st.columns([1, 0.9, 1, 1.3, 3])

with nav_c1:
    is_sel = st.session_state["active_nav"] == "📅 Calendar"
    if st.button("📅 Calendar", key="nav_btn_cal", use_container_width=True, type="primary" if is_sel else "secondary"):
        st.session_state["active_nav"] = "📅 Calendar"
        st.rerun()

with nav_c2:
    is_sel = st.session_state["active_nav"] == "💬 Chat"
    if st.button("💬 Chat", key="nav_btn_chat", use_container_width=True, type="primary" if is_sel else "secondary"):
        st.session_state["active_nav"] = "💬 Chat"
        st.rerun()

with nav_c3:
    is_sel = st.session_state["active_nav"] == "💡 Insights"
    if st.button("💡 Insights", key="nav_btn_ins", use_container_width=True, type="primary" if is_sel else "secondary"):
        st.session_state["active_nav"] = "💡 Insights"
        st.rerun()

with nav_c4:
    is_sel = st.session_state["active_nav"] == "📝 Symptoms Update"
    if st.button("📝 Symptoms Update", key="nav_btn_sym", use_container_width=True, type="primary" if is_sel else "secondary"):
        st.session_state["active_nav"] = "📝 Symptoms Update"
        st.rerun()

st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

# =========================================================
# VIEW 1: 📅 Calendar (Flo-Style 3-Month View & Export)
# =========================================================
if st.session_state["active_nav"] == "📅 Calendar":
    # 1. Build calendar events with ALL user history logs and future cycles
    events = build_calendar_events(
        cycles=cycles,
        user_symptoms=user_symptoms,
        phase_advisories=health_res["phase_advisories"],
        user_logs=user_logs,
        period_length=period_length,
        cycle_length=cycle_length_used
    )

    # 2. Determine latest period happened month as anchor
    latest_happened_date = user_logs[-1] if user_logs else start_date

    # Track user profile changes to sync calendar anchor
    if st.session_state.get("cal_user_id") != user_id:
        st.session_state["cal_user_id"] = user_id
        st.session_state["cal_nav_year"] = latest_happened_date.year
        st.session_state["cal_nav_month"] = latest_happened_date.month

    if "cal_nav_year" not in st.session_state or "cal_nav_month" not in st.session_state:
        st.session_state["cal_nav_year"] = latest_happened_date.year
        st.session_state["cal_nav_month"] = latest_happened_date.month

    st.markdown("### 📅 Cycle Calendar")
    st.markdown("<div style='font-size: 8pt; color: #64748b; margin-bottom: 6px;'>🩸 Bleeding &nbsp;&bull;&nbsp; 🌱 Fertile window &nbsp;&bull;&nbsp; 🟣 Ovulation &nbsp;&bull;&nbsp; ✨ PMS window &nbsp;&bull;&nbsp; 🔮 Forecast &nbsp;&bull;&nbsp; 📝 Logged</div>", unsafe_allow_html=True)

    # Flo-Style Navigation Bar: [ ◀ Previous ]  [ Month Range ]  [ Next ▶ ]  [ 📍 Latest Period ]
    cal_nav1, cal_nav2, cal_nav3, cal_nav4 = st.columns([1.2, 2.6, 1.2, 1.4])

    with cal_nav1:
        if st.button("◀ Previous Month", key="btn_cal_prev", use_container_width=True, help="Move 1 month back into history"):
            if st.session_state["cal_nav_month"] == 1:
                st.session_state["cal_nav_month"] = 12
                st.session_state["cal_nav_year"] -= 1
            else:
                st.session_state["cal_nav_month"] -= 1
            st.rerun()

    with cal_nav3:
        if st.button("Next Month ▶", key="btn_cal_next", use_container_width=True, help="Move 1 month forward into forecast"):
            if st.session_state["cal_nav_month"] == 12:
                st.session_state["cal_nav_month"] = 1
                st.session_state["cal_nav_year"] += 1
            else:
                st.session_state["cal_nav_month"] += 1
            st.rerun()

    with cal_nav4:
        is_at_latest = (
            st.session_state["cal_nav_year"] == latest_happened_date.year and
            st.session_state["cal_nav_month"] == latest_happened_date.month
        )
        if st.button("📍 Latest Period", key="btn_cal_reset", use_container_width=True, disabled=is_at_latest, help="Jump back to latest period happened month"):
            st.session_state["cal_nav_year"] = latest_happened_date.year
            st.session_state["cal_nav_month"] = latest_happened_date.month
            st.rerun()

    # Compute the 3 consecutive months: Month 1 = base month, Month 2 = +1, Month 3 = +2
    cur_base_y = st.session_state["cal_nav_year"]
    cur_base_m = st.session_state["cal_nav_month"]

    display_months = []
    for offset in range(3):
        total_mo = (cur_base_m - 1) + offset
        y = cur_base_y + total_mo // 12
        m = (total_mo % 12) + 1
        display_months.append((y, m))

    m_start_name = f"{calendar.month_name[display_months[0][1]]} {display_months[0][0]}"
    m_end_name = f"{calendar.month_name[display_months[2][1]]} {display_months[2][0]}"

    with cal_nav2:
        st.markdown(
            f"<div style='text-align:center; padding: 4px 0; font-weight: 700; font-size: 8pt; color: #9d174d; background: #fff1f2; border: 1px solid #fbcfe8; border-radius: 8px;'>"
            f"🌸 {m_start_name} &nbsp;–&nbsp; {m_end_name}"
            f"</div>",
            unsafe_allow_html=True
        )

    st.caption(f"💡 Showing 3-month window from **{m_start_name}** to **{m_end_name}**. Use **◀ Previous Month** and **Next Month ▶** to glide through past history and upcoming forecasts for the next 2 years. Hover over any date for phase details, physical symptoms, mood cues, and care tips.")

    # Render exactly 3 side-by-side month cards
    cal_cols = st.columns(3)
    for col_idx, (year, month) in enumerate(display_months):
        with cal_cols[col_idx]:
            st.markdown(calendar_html(year, month, events), unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    c_exp1, c_exp2 = st.columns([3, 1])
    with c_exp1:
        st.markdown("#### 📲 Sync Predicted Cycles to Phone Calendar")
        st.caption("Download an `.ics` calendar file to automatically import period start dates and ovulation windows into Apple Calendar, Google Calendar, or Outlook.")
    with c_exp2:
        ics_content = generate_ics(cycles, username)
        st.download_button(
            label="📅 Download Calendar (.ics)",
            data=ics_content,
            file_name=f"Relax_Cycle_{username}.ics",
            mime="text/calendar",
            type="primary",
            use_container_width=True
        )

# =========================================================
# VIEW 2: 💬 Chat (AI Cycle & Menstrual Wellness Assistant)
# =========================================================
elif st.session_state["active_nav"] == "💬 Chat":
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
elif st.session_state["active_nav"] == "💡 Insights":
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
elif st.session_state["active_nav"] == "📝 Symptoms Update":
    st.markdown("### 📝 Daily Symptoms, Mood & Health Update")
    st.caption(f"Log your daily cues for **{username}** to track physical patterns, energy shifts, and emotions across your cycle.")

    sym_form_col, sym_hist_col = st.columns([1.2, 1])

    with sym_form_col:
        st.markdown("#### ✍️ Log Symptoms for a Date")
        log_date = st.date_input("Select Date", value=today, max_value=today + timedelta(days=7), key="symptom_log_date")
        
        row1_c1, row1_c2 = st.columns(2)
        with row1_c1:
            flow_option = st.selectbox("Flow Intensity", ["None", "Spotting", "Light", "Medium", "Heavy"], key="sym_flow")
        with row1_c2:
            energy_option = st.selectbox("Energy Level", ["High ⚡", "Moderate 🌿", "Low / Fatigued 😴"], key="sym_energy")
            
        mood_options = st.multiselect(
            "Mood & Emotions",
            ["Happy 😊", "Calm 🧘", "Energetic ⚡", "Confident ✨", "Sensitive 🥺", "Irritable 😤", "Anxious 😟", "Brain Fog 🌫️", "Low Mood 🌧️"],
            key="sym_mood"
        )
        symptom_options = st.multiselect(
            "Physical Symptoms",
            ["Cramps 💥", "Bloating 🎈", "Headache 🤕", "Tender Breasts 🌸", "Acne 💧", "Lower Back Pain 🦴", "Cravings 🍫", "Insomnia 🌙"],
            key="sym_phys"
        )
        note_text = st.text_area("Personal Notes & Self-Care Reflections", placeholder="E.g., chamomile tea helped cramps, slept 8 hours...", key="sym_notes")
        
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
