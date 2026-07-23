import streamlit as st
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

# --- STREAMLIT UI & SESSION STATE ---
st.set_page_config(page_title="Quran Memorization Tracker", layout="wide")

if "cat1" not in st.session_state: st.session_state["cat1"] = []
if "cat2" not in st.session_state: st.session_state["cat2"] = []

def add_juz_30():
    juz_30 = [f"{s[0]}. {s[1]}" for s in SURAH_DATA if s[0] >= 78]
    st.session_state["cat1"] = list(set(st.session_state["cat1"] + juz_30))
def add_juz_29():
    juz_29 = [f"{s[0]}. {s[1]}" for s in SURAH_DATA if 67 <= s[0] <= 77]
    st.session_state["cat1"] = list(set(st.session_state["cat1"] + juz_29))
def add_juz_30_cat2():
    juz_30 = [f"{s[0]}. {s[1]}" for s in SURAH_DATA if s[0] >= 78]
    st.session_state["cat2"] = list(set(st.session_state["cat2"] + juz_30))
def add_juz_29_cat2():
    juz_29 = [f"{s[0]}. {s[1]}" for s in SURAH_DATA if 67 <= s[0] <= 77]
    st.session_state["cat2"] = list(set(st.session_state["cat2"] + juz_29))

col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("📖 Quran Memorization Tracker")
with col_btn:
    st.write("") 
    if st.button("🗑️ Clear All Selections"):
        st.session_state["cat1"] = []
        st.session_state["cat2"] = []
        st.rerun()

st.write("Generate a custom daily Excel tracker based on your memorization progress.")

st.markdown("### ⏳ Daily Commitment")
daily_time = st.text_input("How much time will you dedicate to the Quran daily?", placeholder="e.g., 30 minutes, 1 hour")

st.markdown("### 🗂️ Categorize the Surahs (Now tracked flawlessly by Page!)")
col1, col2 = st.columns(2)
with col1:
    st.button("⚡ Quick Add: Juz 30 to Category 1", on_click=add_juz_30)
with col2:
    st.button("⚡ Quick Add: Juz 29 to Category 1", on_click=add_juz_29)
cat1_selections = st.multiselect("🟢 Category 1: Memorized with Confidence", options=surah_options, key="cat1")

col3, col4 = st.columns(2)
with col3:
    st.button("⚡ Quick Add: Juz 30 to Category 2", on_click=add_juz_30_cat2)
with col4:
    st.button("⚡ Quick Add: Juz 29 to Category 2", on_click=add_juz_29_cat2)
cat2_selections = st.multiselect("🟡 Category 2: Needs Revision", options=surah_options, key="cat2")

