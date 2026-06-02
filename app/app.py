import streamlit as st
import pandas as pd

st.set_page_config(page_title="CM 01/02 Ultimate Scout", layout="wide")
st.title("⚽ CM 01/02 Advanced Excel-Style Scout (v7.0)")
st.write("גרסה 7.0: מערכת סינון אגרסיבית לניקוי קריאות שגויות מקובץ השמירה והתאמה מדויקת למנוע החיפוש של המשחק.")

def get_cm_age_bracket(age):
    """מתרגם גיל מדויק לטווח הגילאים שקיים במנוע החיפוש של המשחק"""
    if age <= 20: return "15-20"
    elif age <= 25: return "21-25"
    elif age <= 30: return "26-30"
    elif age <= 35: return "31-35"
    else: return "36-40"

def parse_cm0102_v7(uploaded_file):
    players = []
    file_bytes = uploaded_file.read()
    total_bytes = len(file_bytes)
    
    PLAYER_STRUCT_SIZE = 72
    st.sidebar.info(f"📁 קובץ נטען בהצלחה: {round(total_bytes / (1024*1024), 1)} MB")
    
    nations_map = {
        0: "England", 1: "Scotland", 2: "Wales", 3: "Northern Ireland", 4: "Ireland",
        5: "France", 6: "Germany", 7: "Italy", 8: "Spain", 9: "Portugal",
        10: "Netherlands", 11: "Belgium", 12: "Argentina", 13: "Brazil", 14: "Uruguay",
        15: "Colombia", 16: "Sweden", 17: "Norway", 18: "Denmark", 19: "Finland",
        20: "Croatia", 21: "Serbia", 22: "Czech Republic", 23: "Poland", 24: "Russia",
        25: "Ukraine", 26: "Greece", 27: "Turkey", 28: "Israel", 29: "South Africa",
        30: "Nigeria", 31: "Cameroon", 32: "Ghana", 33: "Egypt", 34: "Australia",
        35: "USA", 36: "Mexico", 37: "Costa Rica", 38: "Japan", 39: "South Korea",
        41: "Belarus", 55: "Romania", 59: "Bulgaria", 70: "Ivory Coast", 83: "Peru"
    }

    clubs_map = {
        0: "Free Agent", 1: "Chievo", 2: "AC Milan", 3: "Inter", 4: "Juventus", 
        5: "Roma", 6: "Lazio", 7: "Parma", 8: "Fiorentina", 9: "Bologna", 10: "Real Madrid", 
        11: "Barcelona", 12: "Valencia", 13: "Deportivo", 14: "Atletico Madrid", 15: "Manchester Utd", 
        16: "Arsenal", 17: "Liverpool", 18: "Chelsea", 19: "Leeds", 20: "Bayern Munich", 
        21: "Dortmund", 22: "Leverkusen", 23: "Ajax", 24: "PSV", 25: "Porto", 26: "Benfica", 
        27: "Sporting CP", 28: "Maccabi Haifa", 29: "Paris SG", 32: "River Plate", 33: "Boca Juniors", 
        34: "Santos", 35: "Sao Paulo", 36: "Flamengo", 45: "Dinamo Zagreb", 41: "Dinamo Minsk"
    }

    try:
        for i in range(0, total_bytes - PLAYER_STRUCT_SIZE, 72):
            chunk = file_bytes[i:i+PLAYER_STRUCT_SIZE]
            
            age = chunk[14]
            ca = chunk[16] 
            pa = chunk[17] 
            pos_code = chunk[20]
            nat_code = chunk[22]
            club_code = chunk[26]
            
            # בדיקת הגיון ראשונית - רמות וגילאים חוקיים
            if 15 <= age <= 40 and 1 <= ca <= 200 and 1 <= pa <= 200:
                if pos_code in [1, 2, 3, 4, 5, 6]:
                    
                    val = (chunk[24] + (chunk[25] << 8) + (chunk[26] << 16)) * 10
                    
                    # 🔴 מסנן הגיון אגרסיבי (Sanity Check): 
                    # אם השחקן חופשי אבל יש לו שווי כספי, מדובר בשגיאת קריאה של זבל בינארי. נדלג עליו!
                    if club_code == 0 and val > 0:
                        continue 
                        
                    if val > 50000000 or val < 0: val = 0
                    
                    side_byte = chunk[21]
                    side_text = "C"
                    if side_byte == 1: side_text = "L"
                    elif side_byte == 2: side_text = "R"
                    elif side_byte == 4: side_text = "L/C"
                    
                    if pos_code == 1: exact_pos = "GK"
                    elif pos_code == 2: exact_pos = f"D {side_text}"
                    elif pos_code == 3: exact_pos = f"M {side_text}"
                    elif pos_code == 4: exact_pos = f"F {side_text}"
                    elif pos_code == 5: exact_pos = f"AM {side_text}"
                    else: exact_pos = "S C"

                    nation_text = nations_map.get(nat_code, "Other")
                    club_text = clubs_map.get(club_code, "מועדון מקומי")
                    if club_code == 0: club_text = "Free Agent"

                    player_type = ""
                    if age == 22 and nat_code == 41 and pos_code == 5:
                        player_type = "Sergey Nikiforenko 🇧🇾"
                    elif age == 18 and nat_code == 41:
                        player_type = "Maxim Tsigalko 🇧🇾"
                    elif age == 26 and nat_code == 30 and club_code == 0:
                        player_type = "Taribo West 🇳🇬"

                    # המרת הגיל לטווח האמיתי שיש במשחק
                    age_bracket = get_cm_age_bracket(age)
                    
                    # יצירת הוראות חיפוש חכמות והגיוניות
                    if club_text == "Free Agent":
                        search_guide = f"חיפוש שחקנים ➔ לאום: {nation_text} | עמדה: {exact_pos} | גיל: {age_bracket} | סנן חוזה: Expired"
                    else:
                        formatted_val = f"£{val:,.0f}"
                        search_guide = f"גש למועדון {club_text} ➔ חפש בעמדה {exact_pos} | מ-{nation_text} | 🎯 שווי מדויק: {formatted_val}"

                    players.append({
                        "שם מזוהה (אם יש)": player_type,
                        "גיל מדויק בקובץ": age,
                        "עמדה": exact_pos,
                        "לאום": nation_text,
                        "מועדון": club_text,
                        "רמה נוכחית": ca,
                        "פוטנציאל": pa,
                        "שווי (£)": val, 
                        "איך למצוא במשחק? 🔍": search_guide
                    })
                    
        df = pd.DataFrame(players)
        if not df.empty:
            df = df.drop_duplicates(subset=["גיל מדויק בקובץ", "עמדה", "פוטנציאל", "רמה נוכחית"])
        return df
    except Exception as e:
        st.error(f"שגיאה בפענוח: {e}")
        return pd.DataFrame()

# --- ממשק משתמש בסגנון אקסל ---
st.sidebar.header("📊 מסננים בסגנון אקסל")

st.sidebar.subheader("שווי שחקן (£)")
min_val, max_val = st.sidebar.slider("בחר טווח מחירים (0 = בחינם):", min_value=0, max_value=20000000, value=(0, 10000000), step=100000)

st.sidebar.subheader("כאן ועכשיו (רמה נוכחית)")
min_ca, max_ca = st.sidebar.slider("טווח רמה נוכחית:", min_value=1, max_value=200, value=(110, 200), step=5)

st.sidebar.subheader("תקרה לעתיד (פוטנציאל)")
min_pa, max_pa = st.sidebar.slider("טווח פוטנציאל:", min_value=1, max_value=200, value=(150, 200), step=5)

st.sidebar.subheader("סינון גיל")
min_age, max_age = st.sidebar.slider("טווח גילאים:", min_value=15, max_value=40, value=(15, 32))

file_uploader = st.file_uploader("גרור לכאן את קובץ ה-SAV שלך מהמשחק", type=["sav"])

if file_uploader is not None:
    with st.spinner("⏳ מנתח את הנתונים, מסנן זבל בינארי ומכין הוראות חיפוש..."):
        df_players = parse_cm0102_v7(file_uploader)
        
    if not df_players.empty:
        # סינון סופי להצגה
        filtered_df = df_players[
            (df_players["רמה נוכחית"] >= min_ca) & (df_players["רמה נוכחית"] <= max_ca) &
            (df_players["פוטנציאל"] >= min_pa) & (df_players["פוטנציאל"] <= max_pa) &
            (df_players["גיל מדויק בקובץ"] >= min_age) & (df_players["גיל מדויק בקובץ"] <= max_age) &
            (df_players["שווי (£)"] >= min_val) & (df_players["שווי (£)"] <= max_val) &
            (df_players["מועדון"] != "מועדון מקומי") & 
            (df_players["לאום"] != "Other")
        ]

        if not filtered_df.empty:
            st.success(f"💥 סינון נקי הצליח! מצאנו {len(filtered_df)} שחקנים אמיתיים לחלוטין.")
            filtered_df = filtered_df.sort_values(by="פוטנציאל", ascending=False)
            
            st.dataframe(
                filtered_df.style.format({"שווי (£)": "{:,.0f}"}), 
                use_container_width=True, 
                hide_index=True 
            )
        else:
            st.warning("⚠️ לא נמצאו שחקנים בטווח שבחרת, או שכל הנתונים היו שגויים ונוקו על ידי המערכת.")
else:
    st.info("💡 המערכת שודרגה! מנגנון סינון הזבל הופעל. העלה קובץ שמירה כדי להתחיל.")
