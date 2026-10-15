import sqlite3
import hashlib
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple

DB_PATH = "relax.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_pin(pin: str) -> str:
    """Hashes a user PIN/password securely with salt."""
    if not pin:
        return ""
    salt = "relax_salt_2026"
    return hashlib.sha256(f"{salt}_{pin}".encode("utf-8")).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        typical_cycle_length INTEGER DEFAULT 28,
        typical_period_length INTEGER DEFAULT 5,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Cycle start dates log (user history)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cycle_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, start_date)
    )
    """)
    
    # 3. Daily symptoms & mood logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_symptoms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        log_date TEXT NOT NULL,
        flow TEXT DEFAULT 'None',
        mood TEXT DEFAULT '',
        symptoms TEXT DEFAULT '',
        energy TEXT DEFAULT 'Normal',
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, log_date)
    )
    """)
    
    # Pre-seed default profile for Krishna if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'Krishna'")
    krishna = cursor.fetchone()
    if not krishna:
        cursor.execute("""
        INSERT INTO users (username, typical_cycle_length, typical_period_length)
        VALUES ('Krishna', 28, 5)
        """)
        krishna_id = cursor.lastrowid
        # Seed 21 September 2026 as latest start date
        cursor.execute("""
        INSERT OR IGNORE INTO cycle_logs (user_id, start_date, notes)
        VALUES (?, '2026-09-21', 'Latest logged period')
        """, (krishna_id,))
        # Seed previous past cycle for history averaging
        cursor.execute("""
        INSERT OR IGNORE INTO cycle_logs (user_id, start_date, notes)
        VALUES (?, '2026-08-24', 'Previous period')
        """, (krishna_id,))
    
    # Ensure health profile & security columns exist in users table
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [c["name"] for c in cursor.fetchall()]
    if "thyroid_status" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN thyroid_status TEXT DEFAULT 'None'")
    if "health_conditions" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN health_conditions TEXT DEFAULT ''")
    if "stress_level" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN stress_level TEXT DEFAULT 'Normal'")
    if "pin_hash" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN pin_hash TEXT DEFAULT ''")
    if "recovery_question" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN recovery_question TEXT DEFAULT ''")
    if "recovery_answer_hash" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN recovery_answer_hash TEXT DEFAULT ''")
    if "recovery_phone" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN recovery_phone TEXT DEFAULT ''")
    if "recovery_type" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN recovery_type TEXT DEFAULT 'question'")
    if "theme_color" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN theme_color TEXT DEFAULT 'Blush Rose'")
    if "language" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'English'")
    if "reminders_json" not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN reminders_json TEXT DEFAULT '{}'")

    conn.commit()
    conn.close()

def get_all_users() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY username ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

def get_or_create_user(username: str, default_cycle: int = 28, default_period: int = 5) -> Dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("""
        INSERT INTO users (username, typical_cycle_length, typical_period_length, thyroid_status, health_conditions, stress_level)
        VALUES (?, ?, ?, 'None', '', 'Normal')
        """, (username, default_cycle, default_period))
        conn.commit()
        user_id = cursor.lastrowid
        user = {
            "id": user_id,
            "username": username,
            "typical_cycle_length": default_cycle,
            "typical_period_length": default_period,
            "thyroid_status": "None",
            "health_conditions": "",
            "stress_level": "Normal"
        }
    else:
        user = dict(row)
    conn.close()
    return user

def update_user_health_profile(user_id: int, thyroid_status: str, health_conditions: str, stress_level: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users 
    SET thyroid_status = ?, health_conditions = ?, stress_level = ?
    WHERE id = ?
    """, (thyroid_status, health_conditions, stress_level, user_id))
    conn.commit()
    conn.close()

def update_user_preferences(user_id: int, cycle_length: int, period_length: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users SET typical_cycle_length = ?, typical_period_length = ? WHERE id = ?
    """, (cycle_length, period_length, user_id))
    conn.commit()
    conn.close()

def get_user_cycle_logs(user_id: int) -> List[date]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT start_date FROM cycle_logs WHERE user_id = ? ORDER BY start_date DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    dates = []
    for r in rows:
        try:
            dates.append(date.fromisoformat(r["start_date"]))
        except ValueError:
            pass
    return sorted(dates)

