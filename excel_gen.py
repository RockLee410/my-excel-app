import streamlit as st
import pandas as pd
import xlsxwriter
from io import BytesIO
from datetime import date, timedelta

# --- DATA: Fully Expanded 114 Surahs (Madinah Mushaf) ---
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

# --- STREAMLIT UI & SESSION STATE ---
st.set_page_config(page_title="Quran Tracker App", layout="wide")

if "cat1" not in st.session_state: st.session_state["cat1"] = []
if "cat2" not in st.session_state: st.session_state["cat2"] = []
if "history" not in st.session_state: st.session_state["history"] = []

st.title("📖 Master Quran Tracker")

# 0. EXPANDABLE ONBOARDING GUIDE
with st.expander("📖 How to use this Tracker (Start Here!)"):
    st.markdown("""
    **Welcome to your automated Quran revision dashboard!** Here is how to set it up in 3 easy steps:
   
    1. **Personalize & Generate:** Enter your name below, add the Surahs you have memorized to the correct categories, and click the blue 'Generate' button to download your tracker.
    2. **Upload to Google Sheets:** Go to [Google Sheets](https://sheets.google.com), open a new blank sheet, and go to **File > Import > Upload** to bring your tracker into the cloud.
    3. **Automatic Refresh:** Once imported into Google Sheets, the dashboard formulas update automatically as you log your daily study and change categories in the tracker.
       
    *That's it! Every day, just log what you studied in the **Daily Log** tab, and your Dashboard and Action Plan will update automatically.*
    """)
    st.markdown("---")

# 1. THE STATEFUL IMPORTER
uploaded_file = st.file_uploader("📂 Have an existing Tracker? Upload it here to carry over your history & settings!", type=["xlsx"])

if uploaded_file is not None and "file_loaded" not in st.session_state:
    try:
        df_dash = pd.read_excel(uploaded_file, sheet_name="Surah Dashboard", skiprows=4)
        df_log = pd.read_excel(uploaded_file, sheet_name="Daily_Log")
        df_log = df_log.dropna(subset=['From Surah'])
        df_log = df_log.fillna("") # Clean NaNs
       
        st.session_state["history"] = df_log.to_dict('records')
       
        # Smart Category Extraction
        if 'Surah' in df_dash.columns and 'Category' in df_dash.columns:
            cat1_surahs = df_dash[df_dash['Category'] == '1 - Confident']['Surah'].dropna().unique()
            cat2_surahs = df_dash[df_dash['Category'] == '2 - Needs Revision']['Surah'].dropna().unique()
           
            c1_list, c2_list = [], []
            for s in SURAH_DATA:
                if s[1] in cat1_surahs: c1_list.append(f"{s[0]}. {s[1]}")
                if s[1] in cat2_surahs: c2_list.append(f"{s[0]}. {s[1]}")
           
            st.session_state["cat1"] = c1_list
            st.session_state["cat2"] = [surah for surah in c2_list if surah not in c1_list]
           
        st.session_state["file_loaded"] = True
        st.rerun()
    except Exception as e:
        st.error(f"Error parsing file. Please make sure it's the correct format. ({e})")

# 2. WEB VISUALIZATIONS
if st.session_state["history"]:
    st.success(f"✅ Successfully loaded {len(st.session_state['history'])} past log entries!")
    st.markdown("### 📈 Your Memorization Velocity")
   
    df_chart = pd.DataFrame(st.session_state["history"])
    df_chart['Date'] = pd.to_datetime(df_chart['Date'])
   
    colA, colB = st.columns(2)
    colA.metric("Total Sessions Logged", len(df_chart))
    if 'Minutes Spent' in df_chart.columns:
        df_chart['Minutes Spent'] = pd.to_numeric(df_chart['Minutes Spent'], errors='coerce').fillna(0)
        colB.metric("Total Hours Logged", round(df_chart['Minutes Spent'].sum() / 60, 1))
   
    daily_counts = df_chart.groupby(df_chart['Date'].dt.date).size().reset_index(name='Sessions')
    st.line_chart(daily_counts.set_index('Date'))
    st.markdown("---")

