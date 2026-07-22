import streamlit as st
import pandas as pd
import xlsxwriter
from io import BytesIO

# --- DATA: Surahs 1-89, plus grouped 90-114 ---
SURAH_DATA = [
    (1, "Al-Fatihah", 7), (2, "Al-Baqarah", 286), (3, "Aal-Imran", 200), (4, "An-Nisa", 176),
    (5, "Al-Ma'idah", 120), (6, "Al-An'am", 165), (7, "Al-A'raf", 206), (8, "Al-Anfal", 75),
    (9, "At-Tawbah", 129), (10, "Yunus", 109), (11, "Hud", 123), (12, "Yusuf", 111),
    (13, "Ar-Ra'd", 43), (14, "Ibrahim", 52), (15, "Al-Hijr", 99), (16, "An-Nahl", 128),
    (17, "Al-Isra", 111), (18, "Al-Kahf", 110), (19, "Maryam", 98), (20, "Taha", 135),
    (21, "Al-Anbiya", 112), (22, "Al-Hajj", 78), (23, "Al-Mu'minun", 118), (24, "An-Nur", 64),
    (25, "Al-Furqan", 77), (26, "Ash-Shu'ara", 227), (27, "An-Naml", 93), (28, "Al-Qasas", 88),
    (29, "Al-Ankabut", 69), (30, "Ar-Rum", 60), (31, "Luqman", 34), (32, "As-Sajdah", 30),
    (33, "Al-Ahzab", 73), (34, "Saba", 54), (35, "Fatir", 45), (36, "Ya-Sin", 83),
    (37, "As-Saffat", 182), (38, "Sad", 88), (39, "Az-Zumar", 75), (40, "Ghafir", 85),
    (41, "Fussilat", 54), (42, "Ash-Shura", 53), (43, "Az-Zukhruf", 89), (44, "Ad-Dukhan", 59),
    (45, "Al-Jathiyah", 37), (46, "Al-Ahqaf", 35), (47, "Muhammad", 38), (48, "Al-Fath", 29),
    (49, "Al-Hujurat", 18), (50, "Qaf", 45), (51, "Ad-Zariyat", 60), (52, "At-Tur", 49),
    (53, "An-Najm", 62), (54, "Al-Qamar", 55), (55, "Ar-Rahman", 78), (56, "Al-Waqi'ah", 96),
    (57, "Al-Hadid", 29), (58, "Al-Mujadila", 22), (59, "Al-Hashr", 24), (60, "Al-Mumtahanah", 13),
    (61, "As-Saff", 14), (62, "Al-Jumu'ah", 11), (63, "Al-Munafiqun", 11), (64, "At-Taghabun", 18),
    (65, "At-Talaq", 12), (66, "At-Tahrim", 12), (67, "Al-Mulk", 30), (68, "Al-Qalam", 52),
    (69, "Al-Haqqah", 52), (70, "Al-Ma'arij", 44), (71, "Nuh", 28), (72, "Al-Jinn", 28),
    (73, "Al-Muzzammil", 20), (74, "Al-Muddaththir", 56), (75, "Al-Qiyamah", 40), (76, "Al-Insan", 31),
    (77, "Al-Mursalat", 50), (78, "An-Naba", 40), (79, "An-Nazi'at", 46), (80, "Abasa", 42),
    (81, "At-Takwir", 29), (82, "Al-Infitar", 19), (83, "Al-Mutaffifin", 36), (84, "Al-Inshiqaq", 25),
    (85, "Al-Buruj", 22), (86, "At-Tariq", 17), (87, "Al-A'la", 19), (88, "Al-Ghashiyah", 26),
    (89, "Al-Fajr", 30),
    (90, "Al-Balad to An-Nas", 208)
]

# --- STREAMLIT UI ---
st.set_page_config(page_title="Quran Memorization Tracker", layout="wide")

st.title("📖 Quran Memorization Tracker")
st.write("Generate a custom daily Excel tracker based on your memorization progress.")

