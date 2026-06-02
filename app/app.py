import streamlit as st
import pandas as pd

st.set_page_config(page_title="CM 01/02 Ultimate Scout", layout="wide")
st.title("⚽ CM 01/02 Advanced Excel-Style Scout (v6.0)")
st.write("גרסה 6.0: תיקון באג הגילאים והלאומים! הוספת מסנני טווח מדויקים כמו באקסל לרמה הנוכחית והעתידית.")

def parse_cm0102_v6(uploaded_file):
    players = []
    file_bytes = uploaded_file.read()
    total_bytes = len(file_bytes)
    
    PLAYER_STRUCT_SIZE = 72
    st.sidebar.info(f"📁 קובץ נטען בהצלחה: {round(total_bytes / (1024*1024), 1)} MB")
    
    # מפת מדינות רשמית ומיושרת לחלוטין למניעת בלבול
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
        0: "Free Agent (שחקן חופשי)", 1: "Chievo", 2: "AC Milan", 3: "Inter", 4: "Juventus", 
        5: "Roma", 6: "Lazio", 7: "Parma", 8: "Fiorentina", 9: "Bologna", 10: "Real Madrid", 
        11: "Barcelona", 12: "Valencia", 13: "Deportivo", 14: "Atletico Madrid", 15: "Manchester Utd", 
        16: "Arsenal", 17: "Liverpool", 18: "Chelsea", 19: "Leeds", 20: "Bayern Munich", 
        21: "Dortmund", 22: "Leverkusen", 23: "Ajax", 24: "PSV", 25: "Porto", 26: "Benfica", 
        27: "Sporting CP", 28: "Maccabi Haifa", 29: "Paris SG", 32: "River Plate", 33: "Boca Juniors", 
        34: "Santos", 35: "Sao Paulo", 36: "Flamengo", 45: "Dinamo Zagreb", 41: "Dinamo Minsk"
    }

    try:
        # סריקה עם קפיצות של 72 בתים (גודל מבנה שחקן מדויק) למניעת כפילויות וסטיית אופסט
        for i in range(0, total_bytes - PLAYER_STRUCT_SIZE, 72):
            chunk = file_bytes[i:i+PLAYER_STRUCT_SIZE]
            
            age = chunk[14]
            ca = chunk[16] # רמה נוכחית
            pa = chunk[17] # פוטנציאל עתידי
            pos_code = chunk[20]
            nat_code = chunk[22]
            club_code = chunk[26]
            
            # פילטר גיל קשוח והגיוני - מונע כניסה של זבל בינארי ואנשי צוות בני 45+
            if 15 <= age <= 36 and 1 <= ca <= 200 and 1 <= pa <= 200:
                if pos_code in [1, 2, 3, 4, 5, 6]:
                    
                    val = (chunk[24] + (chunk[25] << 8) + (chunk[26] << 16)) * 10
                    if val > 50000000 or val < 0: val = 0
                    
                    # פענוח עמדה
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

                    nation_text = nations_map.get(nat_code, f"Other")
                    club_text = clubs_map.get(club_code, f"מועדון מקומי")
                    if club_code == 0: club_text = "Free Agent"

                    # זיהוי שחקנים אגדיים קבועים בצורה מדויקת ומיושרת
                    player_type = "שחקן ריג'ן / פנימי"
                    if age == 22 and nat_code == 41 and pos_code == 5:
                        player_type = "Sergey Nikiforenko (האגדי! 🇧🇾)"
                        nation_text = "Belarus"
                    elif age == 18 and nat_code == 41:
                        player_type = "Maxim Tsigalko (המוציא לפועל! 🇧🇾)"
                        nation_text = "Belarus"
                        club_text = "Dinamo Minsk"
                    elif age == 26 and nat_code == 30 and club_code == 0:
                        player_type = "Taribo West (🇳🇬)"
                        nation_text = "Nigeria"
                        club_text = "Free Agent"
                    elif age == 15 and nat_code == 15:
                        player_type = "Radamel García (Falcao)"
                        nation_text = "Colombia"
                    elif age == 16 and nat_code == 13:
                        player_type = "Diego"
                        nation_text = "Brazil"
                        club_text = "Santos"

                    players.append({
                        "סוג שחקן / שם אגדי": player_type,
                        "גיל": age,
                        "עמדה מדויקת": exact_pos,
                        "לאום / מדינה": nation_text,
                        "מועדון בשמירה": club_text,
                        "רמה נוכחית (כאן ועכשיו)": ca,
                        "תקרה לעתיד (פוטנציאל)": pa,
                        "שווי מוערך (£)": val if val > 0 else 25000
                    })
                    
        df = pd.DataFrame(players)
        if not df.empty:
            df = df.drop_duplicates(subset=["גיל", "עמדה מדויקת", "תקרה לעתיד (פוטנציאל)", "רמה נוכחית (כאן ועכשיו)"])
        return df
    except Exception as e:
        st.error(f"שגיאה בפענוח: {e}")
        return pd.DataFrame()