# --- GENERATOR SETTINGS ---
def remove_category_overlap(changed_category):
    other_category = "cat2" if changed_category == "cat1" else "cat1"
    st.session_state[other_category] = [
        surah for surah in st.session_state[other_category]
        if surah not in st.session_state[changed_category]
    ]

def add_to_category(category, surahs):
    existing = st.session_state[category]
    st.session_state[category] = existing + [surah for surah in surahs if surah not in existing]
    remove_category_overlap(category)

def add_juz_30():
    add_to_category("cat1", [f"{s[0]}. {s[1]}" for s in SURAH_DATA if s[0] >= 78])

def add_juz_29():
    add_to_category("cat1", [f"{s[0]}. {s[1]}" for s in SURAH_DATA if 67 <= s[0] <= 77])

def add_juz_30_cat2():
    add_to_category("cat2", [f"{s[0]}. {s[1]}" for s in SURAH_DATA if s[0] >= 78])

def add_juz_29_cat2():
    add_to_category("cat2", [f"{s[0]}. {s[1]}" for s in SURAH_DATA if 67 <= s[0] <= 77])


st.markdown("### 👤 1. Personalize Your Tracker")
user_name = st.text_input("What is your name?", "My")

st.markdown("### 🗂️ 2. Manage Categorized Surahs")

col1, col2 = st.columns(2)
with col1:
    st.button("⚡ Quick Add: Juz 30 to Category 1", on_click=add_juz_30)
with col2:
    st.button("⚡ Quick Add: Juz 29 to Category 1", on_click=add_juz_29)
cat1_selections = st.multiselect(
    "🟢 Category 1: Memorized with Confidence",
    options=surah_options,
    key="cat1",
    on_change=remove_category_overlap,
    args=("cat1",),
)

col3, col4 = st.columns(2)
with col3:
    st.button("⚡ Quick Add: Juz 30 to Category 2", on_click=add_juz_30_cat2)
with col4:
    st.button("⚡ Quick Add: Juz 29 to Category 2", on_click=add_juz_29_cat2)
cat2_selections = st.multiselect(
    "🟡 Category 2: Needs Revision",
    options=surah_options,
    key="cat2",
    on_change=remove_category_overlap,
    args=("cat2",),
)

