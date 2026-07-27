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
total_surahs = len(SURAH_DATA)

def get_juz(page_num):
    juz_starts = [1, 22, 42, 62, 82, 102, 122, 142, 162, 182, 202, 222, 242, 262, 282, 302, 322, 342, 362, 382, 402, 422, 442, 462, 482, 502, 522, 542, 562, 582]
    for i, start in reversed(list(enumerate(juz_starts))):
        if page_num >= start:
            return i + 1
    return 1

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Quran Tracker App", layout="wide", initial_sidebar_state="expanded")

# --- INITIALIZE DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase: Client = init_connection()
except Exception as e:
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
            except Exception as e:
                st.error("Login failed. Check your credentials.")

    with tab2:
        st.write("Create a free account to sync your progress to the cloud.")
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
    st.stop()  # Stop rendering the rest of the app until logged in

user_email = st.session_state["user"].email

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.write(f"👤 Logged in as: **{user_email.split('@')[0]}**")
    if st.button("Logout"):
        supabase.auth.sign_out()
        st.session_state["user"] = None
        st.rerun()
    
    st.markdown("---")
    page = st.radio("📌 Navigation", ["📊 Dashboard", "📝 Log Session", "🚀 Today's Action Plan", "📜 View History", "⚙️ Manage Priorities"])

# --- DATA FETCHING HELPERS ---
def fetch_logs():
    res = supabase.table('daily_logs').select("*").eq("user_name", user_email).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def fetch_priorities():
    res = supabase.table('surah_categories').select("*").eq("user_name", user_email).execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

# --- PAGE 1: DASHBOARD ---
if page == "📊 Dashboard":
    st.title("📊 Progress Dashboard")
    
    df_logs = fetch_logs()
    df_priorities = fetch_priorities()
    
    # Calculate Metrics
    total_sessions = len(df_logs)
    total_hours = round(df_logs['minutes'].sum() / 60, 1) if not df_logs.empty else 0
    
    # Streak Calculation
    streak = 0
    if not df_logs.empty:
        df_logs['log_date'] = pd.to_datetime(df_logs['log_date']).dt.date
        unique_dates = sorted(df_logs['log_date'].unique(), reverse=True)
        today = date.today()
        
        if today in unique_dates or (today - timedelta(days=1)) in unique_dates:
            current = today if today in unique_dates else today - timedelta(days=1)
            streak = 1
            for d in unique_dates:
                if d == current: continue
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
    
    # Priorities Pie Chart
    col_pie, col_chart = st.columns(2)
    with col_pie:
        st.subheader("📚 Memorization Status")
        if df_priorities.empty:
            st.info("Assign Surahs in 'Manage Priorities' to see your progress.")
        else:
            cat_counts = df_priorities['category'].value_counts().reset_index()
            cat_counts.columns = ['Priority', 'Count']
            chart = alt.Chart(cat_counts).mark_arc().encode(
                theta="Count",
                color=alt.Color("Priority", scale=alt.Scale(domain=["1 - Confident", "2 - Needs Revision"], range=["#2E7D32", "#F57F17"])),
                tooltip=["Priority", "Count"]
            ).properties(width=300, height=300)
            st.altair_chart(chart, use_container_width=True)

    # Velocity Line Chart
    with col_chart:
        st.subheader("📈 Consistency (Last 14 Days)")
        if not df_logs.empty:
            last_14 = date.today() - timedelta(days=14)
            recent_logs = df_logs[df_logs['log_date'] >= last_14]
            if not recent_logs.empty:
                daily_counts = recent_logs.groupby('log_date').size().reset_index(name='Sessions')
                st.line_chart(daily_counts.set_index('log_date'))
            else:
                st.write("No logs in the last 14 days.")