def add_cycle_log(user_id: int, start_date: date, notes: str = "") -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO cycle_logs (user_id, start_date, notes)
        VALUES (?, ?, ?)
        """, (user_id, start_date.isoformat(), notes))
        conn.commit()
        success = True
    except Exception:
        success = False
    conn.close()
    return success

def delete_cycle_log(user_id: int, start_date: date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cycle_logs WHERE user_id = ? AND start_date = ?", (user_id, start_date.isoformat()))
    conn.commit()
    conn.close()

def save_daily_symptom(user_id: int, log_date: date, flow: str, mood: str, symptoms: str, energy: str, notes: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR REPLACE INTO daily_symptoms (user_id, log_date, flow, mood, symptoms, energy, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, log_date.isoformat(), flow, mood, symptoms, energy, notes))
    conn.commit()
    conn.close()

# Alias for backward and cross-module compatibility
add_daily_symptoms = save_daily_symptom


def get_daily_symptoms(user_id: int) -> Dict[date, Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT log_date, flow, mood, symptoms, energy, notes FROM daily_symptoms WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    result = {}
    for r in rows:
        try:
            d = date.fromisoformat(r["log_date"])
            result[d] = dict(r)
        except ValueError:
            pass
    return result

def delete_daily_symptom(user_id: int, log_date: date) -> bool:
    """Deletes a daily symptom record for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_symptoms WHERE user_id = ? AND log_date = ?", (user_id, log_date.isoformat()))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def register_user(username: str, pin: str = "", default_cycle: int = 28, default_period: int = 5) -> Tuple[bool, str, Optional[Dict]]:
    """Registers a new user in the database with optional secure PIN."""
    clean_username = username.strip()
    if not clean_username:
        return False, "Username cannot be empty.", None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (clean_username,))
    if cursor.fetchone():
        conn.close()
        return False, f"Username '{clean_username}' already exists. Please choose another name or login.", None
    
    pin_h = hash_pin(pin) if pin else ""
    cursor.execute("""
    INSERT INTO users (username, typical_cycle_length, typical_period_length, thyroid_status, health_conditions, stress_level, pin_hash)
    VALUES (?, ?, ?, 'None / Normal Thyroid', '', 'Low / Managed', ?)
    """, (clean_username, default_cycle, default_period, pin_h))
    conn.commit()
    user_id = cursor.lastrowid
    user = {
        "id": user_id,
        "username": clean_username,
        "typical_cycle_length": default_cycle,
        "typical_period_length": default_period,
        "thyroid_status": "None / Normal Thyroid",
        "health_conditions": "",
        "stress_level": "Low / Managed",
        "pin_hash": pin_h
    }
    conn.close()
    return True, f"Account '{clean_username}' created successfully in database!", user

