import streamlit as st
import pandas as pd
import xlsxwriter
from io import BytesIO
from datetime import date, timedelta

# --- DATA: Surahs 1-89, plus grouped 90-114 ---
SURAH_DATA = [
    (1, "Al-Fatihah", 7, 1), (2, "Al-Baqarah", 286, 48), (3, "Aal-Imran", 200, 27), (4, "An-Nisa", 176, 29),
    (5, "Al-Ma'idah", 120, 21), (6, "Al-An'am", 165, 23), (7, "Al-A'raf", 206, 26), (8, "Al-Anfal", 75, 10),
    (9, "At-Tawbah", 129, 21), (10, "Yunus", 109, 13), (11, "Hud", 123, 13), (12, "Yusuf", 111, 13),
    (13, "Ar-Ra'd", 43, 6), (14, "Ibrahim", 52, 7), (15, "Al-Hijr", 99, 5), (16, "An-Nahl", 128, 15),
    (17, "Al-Isra", 111, 11), (18, "Al-Kahf", 110, 11), (19, "Maryam", 98, 7), (20, "Taha", 135, 10),
    (21, "Al-Anbiya", 112, 10), (22, "Al-Hajj", 78, 10), (23, "Al-Mu'minun", 118, 8), (24, "An-Nur", 64, 9),
    (25, "Al-Furqan", 77, 7), (26, "Ash-Shu'ara", 227, 10), (27, "An-Naml", 93, 9), (28, "Al-Qasas", 88, 11),
    (29, "Al-Ankabut", 69, 9), (30, "Ar-Rum", 60, 6), (31, "Luqman", 34, 4), (32, "As-Sajdah", 30, 3),
    (33, "Al-Ahzab", 73, 10), (34, "Saba", 54, 6), (35, "Fatir", 45, 5), (36, "Ya-Sin", 83, 6),
    (37, "As-Saffat", 182, 7), (38, "Sad", 88, 5), (39, "Az-Zumar", 75, 9), (40, "Ghafir", 85, 9),
    (41, "Fussilat", 54, 6), (42, "Ash-Shura", 53, 6), (43, "Az-Zukhruf", 89, 7), (44, "Ad-Dukhan", 59, 3),
    (45, "Al-Jathiyah", 37, 4), (46, "Al-Ahqaf", 35, 5), (47, "Muhammad", 38, 4), (48, "Al-Fath", 29, 5),
    (49, "Al-Hujurat", 18, 3), (50, "Qaf", 45, 3), (51, "Ad-Zariyat", 60, 3), (52, "At-Tur", 49, 3),
    (53, "An-Najm", 62, 3), (54, "Al-Qamar", 55, 3), (55, "Ar-Rahman", 78, 3), (56, "Al-Waqi'ah", 96, 3),
    (57, "Al-Hadid", 29, 4), (58, "Al-Mujadila", 22, 3), (59, "Al-Hashr", 24, 4), (60, "Al-Mumtahanah", 13, 3),
    (61, "As-Saff", 14, 2), (62, "Al-Jumu'ah", 11, 2), (63, "Al-Munafiqun", 11, 2), (64, "At-Taghabun", 18, 2),
    (65, "At-Talaq", 12, 2), (66, "At-Tahrim", 12, 2), (67, "Al-Mulk", 30, 2.5), (68, "Al-Qalam", 52, 2),
    (69, "Al-Haqqah", 52, 2), (70, "Al-Ma'arij", 44, 2), (71, "Nuh", 28, 2), (72, "Al-Jinn", 28, 2),
    (73, "Al-Muzzammil", 20, 1.5), (74, "Al-Muddaththir", 56, 2), (75, "Al-Qiyamah", 40, 1.5), (76, "Al-Insan", 31, 2),
    (77, "Al-Mursalat", 50, 1.5), (78, "An-Naba", 40, 1.5), (79, "An-Nazi'at", 46, 1.5), (80, "Abasa", 42, 1.5),
    (81, "At-Takwir", 29, 1), (82, "Al-Infitar", 19, 1), (83, "Al-Mutaffifin", 36, 1.5), (84, "Al-Inshiqaq", 25, 1),
    (85, "Al-Buruj", 22, 1), (86, "At-Tariq", 17, 0.5), (87, "Al-A'la", 19, 0.5), (88, "Al-Ghashiyah", 26, 1),
    (89, "Al-Fajr", 30, 1.5),
    (90, "Al-Balad to An-Nas", 208, 10)
]

