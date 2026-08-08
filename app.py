import base64
import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date, timedelta, datetime
import altair as alt
import extra_streamlit_components as stx
import time
import streamlit.components.v1 as components


# --- DATA: Fully Expanded 114 Surahs ---
SURAH_DATA = [
    (1, "Al-Fatihah", 1, 1), (2, "Al-Baqarah", 2, 49), (3, "Aal-Imran", 50, 76), 
    (4, "An-Nisa", 77, 106), (5, "Al-Ma'idah", 106, 127), (6, "Al-An'am", 128, 150), 
    (7, "Al-A'raf", 151, 176), (8, "Al-Anfal", 177, 186), (9, "At-Tawbah", 187, 207), 
    (10, "Yunus", 208, 221), (11, "Hud", 221, 235), (12, "Yusuf", 235, 248), 
    (13, "Ar-Ra'd", 249, 255), (14, "Ibrahim", 255, 261), (15, "Al-Hijr", 262, 267), 
    (16, "An-Nahl", 267, 281), (17, "Al-Isra", 282, 293), (18, "Al-Kahf", 293, 304), 
    (19, "Maryam", 305, 312), (20, "Taha", 312, 321), (21, "Al-Anbiya", 322, 331), 
    (22, "Al-Hajj", 332, 341), (23, "Al-Mu'minun", 342, 349), (24, "An-Nur", 350, 359), 
    (25, "Al-Furqan", 359, 366), (26, "Ash-Shu'ara", 367, 376), (27, "An-Naml", 377, 385), 
    (28, "Al-Qasas", 385, 396), (29, "Al-Ankabut", 396, 404), (30, "Ar-Rum", 404, 410), 
    (31, "Luqman", 411, 414), (32, "As-Sajdah", 415, 417), (33, "Al-Ahzab", 418, 427), 
    (34, "Saba", 428, 434), (35, "Fatir", 434, 440), (36, "Ya-Sin", 440, 445), 
    (37, "As-Saffat", 446, 452), (38, "Sad", 453, 458), (39, "Az-Zumar", 458, 467), 
    (40, "Ghafir", 467, 476), (41, "Fussilat", 477, 482), (42, "Ash-Shura", 483, 489), 
    (43, "Az-Zukhruf", 489, 495), (44, "Ad-Dukhan", 496, 498), (45, "Al-Jathiyah", 499, 502), 
    (46, "Al-Ahqaf", 502, 506), (47, "Muhammad", 507, 510), (48, "Al-Fath", 511, 515), 
    (49, "Al-Hujurat", 515, 517), (50, "Qaf", 518, 520), (51, "Ad-Zariyat", 520, 523), 
    (52, "At-Tur", 523, 525), (53, "An-Najm", 526, 528), (54, "Al-Qamar", 528, 531), 
    (55, "Ar-Rahman", 531, 534), (56, "Al-Waqi'ah", 534, 537), (57, "Al-Hadid", 537, 541), 
    (58, "Al-Mujadila", 542, 545), (59, "Al-Hashr", 545, 548), (60, "Al-Mumtahanah", 549, 551), 
    (61, "As-Saff", 551, 552), (62, "Al-Jumu'ah", 553, 554), (63, "Al-Munafiqun", 554, 555), 
    (64, "At-Taghabun", 556, 557), (65, "At-Talaq", 558, 559), (66, "At-Tahrim", 560, 561), 
    (67, "Al-Mulk", 562, 564), (68, "Al-Qalam", 564, 566), (69, "Al-Haqqah", 566, 568), 
    (70, "Al-Ma'arij", 568, 570), (71, "Nuh", 570, 571), (72, "Al-Jinn", 572, 573), 
    (73, "Al-Muzzammil", 574, 575), (74, "Al-Muddaththir", 575, 577), (75, "Al-Qiyamah", 577, 578), 
    (76, "Al-Insan", 578, 580), (77, "Al-Mursalat", 580, 581), (78, "An-Naba", 582, 583), 
    (79, "An-Nazi'at", 583, 584), (80, "Abasa", 585, 585), (81, "At-Takwir", 586, 586), 
    (82, "Al-Infitar", 587, 587), (83, "Al-Mutaffifin", 587, 589), (84, "Al-Inshiqaq", 589, 589), 
    (85, "Al-Buruj", 590, 590), (86, "At-Tariq", 591, 591), (87, "Al-A'la", 591, 592), 
    (88, "Al-Ghashiyah", 592, 592), (89, "Al-Fajr", 593, 594), (90, "Al-Balad", 594, 594), 
    (91, "Ash-Shams", 595, 595), (92, "Al-Lail", 595, 596), (93, "Ad-Duha", 596, 596), 
    (94, "Ash-Sharh", 596, 596), (95, "At-Tin", 597, 597), (96, "Al-Alaq", 597, 598), 
    (97, "Al-Qadr", 598, 598), (98, "Al-Bayyinah", 598, 599), (99, "Az-Zalzalah", 599, 599), 
    (100, "Al-Adiyat", 599, 600), (101, "Al-Qari'ah", 600, 600), (102, "At-Takathur", 600, 600), 
    (103, "Al-Asr", 601, 601), (104, "Al-Humazah", 601, 601), (105, "Al-Fil", 601, 601), 
    (106, "Quraish", 602, 602), (107, "Al-Ma'un", 602, 602), (108, "Al-Kawthar", 602, 602), 
    (109, "Al-Kafirun", 603, 603), (110, "An-Nasr", 603, 603), (111, "Al-Masad", 603, 603), 
    (112, "Al-Ikhlas", 604, 604), (113, "Al-Falaq", 604, 604), (114, "An-Nas", 604, 604)
]
surah_options = [f"{s[0]}. {s[1]}" for s in SURAH_DATA]

def get_juz(page_num):
    juz_starts = [1, 22, 42, 62, 82, 102, 122, 142, 162, 182, 202, 222, 242, 262, 282, 302, 322, 342, 362, 382, 402, 422, 442, 462, 482, 502, 522, 542, 562, 582]
    for i, start in reversed(list(enumerate(juz_starts))):
        if page_num >= start: return i + 1
    return 1

def get_juz_page_range(juz_num):
    juz_starts = [1, 22, 42, 62, 82, 102, 122, 142, 162, 182, 202, 222, 242, 262, 282, 302, 322, 342, 362, 382, 402, 422, 442, 462, 482, 502, 522, 542, 562, 582]
    start = juz_starts[juz_num - 1]
    end = juz_starts[juz_num] - 1 if juz_num < 30 else 604
    return start, end

