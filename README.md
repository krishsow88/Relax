# 🌸 Relax - Menstrual Health & Wellness

**Relax** is a full-featured, multi-user menstrual cycle tracking, mood logging, health conditions profiling, and hormonal forecasting web application.

---

## ✨ Features

- **🩺 Health & Thyroid Fluctuation Engine:**
  - Dynamic profiling for **Thyroid conditions** (Hypothyroidism, Hyperthyroidism, Hashimoto's), **Reproductive health** (PCOS / PCOD, Endometriosis, Fibroids, Perimenopause, Birth Control), and **Stress levels** (Chronic stress, burnout).
  - Calculates biological **Period Fluctuation Margins (`±X days`)**, uncertainty windows, and **Cycle Predictability Scores**.
  - Provides evidence-based clinical insights explaining endocrine mechanisms (TRH, prolactin, GnRH, LH surge, cortisol) and targeted nutrition/lifestyle care protocols.
- **Multi-User Profiles:** Independent profiles with persistent SQLite database storage (`relax.db`). Switch between users or add new ones in one click.
- **Cycle Phase Hero Card:** Instant status displaying current cycle day, active phase (Menstrual, Follicular, Fertile Window, Ovulation, Luteal, PMS), next period countdown, and active fluctuation window.
- **3-Month Interactive Calendar:** Color-coded days with rich hover tooltips detailing estimated ovulation timing, expected mood shifts, physical symptoms, personalized condition cues, and self-care tips.
- **Daily Symptom & Mood Logger:** Log daily flow intensity, moods (happy, anxious, irritable, calm), physical symptoms (cramps, bloating, headache), energy levels, and personal notes.
- **Color-Coded Forecast Table with Fluctuation Windows:** Clearly distinguishes past dates (🔴 rose), today (🟡 amber), future projections (🟢 mint), and calculated fluctuation windows (`±Margin`).
- **Cycle Trend Chart:** Interactive Plotly graph showing cycle durations and regularity trends.
- **Phone Calendar Sync (.ics):** 1-click export to download an iCalendar file compatible with Apple Calendar, Google Calendar, and Microsoft Outlook.

---

## 🚀 Running Locally

### 1-Click Launch (Windows)
Double-click **`run.bat`** to start the app and automatically open your browser.  
To stop, double-click **`stop.bat`**.

### Terminal Setup
```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies (if needed)
pip install -r requirements.txt

# 3. Launch the Relax app
streamlit run app.py
```
Open **http://localhost:8501** in your browser.

---

## 🌐 Deploying to the Web (Free Cloud Hosting)

Relax is ready for free one-click deployment:

### Option 1: Streamlit Community Cloud (Recommended)
1. Push this folder to a GitHub repository.
2. Sign in to [share.streamlit.io](https://share.streamlit.io/) with GitHub.
3. Click **"New app"**, select your repo, branch (`main`), and file (`app.py`).
4. Click **"Deploy"**! You will receive a public HTTPS URL (e.g. `https://relax-cycle.streamlit.app`) accessible from any phone or computer worldwide.

### Option 2: Render / Hugging Face Spaces
- Works as a standard Python web service running `streamlit run app.py --server.port $PORT`.

---

## ⚕️ Important Disclaimer
Relax is an educational and wellness tracking tool. Calendar algorithms provide statistical estimates and should not be used as a medical diagnosis or contraceptive method.