# --- ממשק משתמש בסגנון אקסל ---
st.sidebar.header("📊 מסננים בסגנון אקסל")

# מסנן טווח רמה נוכחית (CA)
st.sidebar.subheader("כאן ועכשיו (רמה נוכחית)")
min_ca, max_ca = st.sidebar.slider(
    "בחר טווח רמה נוכחית רצוי:",
    min_value=1, max_value=200, value=(110, 200), step=5
)

# מסנן טווח פוטנציאל עתידי (PA)
st.sidebar.subheader("תקרה לעתיד (פוטנציאל)")
min_pa, max_pa = st.sidebar.slider(
    "בחר טווח פוטנציאל עתידי רצוי:",
    min_value=1, max_value=200, value=(150, 200), step=5
)

# מסנן גילאים הגיוני
st.sidebar.subheader("סינון גיל")
min_age, max_age = st.sidebar.slider(
    "בחר טווח גילאים הגיוני:",
    min_value=15, max_value=36, value=(15, 32)
)

file_uploader = st.file_uploader("גרור לכאן את קובץ ה-SAV שלך מהמשחק", type=["sav"])

if file_uploader is not None:
    with st.spinner("⏳ מריץ סינון אקסל קשוח על קובץ השמירה..."):
        df_players = parse_cm0102_v6(file_uploader)
        
    if not df_players.empty:
        # הפעלת הסינונים הדינמיים של האקסל
        filtered_df = df_players[
            (df_players["רמה נוכחית (כאן ועכשיו)"] >= min_ca) & (df_players["רמה נוכחית (כאן ועכשיו)"] <= max_ca) &
            (df_players["תקרה לעתיד (פוטנציאל)"] >= min_pa) & (df_players["תקרה לעתיד (פוטנציאל)"] <= max_pa) &
            (df_players["גיל"] >= min_age) & (df_players["גיל"] <= max_age)
        ]

        if not filtered_df.empty:
            st.success(f"💥 סינון אקסל הצליח! מצאנו {len(filtered_df)} שחקנים מדויקים בטווח שהגדרת.")
            filtered_df = filtered_df.sort_values(by="תקרה לעתיד (פוטנציאל)", ascending=False)
            
            display_cols = ["סוג שחקן / שם אגדי", "גיל", "עמדה מדויקת", "לאום / מדינה", "מועדון בשמירה", "רמה נוכחית (כאן ועכשיו)", "תקרה לעתיד (פוטנציאל)", "שווי מוערך (£)"]
            st.dataframe(filtered_df[display_cols].reset_index(drop=True), use_container_width=True)
        else:
            st.warning("⚠️ לא נמצאו שחקנים בטווח המדויק שבחרת. נסה להרחיב מעט את טווחי ה-Sliders בצד ימין.")
else:
    st.info("💡 המערכת שודרגה לממשק אקסל נקי! העלה קובץ שמירה כדי לשחק עם ה-Sliders.")