# --- STREAMLIT UI SETUP ---
# Helper to encode local PNG to Base64 for iOS Safari
def get_base64_image(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

logo_b64 = get_base64_image("logo.png")

st.set_page_config(
    page_title="Quran Tracker Cloud", 
    page_icon="logo.png", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)
# Inject Base64 PNG directly so iOS Safari can read it instantly
if logo_b64:
    st.markdown(
        f"""
        <link rel="apple-touch-icon" href="data:image/png;base64,{logo_b64}">
        """,
        unsafe_allow_html=True
    )
# --- ISLAMIC THEME CSS ---
st.markdown("""
<style>
    /* Injects a subtle, transparent geometric star pattern into the main background */
    .stApp {
        background-color: #022c22;
        background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23d4af37' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    }
    
    /* Makes the metric numbers (Streak, Hours, etc.) pop in Gold */
    [data-testid="stMetricValue"] {
        color: #d4af37 !important;
    }
</style>
""", unsafe_allow_html=True)
# -------------------------


if "sidebar_nav" not in st.session_state:
    st.session_state.sidebar_nav = "📊 Dashboard"

cookie_manager = stx.CookieManager(key="quran_tracker_cookies")

# --- INITIALIZE DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase: Client = init_connection()
except Exception:
    st.error("❌ Connection to database failed. Please check your secrets.")
    st.stop()

# --- AUTHENTICATION SYSTEM ---
if "user" not in st.session_state:
    st.session_state["user"] = None

qt_access = cookie_manager.get("qt_access")
qt_refresh = cookie_manager.get("qt_refresh")

if st.session_state["user"] is None and qt_refresh:
    try:
        res = supabase.auth.set_session(qt_access, qt_refresh)
        st.session_state["user"] = res.user
        
        expire_date = datetime.now() + timedelta(days=30)
        cookie_manager.set("qt_access", res.session.access_token, expires_at=expire_date, key="set_access_auto")
        cookie_manager.set("qt_refresh", res.session.refresh_token, expires_at=expire_date, key="set_refresh_auto")
    except Exception:
        pass
# --- 1. JAVASCRIPT HASH CONVERTER (For Default Supabase Links) ---
components.html(
    """
    <script>
    const parentUrl = window.parent.location.href;
    if (parentUrl.includes('#access_token=')) {
        const hash = window.parent.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        const accessToken = params.get('access_token');
        const refreshToken = params.get('refresh_token');
        const type = params.get('type');
        
        if (type === 'recovery' && accessToken) {
            window.parent.location.href = window.parent.location.origin + window.parent.location.pathname + '?access_token=' + accessToken + '&refresh_token=' + refreshToken;
        }
    }
    </script>
    """,
    height=0,
)

# --- 2. CATCH ACCESS TOKEN & AUTHENTICATE ---
if "access_token" in st.query_params:
    try:
        access_token = st.query_params["access_token"]
        refresh_token = st.query_params.get("refresh_token", "")
        res = supabase.auth.set_session(access_token, refresh_token)
        st.session_state["user"] = res.user
        st.session_state["is_resetting_password"] = True
        st.query_params.clear()
    except Exception as e:
        st.error(f"❌ Reset link expired or invalid: {e}")

# --- 3. RENDER SET NEW PASSWORD SCREEN ---
def render_reset_password_screen():
    st.title("🔑 Create New Password")
    st.write("Please enter your new password below.")
    
    with st.form("new_password_form"):
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Update Password", type="primary")
        
        if submit:
            if len(new_pw) < 6:
                st.error("❌ Password must be at least 6 characters long.")
            elif new_pw != confirm_pw:
                st.error("❌ Passwords do not match.")
            else:
                try:
                    supabase.auth.update_user({"password": new_pw})
                    st.toast("✅ Password updated successfully!")
                    st.success("✅ Password updated successfully! Redirecting...")
                    st.session_state["is_resetting_password"] = False
                    time.sleep(1.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Could not update password: {e}")

if st.session_state.get("is_resetting_password", False):
    render_reset_password_screen()
    st.stop()
def render_login():
    st.title("🔐 Login to Quran Tracker")
    # Make sure tab3 is declared here:
    tab1, tab2, tab3 = st.tabs(["Login", "Sign Up", "🔑 Forgot Password"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary"):
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user"] = response.user

                expire_date = datetime.now() + timedelta(days=30)
                cookie_manager.set("qt_access", response.session.access_token, expires_at=expire_date, key="set_access_login")
                cookie_manager.set("qt_refresh", response.session.refresh_token, expires_at=expire_date, key="set_refresh_login")

                time.sleep(0.5)
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

    with tab2:
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password (min 6 chars)", type="password", key="reg_pass")
        if st.button("Sign Up"):
            try:
                supabase.auth.sign_up({"email": new_email, "password": new_password})
                st.success("✅ Account created! You can now log in.")
            except Exception as e:
                st.error(f"Sign up failed: {e}")

    with tab3:
        st.write("Enter your email address to receive a password reset link.")
        reset_email = st.text_input("Registered Email", key="reset_email")
        if st.button("Send Reset Link"):
            if not reset_email:
                st.error("Please enter your email address.")
            else:
                try:
                    supabase.auth.reset_password_for_email(
                        reset_email,
                        {"redirect_to": "https://my-quran-tracker.streamlit.app"} # Replace with your live app URL
                    )
                    st.success("📩 Password reset link sent! Please check your email inbox.")
                except Exception as e:
                    st.error(f"Could not send reset link: {e}")
if st.session_state["user"] is None:
    render_login()
    st.stop()

user_email = st.session_state["user"].email

# --- DATA FETCHERS ---
def fetch_logs():
    res = supabase.table('daily_logs').select("*").eq("user_name", user_email).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def fetch_priorities_raw():
    res = supabase.table('surah_categories').select("*").eq("user_name", user_email).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def fetch_page_priorities():
    res = supabase.table('page_priorities').select("*").eq("user_name", user_email).execute()
    return res.data if res.data else []
# --- USER SETTINGS FETCHERS ---
def fetch_user_settings():
    res = supabase.table('user_settings').select("*").eq("user_name", user_email).execute()
    if res.data:
        return res.data[0]
    return {"email_reminders": False, "reminder_time": "20:00"}

def save_user_settings(enabled, rem_time):
    payload = {
        "user_name": user_email,
        "email_reminders": enabled,
        "reminder_time": rem_time
    }
    supabase.table('user_settings').upsert(payload).execute()
raw_priorities = fetch_priorities_raw()
is_onboarded = not raw_priorities.empty
df_priorities = raw_priorities[raw_priorities['surah_number'] > 0] if is_onboarded else pd.DataFrame()

# --- PRIORITY MANAGEMENT LOGIC ---
def get_page_priority_state():
    key = f"page_priority_map_{user_email}"
    if key not in st.session_state:
        state = {}
        db_overrides = fetch_page_priorities()
        for record in db_overrides:
            state[f"{record['surah_name']}::{record['page_number']}"] = record['category']
        st.session_state[key] = state
    return st.session_state[key]

def set_page_priority(surah_name, page_num, priority):
    state = get_page_priority_state()
    state[f"{surah_name}::{page_num}"] = priority
    st.session_state[f"page_priority_map_{user_email}"] = state

def get_page_priority(surah_name, page_num):
    return get_page_priority_state().get(f"{surah_name}::{page_num}")

def build_priority_counts(df_priorities):
    priority_order = ["1 - Confident", "2 - Needs Revision", "3 - Not Memorized"]
    priority_lookup = {}
    if not df_priorities.empty:
        for _, row in df_priorities.iterrows():
            priority_lookup[row['surah_name']] = row['category']

    counts = {priority: 0 for priority in priority_order}
    for surah in SURAH_DATA:
        surah_name = surah[1]
        base_priority = priority_lookup.get(surah_name, "3 - Not Memorized")
        
        for page_num in range(surah[2], surah[3] + 1):
            override_priority = get_page_priority(surah_name, page_num)
            final_priority = override_priority if override_priority else base_priority
            
            if surah_name == "Al-Fatihah":
                final_priority = "1 - Confident"
                
            if final_priority in counts:
                counts[final_priority] += 1
            else:
                counts["3 - Not Memorized"] += 1

    return pd.DataFrame({"Priority": priority_order, "Count": [counts[p] for p in priority_order]})

def get_active_surah_options(df_priorities):
    priority_lookup = {}
    if not df_priorities.empty:
        for _, row in df_priorities.iterrows():
            priority_lookup[row['surah_name']] = row['category']

    active_surahs = []
    for surah in SURAH_DATA:
        surah_name = surah[1]

        if surah_name == "Al-Fatihah":
            continue

        base_priority = priority_lookup.get(surah_name, "3 - Not Memorized")
        is_active = False
        for page_num in range(surah[2], surah[3] + 1):
            override_priority = get_page_priority(surah_name, page_num)
            final_priority = override_priority if override_priority else base_priority
            if final_priority in ["1 - Confident", "2 - Needs Revision"]:
                is_active = True
                break
        if is_active:
            active_surahs.append(f"{surah[0]}. {surah[1]}")

    return active_surahs

def build_dashboard_rows(df_logs, df_priorities):
    # Key last revised by (Surah_Name, Page_Number) to prevent boundary pages from leaking into unread Surahs
    page_last_revised = {(s[1], p): None for s in SURAH_DATA for p in range(s[2], s[3] + 1)}
    
    if not df_logs.empty:
        logs = df_logs.copy()
        logs['log_date'] = pd.to_datetime(logs['log_date']).dt.date
        for _, log in logs.iterrows():
            log_date = log['log_date']
            
            f_p = log.get('from_page')
            t_p = log.get('to_page')
            
            from_surah_str = str(log.get('from_surah') or '').strip()
            to_surah_str = str(log.get('to_surah') or '').strip() or from_surah_str
            
            f_match = [x for x in SURAH_DATA if f"{x[0]}. {x[1]}" == from_surah_str]
            t_match = [x for x in SURAH_DATA if f"{x[0]}. {x[1]}" == to_surah_str]

            # 1. Determine which Surahs were explicitly covered by this log session
            if f_match and t_match:
                num_start = min(f_match[0][0], t_match[0][0])
                num_end = max(f_match[0][0], t_match[0][0])
                covered_surahs = [x for x in SURAH_DATA if num_start <= x[0] <= num_end]
            elif f_match:
                covered_surahs = [f_match[0]]
            else:
                covered_surahs = SURAH_DATA # Fallback if only page numbers were logged without Surahs

            # 2. Extract start and end page bounds
            if pd.isna(f_p) or f_p == 0:
                if f_match: f_p = f_match[0][2]
            
            if pd.isna(t_p) or t_p == 0:
                if t_match: t_p = t_match[0][3]
                elif f_match: t_p = f_match[0][3]
                else: t_p = f_p 

            # 3. Only apply revision dates to pages belonging to the covered Surahs
            if pd.notna(f_p) and f_p > 0:
                f_p, t_p = int(f_p), int(t_p)
                start_page = min(f_p, t_p)
                end_page = max(f_p, t_p)
                
                for surah in covered_surahs:
                    s_name = surah[1]
                    s_start_p = surah[2]
                    s_end_p = surah[3]
                    
                    # Intersect the logged page range with the specific Surah's page range
                    p_start = max(start_page, s_start_p)
                    p_end = min(end_page, s_end_p)
                    
                    if p_start <= p_end:
                        for p in range(p_start, p_end + 1):
                            if 1 <= p <= 604:
                                key = (s_name, p)
                                if page_last_revised[key] is None or log_date > page_last_revised[key]:
                                    page_last_revised[key] = log_date

    priority_lookup = {}
    if not df_priorities.empty:
        for _, row in df_priorities.iterrows():
            priority_lookup[row['surah_name']] = row['category']

    # --- DYNAMIC REVISION CYCLE CALCULATION ---
    # First pass: Count total confident pages across all 604 pages
    confident_pages_count = 0
    for s in SURAH_DATA:
        base_priority = priority_lookup.get(s[1], "3 - Not Memorized")
        for p in range(s[2], s[3] + 1):
            override_priority = get_page_priority(s[1], p)
            final_prio = override_priority if override_priority else base_priority
            if s[1] == "Al-Fatihah":
                final_prio = "1 - Confident"
            if final_prio == "1 - Confident":
                confident_pages_count += 1

    # Determine revision cycle days based on % confident (out of 604 total pages)
    # 75% = 453 pages | 50% = 302 pages
    if confident_pages_count >= 453:
        cycle_days = 30
    elif confident_pages_count >= 302:
        cycle_days = 21
    else:
        cycle_days = 14

    rows = []
    today = date.today()
    for s in SURAH_DATA:
        surah_string = f"{s[0]}. {s[1]}"
        base_priority = priority_lookup.get(s[1], "3 - Not Memorized")
        for p in range(s[2], s[3] + 1):
            override_priority = get_page_priority(s[1], p)
            priority = override_priority if override_priority else base_priority

            if s[1] == "Al-Fatihah":
                priority = "1 - Confident"

            # Fetch revision specifically for THIS Surah on THIS page
            last_rev = page_last_revised.get((s[1], p))
            
            if priority == "3 - Not Memorized":
                status = "⚪ Not Started"
                score = 600000 + p
                next_due = ""
            elif last_rev is None:
                if priority == "1 - Confident":
                    status = "⏳ Pending (Cat 1)"
                    score = 300000 + p
                else: 
                    status = "⏳ Pending (Cat 2)"
                    score = 500000 + p
                next_due = ""
            else:
                days_since = (today - last_rev).days
                next_due = last_rev + timedelta(days=cycle_days)
                if days_since > cycle_days:
                    status = "🔴 Overdue"
                    score = 100000 + p
                elif days_since >= (cycle_days - 2):
                    status = "🟡 Due Soon"
                    score = 200000 + p
                else:
                    if priority == "2 - Needs Revision":
                        status = "🟡 Needs Revision"
                        score = 400000 + p 
                    else:
                        status = "🟢 Good"
                        score = 900000 + p

            rows.append({
                'Surah': surah_string,
                'Juz': get_juz(p),
                'Page': p,
                'Priority': priority,
                'Last Revised': last_rev.strftime('%Y-%m-%d') if last_rev else 'Never',
                'Next Revision Due': next_due.strftime('%Y-%m-%d') if isinstance(next_due, date) else '',
                'Status': status,
                'Score': score,
            })

    return pd.DataFrame(rows)
def calculate_user_streaks(df_logs):
    if df_logs.empty:
        return 0, 0

    # Extract unique, sorted dates
    dates = sorted(pd.to_datetime(df_logs['log_date']).dt.date.unique())
    if not dates:
        return 0, 0

    today = date.today()

    # 1. Calculate Longest Streak (Max Streak ever)
    max_streak = 1
    current_run = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current_run += 1
        elif (dates[i] - dates[i - 1]).days > 1:
            current_run = 1
        if current_run > max_streak:
            max_streak = current_run

    # 2. Calculate Current Active Streak
    latest_date = dates[-1]
    days_since_latest = (today - latest_date).days

    if days_since_latest > 1:
        current_streak = 0  # Streak broken
    else:
        current_streak = 1
        for i in range(len(dates) - 1, 0, -1):
            if (dates[i] - dates[i - 1]).days == 1:
                current_streak += 1
            else:
                break

    return current_streak, max_streak

def render_priority_manager(onboarding=False):
    def apply_page_range_priority(start_p, end_p, priority):
        for page_num in range(start_p, end_p + 1):
            for s in SURAH_DATA:
                if s[2] <= page_num <= s[3]:
                    if s[1] != "Al-Fatihah":
                        set_page_priority(s[1], page_num, priority)
                    
    def render_onboarding_tabs(target_priority, key_prefix):
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📖 Specific Surah(s)", "📚 Range of Surahs", "📄 Range of Pages", "🔸 Specific Juz(s)", "🔄 Range of Juzs"])
        surah_options_full = [f"{s[0]}. {s[1]}" for s in SURAH_DATA if s[1] != "Al-Fatihah"]
        juz_options = [f"Juz {i}" for i in range(1, 31)]

        with tab1:
            selected_surahs = st.multiselect("Select Surah(s)", options=surah_options_full, key=f"{key_prefix}_t1")
            if st.button("Apply", key=f"{key_prefix}_b1"):
                if selected_surahs:
                    for surah_label in selected_surahs:
                        surah_num = int(surah_label.split('. ', 1)[0])
                        surah_record = next(s for s in SURAH_DATA if s[0] == surah_num)
                        if surah_record[1] != "Al-Fatihah":
                            for page_num in range(surah_record[2], surah_record[3] + 1):
                                set_page_priority(surah_record[1], page_num, target_priority)
                    st.toast(f"✅ Applied to {target_priority}!")
                else:
                    st.warning("Please select at least one.")
        
        with tab2:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                start_s = st.selectbox("From Surah", options=surah_options_full, index=0, key=f"{key_prefix}_t2_start")
            with col_s2:
                end_s = st.selectbox("To Surah", options=surah_options_full, index=len(surah_options_full) - 1, key=f"{key_prefix}_t2_end")
            if st.button("Apply", key=f"{key_prefix}_b2"):
                num_start = int(start_s.split('. ', 1)[0])
                num_end = int(end_s.split('. ', 1)[0])
                if num_start > num_end:
                    st.error("❌ 'From Surah' must be before 'To Surah'.")
                else:
                    for s in SURAH_DATA:
                        if num_start <= s[0] <= num_end:
                            if s[1] != "Al-Fatihah":
                                for page_num in range(s[2], s[3] + 1):
                                    set_page_priority(s[1], page_num, target_priority)
                    st.toast(f"✅ Applied {start_s} to {end_s} to {target_priority}!")

        with tab3:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                start_p = st.number_input("From Page", min_value=1, max_value=604, value=1, step=1, key=f"{key_prefix}_t3_start")
            with col_p2:
                end_p = st.number_input("To Page", min_value=1, max_value=604, value=10, step=1, key=f"{key_prefix}_t3_end")
            if st.button("Apply", key=f"{key_prefix}_b3"):
                if start_p > end_p:
                    st.error("❌ 'From Page' must be before 'To Page'.")
                else:
                    apply_page_range_priority(start_p, end_p, target_priority)
                    st.toast(f"✅ Applied Pages {start_p}-{end_p} to {target_priority}!")

        with tab4:
            selected_juzs = st.multiselect("Select Juz(s)", options=juz_options, key=f"{key_prefix}_t4")
            if st.button("Apply", key=f"{key_prefix}_b4"):
                if selected_juzs:
                    for j_str in selected_juzs:
                        j_num = int(j_str.replace("Juz ", ""))
                        start_p, end_p = get_juz_page_range(j_num)
                        apply_page_range_priority(start_p, end_p, target_priority)
                    st.toast(f"✅ Applied to {target_priority}!")
                else:
                    st.warning("Please select at least one.")

        with tab5:
            col_j1, col_j2 = st.columns(2)
            with col_j1:
                start_j = st.selectbox("From Juz", options=juz_options, index=0, key=f"{key_prefix}_t5_start")
            with col_j2:
                end_j = st.selectbox("To Juz", options=juz_options, index=29, key=f"{key_prefix}_t5_end")
            if st.button("Apply", key=f"{key_prefix}_b5"):
                num_start = int(start_j.replace("Juz ", ""))
                num_end = int(end_j.replace("Juz ", ""))
                if num_start > num_end:
                    st.error("❌ 'From Juz' must be before 'To Juz'.")
                else:
                    for j_num in range(num_start, num_end + 1):
                        start_p, end_p = get_juz_page_range(j_num)
                        apply_page_range_priority(start_p, end_p, target_priority)
                    st.toast(f"✅ Applied {start_j} to {end_j} to {target_priority}!")

    def save_priorities_to_db(success_msg="✅ Page priorities permanently saved to the cloud!"):
        state = get_page_priority_state()
        try:
            supabase.table('page_priorities').delete().eq('user_name', user_email).execute()
            inserts = []
            for k, cat in state.items():
                surah_n, page_n = k.split("::")
                inserts.append({
                    "user_name": user_email,
                    "surah_name": surah_n,
                    "page_number": int(page_n),
                    "category": cat
                })
            if inserts:
                supabase.table('page_priorities').insert(inserts).execute()
            if not is_onboarded:
                supabase.table('surah_categories').insert([{"user_name": user_email, "surah_number": 0, "surah_name": "ONBOARDED", "category": "SYSTEM"}]).execute()
            st.success(success_msg)
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Database Save Error: {e}")

    # ==========================================================
    # ONBOARDING FLOW ONLY (Setup Page)
    # ==========================================================
    if onboarding:
        st.title("👋 Welcome to your Quran Tracker!")
        st.write("Let's build your baseline by answering two simple questions. *Al-Fatihah is excluded here and defaults to Confident automatically.*")
        
        if st.button("⏭️ Skip Setup & Go to Dashboard"):
            supabase.table('surah_categories').insert([{"user_name": user_email, "surah_number": 0, "surah_name": "ONBOARDED", "category": "SYSTEM"}]).execute()
            st.rerun()
            
        st.markdown("---")
        
        st.markdown("### 🟢 First, tell us what surahs/portions you are confident about?")
        st.write("These will be set to **Priority 1**.")
        render_onboarding_tabs("1 - Confident", "q1")
        
        st.markdown("---")
        
        st.markdown("### 🟡 Second, tell us what surahs you've memorized before but need revision?")
        st.write("These will be set to **Priority 2**.")
        render_onboarding_tabs("2 - Needs Revision", "q2")
        
        st.markdown("---")
        if st.button("💾 Complete Setup & Save to Cloud", type="primary", use_container_width=True):
            save_priorities_to_db("✅ Setup complete! Redirecting to Dashboard...")

    # ==========================================================
    # MANAGE PRIORITIES FLOW ONLY
    # ==========================================================
    else:
        st.title("🗂️ Manage Surah Priorities")
        st.write("Use the tools below to quickly update your active priorities. *Al-Fatihah is excluded here and defaults to Confident automatically.*")
        
        # --- CURRENT SETUP VIEWER ---
        st.markdown("#### 📊 Current Setup")
        
        priority_lookup = {}
        if not df_priorities.empty:
            for _, row in df_priorities.iterrows():
                priority_lookup[row['surah_name']] = row['category']
                
        setup_rows = []
        for s in SURAH_DATA:
            if s[1] == "Al-Fatihah":
                continue

            surah_name = s[1]
            base_priority = priority_lookup.get(surah_name, "3 - Not Memorized")
            
            page_priorities = set()
            for p in range(s[2], s[3] + 1):
                override = get_page_priority(surah_name, p)
                page_priorities.add(override if override else base_priority)
            
            if len(page_priorities) == 1:
                display_pri = list(page_priorities)[0]
            else:
                display_pri = "🔄 Mixed (Page-level overrides)"
                
            setup_rows.append({
                "No.": s[0],
                "Surah": s[1],
                "Current Priority": display_pri
            })
            
        st.dataframe(
            pd.DataFrame(setup_rows), 
            use_container_width=True, 
            hide_index=True, 
            height=250,
            column_config={
                "No.": st.column_config.NumberColumn("No.", width="small"),
                "Surah": st.column_config.TextColumn("Surah", width="medium"),
                "Current Priority": st.column_config.TextColumn("Priority Level")
            }
        )
        st.markdown("---")
        
        # --- NEW ASSIGNMENT METHOD (Mirroring Setup Page) ---
        st.markdown("### 🟢 Update confident surahs/portions")
        st.write("These will be set to **Priority 1**.")
        render_onboarding_tabs("1 - Confident", "m1")
        
        st.markdown("---")
        
        st.markdown("### 🟡 Update surahs/portions that need revision")
        st.write("These will be set to **Priority 2**.")
        render_onboarding_tabs("2 - Needs Revision", "m2")
        
        st.markdown("---")

        # --- SAVE BUTTON ---
        if st.button("💾 Save Page Priorities to Cloud", type="primary", use_container_width=True):
            save_priorities_to_db()

        # --- FACTORY RESET ---
        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")
        with st.expander("Need to start over?"):
            st.warning("This will permanently delete all your assigned priorities and send you back to the initial setup screen. Your daily study logs will NOT be deleted.")
            if st.button("🗑️ Reset All Priorities", type="secondary"):
                try:
                    supabase.table('page_priorities').delete().eq('user_name', user_email).execute()
                    supabase.table('surah_categories').delete().eq('user_name', user_email).execute()
                    
                    cache_key = f"page_priority_map_{user_email}"
                    if cache_key in st.session_state:
                        del st.session_state[cache_key]
                        
                    st.success("✅ Priorities reset! Redirecting to setup...")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to reset: {e}")

# --- NEW: ONBOARDING POP-UP DIALOG ---
@st.dialog("Welcome to your daily journey! 📖")
def show_intro_popup():
    step = st.session_state.get('intro_step', 1)
    
    if step == 1:
        st.subheader("Welcome to Quran Tracker Cloud!")
        st.write("The ultimate goal of this app is simple: to help you read, revise, and memorize the Quran every single day.")
        st.write("It does not matter how long it takes you to finish the Quran. Whether you can commit to 15 minutes, 30 minutes, or an hour a day—what truly matters is your consistency. This tool is designed to help you build and maintain a lifelong relationship with the Quran at your own pace.")
        
        if st.button("Next ➔", type="primary", use_container_width=True):
            st.session_state.intro_step = 2
            st.rerun()
            
    elif step == 2:
        st.subheader("Never Forget What You've Learned")
        st.write("Memorizing is great, but retaining it is harder. To make sure you never forget what you have already memorized, this app uses a smart ranking engine to build your daily tasks.")
        st.write("**1 - Confident:** We protect what you know. Pages you are confident in will be surfaced exactly when they need a quick review.")
        st.write("**2 - Needs Revision:** Next, we focus on pages you have memorized in the past but need some active work to lock them in.")
        st.write("**3 - Not Memorized:** Only after your previous memorization is secure will the app guide you to focus on brand-new pages.")
        
        col1, col2 = st.columns(2)
        if col1.button("⬅ Back", use_container_width=True):
            st.session_state.intro_step = 1
            st.rerun()
        if col2.button("Next ➔", type="primary", use_container_width=True):
            st.session_state.intro_step = 3
            st.rerun()
            
    elif step == 3:
        st.subheader("Setting Your Baseline")
        st.write("Before we can build your personalized **Next on The To-Do List**, we need to know where you currently stand.")
        st.write("In the next screen, you will be asked to assign your current memorization levels to the Surahs (or specific pages) you already know.")
        
        col1, col2 = st.columns(2)
        if col1.button("⬅ Back", use_container_width=True):
            st.session_state.intro_step = 2
            st.rerun()
        if col2.button("🚀 Start Setup", type="primary", use_container_width=True):
            st.session_state.intro_complete = True
            st.rerun()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.write(f"👤 Logged in as: **{user_email.split('@')[0]}**")
    with st.expander("🔑 Change Password"):
        with st.form("change_pass_form", clear_on_submit=True):
            new_pw = st.text_input("New Password", type="password", key="side_new_pw")
            confirm_pw = st.text_input("Confirm New Password", type="password", key="side_conf_pw")
            submit_pw = st.form_submit_button("Update Password", use_container_width=True)
            
            if submit_pw:
                if len(new_pw) < 6:
                    st.error("❌ Password must be at least 6 characters long.")
                elif new_pw != confirm_pw:
                    st.error("❌ Passwords do not match.")
                else:
                    try:
                        # Supabase updates the password for the currently active session
                        supabase.auth.update_user({"password": new_pw})
                        st.toast("✅ Password updated successfully!")
                        st.success("✅ Password updated!")
                    except Exception as e:
                        st.error(f"❌ Failed to update password: {e}")
    # --- NEW: EMAIL REMINDERS EXPANDER ---
    with st.expander("🔔 Daily Reminders"):
        current_settings = fetch_user_settings()
        
        with st.form("reminder_settings_form"):
            rem_enabled = st.checkbox("Enable Daily Email Reminders", value=current_settings.get("email_reminders", False))
            
            # Format time options in 12-hour AM/PM format
            time_options = [f"{h:02d}:00" for h in range(24)]
            time_labels = [datetime.strptime(t, "%H:%M").strftime("%I:00 %p") for t in time_options]
            
            curr_time_str = current_settings.get("reminder_time", "20:00")
            curr_index = time_options.index(curr_time_str) if curr_time_str in time_options else 20
            
            selected_time_label = st.selectbox("Preferred Time", options=time_labels, index=curr_index)
            selected_time = time_options[time_labels.index(selected_time_label)]
            
            submit_rem = st.form_submit_button("Save Reminder Settings", use_container_width=True)
            
            if submit_rem:
                try:
                    save_user_settings(rem_enabled, selected_time)
                    st.toast("✅ Reminder settings saved!")
                    st.success("✅ Settings saved!")
                except Exception as e:
                    st.error(f"❌ Could not save settings: {e}")
    if st.button("Logout", use_container_width=True):
        try:
            supabase.auth.sign_out()
        except Exception:
            pass

        # Safely attempt cookie deletion without crashing if already removed
        try:
            cookie_manager.delete("qt_access", key="del_access")
        except Exception:
            pass

        try:
            cookie_manager.delete("qt_refresh", key="del_refresh")
        except Exception:
            pass

        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["user"] = None
        
        time.sleep(0.3)
        st.rerun()
    st.markdown("---")
    
    if not is_onboarded:
        st.warning("⚠️ Setup Required")
        st.write("Please complete setup (or skip) to unlock the app.")
        page = "⚙️ Manage Priorities"
    else:
        page = st.radio("📌 Navigation", ["📊 Dashboard", "📝 Log Session", "📋 Next on The To-Do List", "📜 View History", "⚙️ Manage Priorities"], key="sidebar_nav")

# --- ONBOARDING GATE (UPDATED FOR POP-UP) ---
if not is_onboarded:
    if not st.session_state.get('intro_complete', False):
        show_intro_popup()
        st.title("👋 Welcome to your Quran Tracker!")
        st.info("Please complete the welcome pop-up to begin. If you accidentally closed it, click the button below.")
        if st.button("Re-open Welcome Guide"):
            st.rerun()
    else:
        render_priority_manager(onboarding=True)
    st.stop()

# --- GAMIFICATION BADGE ENGINE ---
def render_achievements_section(df_logs, df_dashboard, max_streak, total_hours):
    st.subheader("🏅 Achievements & Milestones")

    total_confident = df_dashboard[df_dashboard['Priority'] == '1 - Confident']['Page'].nunique()
    total_sessions = len(df_logs)

    badges = [
        {
            "title": "First Step",
            "icon": "🌱",
            "desc": "Logged your 1st session",
            "unlocked": total_sessions >= 1,
            "progress": f"{min(total_sessions, 1)}/1 session"
        },
        {
            "title": "Week Warrior",
            "icon": "🔥",
            "desc": "7-day streak reached",
            "unlocked": max_streak >= 7,
            "progress": f"{min(max_streak, 7)}/7 days"
        },
        {
            "title": "Monthly Master",
            "icon": "⚡",
            "desc": "30-day streak reached",
            "unlocked": max_streak >= 30,
            "progress": f"{min(max_streak, 30)}/30 days"
        },
        {
            "title": "Time Dedicated",
            "icon": "⏱️",
            "desc": "10+ Hours logged",
            "unlocked": total_hours >= 10,
            "progress": f"{min(total_hours, 10.0)}/10 hrs"
        },
        {
            "title": "Quarter Mark",
            "icon": "📐",
            "desc": "151 pages confident",
            "unlocked": total_confident >= 151,
            "progress": f"{min(total_confident, 151)}/151 pgs"
        },
        {
            "title": "Halfway Mark",
            "icon": "🏛️",
            "desc": "302 pages confident",
            "unlocked": total_confident >= 302,
            "progress": f"{min(total_confident, 302)}/302 pgs"
        },
        {
            "title": "100-Day Legend",
            "icon": "👑",
            "desc": "100-day streak reached",
            "unlocked": max_streak >= 100,
            "progress": f"{min(max_streak, 100)}/100 days"
        },
        {
            "title": "Hafiz Level",
            "icon": "🌟",
            "desc": "604 pages confident",
            "unlocked": total_confident >= 604,
            "progress": f"{total_confident}/604 pgs"
        }
    ]

    # Render badges in a 4-column responsive grid
    cols = st.columns(4)
    for idx, badge in enumerate(badges):
        col = cols[idx % 4]
        with col:
            if badge["unlocked"]:
                card_html = f"""
                <div style="background-color: rgba(212, 175, 55, 0.1); border: 1.5px solid #d4af37; border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 10px;">
                    <div style="font-size: 1.8rem;">{badge['icon']}</div>
                    <div style="font-weight: bold; color: #d4af37; font-size: 0.9rem; margin-top: 2px;">{badge['title']}</div>
                    <div style="font-size: 0.72rem; color: #e5e7eb; margin-top: 1px;">{badge['desc']}</div>
                    <div style="font-size: 0.68rem; color: #10b981; font-weight: bold; margin-top: 4px;">Unlocked!</div>
                </div>
                """
            else:
                card_html = f"""
                <div style="background-color: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 10px; text-align: center; opacity: 0.55; margin-bottom: 10px;">
                    <div style="font-size: 1.8rem; filter: grayscale(100%);">{badge['icon']}</div>
                    <div style="font-weight: bold; color: #9ca3af; font-size: 0.9rem; margin-top: 2px;">{badge['title']}</div>
                    <div style="font-size: 0.72rem; color: #6b7280; margin-top: 1px;">{badge['desc']}</div>
                    <div style="font-size: 0.68rem; color: #d1d5db; margin-top: 4px;">🔒 {badge['progress']}</div>
                </div>
                """
            st.markdown(card_html, unsafe_allow_html=True)

# --- PAGE 1: DASHBOARD ---
if page == "📊 Dashboard":
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.title("📊 Progress Dashboard")
    with head_col2:
        st.write("") 
        def jump_to_log():
            st.session_state.sidebar_nav = "📝 Log Session"
        st.button("📝 Log Session", type="primary", on_click=jump_to_log, use_container_width=True)
    df_logs = fetch_logs()
    df_dashboard = build_dashboard_rows(df_logs, df_priorities)

    # Global Progress Bar
    total_confident = df_dashboard[df_dashboard['Priority'] == '1 - Confident']['Page'].nunique()
    progress_pct = min(total_confident / 604.0, 1.0)
    st.markdown(f"### 🏆 Memorization Progress: {int(progress_pct * 100)}%")
    st.progress(progress_pct, text=f"{total_confident} out of 604 pages confidently memorized")
    st.markdown("---")
    # --- NEW: LAST SESSION CALLOUT ---
    if not df_logs.empty:
        # Sort logs to find the absolute newest one
        latest_log = df_logs.sort_values(by="log_date", ascending=False).iloc[0]
    
        l_date = pd.to_datetime(latest_log['log_date']).strftime('%B %d, %Y')
        l_mins = int(latest_log.get('minutes', 0))
    
        # Safely clean the data in case some fields are empty (NaN)
        f_surah_raw = "" if pd.isna(latest_log.get('from_surah')) else str(latest_log.get('from_surah')).strip()
        t_surah_raw = "" if pd.isna(latest_log.get('to_surah')) else str(latest_log.get('to_surah')).strip()
        f_page = 0 if pd.isna(latest_log.get('from_page')) else int(latest_log.get('from_page'))
        t_page = 0 if pd.isna(latest_log.get('to_page')) else int(latest_log.get('to_page'))
    
        # FIXED: Strip out the number prefix (e.g., "18. Al-Kahf" becomes "Al-Kahf")
        f_surah = f_surah_raw.split('. ', 1)[1] if '. ' in f_surah_raw else f_surah_raw
        t_surah = t_surah_raw.split('. ', 1)[1] if '. ' in t_surah_raw else t_surah_raw
    
        # Build the dynamic reading span text
        if not t_surah and t_page == 0:
            loc_str = f"Surah {f_surah} (Page {f_page})" if f_page > 0 else f"Surah {f_surah}"
        else:
            actual_t_surah = t_surah if t_surah else f_surah
    
            # Make it read cleanly if it's all within the same Surah
            if f_surah == actual_t_surah and f_page > 0 and t_page > 0:
                loc_str = f"Surah {f_surah} (Pages {f_page} to {t_page})"
            else:
                start_str = f"Surah {f_surah} (Page {f_page})" if f_page > 0 else f"Surah {f_surah}"
                end_str = f"Surah {actual_t_surah} (Page {t_page})" if t_page > 0 else f"Surah {actual_t_surah}"
                loc_str = f"from {start_str} to {end_str}"
    
        st.caption(f"🕒 **Last logged session:** {l_date} - {l_mins} min - {loc_str}")
    # --- NEXT ON TO-DO LIST ---
    df_actions = df_dashboard[(df_dashboard['Status'] != '🟢 Good') & (df_dashboard['Surah'] != '1. Al-Fatihah')].copy()
    if not df_actions.empty:
        top_action = df_actions.sort_values('Score').iloc[0]
        
        current_cat = top_action['Priority']
        surah_str = top_action['Surah']
        surah_name = surah_str.split('. ', 1)[1] # Extracts just the name!
        page_val = int(top_action['Page'])
        
        # FIXED: Using the clean 'surah_name' instead of 'surah_str' here
        st.info(f"🎯 **NEXT ON TO-DO LIST:** Start Reading from Surah {surah_name} (Page {page_val})")

        # --- BULLETPROOF CALLBACKS ---
        # The callbacks now accept explicit parameters to avoid Streamlit state bugs,
        # and execute microscopic, targeted database updates instead of bulk flushes.
        def upgrade_single_page(s_name, p_val, target_priority):
            set_page_priority(s_name, p_val, target_priority)
            try:
                supabase.table('page_priorities').delete().eq('user_name', user_email).eq('surah_name', s_name).eq('page_number', p_val).execute()
                supabase.table('page_priorities').insert({
                    "user_name": user_email,
                    "surah_name": s_name,
                    "page_number": p_val,
                    "category": target_priority
                }).execute()
            except Exception as e:
                st.error(f"Failed to update database: {e}")
            st.toast(f"✅ Page {p_val} upgraded to {target_priority.split(' - ')[1]}!")

        def upgrade_full_surah(s_str, target_priority):
            surah_record = next((s for s in SURAH_DATA if f"{s[0]}. {s[1]}" == s_str), None)
            if surah_record:
                s_name = surah_record[1]
                for p in range(surah_record[2], surah_record[3] + 1):
                    set_page_priority(s_name, p, target_priority)
                try:
                    supabase.table('page_priorities').delete().eq('user_name', user_email).eq('surah_name', s_name).execute()
                    inserts = [{"user_name": user_email, "surah_name": s_name, "page_number": p, "category": target_priority} for p in range(surah_record[2], surah_record[3] + 1)]
                    if inserts:
                        supabase.table('page_priorities').insert(inserts).execute()
                except Exception as e:
                    st.error(f"Failed to update database: {e}")
                st.toast(f"✅ {s_str} upgraded to {target_priority.split(' - ')[1]}!")
            else:
                st.toast("❌ Could not find the Surah in the database.")

        # --- NEXT ON TO-DO LIST BUTTONS ---
        if current_cat == "2 - Needs Revision":
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.button(f"🟢 I am confident of Surah {surah_name}", on_click=upgrade_full_surah, args=(surah_str, "1 - Confident"), use_container_width=True)
            with col_b2:
                st.button(f"🟢 I'm confident of page {page_val} of Surah {surah_name}", on_click=upgrade_single_page, args=(surah_name, page_val, "1 - Confident"), use_container_width=True)
                
        elif current_cat == "3 - Not Memorized":
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.button(f"🟡 Surah {surah_name} needs revision", on_click=upgrade_full_surah, args=(surah_str, "2 - Needs Revision"), use_container_width=True)
            with col_b2:
                st.button(f"🟡 Page {page_val} of Surah {surah_name} needs revision", on_click=upgrade_single_page, args=(surah_name, page_val, "2 - Needs Revision"), use_container_width=True)
                
    else:
        st.success("🎉 **NEXT ON TO-DO LIST:** All caught up! No pages are due for revision.")
    # --------------------------------

    total_sessions = len(df_logs)
    total_hours = round(df_logs['minutes'].sum() / 60, 1) if not df_logs.empty else 0

    # Calculate both active and maximum streak
    current_streak, max_streak = calculate_user_streaks(df_logs)

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Current Streak", f"{current_streak} Days")
    col2.metric("⏱️ Total Time Spent", f"{total_hours} Hours")
    col3.metric("📅 Total Sessions", total_sessions)

    st.markdown("---")

    df_active = df_dashboard[(df_dashboard['Priority'].isin(["1 - Confident", "2 - Needs Revision"])) & (df_dashboard['Surah'] != '1. Al-Fatihah')].copy()
    if df_active.empty:
        st.info("No active priority surahs yet. Use the Manage Priorities page to assign some.")
    else:
        st.subheader("📚 Visual Progress Timeline")
        st.write("Tap any block on the timeline below to view its revision details.")
        
        # Filter out Al-Fatihah
        df_timeline = df_dashboard[df_dashboard['Surah'] != '1. Al-Fatihah'].copy()
        df_timeline['Clean_Surah'] = df_timeline['Surah'].apply(lambda x: x.split('. ', 1)[1] if '. ' in x else x)

        # --- 1. AGGREGATE PER PHYSICAL PAGE ---
        aggregated_rows = []
        for p_num, group in df_timeline.groupby('Page', sort=True):
            sorted_group = group.sort_values('Score')
            top_row = sorted_group.iloc[0].copy()
            
            all_surahs = group['Clean_Surah'].unique()
            top_row['Clean_Surah'] = " / ".join(all_surahs)
            aggregated_rows.append(top_row)

        chart_df = pd.DataFrame(aggregated_rows)

        # --- 2. CALCULATE JUZ OFFSETS & CENTER POINTS FOR TEXT ---
        def get_juz_start(juz_num):
            juz_starts = [1, 22, 42, 62, 82, 102, 122, 142, 162, 182, 202, 222, 242, 262, 282, 302, 322, 342, 362, 382, 402, 422, 442, 462, 482, 502, 522, 542, 562, 582]
            return juz_starts[int(juz_num) - 1]

        chart_df['Juz_Start'] = chart_df['Juz'].apply(get_juz_start)
        chart_df['Relative_Page'] = chart_df['Page'] - chart_df['Juz_Start'] + 1
        chart_df['Relative_Page_End'] = chart_df['Relative_Page'] + 1
        chart_df['Center_Page'] = chart_df['Relative_Page'] + 0.5  # Centers numbers inside each cell

        # FIXED: Distinct High-Contrast Palette
        status_domain = ["🟢 Good", "🟡 Due Soon", "🟡 Needs Revision", "🔴 Overdue", "⏳ Pending (Cat 1)", "⏳ Pending (Cat 2)", "⚪ Not Started"]
        status_colors = [
            "#10b981",  # Emerald Green
            "#ddd012",  # Bright Electric Yellow (Due Soon)
            "#F57F17",  # Deep Blaze Orange (Needs Revision - very distinct!)
            "#ef4444",  # Ruby Red
            "#3b82f6",  # Sky Blue
            "#8b5cf6",  # Deep Purple
            "#BDBDBD"   # Dark Charcoal
        ]

        # --- 3. BUILD LAYERED ALTAIR CHART (Rectangles + Page Numbers) ---
        click = alt.selection_point(name='click', fields=['Page'])

        base_chart = alt.Chart(chart_df)

        # Layer A: Colored Rectangles
        rects = base_chart.mark_rect(
            stroke='#022c22',
            strokeWidth=1.5,
            cornerRadius=2
        ).encode(
            x=alt.X('Relative_Page:Q', title="Page within Juz", axis=alt.Axis(labels=False, ticks=False, grid=False)),
            x2='Relative_Page_End:Q',
            y=alt.Y('Juz:O', title="Juz", sort=alt.EncodingSortField(field="Juz", order="ascending")),
            color=alt.Color('Status:N', scale=alt.Scale(domain=status_domain, range=status_colors), legend=alt.Legend(title="Status", orient="bottom", columns=3)),
            opacity=alt.condition(click, alt.value(1.0), alt.value(0.3))
        )

        # Layer B: Page Number Labels
        text = base_chart.mark_text(
            baseline='middle',
            align='center',
            fontSize=8,
            fontWeight='bold'
        ).encode(
            x=alt.X('Center_Page:Q'),
            y=alt.Y('Juz:O'),
            text=alt.Text('Page:Q'),
            color=alt.condition(
                (alt.datum.Status == '⚪ Not Started') | (alt.datum.Status == '🔴 Overdue') | (alt.datum.Status == '⏳ Pending (Cat 2)'),
                alt.value('#ffffff'),
                alt.value('#022c22')
            ),
            opacity=alt.condition(click, alt.value(1.0), alt.value(0.3))
        )

        timeline_chart = (rects + text).add_params(click).properties(height=600)

        chart_event = st.altair_chart(timeline_chart, use_container_width=True, theme=None, on_select="rerun")

        # --- 4. RENDER TAP DETAILS ---
        if chart_event and chart_event.selection and "click" in chart_event.selection:
            selections = chart_event.selection["click"]
            if selections:
                selected_page = selections[0]["Page"]
                
                page_surahs = df_dashboard[(df_dashboard['Page'] == selected_page) & (df_dashboard['Surah'] != '1. Al-Fatihah')]
                
                if len(page_surahs) == 1:
                    r = page_surahs.iloc[0]
                    c_name = r['Surah'].split('. ', 1)[1] if '. ' in r['Surah'] else r['Surah']
                    next_due_str = f" &nbsp; | &nbsp; **Next Due:** {r['Next Revision Due']}" if r['Next Revision Due'] else ""
                    st.success(
                        f"**📖 Surah {c_name}** (Page {selected_page} | Juz {r['Juz']})  \n"
                        f"**📊 Status:** {r['Status']}  \n"
                        f"**📅 Last Revised:** {r['Last Revised']}{next_due_str}"
                    )
                elif len(page_surahs) > 1:
                    juz_num = page_surahs.iloc[0]['Juz']
                    surah_lines = []
                    for _, r in page_surahs.iterrows():
                        c_name = r['Surah'].split('. ', 1)[1] if '. ' in r['Surah'] else r['Surah']
                        due_info = f" | Next Due: {r['Next Revision Due']}" if r['Next Revision Due'] else ""
                        surah_lines.append(f"• **Surah {c_name}**: {r['Status']} (Last Revised: {r['Last Revised']}{due_info})")
                    
                    details_text = "  \n".join(surah_lines)
                    st.success(
                        f"**📖 Page {selected_page} (Juz {juz_num}) — Contains {len(page_surahs)} Surahs:**  \n"
                        f"{details_text}"
                    )
            else:
                st.info("👆 Tap any colored block on the timeline above to see page details.")
        else:
            st.info("👆 Tap any colored block on the timeline above to see page details.")

        st.markdown("---")
        
        # --- NEW: RENDER ACHIEVEMENTS & BADGES ---
        render_achievements_section(df_logs, df_dashboard, max_streak, total_hours)

        st.markdown("---")
        col_pie, col_chart = st.columns(2)
        with col_pie:
            st.subheader("📊 Priority Distribution")
            priority_counts = build_priority_counts(df_priorities)
            chart = alt.Chart(priority_counts).mark_arc().encode(
                theta="Count",
                color=alt.Color("Priority", scale=alt.Scale(domain=["1 - Confident", "2 - Needs Revision", "3 - Not Memorized"], range=["#2E7D32", "#F57F17", "#BDBDBD"])),
                tooltip=["Priority", "Count"]
            ).properties(width=300, height=300)
            st.altair_chart(chart, use_container_width=True)

        with col_chart:
            st.subheader("📈 Consistency (Last 14 Days)")
            if not df_logs.empty:
                last_14 = date.today() - timedelta(days=14)
                recent_logs = df_logs.copy()
                recent_logs['log_date'] = pd.to_datetime(recent_logs['log_date']).dt.date
                recent_logs = recent_logs[recent_logs['log_date'] >= last_14]
                
                if not recent_logs.empty:
                    pages_read_list = []
                    for _, log in recent_logs.iterrows():
                        f_p = log.get('from_page')
                        t_p = log.get('to_page')
                        
                        from_surah_str = str(log.get('from_surah') or '').strip()
                        to_surah_str = str(log.get('to_surah') or '').strip() or from_surah_str
                        
                        f_match = [x for x in SURAH_DATA if f"{x[0]}. {x[1]}" == from_surah_str]
                        t_match = [x for x in SURAH_DATA if f"{x[0]}. {x[1]}" == to_surah_str]

                        if pd.isna(f_p) or f_p == 0:
                            if f_match: f_p = f_match[0][2]
                        
                        if pd.isna(t_p) or t_p == 0:
                            if t_match: t_p = t_match[0][3]
                            elif f_match: t_p = f_match[0][3]
                            else: t_p = f_p
                            
                        if pd.notna(f_p) and pd.notna(t_p) and f_p > 0:
                            pages = abs(int(t_p) - int(f_p)) + 1
                        else:
                            pages = 0
                            
                        pages_read_list.append(pages)
                        
                    recent_logs['Pages Read'] = pages_read_list
                    
                    daily_counts = recent_logs.groupby('log_date')['Pages Read'].sum().reset_index()
                    st.line_chart(daily_counts.set_index('log_date'))
                else:
                    st.write("No logs in the last 14 days.")

# --- PAGE 2: LOG SESSION ---
elif page == "📝 Log Session":
    st.title("📝 Log Your Revision")
    
    active_surah_options = [""] + get_active_surah_options(df_priorities)
    
    # Split into two tabs: Single Entry vs Bulk Upload
    tab_single, tab_bulk = st.tabs(["📝 Log Single Session", "📤 Bulk Import from Excel"])
    
    # --- TAB 1: SINGLE LOG FORM ---
    with tab_single:
        with st.form("daily_log_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                log_date = st.date_input("Date", date.today())
                from_surah = st.selectbox("From Surah*", options=active_surah_options)
                from_page = st.number_input("From Page (Optional)", min_value=0, max_value=604, value=0, step=1)
            with col2:
                minutes = st.number_input("Minutes Spent*", min_value=1, value=15, step=5)
                to_surah = st.selectbox("To Surah (Optional)", options=[""] + active_surah_options)
                to_page = st.number_input("To Page (Optional)", min_value=0, max_value=604, value=0, step=1)
            
            notes = st.text_input("Notes / Specific Verses")
            submitted = st.form_submit_button("💾 Save Session to Cloud")
            
            if submitted:
                if to_page > 0 and from_page > 0 and to_page < from_page:
                    st.error("❌ Validation Error: 'To Page' cannot be smaller than 'From Page'.")
                elif minutes > 300:
                    st.error("❌ Validation Error: Session exceeds 5 hours (300 mins).")
                elif not from_surah:
                    st.error("❌ Validation Error: Please select a 'From Surah'.")
                else:
                    new_log = {
                        "user_name": user_email,
                        "log_date": str(log_date),
                        "from_surah": from_surah if from_surah else None,
                        "to_surah": to_surah if to_surah else None,
                        "from_page": int(from_page) if from_page and from_page > 0 else None,
                        "to_page": int(to_page) if to_page and to_page > 0 else None,
                        "minutes": minutes,
                        "notes": notes
                    }
                    supabase.table('daily_logs').insert(new_log).execute()
                    
                    st.toast("✅ Log saved successfully!")
                    st.balloons()

    # --- TAB 2: BULK EXCEL IMPORTER ---
    with tab_bulk:
        st.subheader("📤 Import Past History from Excel")
        st.write("Upload your existing Quran Tracker Excel or CSV file to instantly transfer your previous logs to your cloud account.")
        # --- SAMPLE TEMPLATE GENERATOR ---
        import io
        template_df = pd.DataFrame([
            {
                "Date": "2026-08-01",
                "From Surah": "18. Al-Kahf",
                "To Surah": "18. Al-Kahf",
                "From Page": 293,
                "To Page": 295,
                "Minutes Spent": 20,
                "Notes": "Example log entry"
            }
        ])
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Logs')
            
        st.download_button(
            label="📥 Download Excel Template",
            data=buffer.getvalue(),
            file_name="Quran_Tracker_Import_Template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.markdown("---")
        uploaded_file = st.file_uploader("Upload Excel (.xlsx) or CSV file", type=["xlsx", "csv"])
        
        if uploaded_file:
            try:
                # Read Excel or CSV
                if uploaded_file.name.endswith('.csv'):
                    import_df = pd.read_csv(uploaded_file)
                else:
                    import_df = pd.read_excel(uploaded_file)
                
                st.write("📋 **Preview of Data to Import:**")
                st.dataframe(import_df.head(10), use_container_width=True)
                
                if st.button("🚀 Import All Logs to Cloud", type="primary"):
                    rows_to_insert = []
                    
                    for _, row in import_df.iterrows():
                        # Standardize column headers (flexible column matching)
                        row_dict = {str(k).strip().lower(): v for k, v in row.to_dict().items()}
                        
                        # Helper function to extract value cleanly
                        def get_col(possible_names, is_int=False):
                            for name in possible_names:
                                if name in row_dict and pd.notna(row_dict[name]):
                                    val = row_dict[name]
                                    if is_int:
                                        try: return int(float(val))
                                        except: return None
                                    return str(val).strip()
                            return None

                        # Extract fields
                        raw_date = get_col(['log_date', 'date', 'log date'])
                        if not raw_date:
                            continue  # Skip rows without a date
                            
                        formatted_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d')
                        f_surah = get_col(['from_surah', 'from surah', 'surah', 'from'])
                        t_surah = get_col(['to_surah', 'to surah', 'to'])
                        f_page = get_col(['from_page', 'from page', 'page start', 'start page'], is_int=True)
                        t_page = get_col(['to_page', 'to page', 'page end', 'end page'], is_int=True)
                        mins = get_col(['minutes', 'minutes spent', 'mins', 'time'], is_int=True) or 15
                        nts = get_col(['notes', 'note', 'comments'])

                        rows_to_insert.append({
                            "user_name": user_email,
                            "log_date": formatted_date,
                            "from_surah": f_surah,
                            "to_surah": t_surah,
                            "from_page": f_page,
                            "to_page": t_page,
                            "minutes": mins,
                            "notes": nts
                        })

                    if rows_to_insert:
                        supabase.table('daily_logs').insert(rows_to_insert).execute()
                        st.success(f"🎉 Successfully imported {len(rows_to_insert)} session logs!")
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("❌ Could not parse any valid rows from the file. Please check your column headers.")
                        
            except Exception as e:
                st.error(f"❌ Failed to parse file: {e}")

# --- PAGE 3: Next on The To-Do List  ---
elif page == "📋 Next on The To-Do List":
    st.title("📋 Next on The To-Do List")
    st.write("This view mirrors the workbook's live ranking engine and surfaces the top pages that need attention.")

    df_logs = fetch_logs()
    df_dashboard = build_dashboard_rows(df_logs, df_priorities)
    df_actions = df_dashboard[(df_dashboard['Status'] != '🟢 Good') & (df_dashboard['Surah'] != '1. Al-Fatihah')].copy()

    if df_actions.empty:
        st.success("🎉 All caught up! No pages are due for revision today.")
    else:
        df_top = df_actions.sort_values('Score').head(25)
        display_df = df_top[['Status', 'Surah', 'Juz', 'Page', 'Priority', 'Last Revised', 'Next Revision Due']]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
       

# --- PAGE 4: VIEW HISTORY ---
elif page == "📜 View History":
    st.title("📜 Complete Study History")
    df_logs = fetch_logs()
    if df_logs.empty:
        st.info("No logs found.")
    else:
        df_logs = df_logs.sort_values(by="log_date", ascending=False).reset_index(drop=True)
        if 'id' in df_logs.columns:
            df_logs['__row_id'] = df_logs['id']
        else:
            df_logs['__row_id'] = [f"row_{i}" for i in range(len(df_logs))]
        df_logs['Delete'] = False

        editable_history = st.data_editor(
            df_logs[['__row_id', 'log_date', 'from_surah', 'to_surah', 'from_page', 'to_page', 'minutes', 'notes', 'Delete']],
            hide_index=True,
            use_container_width=True,
            disabled=['__row_id'],
            column_config={
                '__row_id': None,
                'Delete': st.column_config.CheckboxColumn('Delete', help='Select rows to delete'),
                'log_date': st.column_config.TextColumn('Date'),
                'from_surah': st.column_config.TextColumn('From Surah'),
                'to_surah': st.column_config.TextColumn('To Surah'),
                'from_page': st.column_config.NumberColumn('From Page', step=1),
                'to_page': st.column_config.NumberColumn('To Page', step=1),
                'minutes': st.column_config.NumberColumn('Minutes', step=1),
                'notes': st.column_config.TextColumn('Notes')
            },
            key='history_editor'
        )

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            with col1:
                if st.button("💾 Save Changes"):
                    def clean_val(val, is_int=False):
                        if pd.isna(val): return None
                        s_val = str(val).strip()
                        if s_val.lower() in ['', 'nan', 'none', '<na>']: return None
                        return int(float(s_val)) if is_int else s_val

                    for _, row in editable_history.iterrows():
                        if row['Delete']: continue
                        row_id = row['__row_id']
                        
                        payload = {
                            'log_date': clean_val(row['log_date']),
                            'from_surah': clean_val(row['from_surah']),
                            'to_surah': clean_val(row['to_surah']),
                            'from_page': clean_val(row['from_page'], is_int=True),
                            'to_page': clean_val(row['to_page'], is_int=True),
                            'minutes': clean_val(row['minutes'], is_int=True),
                            'notes': clean_val(row['notes'])
                        }
                        
                        try:
                            supabase.table('daily_logs').update(payload).eq('id', row_id).execute()
                        except Exception:
                            if row_id.startswith('row_'): continue
                            else: raise
                    st.success("✅ History updated.")
                    st.rerun()

        with col2:
            if st.button("🗑️ Delete Selected"):
                for _, row in editable_history.iterrows():
                    if row['Delete']:
                        row_id = row['__row_id']
                        try:
                            supabase.table('daily_logs').delete().eq('id', row_id).execute()
                        except Exception:
                            if not row_id.startswith('row_'): raise
                st.success("✅ Selected entries deleted.")
                st.rerun()

        with col3:
            if st.button("🧹 Reset All History", type="secondary"):
                supabase.table('daily_logs').delete().eq('user_name', user_email).execute()
                st.success("✅ All history cleared.")
                st.rerun()

# --- PAGE 5: MANAGE PRIORITIES ---
elif page == "⚙️ Manage Priorities":
    render_priority_manager(onboarding=False)