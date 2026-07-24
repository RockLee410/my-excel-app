import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

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

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="Quran Tracker App", layout="centered")

# --- INITIALIZE DATABASE CONNECTION ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error(f"❌ Connection failed. Please check your secrets.toml file. Error: {e}")
    st.stop()

# --- APP HEADER & SIMPLE AUTH ---
st.title("📖 Cloud Quran Tracker")

# We use the sidebar to let users "log in" by typing their name
with st.sidebar:
    st.header("👤 Identity")
    user_name = st.text_input("Enter your name to load your tracker:", value="User").strip()

# --- DAILY LOG FORM ---
st.markdown("### 📝 Log Today's Revision")
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
        if not user_name:
            st.error("Please enter your name in the sidebar first!")
        else:
            # Package the data to send to Supabase
            new_log = {
                "user_name": user_name,
                "log_date": str(log_date),
                "from_surah": from_surah,
                "to_surah": to_surah if to_surah else None,
                "from_page": from_page,
                "to_page": to_page if to_page > 0 else None,
                "minutes": minutes,
                "notes": notes
            }
            # Insert into database
            response = supabase.table('daily_logs').insert(new_log).execute()
            st.success("✅ Log saved successfully!")
            st.balloons()

# --- VIEW LIVE DATA ---
st.markdown("---")
st.markdown("### 📊 Your Recent History")

# Fetch only the logs for the person currently "logged in" via the sidebar
response = supabase.table('daily_logs').select("*").eq("user_name", user_name).order('log_date', desc=True).limit(10).execute()

if len(response.data) == 0:
    st.info(f"No logs found for {user_name} yet. Submit a session above to see it here!")
else:
    # Convert cloud data directly to a Pandas DataFrame and display it beautifully!
    df = pd.DataFrame(response.data)
    # Clean up the display columns
    df = df[['log_date', 'from_surah', 'to_surah', 'from_page', 'to_page', 'minutes', 'notes']]
    st.dataframe(df, use_container_width=True, hide_index=True)