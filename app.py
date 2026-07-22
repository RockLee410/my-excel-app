import streamlit as st
import pandas as pd
import xlsxwriter
from io import BytesIO

# --- DATA: Surahs 1-89, plus grouped 90-114 ---
# Now includes a 4th value: Exact Page Count (based on Madinah Mushaf)
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
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
    border_format = workbook.add_format({'border': 1})
    formula_gray_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'num_format': 'yyyy-mm-dd'})
   
    # --- SHEET 1: SURAH DASHBOARD & VISUALS ---
    worksheet = workbook.add_worksheet('Surah Dashboard')
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 25)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 12)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 18)
    worksheet.set_column('G:G', 18)
    worksheet.set_column('H:H', 15)
    worksheet.set_column('I:I', 20)

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
        worksheet.write(excel_row, 3, df.iloc[row_num]['Total Pages'], border_format)
        worksheet.write(excel_row, 4, df.iloc[row_num]['Category'], border_format)
       
        range_formula = f'=IF(MAXIFS(\'Daily Log\'!$A$2:$A$1001, \'Daily Log\'!$H$2:$H$1001, "<="&$A{excel_row+1}, \'Daily Log\'!$I$2:$I$1001, ">="&$A{excel_row+1})=0, "", MAXIFS(\'Daily Log\'!$A$2:$A$1001, \'Daily Log\'!$H$2:$H$1001, "<="&$A{excel_row+1}, \'Daily Log\'!$I$2:$I$1001, ">="&$A{excel_row+1}))'
        worksheet.write_formula(excel_row, 5, range_formula, formula_gray_format)
       
        f_formula = f'=IF(OR(E{excel_row+1}="1 - Confident", E{excel_row+1}="2 - Needs Revision"), IF(F{excel_row+1}="", "", F{excel_row+1}+14), "")'
        worksheet.write_formula(excel_row, 6, f_formula, formula_gray_format)
       
        g_formula = f'=IF(E{excel_row+1}="3 - Not Memorized", "⚪ Not Started", IF(F{excel_row+1}="", "Pending", IF(TODAY()>G{excel_row+1}, "🔴 Overdue", "🟢 Good")))'
        worksheet.write_formula(excel_row, 7, g_formula, border_format)
       
        worksheet.write_blank(excel_row, 8, None, border_format)

    for row in range(5, len(df) + 5):
        worksheet.data_validation(row, 4, row, 4, {
            'validate': 'list',
            'source': ['1 - Confident', '2 - Needs Revision', '3 - Not Memorized']
        })

    # Updated Pie Chart math to sum the Pages (Col D) based on Category (Col E)
    last_row = len(df) + 5
    worksheet.write('L4', 'Category', header_format)
    worksheet.write('M4', 'Total Pages', header_format)
    worksheet.write('L5', '1 - Confident')
    worksheet.write_formula('M5', f'=SUMIF($E$6:$E${last_row}, "1 - Confident", $D$6:$D${last_row})')
    worksheet.write('L6', '2 - Needs Revision')
    worksheet.write_formula('M6', f'=SUMIF($E$6:$E${last_row}, "2 - Needs Revision", $D$6:$D${last_row})')
    worksheet.write('L7', '3 - Not Memorized')
    worksheet.write_formula('M7', f'=SUMIF($E$6:$E${last_row}, "3 - Not Memorized", $D$6:$D${last_row})')

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
    log_sheet = workbook.add_worksheet('Daily Log')
    log_sheet.set_column('A:A', 15, date_format)
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
   
    for i in range(90):
        dash_row = i + 6
        log_sheet.write_formula(f'Z{i+1}', f'=IF(\'Surah Dashboard\'!E{dash_row}<>"3 - Not Memorized", \'Surah Dashboard\'!A{dash_row} & ". " & \'Surah Dashboard\'!B{dash_row}, "")')
   
    day_format = workbook.add_format({'bg_color': '#F2F2F2', 'border': 1, 'italic': True})
   
    for row in range(1, 1001):
        log_sheet.write_formula(row, 1, f'=IF(ISBLANK(A{row+1}), "", TEXT(A{row+1}, "dddd"))', day_format)
       
        log_sheet.data_validation(row, 2, row, 2, {'validate': 'list', 'source': '=$Z$1:$Z$90', 'ignore_blank': True})
        log_sheet.data_validation(row, 3, row, 3, {'validate': 'list', 'source': '=$Z$1:$Z$90', 'ignore_blank': True})
        log_sheet.data_validation(row, 4, row, 4, {'validate': 'list', 'source': ['Yes', 'No']})
        log_sheet.data_validation(row, 6, row, 6, {'validate': 'list', 'source': ['Revision', 'New Memorization']})
       
        log_sheet.write_formula(row, 7, f'=IFERROR(VALUE(LEFT(C{row+1}, FIND(".", C{row+1})-1)), 0)')
        log_sheet.write_formula(row, 8, f'=IFERROR(IF(D{row+1}="", H{row+1}, VALUE(LEFT(D{row+1}, FIND(".", D{row+1})-1))), 0)')
       
    workbook.close()
   
    st.success("✅ Your custom tracker is ready!")
    st.download_button(label="📥 Download Excel Tracker", data=output.getvalue(), file_name="Quran_Memorization_Tracker.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")