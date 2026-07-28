import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date, timedelta
import altair as alt

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

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Quran Tracker Cloud", layout="wide", initial_sidebar_state="expanded")

if "sidebar_nav" not in st.session_state:
    st.session_state.sidebar_nav = "📊 Dashboard"

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
                st.rerun()
            except Exception:
                st.error("Login failed. Check your credentials.")

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
            t_p = log.get('to_page') if pd.notna(log.get('to_page')) and log.get('to_page') > 0 else f_p

            if pd.isna(f_p) or f_p == 0:
                from_surah = str(log.get('from_surah') or '').strip()
                to_surah = str(log.get('to_surah') or '').strip() or from_surah
                f_match = [x for x in SURAH_DATA if f"{x[0]}. {x[1]}" == from_surah]
                t_match = [x for x in SURAH_DATA if f"{x[0]}. {x[1]}" == to_surah]
                if f_match: f_p = f_match[0][2]
                if t_match: t_p = t_match[0][3]
                elif f_match: t_p = f_match[0][3]

            if pd.notna(f_p) and f_p > 0:
                f_p, t_p = int(f_p), int(t_p)
                for p in range(f_p, t_p + 1):
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
            last_rev = page_last_revised[p]
            
            if priority == "3 - Not Memorized":
                status = "⚪ Not Started"
                score = 500000 + p
                next_due = ""
            elif last_rev is None:
                status = "⏳ Pending"
                score = 200000 + p
                next_due = ""
            else:
                days_since = (today - last_rev).days
                next_due = last_rev + timedelta(days=14)
                if days_since > 14:
                    status = "🔴 Overdue"
                    score = 100000 + p
                elif days_since >= 11:
                    status = "🟡 Due Soon"
                    score = 400000 + p
                else:
                    if priority == "2 - Needs Revision":
                        status = "🟡 Needs Revision"
                        score = 300000 + p
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
    if onboarding:
        st.title("👋 Welcome to your Quran Tracker!")
        st.write("Assign priorities to your Surahs or pages below to build your baseline.")
        
        if st.button("⏭️ Skip Setup & Go to Dashboard"):
            supabase.table('surah_categories').insert([{"user_name": user_email, "surah_number": 0, "surah_name": "ONBOARDED", "category": "SYSTEM"}]).execute()
            st.rerun()
            
        st.markdown("---")
    else:
        st.title("🗂️ Manage Surah Priorities")
        st.write("Use the tools below to quickly update your active priorities.")

    # --- QUICK ADD JUZ SECTION ---
    def apply_juz_priority(start_surah, end_surah, priority):
        for s in SURAH_DATA:
            if start_surah <= s[0] <= end_surah:
                for page_num in range(s[2], s[3] + 1):
                    set_page_priority(s[1], page_num, priority)

    st.markdown("#### ⚡ Quick Adds")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        if st.button("🟢 Set Juz 30 to Priority 1", use_container_width=True):
            apply_juz_priority(78, 114, "1 - Confident")
            st.toast("✅ Juz 30 updated! Remember to click Save below.")
        if st.button("🟢 Set Juz 29 to Priority 1", use_container_width=True):
            apply_juz_priority(67, 77, "1 - Confident")
            st.toast("✅ Juz 29 updated! Remember to click Save below.")
    with q_col2:
        if st.button("🟡 Set Juz 30 to Priority 2", use_container_width=True):
            apply_juz_priority(78, 114, "2 - Needs Revision")
            st.toast("✅ Juz 30 updated! Remember to click Save below.")
        if st.button("🟡 Set Juz 29 to Priority 2", use_container_width=True):
            apply_juz_priority(67, 77, "2 - Needs Revision")
            st.toast("✅ Juz 29 updated! Remember to click Save below.")
            
    st.markdown("---")
    
    # --- TAB-BASED ASSIGNMENT UI ---
    st.markdown("#### 🎯 Assign Priorities")
    tab1, tab2, tab3 = st.tabs(["📖 Specific Surah(s)", "📚 Range of Surahs", "📄 Range of Pages"])
    
    priority_options = ["1 - Confident", "2 - Needs Revision", "3 - Not Memorized"]
    surah_options_full = [f"{s[0]}. {s[1]}" for s in SURAH_DATA]
    
    with tab1:
        st.write("Select one or more specific Surahs from the list.")
        selected_surahs = st.multiselect("Select Surah(s)", options=surah_options_full, key="tab1_surahs")
        t1_priority = st.selectbox("Priority to apply", priority_options, key="tab1_pri")
        if st.button("Apply to Selected Surah(s)", key="btn_tab1"):
            if selected_surahs:
                for surah_label in selected_surahs:
                    surah_num = int(surah_label.split('. ', 1)[0])
                    surah_record = next(s for s in SURAH_DATA if s[0] == surah_num)
                    for page_num in range(surah_record[2], surah_record[3] + 1):
                        set_page_priority(surah_record[1], page_num, t1_priority)
                st.success("✅ Priorities applied! Remember to click Save below.")
            else:
                st.warning("Please select at least one Surah.")
                
    with tab2:
        st.write("Apply a priority to a continuous range of Surahs.")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            start_s = st.selectbox("From Surah", options=surah_options_full, index=0, key="tab2_start")
        with col_s2:
            end_s = st.selectbox("To Surah", options=surah_options_full, index=113, key="tab2_end")
            
        t2_priority = st.selectbox("Priority to apply", priority_options, key="tab2_pri")
        if st.button("Apply to Surah Range", key="btn_tab2"):
            num_start = int(start_s.split('. ', 1)[0])
            num_end = int(end_s.split('. ', 1)[0])
            
            if num_start > num_end:
                st.error("❌ 'From Surah' must be before 'To Surah'.")
            else:
                for s in SURAH_DATA:
                    if num_start <= s[0] <= num_end:
                        for page_num in range(s[2], s[3] + 1):
                            set_page_priority(s[1], page_num, t2_priority)
                st.success(f"✅ Priorities applied from {start_s} to {end_s}! Remember to click Save below.")

    with tab3:
        st.write("Apply a priority to a continuous range of physical pages (e.g., Pages 1 to 10).")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            start_p = st.number_input("From Page", min_value=1, max_value=604, value=1, step=1, key="tab3_start")
        with col_p2:
            end_p = st.number_input("To Page", min_value=1, max_value=604, value=10, step=1, key="tab3_end")
            
        t3_priority = st.selectbox("Priority to apply", priority_options, key="tab3_pri")
        if st.button("Apply to Page Range", key="btn_tab3"):
            if start_p > end_p:
                st.error("❌ 'From Page' must be before 'To Page'.")
            else:
                for page_num in range(start_p, end_p + 1):
                    for s in SURAH_DATA:
                        if s[2] <= page_num <= s[3]:
                            set_page_priority(s[1], page_num, t3_priority)
                            break
                st.success(f"✅ Priorities applied to pages {start_p}-{end_p}! Remember to click Save below.")

    st.markdown("---")

    # --- SAVE BUTTON ---
    if st.button("💾 Save Page Priorities to Cloud", type="primary"):
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
                
            st.success("✅ Page priorities permanently saved to the cloud!")
        except Exception as e:
            st.error(f"❌ Database Save Error: {e}")

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

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.write(f"👤 Logged in as: **{user_email.split('@')[0]}**")
    if st.button("Logout"):
        supabase.auth.sign_out()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state["user"] = None
        st.rerun()
    st.markdown("---")
    
    if not is_onboarded:
        st.warning("⚠️ Setup Required")
        st.write("Please complete setup (or skip) to unlock the app.")
        page = "⚙️ Manage Priorities"
    else:
        page = st.radio("📌 Navigation", ["📊 Dashboard", "📝 Log Session", "🚀 Today's Action Plan", "📜 View History", "⚙️ Manage Priorities"], key="sidebar_nav")

# --- ONBOARDING GATE ---
if not is_onboarded:
    render_priority_manager(onboarding=True)
    st.stop()

# --- PAGE 1: DASHBOARD ---
if page == "📊 Dashboard":
    st.title("📊 Progress Dashboard")
    df_logs = fetch_logs()
    df_dashboard = build_dashboard_rows(df_logs, df_priorities)

    # NEW: Global Progress Bar
    total_confident = df_dashboard[df_dashboard['Priority'] == '1 - Confident'].shape[0]
    progress_pct = total_confident / 604.0
    st.markdown(f"### 🏆 Memorization Progress: {int(progress_pct * 100)}%")
    st.progress(progress_pct, text=f"{total_confident} out of 604 pages confidently memorized")
    st.markdown("---")

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
    st.markdown("---")

    df_active = df_dashboard[df_dashboard['Priority'].isin(["1 - Confident", "2 - Needs Revision"])]
    if df_active.empty:
        st.info("No active priority surahs yet. Use the Manage Priorities page to assign some.")
    else:
        st.subheader("📚 Page-by-Page Tracker")
        display_df = df_active[['Surah', 'Juz', 'Page', 'Priority', 'Last Revised', 'Next Revision Due', 'Status']]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

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
                    daily_counts = recent_logs.groupby('log_date').size().reset_index(name='Sessions')
                    st.line_chart(daily_counts.set_index('log_date'))
                else:
                    st.write("No logs in the last 14 days.")

# --- PAGE 2: LOG SESSION ---
elif page == "📝 Log Session":
    st.title("📝 Log Today's Revision")
    
    # NEW: Pull pre-filled data from Action Plan Quick Log
    prefill_surah = st.session_state.get("prefill_surah", "")
    prefill_page = st.session_state.get("prefill_page", 0)
    
    active_surah_options = [""] + get_active_surah_options(df_priorities)
    surah_index = active_surah_options.index(prefill_surah) if prefill_surah in active_surah_options else 0
    
    with st.form("daily_log_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date", date.today())
            from_surah = st.selectbox("From Surah*", options=active_surah_options, index=surah_index)
            from_page = st.number_input("From Page (Optional)", min_value=0, max_value=604, value=prefill_page, step=1)
        with col2:
            minutes = st.number_input("Minutes Spent*", min_value=1, value=15, step=5)
            to_surah = st.selectbox("To Surah (Optional)", options=[""] + active_surah_options)
            to_page = st.number_input("To Page (Optional)", min_value=0, max_value=604, value=0, step=1)
        
        notes = st.text_input("Notes / Specific Verses")
        submitted = st.form_submit_button("💾 Save Session to Cloud")
        
        if submitted:
            # NEW: Strict Form Guardrails and Validation
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
                
                # Clear prefills after successful save
                if "prefill_surah" in st.session_state: del st.session_state["prefill_surah"]
                if "prefill_page" in st.session_state: del st.session_state["prefill_page"]
                
                st.success("✅ Log saved successfully!")
                st.balloons()

# --- PAGE 3: TODAY'S ACTION PLAN ---
elif page == "🚀 Today's Action Plan":
    st.title("🚀 Today's Action Plan")
    st.write("This view mirrors the workbook's live ranking engine and surfaces the top pages that need attention.")

    df_logs = fetch_logs()
    df_dashboard = build_dashboard_rows(df_logs, df_priorities)
    df_actions = df_dashboard[df_dashboard['Status'] != '🟢 Good'].copy()

    if df_actions.empty:
        st.success("🎉 All caught up! No pages are due for revision today.")
    else:
        df_top = df_actions.sort_values('Score').head(25)
        display_df = df_top[['Surah', 'Juz', 'Page', 'Priority', 'Last Revised', 'Next Revision Due', 'Status']]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # NEW: One-Click Quick Log Workflow
        st.markdown("---")
        st.subheader("⚡ Quick Log")
        st.write("Select one of your top priority actions and jump straight to the log tab.")
        
        action_options = [f"{row['Surah']} (Page {row['Page']})" for _, row in df_top.iterrows()]
        selected_action = st.selectbox("Select an action to log:", action_options)
        
        # Define the callback function
        def trigger_quick_log(action_string):
            surah_part = action_string.split(" (Page ")[0]
            page_part = int(action_string.split(" (Page ")[1].replace(")", ""))
            
            st.session_state.prefill_surah = surah_part
            st.session_state.prefill_page = page_part
            st.session_state.sidebar_nav = "📝 Log Session"

        # Tie the callback to the button using on_click
        st.button("📝 Log This Action", type="primary", on_click=trigger_quick_log, args=(selected_action,))

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
                '__row_id': st.column_config.TextColumn('Row ID', disabled=True),
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
            if st.button("💾 Save Changes"):
                for _, row in editable_history.iterrows():
                    if row['Delete']: continue
                    row_id = row['__row_id']
                    payload = {
                        'log_date': row['log_date'],
                        'from_surah': row['from_surah'] if str(row['from_surah']).strip() else None,
                        'to_surah': row['to_surah'] if str(row['to_surah']).strip() else None,
                        'from_page': int(row['from_page']) if pd.notna(row['from_page']) and str(row['from_page']).strip() not in ['', 'nan'] else None,
                        'to_page': int(row['to_page']) if pd.notna(row['to_page']) and str(row['to_page']).strip() not in ['', 'nan'] else None,
                        'minutes': int(row['minutes']) if pd.notna(row['minutes']) else None,
                        'notes': row['notes'] if str(row['notes']).strip() else None,
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