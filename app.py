import streamlit as st
import pandas as pd
import xlsxwriter
from io import BytesIO

# --- DATA: All 114 Surahs and their verse counts ---
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
    (89, "Al-Fajr", 30), (90, "Al-Balad", 20), (91, "Ash-Shams", 15), (92, "Al-Lail", 21),
    (93, "Ad-Duha", 11), (94, "Ash-Sharh", 8), (95, "At-Tin", 8), (96, "Al-Alaq", 19),
    (97, "Al-Qadr", 5), (98, "Al-Bayyinah", 8), (99, "Az-Zalzalah", 8), (100, "Al-Adiyat", 11),
    (101, "Al-Qari'ah", 11), (102, "At-Takathur", 8), (103, "Al-Asr", 3), (104, "Al-Humazah", 9),
    (105, "Al-Fil", 5), (106, "Quraysh", 4), (107, "Al-Ma'un", 7), (108, "Al-Kawthar", 3),
    (109, "Al-Kafirun", 6), (110, "An-Nasr", 3), (111, "Al-Masad", 5), (112, "Al-Ikhlas", 4),
    (113, "Al-Falaq", 5), (114, "An-Nas", 6)
]

# --- STREAMLIT UI ---
st.set_page_config(page_title="Quran Memorization Tracker", layout="centered")

st.title("📖 Quran Memorization Tracker")
st.write("Generate a custom daily Excel tracker based on your memorization progress.")

st.markdown("### ⏳ Daily Commitment")
daily_time = st.text_input("How much time will you dedicate to the Quran daily?", placeholder="e.g., 30 minutes, 1 hour")

st.markdown("### 🗂️ Categorize the Surahs")
st.write("Select the Surahs for Categories 1 and 2. Any unselected Surahs will automatically be placed in Category 3 (Not Memorized).")

surah_options = [f"{s[0]}. {s[1]}" for s in SURAH_DATA]

# Category 1 Input
cat1_selections = st.multiselect(
    "🟢 Category 1: Memorized with Confidence",
    options=surah_options,
    help="These Surahs require revision once every 14 days."
)

# Filter out Cat 1 from Cat 2 options
remaining_for_cat2 = [s for s in surah_options if s not in cat1_selections]

# Category 2 Input
cat2_selections = st.multiselect(
    "🟡 Category 2: Needs Revision",
    options=remaining_for_cat2,
    help="These are your priority for daily revision."
)

# --- EXCEL GENERATION LOGIC ---
if st.button("Generate My Custom Excel Tracker"):
    # Build the base data
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
            "Last Revised (Date)": "",  # Blank for user to fill in Excel
            "Next Revision Due": "",    # Will be a formula
            "Status": "",               # Will be a formula
            "Notes / Verses Revised": ""
        })

    df = pd.DataFrame(tracker_data)

    # Write to Excel using xlsxwriter to inject formulas & formatting
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
   
    # Format settings
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D3D3D3', 'border': 1})
    bold_format = workbook.add_format({'bold': True})
    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd', 'border': 1})
    border_format = workbook.add_format({'border': 1})
   
    # Sheet 1: Master Dashboard
    worksheet = workbook.add_worksheet('Surah Dashboard')
   
    # Set Columns width
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 18)
    worksheet.set_column('C:C', 12)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 18)
    worksheet.set_column('F:F', 18)
    worksheet.set_column('G:G', 15)
    worksheet.set_column('H:H', 30)

    # Add motivational header
    worksheet.write('A1', f"Daily Dedication Goal: {daily_time if daily_time else 'Not specified'}", bold_format)
    worksheet.write('A2', "Rule: Category 1 Surahs must be revised every 14 days. Prioritize Category 2 before starting Category 3.")
   
    # Write Headers
    headers = list(df.columns)
    for col_num, data in enumerate(headers):
        worksheet.write(4, col_num, data, header_format)

    # Write Data and Formulas
    for row_num in range(len(df)):
        excel_row = row_num + 5  # +5 because data starts on row 6 (index 5)
       
        # Write basic static data
        worksheet.write(excel_row, 0, df.iloc[row_num]['No.'], border_format)
        worksheet.write(excel_row, 1, df.iloc[row_num]['Surah'], border_format)
        worksheet.write(excel_row, 2, df.iloc[row_num]['Total Verses'], border_format)
        worksheet.write(excel_row, 3, df.iloc[row_num]['Category'], border_format)
       
        # Apply blank cell with border for Date entry
        worksheet.write_blank(excel_row, 4, None, date_format)
       
        # Formula for Next Revision Due (E column is 5th column, so E6, E7 etc.)
        # If Last Revised (E) is empty, leave F empty. Otherwise add 14 days.
        f_formula = f'=IF(ISBLANK(E{excel_row+1}), "", E{excel_row+1}+14)'
        worksheet.write_formula(excel_row, 5, f_formula, date_format)
       
        # Formula for Status (Overdue or Good)
        g_formula = f'=IF(ISBLANK(E{excel_row+1}), "Pending", IF(TODAY()>F{excel_row+1}, "🔴 Overdue", "🟢 Good"))'
        worksheet.write_formula(excel_row, 6, g_formula, border_format)
       
        worksheet.write_blank(excel_row, 7, None, border_format)

    # Sheet 2: Daily Log (Blank structured sheet for raw daily inputs)
    log_sheet = workbook.add_worksheet('Daily Log')
    log_sheet.set_column('A:A', 15)
    log_sheet.set_column('B:B', 20)
    log_sheet.set_column('C:C', 15)
    log_sheet.set_column('D:D', 15)
    log_sheet.set_column('E:E', 30)
   
    log_headers = ['Date', 'Surah', 'From Verse', 'To Verse', 'Type (Revision/New)']
    for col_num, data in enumerate(log_headers):
        log_sheet.write(0, col_num, data, header_format)
       
    workbook.close()
   
    st.success("✅ Your custom tracker is ready!")
   
    st.download_button(
        label="📥 Download Excel Tracker",
        data=output.getvalue(),
        file_name="Quran_Memorization_Tracker.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )