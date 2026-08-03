import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date, timedelta, datetime
import altair as alt
import extra_streamlit_components as stx
import time

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
st.set_page_config(page_title="Quran Tracker Cloud", layout="wide", initial_sidebar_state="expanded")

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

def render_login():
    st.title("🔐 Login to Quran Tracker")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
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
    page_last_revised = {p: None for p in range(1, 605)}
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

            if pd.isna(f_p) or f_p == 0:
                if f_match: f_p = f_match[0][2]
            
            if pd.isna(t_p) or t_p == 0:
                if t_match: t_p = t_match[0][3]
                elif f_match: t_p = f_match[0][3]
                else: t_p = f_p 

            if pd.notna(f_p) and f_p > 0:
                f_p, t_p = int(f_p), int(t_p)
                start_page = min(f_p, t_p)
                end_page = max(f_p, t_p)
                
                for p in range(start_page, end_page + 1):
                    if 1 <= p <= 604:
                        if page_last_revised[p] is None or log_date > page_last_revised[p]:
                            page_last_revised[p] = log_date

    priority_lookup = {}
    if not df_priorities.empty:
        for _, row in df_priorities.iterrows():
            priority_lookup[row['surah_name']] = row['category']

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

            last_rev = page_last_revised[p]
            
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
                next_due = last_rev + timedelta(days=14)
                if days_since > 14:
                    status = "🔴 Overdue"
                    score = 100000 + p
                elif days_since >= 12:
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
    if st.button("Logout"):
        supabase.auth.sign_out()

        cookie_manager.delete("qt_access", key="del_access")
        cookie_manager.delete("qt_refresh", key="del_refresh")

        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["user"] = None
        
        time.sleep(0.5)
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

        if current_cat == "2 - Needs Revision":
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.button(f"🟢 I am confident of Surah {surah_str}", on_click=upgrade_full_surah, args=(surah_str, "1 - Confident"), use_container_width=True)
            with col_b2:
                st.button(f"🟢 I'm confident of page {page_val} of {surah_str}", on_click=upgrade_single_page, args=(surah_name, page_val, "1 - Confident"), use_container_width=True)
                
        elif current_cat == "3 - Not Memorized":
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                st.button(f"🟡 Surah {surah_str} needs revision", on_click=upgrade_full_surah, args=(surah_str, "2 - Needs Revision"), use_container_width=True)
            with col_b2:
                st.button(f"🟡 page {page_val} of {surah_str} need revision", on_click=upgrade_single_page, args=(surah_name, page_val, "2 - Needs Revision"), use_container_width=True)
                
    else:
        st.success("🎉 **NEXT ON TO-DO LIST:** All caught up! No pages are due for revision.")
    # --------------------------------

    total_sessions = len(df_logs)
    total_hours = round(df_logs['minutes'].sum() / 60, 1) if not df_logs.empty else 0

    streak = 0
    if not df_logs.empty:
        df_logs_work = df_logs.copy()
        df_logs_work['log_date'] = pd.to_datetime(df_logs_work['log_date']).dt.date
        unique_dates = sorted(df_logs_work['log_date'].unique(), reverse=True)
        today = date.today()
        if today in unique_dates or (today - timedelta(days=1)) in unique_dates:
            current = today if today in unique_dates else today - timedelta(days=1)
            streak = 1
            for d in unique_dates:
                if d == current:
                    continue
                if d == current - timedelta(days=1):
                    streak += 1
                    current = d
                else:
                    break

    col1, col2, col3 = st.columns(3)
    col1.metric("🔥 Current Streak", f"{streak} Days")
    col2.metric("⏱️ Total Time Spent", f"{total_hours} Hours")
    col3.metric("📅 Total Sessions", total_sessions)

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

    st.markdown("---")

    df_active = df_dashboard[(df_dashboard['Priority'].isin(["1 - Confident", "2 - Needs Revision"])) & (df_dashboard['Surah'] != '1. Al-Fatihah')].copy()
    if df_active.empty:
        st.info("No active priority surahs yet. Use the Manage Priorities page to assign some.")
    else:
        df_active = df_dashboard[(df_dashboard['Priority'].isin(["1 - Confident", "2 - Needs Revision"])) & (df_dashboard['Surah'] != '1. Al-Fatihah')].copy()
    if df_active.empty:
        st.info("No active priority surahs yet. Use the Manage Priorities page to assign some.")
    else:
        st.subheader("📚 Visual Progress Timeline")
        st.write("Hover over any segment of the timeline to see exact page details, revision status, and due dates.")
        
       # We use the FULL dashboard dataframe so the timeline represents the entire Quran
        chart_df = df_dashboard[df_dashboard['Surah'] != '1. Al-Fatihah'].copy()
        
        # Create an 'End Page' for the rectangles so every single page renders as a continuous block
        chart_df['Page_End'] = chart_df['Page'] + 1
        
        # Clean up the Surah name for the tooltip
        chart_df['Clean_Surah'] = chart_df['Surah'].apply(lambda x: x.split('. ', 1)[1] if '. ' in x else x)
        
        # --- FIXED 1: Add a dummy variable to force the rectangles to have thickness ---
        chart_df['Timeline'] = "Quran Progress"
        
        # Define the exact colors to match our new Islamic Theme
        status_domain = [
            "🟢 Good", 
            "🟡 Due Soon", 
            "🟡 Needs Revision", 
            "🔴 Overdue", 
            "⏳ Pending (Cat 1)", 
            "⏳ Pending (Cat 2)", 
            "⚪ Not Started"
        ]
        status_colors = [
            "#10b981", # Emerald Green
            "#fde047", # Soft Yellow
            "#f59e0b", # Orange
            "#ef4444", # Red
            "#3b82f6", # Blue
            "#8b5cf6", # Purple
            "#1f2937"  # Dark Slate (blends into the background for unstarted pages)
        ]
        
        # Build the horizontal ribbon chart
        timeline_chart = alt.Chart(chart_df).mark_rect().encode(
            x=alt.X('Page:Q', scale=alt.Scale(domain=[2, 605]), title="Quran Page Number", axis=alt.Axis(tickCount=10, grid=False)),
            x2='Page_End:Q',
            # --- FIXED 1: Map the Y-axis and hide the labels so it just looks like a floating ribbon ---
            y=alt.Y('Timeline:N', title=None, axis=alt.Axis(labels=False, ticks=False, domain=False)),
            color=alt.Color('Status:N', scale=alt.Scale(domain=status_domain, range=status_colors), legend=alt.Legend(title="Status", orient="bottom", columns=4)),
            tooltip=[
                alt.Tooltip('Clean_Surah:N', title='Surah'),
                alt.Tooltip('Page:Q', title='Page'),
                alt.Tooltip('Status:N', title='Status'),
                alt.Tooltip('Last Revised:N', title='Last Revised'),
                alt.Tooltip('Next Revision Due:N', title='Due Date')
            ]
        ).properties(
            height=120 
        ).interactive() 
        
        # --- FIXED 2: Tell Streamlit to respect our custom Islamic colors (theme=None) ---
        st.altair_chart(timeline_chart, use_container_width=True, theme=None)
        
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
    st.title("📝 Log Today's Revision")
    
    active_surah_options = [""] + get_active_surah_options(df_priorities)
    
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
                st.error("❌ Validation Error: Session exceeds 5 hours (300 mins). Please enter a realistic time to keep your data accurate.")
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