# --- EXCEL GENERATION LOGIC ---
if st.button("Generate My Custom Excel Tracker", type="primary"):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    
    # Formats
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
    bold_format = workbook.add_format({'bold': True})
    progress_format = workbook.add_format({'bold': True, 'font_color': '#006100', 'font_size': 14})
    fire_format = workbook.add_format({'bold': True, 'font_color': '#D9534F', 'font_size': 14})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
    border_format = workbook.add_format({'border': 1})
    formula_gray_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'num_format': 'yyyy-mm-dd'})
    
    merge_format_center = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
    merge_format_left = workbook.add_format({'border': 1, 'align': 'left', 'valign': 'vcenter'})
    
    red_bg = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
    green_bg = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    
    # --- SHEET 1: SURAH DASHBOARD ---
    worksheet = workbook.add_worksheet('Surah Dashboard')
    worksheet.freeze_panes(5, 3) 
    
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 22)
    worksheet.set_column('C:C', 10)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 18)
    worksheet.set_column('F:F', 18)
    worksheet.set_column('G:G', 15)
    worksheet.set_column('H:H', 20)

    worksheet.write('A1', f"Daily Dedication Goal: {daily_time if daily_time else 'Not specified'}", bold_format)
    worksheet.write('A2', "Rule: Category 1 & 2 Pages must be revised every 14 days.")
    worksheet.write_formula('A4', '="🔥 Total Days Logged: " & COUNTA(Daily_Log!A2:A1001) & " Days"', fire_format)
    
    headers = ['No.', 'Surah', 'Page', 'Category', 'Last Revised (Date)', 'Next Revision Due', 'Status', 'Notes']
    for col_num, data in enumerate(headers):
        worksheet.write(4, col_num, data, header_format)

    current_excel_row = 5 # Starts at row 6 in Excel
    
    for s in SURAH_DATA:
        surah_string = f"{s[0]}. {s[1]}"
        if surah_string in cat1_selections:
            category = "1 - Confident"
        elif surah_string in cat2_selections:
            category = "2 - Needs Revision"
        else:
            category = "3 - Not Memorized"
            
        pages = list(range(s[2], s[3] + 1))
        num_pages = len(pages)
        start_row = current_excel_row
        end_row = current_excel_row + num_pages - 1
        
        # Merge Cells for Surahs spanning multiple pages!
        if num_pages > 1:
            worksheet.merge_range(start_row, 0, end_row, 0, s[0], merge_format_center)
            worksheet.merge_range(start_row, 1, end_row, 1, s[1], merge_format_left)
        else:
            worksheet.write(start_row, 0, s[0], merge_format_center)
            worksheet.write(start_row, 1, s[1], merge_format_left)
            
        for i, p in enumerate(pages):
            row = start_row + i
            worksheet.write(row, 2, p, border_format)
            worksheet.write(row, 3, category, border_format)
            
            # The Math Engine now checks the hidden 'Effective Start Page' (H) and 'Effective End Page' (I) in Daily Log
            range_formula = f'=IF(MAXIFS(Daily_Log!$A$2:$A$1001, Daily_Log!$H$2:$H$1001, "<="&$C{row+1}, Daily_Log!$I$2:$I$1001, ">="&$C{row+1})=0, "", MAXIFS(Daily_Log!$A$2:$A$1001, Daily_Log!$H$2:$H$1001, "<="&$C{row+1}, Daily_Log!$I$2:$I$1001, ">="&$C{row+1}))'
            worksheet.write_formula(row, 4, range_formula, formula_gray_format) 
            
            f_formula = f'=IF(OR(D{row+1}="1 - Confident", D{row+1}="2 - Needs Revision"), IF(E{row+1}="", "", E{row+1}+14), "")'
            worksheet.write_formula(row, 5, f_formula, formula_gray_format)
            
            g_formula = f'=IF(D{row+1}="3 - Not Memorized", "⚪ Not Started", IF(E{row+1}="", "Pending", IF(TODAY()>F{row+1}, "🔴 Overdue", "🟢 Good")))'
            worksheet.write_formula(row, 6, g_formula, border_format)
            
            worksheet.write_blank(row, 7, None, border_format)
            
        current_excel_row += num_pages
        
    last_dash_row = current_excel_row + 4 # Account for header offset
    
    # Needs to be written after last_dash_row is calculated
    worksheet.write_formula('A3', f'="🏆 Total Pages Memorized: " & TEXT(COUNTIF(D6:D{last_dash_row}, "1 - Confident")/604, "0.0%") & " (" & COUNTIF(D6:D{last_dash_row}, "1 - Confident") & " / 604 pages)"', progress_format)

    for row in range(5, last_dash_row):
        worksheet.data_validation(row, 3, row, 3, {
            'validate': 'list',
            'source': ['1 - Confident', '2 - Needs Revision', '3 - Not Memorized']
        })
        
    worksheet.conditional_format(f'G6:G{last_dash_row}', {'type': 'cell', 'criteria': '==', 'value': '"🔴 Overdue"', 'format': red_bg})
    worksheet.conditional_format(f'G6:G{last_dash_row}', {'type': 'cell', 'criteria': '==', 'value': '"🟢 Good"', 'format': green_bg})

    # Chart tracking
    worksheet.write('J4', 'Category', header_format)
    worksheet.write('K4', 'Total Pages', header_format)
    worksheet.write('J5', '1 - Confident')
    worksheet.write_formula('K5', f'=COUNTIF($D$6:$D${last_dash_row}, "1 - Confident")')
    worksheet.write('J6', '2 - Needs Revision')
    worksheet.write_formula('K6', f'=COUNTIF($D$6:$D${last_dash_row}, "2 - Needs Revision")')
    worksheet.write('J7', '3 - Not Memorized')
    worksheet.write_formula('K7', f'=COUNTIF($D$6:$D${last_dash_row}, "3 - Not Memorized")')

    chart = workbook.add_chart({'type': 'pie'})
    chart.add_series({
        'name': 'Memorization Progress',
        'categories': "='Surah Dashboard'!$J$5:$J$7",
        'values': "='Surah Dashboard'!$K$5:$K$7",
        'points': [{'fill': {'color': '#92D050'}}, {'fill': {'color': '#FFC000'}}, {'fill': {'color': '#D9D9D9'}}],
    })
    chart.set_title({'name': 'Memorization by Page Count'})
    worksheet.insert_chart('J9', chart, {'x_scale': 1.2, 'y_scale': 1.2})

    # --- SHEET 2: DAILY LOG ---
    log_sheet = workbook.add_worksheet('Daily_Log') 
    log_sheet.freeze_panes(1, 0) 
    
    log_sheet.set_column('A:A', 15, date_format) 
    log_sheet.set_column('B:B', 15) 
    log_sheet.set_column('C:C', 25) 
    log_sheet.set_column('D:D', 20) 
    log_sheet.set_column('E:F', 20)
    log_sheet.set_column('G:G', 35)
    
    log_headers = ['Date', 'Day', 'Surah', 'Read Entire Surah?', 'Start Page (If No)', 'End Page (Optional)', 'Notes / Specific Verses']
    for col_num, data in enumerate(log_headers):
        log_sheet.write(0, col_num, data, header_format)
        
    start_date = date.today()
    
    # Hide the complex math lookups completely from view
    log_sheet.set_column('H:I', None, None, {'hidden': True})
    log_sheet.set_column('AA:AC', None, None, {'hidden': True})
    
    # Populate the hidden exact dictionary for the Full Surah feature (Columns AA, AB, AC)
    for i, s in enumerate(SURAH_DATA):
        log_sheet.write_string(i, 26, s[1]) # Name
        log_sheet.write_number(i, 27, s[2]) # Start Page
        log_sheet.write_number(i, 28, s[3]) # End Page
        
    day_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'italic': True})
    
    for row in range(1, 1001):
        current_date = start_date + timedelta(days=row-1)
        
        log_sheet.write_datetime(row, 0, current_date, date_format)
        log_sheet.write_formula(row, 1, f'=IF(ISBLANK(A{row+1}), "", TEXT(A{row+1}, "dddd"))', day_format)
        
        # New Dropdowns
        log_sheet.data_validation(row, 2, row, 2, {'validate': 'list', 'source': f'=$AA$1:$AA${total_surahs}', 'ignore_blank': True})
        log_sheet.data_validation(row, 3, row, 3, {'validate': 'list', 'source': ['Yes', 'No'], 'ignore_blank': True})
        
        # The Hidden Brain (Columns H and I): It checks if "Yes" is selected. If so, it instantly VLOOKUPs the real pages!
        log_sheet.write_formula(row, 7, f'=IFERROR(IF($D{row+1}="Yes", VLOOKUP($C{row+1}, $AA$1:$AC$114, 2, FALSE), $E{row+1}), 0)')
        log_sheet.write_formula(row, 8, f'=IFERROR(IF($D{row+1}="Yes", VLOOKUP($C{row+1}, $AA$1:$AC$114, 3, FALSE), IF(ISBLANK($F{row+1}), $H{row+1}, $F{row+1})), 0)')
        
    workbook.close()
    
    st.success("✅ Your custom tracker is ready!")
    st.download_button(label="📥 Download Excel Tracker", data=output.getvalue(), file_name="Quran_Memorization_Tracker.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")