# --- PAGE 2: LOG SESSION ---
elif page == "📝 Log Session":
    st.title("📝 Log Today's Revision")
    with st.form("daily_log_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            log_date = st.date_input("Date", date.today())
            from_surah = st.selectbox("From Surah*", options=surah_options)
            from_page = st.number_input("From Page", min_value=1, max_value=604, value=1, step=1)
        with col2:
            minutes = st.number_input("Minutes Spent*", min_value=1, value=15, step=5)
            to_surah = st.selectbox("To Surah (Optional)", options=[""] + surah_options)
            to_page = st.number_input("To Page (Optional)", min_value=0, max_value=604, value=0, step=1)
        
        notes = st.text_input("Notes / Specific Verses")
        submitted = st.form_submit_button("💾 Save Session to Cloud")
        
        if submitted:
            new_log = {
                "user_name": user_email,
                "log_date": str(log_date),
                "from_surah": from_surah,
                "to_surah": to_surah if to_surah else None,
                "from_page": from_page,
                "to_page": to_page if to_page > 0 else None,
                "minutes": minutes,
                "notes": notes
            }
            supabase.table('daily_logs').insert(new_log).execute()
            st.success("✅ Log saved successfully!")
            st.balloons()

# --- PAGE 3: TODAY'S ACTION PLAN ---
elif page == "🚀 Today's Action Plan":
    st.title("🚀 Today's Action Plan")
    st.write("This engine scans your active priorities and cross-references your history to find what is due for a 14-day revision.")
    
    df_priorities = fetch_priorities()
    df_logs = fetch_logs()
    
    if df_priorities.empty:
        st.warning("You haven't added any Surahs to your priorities yet. Go to 'Manage Priorities' first!")
    elif df_logs.empty:
        st.info("You haven't logged any sessions yet! Log your first session to trigger the algorithm.")
    else:
        # Recreate the Excel Due Date Logic in Pandas
        due_list = []
        df_logs['log_date'] = pd.to_datetime(df_logs['log_date']).dt.date
        
        for _, row in df_priorities.iterrows():
            surah_str = f"{row['surah_number']}. {row['surah_name']}"
            
            # Find all logs that mention this Surah
            surah_logs = df_logs[(df_logs['from_surah'] == surah_str) | (df_logs['to_surah'] == surah_str)]
            
            if surah_logs.empty:
                last_revised = "Never"
                days_since = 999
            else:
                last_revised = surah_logs['log_date'].max()
                days_since = (date.today() - last_revised).days
            
            # 14 Day Rule
            if days_since >= 14:
                status = "🔴 Overdue"
            elif days_since >= 11:
                status = "🟡 Due Soon"
            else:
                status = "🟢 Good"
                
            if status != "🟢 Good":
                due_list.append({
                    "Surah": surah_str,
                    "Priority": row['category'],
                    "Last Revised": str(last_revised),
                    "Status": status
                })
        
        if due_list:
            st.dataframe(pd.DataFrame(due_list), use_container_width=True, hide_index=True)
        else:
            st.success("🎉 All caught up! No pages are due for revision today.")

# --- PAGE 4: VIEW HISTORY ---
elif page == "📜 View History":
    st.title("📜 Complete Study History")
    df_logs = fetch_logs()
    if df_logs.empty:
        st.info("No logs found.")
    else:
        df_logs = df_logs.sort_values(by="log_date", ascending=False)
        display_df = df_logs[['log_date', 'from_surah', 'to_surah', 'from_page', 'to_page', 'minutes', 'notes']]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# --- PAGE 5: MANAGE PRIORITIES ---
elif page == "⚙️ Manage Priorities":
    st.title("🗂️ Manage Surah Priorities")
    st.write("Assign your Surahs to priorities so the Action Plan knows what to test you on.")
    
    # Get current saved priorities from DB
    df_priorities = fetch_priorities()
    saved_cat1, saved_cat2 = [], []
    
    if not df_priorities.empty:
        saved_cat1 = [f"{r['surah_number']}. {r['surah_name']}" for _, r in df_priorities[df_priorities['category'] == '1 - Confident'].iterrows()]
        saved_cat2 = [f"{r['surah_number']}. {r['surah_name']}" for _, r in df_priorities[df_priorities['category'] == '2 - Needs Revision'].iterrows()]

    with st.form("priority_form"):
        new_cat1 = st.multiselect("🟢 Priority 1: Memorized with Confidence", options=surah_options, default=saved_cat1)
        new_cat2 = st.multiselect("🟡 Priority 2: Needs Revision", options=surah_options, default=saved_cat2)
        
        if st.form_submit_button("Update Priorities"):
            # Prevent overlap
            overlap = set(new_cat1).intersection(set(new_cat2))
            if overlap:
                st.error(f"A Surah cannot be in both priorities! Conflicting: {', '.join(overlap)}")
            else:
                # Wipe old categories and insert new ones
                supabase.table('surah_categories').delete().eq('user_name', user_email).execute()
                
                inserts = []
                for s in new_cat1:
                    num, name = s.split(". ")
                    inserts.append({"user_name": user_email, "surah_number": int(num), "surah_name": name, "category": "1 - Confident"})
                for s in new_cat2:
                    num, name = s.split(". ")
                    inserts.append({"user_name": user_email, "surah_number": int(num), "surah_name": name, "category": "2 - Needs Revision"})
                
                if inserts:
                    supabase.table('surah_categories').insert(inserts).execute()
                
                st.success("✅ Priorities updated successfully!")
                st.rerun()