def verify_user_login(username: str, pin: str = "") -> Tuple[bool, str, Optional[Dict]]:
    """Verifies user credentials against SQLite database."""
    clean_username = username.strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (clean_username,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False, f"User '{clean_username}' not found. Please register an account.", None
    
    user = dict(row)
    stored_pin_hash = user.get("pin_hash", "") or ""
    if stored_pin_hash:
        if hash_pin(pin) != stored_pin_hash:
            return False, "Incorrect PIN. Please enter your correct PIN to unlock your profile.", None
    return True, f"Welcome back, {user['username']}!", user

def set_user_pin(user_id: int, new_pin: str) -> bool:
    """Sets or updates a PIN for the user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET pin_hash = ? WHERE id = ?", (hash_pin(new_pin), user_id))
    conn.commit()
    conn.close()
    return True

def set_user_security(user_id: int, new_pin: str, recovery_question: str = "", recovery_answer: str = "") -> bool:
    """Sets or updates PIN and recovery question/answer for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    pin_h = hash_pin(new_pin) if new_pin else ""
    ans_h = hash_pin(recovery_answer.strip().lower()) if recovery_answer.strip() else ""
    
    if recovery_question.strip():
        cursor.execute("""
        UPDATE users 
        SET pin_hash = ?, recovery_question = ?, recovery_answer_hash = ?
        WHERE id = ?
        """, (pin_h, recovery_question.strip(), ans_h, user_id))
    else:
        cursor.execute("UPDATE users SET pin_hash = ? WHERE id = ?", (pin_h, user_id))
    conn.commit()
    conn.close()
    return True

def verify_recovery_answer(user_id: int, answer: str) -> bool:
    """Checks whether the provided recovery answer matches."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT recovery_answer_hash FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return False
    stored = row["recovery_answer_hash"]
    if not stored:
        return False
    return hash_pin(answer.strip().lower()) == stored

def reset_user_pin_with_recovery(user_id: int, answer: str, new_pin: str) -> Tuple[bool, str]:
    """Resets user PIN using the security answer."""
    if not verify_recovery_answer(user_id, answer):
        return False, "Incorrect recovery answer. Please try again."
    set_user_pin(user_id, new_pin)
    return True, "PIN reset successfully! You can now use your new PIN."

def remove_user_pin(user_id: int) -> bool:
    """Removes PIN protection and recovery credentials for the user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET pin_hash = '', recovery_question = '', recovery_answer_hash = '' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def get_user_security_info(user_id: int) -> Dict:
    """Retrieves security status for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT pin_hash, recovery_question, recovery_phone, recovery_type FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"has_pin": False, "recovery_question": "", "recovery_phone": "", "recovery_type": "question"}
    cols = row.keys()
    return {
        "has_pin": bool(row["pin_hash"]),
        "recovery_question": row["recovery_question"] or "",
        "recovery_phone": row["recovery_phone"] if "recovery_phone" in cols and row["recovery_phone"] else "",
        "recovery_type": row["recovery_type"] if "recovery_type" in cols and row["recovery_type"] else "question"
    }

def set_user_security_v2(user_id: int, new_pin: str, recovery_type: str = "question", recovery_question: str = "", recovery_answer: str = "", recovery_phone: str = "") -> bool:
    """Sets or updates PIN with choice of recovery question or phone number."""
    conn = get_connection()
    cursor = conn.cursor()
    pin_h = hash_pin(new_pin) if new_pin else ""
    ans_h = hash_pin(recovery_answer.strip().lower()) if recovery_answer.strip() else ""
    phone_clean = recovery_phone.strip()
    
    cursor.execute("""
    UPDATE users 
    SET pin_hash = ?, recovery_type = ?, recovery_question = ?, recovery_answer_hash = ?, recovery_phone = ?
    WHERE id = ?
    """, (pin_h, recovery_type, recovery_question.strip(), ans_h, phone_clean, user_id))
    conn.commit()
    conn.close()
    return True

def get_user_app_settings(user_id: int) -> Dict:
    """Retrieves theme, language, and reminders settings for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT theme_color, language, reminders_json FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return {"theme_color": "Blush Rose", "language": "English", "reminders": {}}
    cols = row.keys()
    theme = row["theme_color"] if "theme_color" in cols and row["theme_color"] else "Blush Rose"
    lang = row["language"] if "language" in cols and row["language"] else "English"
    import json
    try:
        reminders = json.loads(row["reminders_json"]) if "reminders_json" in cols and row["reminders_json"] else {}
    except Exception:
        reminders = {}
    return {
        "theme_color": theme,
        "language": lang,
        "reminders": reminders
    }

def save_user_app_settings(user_id: int, theme_color: str, language: str, reminders: Dict):
    """Saves user theme, language, and stage reminders."""
    import json
    conn = get_connection()
    cursor = conn.cursor()
    rem_str = json.dumps(reminders)
    cursor.execute("""
    UPDATE users SET theme_color = ?, language = ?, reminders_json = ? WHERE id = ?
    """, (theme_color, language, rem_str, user_id))
    conn.commit()
    conn.close()

def export_user_data(user_id: int) -> Dict:
    """Exports all user data (profile, cycles, symptoms) to a structured dictionary for backup/JSON download."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    u_row = cursor.fetchone()
    if not u_row:
        conn.close()
        return {}
    user_data = dict(u_row)
    user_data.pop("pin_hash", None)
    
    cursor.execute("SELECT start_date, notes, created_at FROM cycle_logs WHERE user_id = ? ORDER BY start_date ASC", (user_id,))
    cycle_logs = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT log_date, flow, mood, symptoms, energy, notes, created_at FROM daily_symptoms WHERE user_id = ? ORDER BY log_date ASC", (user_id,))
    symptoms = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    return {
        "app": "Relax",
        "version": "2.0",
        "exported_at": datetime.now().isoformat(),
        "user_profile": user_data,
        "cycle_logs": cycle_logs,
        "daily_symptoms": symptoms
    }

def import_user_data(user_id: int, backup_data: Dict) -> Tuple[bool, str]:
    """Imports backed-up cycles and symptoms into user's database account."""
    if not isinstance(backup_data, dict) or "app" not in backup_data:
        return False, "Invalid Relax backup format."
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cycles_imported = 0
    for c in backup_data.get("cycle_logs", []):
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO cycle_logs (user_id, start_date, notes)
            VALUES (?, ?, ?)
            """, (user_id, c["start_date"], c.get("notes", "")))
            cycles_imported += 1
        except Exception:
            pass
            
    symptoms_imported = 0
    for s in backup_data.get("daily_symptoms", []):
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO daily_symptoms (user_id, log_date, flow, mood, symptoms, energy, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, s["log_date"], s.get("flow", "None"), s.get("mood", ""), s.get("symptoms", ""), s.get("energy", "Normal"), s.get("notes", "")))
            symptoms_imported += 1
        except Exception:
            pass
            
    prof = backup_data.get("user_profile", {})
    if prof:
        cursor.execute("""
        UPDATE users SET 
            typical_cycle_length = COALESCE(?, typical_cycle_length),
            typical_period_length = COALESCE(?, typical_period_length),
            thyroid_status = COALESCE(?, thyroid_status),
            health_conditions = COALESCE(?, health_conditions),
            stress_level = COALESCE(?, stress_level)
        WHERE id = ?
        """, (
            prof.get("typical_cycle_length"),
            prof.get("typical_period_length"),
            prof.get("thyroid_status"),
            prof.get("health_conditions"),
            prof.get("stress_level"),
            user_id
        ))
        
    conn.commit()
    conn.close()
    return True, f"Successfully restored {cycles_imported} cycles and {symptoms_imported} daily symptom logs!"

def get_database_stats() -> Dict:
    """Returns overall database statistics for display."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) as count FROM cycle_logs")
    cycle_count = cursor.fetchone()["count"]
    cursor.execute("SELECT COUNT(*) as count FROM daily_symptoms")
    symptom_count = cursor.fetchone()["count"]
    conn.close()
    return {
        "engine": "SQLite",
        "database_file": DB_PATH,
        "total_users": user_count,
        "total_cycles_saved": cycle_count,
        "total_symptoms_saved": symptom_count,
        "status": "Connected & Healthy 🟢"
    }