st.markdown("### ⏳ Daily Commitment")
daily_time = st.text_input("How much time will you dedicate to the Quran daily?", placeholder="e.g., 30 minutes, 1 hour")

st.markdown("### 🗂️ Categorize the Surahs")
surah_options = [f"{s[0]}. {s[1]}" for s in SURAH_DATA]

cat1_selections = st.multiselect("🟢 Category 1: Memorized with Confidence", options=surah_options)
remaining_for_cat2 = [s for s in surah_options if s not in cat1_selections]
cat2_selections = st.multiselect("🟡 Category 2: Needs Revision", options=remaining_for_cat2)

# --- EXCEL GENERATION LOGIC ---
if st.button("Generate My Custom Excel Tracker"):
    tracker_data = []
    for s in SURAH_DATA:
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
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
    border_format = workbook.add_format({'border': 1})
    formula_gray_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'num_format': 'yyyy-mm-dd'})
   
    # --- SHEET 1: SURAH DASHBOARD & VISUALS ---
    worksheet = workbook.add_worksheet('Surah Dashboard')
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 25)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 18)
    worksheet.set_column('F:F', 18)
    worksheet.set_column('G:G', 15)
    worksheet.set_column('H:H', 20)

    worksheet.write('A1', f"Daily Dedication Goal: {daily_time if daily_time else 'Not specified'}", bold_format)
    worksheet.write('A2', "Rule: Category 1 Surahs must be revised every 14 days. Prioritize Category 2 before starting Category 3.")
   
    headers = list(df.columns)
    for col_num, data in enumerate(headers):
        worksheet.write(4, col_num, data, header_format)

    for row_num in range(len(df)):
        excel_row = row_num + 5
        worksheet.write(excel_row, 0, df.iloc[row_num]['No.'], border_format)
        worksheet.write(excel_row, 1, df.iloc[row_num]['Surah'], border_format)
        worksheet.write(excel_row, 2, df.iloc[row_num]['Total Verses'], border_format)
        worksheet.write(excel_row, 3, df.iloc[row_num]['Category'], border_format)
       
        range_formula = f'=IF(MAXIFS(\'Daily Log\'!$A$2:$A$1001, \'Daily Log\'!$H$2:$H$1001, "<="&$A{excel_row+1}, \'Daily Log\'!$I$2:$I$1001, ">="&$A{excel_row+1})=0, "", MAXIFS(\'Daily Log\'!$A$2:$A$1001, \'Daily Log\'!$H$2:$H$1001, "<="&$A{excel_row+1}, \'Daily Log\'!$I$2:$I$1001, ">="&$A{excel_row+1}))'
        worksheet.write_formula(excel_row, 4, range_formula, formula_gray_format)
       
        f_formula = f'=IF(D{excel_row+1}="1 - Confident", IF(E{excel_row+1}="", "", E{excel_row+1}+14), "")'
        worksheet.write_formula(excel_row, 5, f_formula, formula_gray_format)
       
        g_formula = f'=IF(D{excel_row+1}="3 - Not Memorized", "⚪ Not Started", IF(D{excel_row+1}="2 - Needs Revision", "🟡 In Progress", IF(E{excel_row+1}="", "Pending", IF(TODAY()>F{excel_row+1}, "🔴 Overdue", "🟢 Good"))))'
        worksheet.write_formula(excel_row, 6, g_formula, border_format)
       
        worksheet.write_blank(excel_row, 7, None, border_format)

    for row in range(5, len(df) + 5):
        worksheet.data_validation(row, 3, row, 3, {
            'validate': 'list',
            'source': ['1 - Confident', '2 - Needs Revision', '3 - Not Memorized']
        })

    last_row = len(df) + 5
    worksheet.write('J4', 'Category', header_format)
    worksheet.write('K4', 'Count', header_format)
    worksheet.write('J5', '1 - Confident')
    worksheet.write_formula('K5', f'=COUNTIF($D$6:$D${last_row}, "1 - Confident")')
    worksheet.write('J6', '2 - Needs Revision')
    worksheet.write_formula('K6', f'=COUNTIF($D$6:$D${last_row}, "2 - Needs Revision")')
    worksheet.write('J7', '3 - Not Memorized')
    worksheet.write_formula('K7', f'=COUNTIF($D$6:$D${last_row}, "3 - Not Memorized")')

    chart = workbook.add_chart({'type': 'pie'})
    chart.add_series({
        'name': 'Memorization Progress',
        'categories': "='Surah Dashboard'!$J$5:$J$7",
        'values': "='Surah Dashboard'!$K$5:$K$7",
        'points': [{'fill': {'color': '#92D050'}}, {'fill': {'color': '#FFC000'}}, {'fill': {'color': '#D9D9D9'}}],
    })
    chart.set_title({'name': 'Memorization Progress Overview'})
    worksheet.insert_chart('J9', chart, {'x_scale': 1.2, 'y_scale': 1.2})

    # --- SHEET 2: DAILY LOG ---
    log_sheet = workbook.add_worksheet('Daily Log')
    log_sheet.set_column('A:A', 15)
    log_sheet.set_column('B:B', 15)
    log_sheet.set_column('C:C', 25)
    log_sheet.set_column('D:D', 25)
    log_sheet.set_column('E:E', 15)
    log_sheet.set_column('F:F', 25)
    log_sheet.set_column('G:G', 25)
   
    log_headers = ['Date', 'Day', 'Start Surah', 'End Surah (Optional)', 'Full Surah?', 'Specific Verses (If No)', 'Type (Revision/New)']
    for col_num, data in enumerate(log_headers):
        log_sheet.write(0, col_num, data, header_format)
       
    log_sheet.set_column('Z:Z', None, None, {'hidden': True})
    log_sheet.set_column('H:I', None, None, {'hidden': True})
   
    # --- NEW: LIVE EXCEL FORMULA FOR DROPDOWN ---
    # This formula filters the Dashboard list and ignores anything marked "3 - Not Memorized"
    log_sheet.write_formula('Z1', '=FILTER(\'Surah Dashboard\'!B6:B95, \'Surah Dashboard\'!D6:D95<>"3 - Not Memorized", "No Active Surahs")')
   
    day_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'italic': True})
   
    for row in range(1, 1001):
        log_sheet.write_formula(row, 1, f'=IF(ISBLANK(A{row+1}), "", TEXT(A{row+1}, "dddd"))', day_format)
       
        # The dropdown source now looks at a large block in Z, but Excel's 'ignore_blank' feature keeps it tidy
        log_sheet.data_validation(row, 2, row, 2, {'validate': 'list', 'source': '=$Z$1:$Z$90', 'ignore_blank': True})
        log_sheet.data_validation(row, 3, row, 3, {'validate': 'list', 'source': '=$Z$1:$Z$90', 'ignore_blank': True})
       
        log_sheet.data_validation(row, 4, row, 4, {'validate': 'list', 'source': ['Yes', 'No']})
        log_sheet.data_validation(row, 6, row, 6, {'validate': 'list', 'source': ['Revision', 'New Memorization']})
       
        log_sheet.write_formula(row, 7, f'=IF(ISBLANK(C{row+1}), "", VALUE(LEFT(C{row+1}, FIND(".", C{row+1})-1)))')
        log_sheet.write_formula(row, 8, f'=IF(ISBLANK(C{row+1}), "", IF(ISBLANK(D{row+1}), H{row+1}, VALUE(LEFT(D{row+1}, FIND(".", D{row+1})-1))))')
       
    workbook.close()
   
    st.success("✅ Your custom tracker is ready!")
    st.download_button(label="📥 Download Excel Tracker", data=output.getvalue(), file_name="Quran_Memorization_Tracker.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")