# --- DYNAMIC SURAH SPLITTER (>= 15 Pages) ---
EXPANDED_SURAH_DATA = []
for s in SURAH_DATA:
    if s[3] >= 15:
        total_verses = s[2]
        total_pages = s[3]
        parts = int(total_pages // 5)
        remainder = total_pages % 5
       
        verses_accumulated = 0
        start_page = 1
       
        for p in range(parts):
            end_page = start_page + 4
            # If this is the absolute last chunk (because there's no remainder), give it the remaining verses to prevent rounding errors
            if p == parts - 1 and remainder == 0:
                verse_est = total_verses - verses_accumulated
            else:
                verse_est = int(round(total_verses * (5 / total_pages)))
           
            verses_accumulated += verse_est
            EXPANDED_SURAH_DATA.append((s[0], f"{s[1]} (Pages {start_page}-{end_page})", verse_est, 5))
            start_page += 5
           
        if remainder > 0:
            verse_est = total_verses - verses_accumulated
            end_page = int(start_page + remainder - 1)
            page_label = f"Page {start_page}" if start_page == end_page else f"Pages {start_page}-{end_page}"
            EXPANDED_SURAH_DATA.append((s[0], f"{s[1]} ({page_label})", verse_est, remainder))
    else:
        EXPANDED_SURAH_DATA.append(s)

surah_options = [f"{s[0]}. {s[1]}" for s in EXPANDED_SURAH_DATA]

# --- STREAMLIT UI & SESSION STATE ---
st.set_page_config(page_title="Quran Memorization Tracker", layout="wide")

if 'cat1' not in st.session_state: st.session_state['cat1'] = []
if 'cat2' not in st.session_state: st.session_state['cat2'] = []

def add_juz_30():
    juz_30 = [f"{s[0]}. {s[1]}" for s in EXPANDED_SURAH_DATA if s[0] >= 78]
    st.session_state['cat1'] = list(set(st.session_state['cat1'] + juz_30))

def add_juz_29():
    juz_29 = [f"{s[0]}. {s[1]}" for s in EXPANDED_SURAH_DATA if 67 <= s[0] <= 77]
    st.session_state['cat1'] = list(set(st.session_state['cat1'] + juz_29))

def add_juz_30_cat2():
    juz_30 = [f"{s[0]}. {s[1]}" for s in EXPANDED_SURAH_DATA if s[0] >= 78]
    st.session_state['cat2'] = list(set(st.session_state['cat2'] + juz_30))

def add_juz_29_cat2():
    juz_29 = [f"{s[0]}. {s[1]}" for s in EXPANDED_SURAH_DATA if 67 <= s[0] <= 77]
    st.session_state['cat2'] = list(set(st.session_state['cat2'] + juz_29))

col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("📖 Quran Memorization Tracker")
with col_btn:
    st.write("")
    if st.button("🗑️ Clear All Selections"):
        st.session_state['cat1'] = []
        st.session_state['cat2'] = []
        st.rerun()

st.write("Generate a custom daily Excel tracker based on your memorization progress.")

st.markdown("### ⏳ Daily Commitment")
daily_time = st.text_input("How much time will you dedicate to the Quran daily?", placeholder="e.g., 30 minutes, 1 hour")

st.markdown("### 🗂️ Categorize the Surahs (Long Surahs are split into 5-page parts!)")

col1, col2 = st.columns(2)
with col1:
    st.button("⚡ Quick Add: Juz 30 to Category 1", on_click=add_juz_30)
with col2:
    st.button("⚡ Quick Add: Juz 29 to Category 1", on_click=add_juz_29)

cat1_selections = st.multiselect("🟢 Category 1: Memorized with Confidence", options=surah_options, key='cat1')

col3, col4 = st.columns(2)
with col3:
    st.button("⚡ Quick Add: Juz 30 to Category 2", on_click=add_juz_30_cat2)
with col4:
    st.button("⚡ Quick Add: Juz 29 to Category 2", on_click=add_juz_29_cat2)

cat2_selections = st.multiselect("🟡 Category 2: Needs Revision", options=surah_options, key='cat2')

# --- EXCEL GENERATION LOGIC ---
if st.button("Generate My Custom Excel Tracker", type="primary"):
    tracker_data = []
    for s in EXPANDED_SURAH_DATA:
        surah_string = f"{s[0]}. {s[1]}"
        if surah_string in cat1_selections:
            category = "1 - Confident"
        elif surah_string in cat2_selections:
            category = "2 - Needs Revision"
        else:
            category = "3 - Not Memorized"
           
        tracker_data.append({
            "No.": s[0],
            "Surah": s[1],
            "Total Verses": s[2],
            "Total Pages": s[3],
            "Category": category,
            "Last Revised (Date)": "",  
            "Next Revision Due": "",    
            "Status": "",              
            "Notes": ""
        })

    df = pd.DataFrame(tracker_data)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
   
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
    bold_format = workbook.add_format({'bold': True})
    progress_format = workbook.add_format({'bold': True, 'font_color': '#006100', 'font_size': 14})
    fire_format = workbook.add_format({'bold': True, 'font_color': '#D9534F', 'font_size': 14})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
    border_format = workbook.add_format({'border': 1})
    formula_gray_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'num_format': 'yyyy-mm-dd'})
   
    red_bg = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    green_bg = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
   
    total_items = len(EXPANDED_SURAH_DATA)
    last_dash_row = total_items + 5
   
    # --- SHEET 1: SURAH DASHBOARD ---
    worksheet = workbook.add_worksheet('Surah Dashboard')
    worksheet.freeze_panes(5, 2)
   
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 32)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 12)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 18)
    worksheet.set_column('G:G', 18)
    worksheet.set_column('H:H', 15)
    worksheet.set_column('I:I', 20)
    worksheet.set_column('J:J', None, None, {'hidden': True})

    worksheet.write('A1', f"Daily Dedication Goal: {daily_time if daily_time else 'Not specified'}", bold_format)
    worksheet.write('A2', "Rule: Category 1 & 2 Surahs must be revised every 14 days.")
    worksheet.write_formula('A3', f'="🏆 Total Quran Memorized: " & TEXT(SUMIF(E6:E{last_dash_row}, "1 - Confident", D6:D{last_dash_row})/604, "0.0%") & " (" & SUMIF(E6:E{last_dash_row}, "1 - Confident", D6:D{last_dash_row}) & " / 604 pages)"', progress_format)
   
    # --- CONSISTENCY TRACKER ---
    worksheet.write_formula('A4', '="🔥 Total Days Logged: " & COUNTA(Daily_Log!C2:C1001) & " Days"', fire_format)
   
    headers = list(df.columns)
    for col_num, data in enumerate(headers):
        worksheet.write(4, col_num, data, header_format)

    for row_num in range(len(df)):
        excel_row = row_num + 5
        worksheet.write(excel_row, 0, df.iloc[row_num]['No.'], border_format)
        worksheet.write(excel_row, 1, df.iloc[row_num]['Surah'], border_format)
        worksheet.write(excel_row, 2, df.iloc[row_num]['Total Verses'], border_format)
        worksheet.write(excel_row, 3, df.iloc[row_num]['Total Pages'], border_format)
        worksheet.write(excel_row, 4, df.iloc[row_num]['Category'], border_format)
       
        # New Bulletproof Internal Math: We hardcode the exact index number into the maxifs query!
        item_index = row_num + 1
        range_formula = f'=IF(MAXIFS(Daily_Log!$A$2:$A$1001, Daily_Log!$H$2:$H$1001, "<={item_index}", Daily_Log!$I$2:$I$1001, ">={item_index}", Daily_Log!$E$2:$E$1001, "Yes")=0, "", MAXIFS(Daily_Log!$A$2:$A$1001, Daily_Log!$H$2:$H$1001, "<={item_index}", Daily_Log!$I$2:$I$1001, ">={item_index}", Daily_Log!$E$2:$E$1001, "Yes"))'
        worksheet.write_formula(excel_row, 5, range_formula, formula_gray_format)
       
        f_formula = f'=IF(OR(E{excel_row+1}="1 - Confident", E{excel_row+1}="2 - Needs Revision"), IF(F{excel_row+1}="", "", F{excel_row+1}+14), "")'
        worksheet.write_formula(excel_row, 6, f_formula, formula_gray_format)
       
        g_formula = f'=IF(E{excel_row+1}="3 - Not Memorized", "⚪ Not Started", IF(F{excel_row+1}="", "Pending", IF(TODAY()>G{excel_row+1}, "🔴 Overdue", "🟢 Good")))'
        worksheet.write_formula(excel_row, 7, g_formula, border_format)
       
        worksheet.write_blank(excel_row, 8, None, border_format)
       
        # Write the full concatenated string to hidden column J so the Daily Log can exact-match it
        worksheet.write_formula(excel_row, 9, f'=$A{excel_row+1} & ". " & $B{excel_row+1}')

    for row in range(5, last_dash_row):
        worksheet.data_validation(row, 4, row, 4, {
            'validate': 'list',
            'source': ['1 - Confident', '2 - Needs Revision', '3 - Not Memorized']
        })
       
    worksheet.conditional_format(f'H6:H{last_dash_row}', {'type': 'cell', 'criteria': '==', 'value': '"🔴 Overdue"', 'format': red_bg})
    worksheet.conditional_format(f'H6:H{last_dash_row}', {'type': 'cell', 'criteria': '==', 'value': '"🟢 Good"', 'format': green_bg})

    worksheet.write('L4', 'Category', header_format)
    worksheet.write('M4', 'Total Pages', header_format)
    worksheet.write('L5', '1 - Confident')
    worksheet.write_formula('M5', f'=SUMIF($E$6:$E${last_dash_row}, "1 - Confident", $D$6:$D${last_dash_row})')
    worksheet.write('L6', '2 - Needs Revision')
    worksheet.write_formula('M6', f'=SUMIF($E$6:$E${last_dash_row}, "2 - Needs Revision", $D$6:$D${last_dash_row})')
    worksheet.write('L7', '3 - Not Memorized')
    worksheet.write_formula('M7', f'=SUMIF($E$6:$E${last_dash_row}, "3 - Not Memorized", $D$6:$D${last_dash_row})')

    chart = workbook.add_chart({'type': 'pie'})
    chart.add_series({
        'name': 'Memorization Progress',
        'categories': "='Surah Dashboard'!$L$5:$L$7",
        'values': "='Surah Dashboard'!$M$5:$M$7",
        'points': [{'fill': {'color': '#92D050'}}, {'fill': {'color': '#FFC000'}}, {'fill': {'color': '#D9D9D9'}}],
    })
    chart.set_title({'name': 'Memorization by Page Count'})
    worksheet.insert_chart('L9', chart, {'x_scale': 1.2, 'y_scale': 1.2})

    # --- SHEET 2: DAILY LOG ---
    log_sheet = workbook.add_worksheet('Daily_Log')
    log_sheet.freeze_panes(1, 0)
   
    log_sheet.set_column('A:A', 15, date_format)
    log_sheet.set_column('B:B', 15)
    log_sheet.set_column('C:C', 35)
    log_sheet.set_column('D:D', 35)
    log_sheet.set_column('E:E', 25)
    log_sheet.set_column('F:F', 25)
    log_sheet.set_column('G:G', 25)
   
    log_headers = ['Date', 'Day', 'Start Surah', 'End Surah (Optional)', 'Completed Surah Today?', 'Specific Verses (If No)', 'Type (Revision/New)']
    for col_num, data in enumerate(log_headers):
        log_sheet.write(0, col_num, data, header_format)
       
    start_date = date.today()
   
    log_sheet.set_column('Z:Z', None, None, {'hidden': True})
    log_sheet.set_column('H:I', None, None, {'hidden': True})
   
    # Generate the dynamic list for the dropdowns
    for i in range(total_items):
        dash_row = i + 6
        log_sheet.write_formula(f'Z{i+1}', f'=IF(\'Surah Dashboard\'!E{dash_row}<>"3 - Not Memorized", \'Surah Dashboard\'!J{dash_row}, "")')
   
    day_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'italic': True})
   
    for row in range(1, 1001):
        current_date = start_date + timedelta(days=row-1)
       
        log_sheet.write_datetime(row, 0, current_date, date_format)
        log_sheet.write_formula(row, 1, f'=IF(ISBLANK(A{row+1}), "", TEXT(A{row+1}, "dddd"))', day_format)
       
        log_sheet.data_validation(row, 2, row, 2, {'validate': 'list', 'source': f'=$Z$1:$Z${total_items}', 'ignore_blank': True})
        log_sheet.data_validation(row, 3, row, 3, {'validate': 'list', 'source': f'=$Z$1:$Z${total_items}', 'ignore_blank': True})
        log_sheet.data_validation(row, 4, row, 4, {'validate': 'list', 'source': ['Yes', 'No']})
        log_sheet.data_validation(row, 6, row, 6, {'validate': 'list', 'source': ['Revision', 'New Memorization']})
       
        # Exact matching IDs to solve the "Split Surah" Bulk Logging!
        log_sheet.write_formula(row, 7, f'=IFERROR(MATCH(C{row+1}, \'Surah Dashboard\'!$J$6:$J${last_dash_row}, 0), 0)')
        log_sheet.write_formula(row, 8, f'=IFERROR(IF(D{row+1}="", H{row+1}, MATCH(D{row+1}, \'Surah Dashboard\'!$J$6:$J${last_dash_row}, 0)), 0)')
       
    workbook.close()
   
    st.success("✅ Your custom tracker is ready!")
    st.download_button(label="📥 Download Excel Tracker", data=output.getvalue(), file_name="Quran_Memorization_Tracker.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