# --- EXCEL GENERATION LOGIC ---
if st.button(f"Generate {user_name.strip()}'s Excel Tracker", type="primary"):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
   
    # Formats
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
    bold_format = workbook.add_format({'bold': True})
    progress_format = workbook.add_format({'bold': True, 'font_color': '#006100', 'font_size': 14})
    fire_format = workbook.add_format({'bold': True, 'font_color': '#D9534F', 'font_size': 14})
   
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
    action_date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
   
    border_format = workbook.add_format({'border': 1})
    formula_gray = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'num_format': 'yyyy-mm-dd'})
    merge_center = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
    merge_left = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
   
    red_bg = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    yellow_bg = workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C6500'})
    green_bg = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
   
    # --- SHEET 1: SURAH DASHBOARD ---
    worksheet = workbook.add_worksheet('Surah Dashboard')
    worksheet.freeze_panes(5, 0)
   
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 22)
    worksheet.set_column('C:C', 8)  
    worksheet.set_column('D:D', 8)  
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 18)
    worksheet.set_column('G:G', 20)
    worksheet.set_column('H:H', 15)
    worksheet.set_column('I:I', 20)
    worksheet.set_column('L:M', 20)

    worksheet.write('A1', "Rule: Category 1 & 2 Pages must be revised every 14 days.")
    worksheet.write_formula('A4', '="🔥 Total Days Logged: " & COUNTA(Daily_Log!C2:C10001) & " Days"', fire_format)
    worksheet.write_formula('D4', '="⏱️ Total Time Spent: " & ROUND(SUM(Daily_Log!G2:G10001)/60, 1) & " Hours"', fire_format)
   
    worksheet.write('G3', "⚡ Current Streak", workbook.add_format({'bold': True}))
    streak_formula = '="⚡ Current Streak: " & IF(TODAY() - MAXIFS(Daily_Log!$A$2:$A$10001, Daily_Log!$C$2:$C$10001, "<>") > 1, 0, IFERROR(MATCH(0, ARRAYFORMULA(COUNTIFS(Daily_Log!$A$2:$A$10001, MAXIFS(Daily_Log!$A$2:$A$10001, Daily_Log!$C$2:$C$10001, "<>") - SEQUENCE(365,1,0), Daily_Log!$C$2:$C$10001, "<>")), 0) - 1, 365)) & " Days"'
    worksheet.write_formula('G4', streak_formula)
   
    headers = ['No.', 'Surah', 'Juz', 'Page', 'Category', 'Last Revised (Date)', 'Next Revision Due', 'Status', 'Notes']
    for col_num, data in enumerate(headers):
        worksheet.write(4, col_num, data, header_format)

    history_data = st.session_state["history"]
    current_excel_row = 5
    dashboard_rows_data = []

    def get_last_revised_date_for_page(page_num, history_rows):
        last_date = None
        for entry in history_rows:
            try:
                entry_date = pd.to_datetime(entry.get('Date', ''), errors='coerce').date()
            except Exception:
                continue
            if not entry_date:
                continue

            start_page = None
            end_page = None

            from_page = str(entry.get('From Page (Opt)', '')).strip()
            to_page = str(entry.get('To Page (Opt)', '')).strip()
            from_surah = str(entry.get('From Surah', '')).strip()
            to_surah = str(entry.get('To Surah (Optional)', '')).strip()

            if from_page:
                start_page = int(float(from_page))
            elif from_surah:
                for surah in SURAH_DATA:
                    if f"{surah[0]}. {surah[1]}" == from_surah:
                        start_page = surah[2]
                        break

            if to_page:
                end_page = int(float(to_page))
            elif to_surah:
                for surah in SURAH_DATA:
                    if f"{surah[0]}. {surah[1]}" == to_surah:
                        end_page = surah[3]
                        break
            elif start_page is not None and from_surah:
                for surah in SURAH_DATA:
                    if f"{surah[0]}. {surah[1]}" == from_surah:
                        end_page = surah[3]
                        break
            elif start_page is not None:
                end_page = start_page

            if start_page is not None and end_page is not None and start_page <= page_num <= end_page:
                if last_date is None or entry_date > last_date:
                    last_date = entry_date

        return last_date

    def get_dashboard_status(category, page_num, history_rows):
        if category == "3 - Not Memorized":
            return "⚪ Not Started"

        last_revised = get_last_revised_date_for_page(page_num, history_rows)
        if not last_revised:
            return "Pending"

        next_due = last_revised + timedelta(days=14)
        today = date.today()
        if today > next_due:
            return "🔴 Overdue"
        if next_due - today <= timedelta(days=3):
            return "🟡 Due Soon"
        return "🟢 Good"
   
    for s in SURAH_DATA:
        surah_string = f"{s[0]}. {s[1]}"
        category = "1 - Confident" if surah_string in cat1_selections else "2 - Needs Revision" if surah_string in cat2_selections else "3 - Not Memorized"
           
        pages = list(range(s[2], s[3] + 1))
        num_pages = len(pages)
        start_row = current_excel_row
        end_row = current_excel_row + num_pages - 1
       
        if num_pages > 1:
            worksheet.merge_range(start_row, 0, end_row, 0, s[0], merge_center)
            worksheet.merge_range(start_row, 1, end_row, 1, s[1], merge_left)
        else:
            worksheet.write(start_row, 0, s[0], merge_center)
            worksheet.write(start_row, 1, s[1], merge_left)
           
        for i, p in enumerate(pages):
            row = start_row + i
            dash_row_num = row + 1
            status = get_dashboard_status(category, p, history_data)
           
            if category == "3 - Not Memorized":
                worksheet.set_row(row, None, None, {'hidden': True})
               
            worksheet.write(row, 2, get_juz(p), merge_center)
            worksheet.write(row, 3, p, border_format)        
            worksheet.write(row, 4, category, border_format)  
           
            range_formula = f'=IF(MAXIFS(Daily_Log!$A$2:$A$10001, Daily_Log!$I$2:$I$10001, "<="&$D{row+1}, Daily_Log!$J$2:$J$10001, ">="&$D{row+1})=0, "", MAXIFS(Daily_Log!$A$2:$A$10001, Daily_Log!$I$2:$I$10001, "<="&$D{row+1}, Daily_Log!$J$2:$J$10001, ">="&$D{row+1}))'
            worksheet.write_formula(row, 5, range_formula, formula_gray)
           
            f_formula = f'=IF(OR(E{row+1}="1 - Confident", E{row+1}="2 - Needs Revision"), IF(F{row+1}="", "", F{row+1}+14), "")'
            worksheet.write_formula(row, 6, f_formula, formula_gray)
           
            g_formula = f'=IF(E{row+1}="3 - Not Memorized", "⚪ Not Started", IF(F{row+1}="", "Pending", IF(TODAY()>G{row+1}, "🔴 Overdue", IF(G{row+1}-TODAY()<=3, "🟡 Due Soon", "🟢 Good"))))'
            worksheet.write_formula(row, 7, g_formula, border_format)
           
            worksheet.write_blank(row, 8, None, border_format)
            dashboard_rows_data.append({
                'dash_row': dash_row_num,
                'surah': s[1],
                'juz': get_juz(p),
                'page': p,
                'category': category,
                'status': status,
            })
           
        current_excel_row += num_pages
       
    last_dash_row = current_excel_row + 4
   
    worksheet.autofilter(4, 0, current_excel_row - 1, 8)
    worksheet.write_formula('A3', f'="🏆 Total Pages Memorized: " & TEXT(COUNTIF(E6:E{last_dash_row}, "1 - Confident")/604, "0.0%") & " (" & COUNTIF(E6:E{last_dash_row}, "1 - Confident") & " / 604 pages)"', progress_format)

    for row in range(5, last_dash_row):
        worksheet.data_validation(row, 4, row, 4, {'validate': 'list', 'source': ['1 - Confident', '2 - Needs Revision', '3 - Not Memorized']})
       
    worksheet.conditional_format(f'H6:H{last_dash_row}', {'type': 'cell', 'criteria': '==', 'value': '"🔴 Overdue"', 'format': red_bg})
    worksheet.conditional_format(f'H6:H{last_dash_row}', {'type': 'cell', 'criteria': '==', 'value': '"🟡 Due Soon"', 'format': yellow_bg})
    worksheet.conditional_format(f'H6:H{last_dash_row}', {'type': 'cell', 'criteria': '==', 'value': '"🟢 Good"', 'format': green_bg})

    # Summary Table
    worksheet.write('L1', 'Category', header_format)
    worksheet.write('M1', 'Total Pages', header_format)
    worksheet.write('L2', '1 - Confident')
    worksheet.write_formula('M2', f'=COUNTIF($E$6:$E${last_dash_row}, "1 - Confident")')
    worksheet.write('L3', '2 - Needs Revision')
    worksheet.write_formula('M3', f'=COUNTIF($E$6:$E${last_dash_row}, "2 - Needs Revision")')
    worksheet.write('L4', '3 - Not Memorized')
    worksheet.write_formula('M4', f'=COUNTIF($E$6:$E${last_dash_row}, "3 - Not Memorized")')

    chart = workbook.add_chart({'type': 'pie'})
    chart.add_series({'categories': "='Surah Dashboard'!$L$2:$L$4", 'values': "='Surah Dashboard'!$M$2:$M$4", 'points': [{'fill': {'color': '#92D050'}}, {'fill': {'color': '#FFC000'}}, {'fill': {'color': '#D9D9D9'}}]})
    chart.set_size({'width': 480, 'height': 300})
    worksheet.insert_chart('O6', chart, {'object_position': 3})

    # --- SHEET 2: TODAY'S ACTION PLAN ---
    action_sheet = workbook.add_worksheet("Today's Action Plan")
    action_sheet.hide_gridlines(2)
   
    action_sheet.set_column('A:B', 22)
    action_sheet.set_column('C:C', 10)
    action_sheet.set_column('D:D', 20)
    action_sheet.set_column('E:F', 18, action_date_format)
    action_sheet.set_column('G:G', 15)
   
    action_sheet.write('A1', "🚀 High Priority Revision Goals", progress_format)
    action_sheet.write('A2', "This page automatically filters out pages that are 'Good' or 'Not Started'. It only shows what needs attention today!")
   
    action_headers = ['Surah', 'Juz', 'Page', 'Category', 'Last Revised', 'Next Due', 'Status']
    for col_num, data in enumerate(action_headers):
        action_sheet.write(3, col_num, data, header_format)
       
    action_sheet.write('A5', "📋 Today's Focus", fire_format)
    relevant_rows = [row for row in dashboard_rows_data if row['status'] in {'🔴 Overdue', '🟡 Due Soon', 'Pending'}]
    if not relevant_rows:
        action_sheet.write('A6', "All caught up! 🎉")
    else:
        action_row = 5
        for row_data in relevant_rows:
            action_row += 1
            dash_row = row_data['dash_row']
            action_sheet.write_formula(action_row, 0, f"='Surah Dashboard'!B{dash_row}")
            action_sheet.write_formula(action_row, 1, f"='Surah Dashboard'!C{dash_row}")
            action_sheet.write_formula(action_row, 2, f"='Surah Dashboard'!D{dash_row}")
            action_sheet.write_formula(action_row, 3, f"='Surah Dashboard'!E{dash_row}")
            action_sheet.write_formula(action_row, 4, f"='Surah Dashboard'!F{dash_row}")
            action_sheet.write_formula(action_row, 5, f"='Surah Dashboard'!G{dash_row}")
            action_sheet.write_formula(action_row, 6, f"='Surah Dashboard'!H{dash_row}")

    # --- SHEET 3: DAILY LOG ---
    log_sheet = workbook.add_worksheet('Daily_Log')
    log_sheet.freeze_panes(1, 0)
   
    log_sheet.set_column('A:A', 15, date_format)
    log_sheet.set_column('B:B', 15)
    log_sheet.set_column('C:D', 22)
    log_sheet.set_column('E:F', 15)
    log_sheet.set_column('G:G', 15)
    log_sheet.set_column('H:H', 35)
   
    log_headers = ['Date', 'Day', 'From Surah', 'To Surah (Optional)', 'From Page (Opt)', 'To Page (Opt)', 'Minutes Spent', 'Notes / Specific Verses']
    for col_num, data in enumerate(log_headers):
        log_sheet.write(0, col_num, data, header_format)
       
    # Hide the backend dynamic columns
    log_sheet.set_column('I:J', None, None, {'hidden': True})
    log_sheet.set_column('AB:AE', None, None, {'hidden': True})
   
   # 1 & 2. Dynamic Dropdown Source + Permanent Lookup Table
    # Google Sheets will recalculate these formulas when the dashboard categories change.
    for i, s in enumerate(SURAH_DATA):
        surah_name = f"{s[0]}. {s[1]}"
        
        # AC Column: Static Master List of Names
        log_sheet.write_string(i, 28, surah_name)
        # AD Column: Master Start Pg
        log_sheet.write_number(i, 29, s[2])
        # AE Column: Master End Pg
        log_sheet.write_number(i, 30, s[3])

    for i, s in enumerate(SURAH_DATA):
        surah_name = f"{s[0]}. {s[1]}"
        start_page = s[2]
        end_page = s[3]
        formula = (
            f'=IF(OR(COUNTIFS(\'Surah Dashboard\'!$D$6:$D${last_dash_row}, ">="&$AD{i+1}, '
            f'\'Surah Dashboard\'!$D$6:$D${last_dash_row}, "<="&$AE{i+1}, '
            f'\'Surah Dashboard\'!$E$6:$E${last_dash_row}, "1 - Confident")>0, '
            f'COUNTIFS(\'Surah Dashboard\'!$D$6:$D${last_dash_row}, ">="&$AD{i+1}, '
            f'\'Surah Dashboard\'!$D$6:$D${last_dash_row}, "<="&$AE{i+1}, '
            f'\'Surah Dashboard\'!$E$6:$E${last_dash_row}, "2 - Needs Revision")>0), '
            f'$AC{i+1}, "")'
        )
        log_sheet.write_formula(i, 27, formula)
       
    day_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'italic': True})
   
    history_data = st.session_state["history"]
    start_date = date.today()
    if history_data:
        try:
            max_date = pd.to_datetime(history_data[-1]['Date']).date()
            start_date = max_date + timedelta(days=1)
        except: pass
       
    for row in range(1, 10001):
        if row - 1 < len(history_data):
            hist = history_data[row-1]
            try: log_date = pd.to_datetime(hist['Date']).date()
            except: log_date = start_date
           
            log_sheet.write_datetime(row, 0, log_date, date_format)
            if str(hist.get('From Surah', '')): log_sheet.write_string(row, 2, str(hist.get('From Surah', '')))
            if str(hist.get('To Surah (Optional)', '')): log_sheet.write_string(row, 3, str(hist.get('To Surah (Optional)', '')))
            if str(hist.get('From Page (Opt)', '')): log_sheet.write_number(row, 4, int(float(hist.get('From Page (Opt)'))))
            if str(hist.get('To Page (Opt)', '')): log_sheet.write_number(row, 5, int(float(hist.get('To Page (Opt)'))))
            if str(hist.get('Minutes Spent', '')): log_sheet.write_number(row, 6, int(float(hist.get('Minutes Spent'))))
            if str(hist.get('Notes / Specific Verses', '')): log_sheet.write_string(row, 7, str(hist.get('Notes / Specific Verses', '')))
        else:
            offset = row - 1 - len(history_data)
            current_date = start_date + timedelta(days=offset)
            log_sheet.write_datetime(row, 0, current_date, date_format)
           
        log_sheet.write_formula(row, 1, f'=IF(ISBLANK(A{row+1}), "", TEXT(A{row+1}, "dddd"))', day_format)
        
        # Point the Data Validation dropdown to the helper list in AB.
        # This range is populated by formulas that recalculate when dashboard categories change.
        log_sheet.data_validation(row, 2, row, 2, {'validate': 'list', 'source': '=$AB$1:$AB$114', 'ignore_blank': True})
        log_sheet.data_validation(row, 3, row, 3, {'validate': 'list', 'source': '=$AB$1:$AB$114', 'ignore_blank': True})
       
        # Update the VLOOKUPs to pull Start and End pages from the new permanent master table (AC1:AE114)
        log_sheet.write_formula(row, 8, f'=IFERROR(IF(ISBLANK(E{row+1}), VLOOKUP(C{row+1}, $AC$1:$AE$114, 2, FALSE), E{row+1}), 0)')
        log_sheet.write_formula(row, 9, f'=IFERROR(IF(NOT(ISBLANK(F{row+1})), F{row+1}, IF(NOT(ISBLANK(D{row+1})), VLOOKUP(D{row+1}, $AC$1:$AE$114, 3, FALSE), IF(NOT(ISBLANK(E{row+1})), E{row+1}, VLOOKUP(C{row+1}, $AC$1:$AE$114, 3, FALSE)))), 0)')
       
    workbook.close()
   
    st.success("✅ Your personalized tracker is ready!")
   
    safe_name = user_name.strip().replace(" ", "_") if user_name.strip() else "My"
    st.download_button(
        label="📥 Download Upgraded Excel Tracker",
        data=output.getvalue(),
        file_name=f"{safe_name}_Quran_Tracker.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )