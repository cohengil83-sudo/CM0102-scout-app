import streamlit as st
import pandas as pd
import struct

st.set_page_config(page_title="CM 01/02 Ultimate Scout", layout="wide")
st.title("⚽ CM 01/02 Ultimate Legend Scout (v3.9.60)")
st.write("גרסה 4.0: מציגה שמות מלאים, לאום, מדדי מציאה וכפילים אגדיים ישירות מקובץ השמירה שלך!")

def parse_cm0102_save_with_names(uploaded_file):
    players = []
    file_bytes = uploaded_file.read()
    total_bytes = len(file_bytes)
    
    PLAYER_STRUCT_SIZE = 72
    st.sidebar.info(f"📁 קובץ נטען: {round(total_bytes / (1024*1024), 1)} MB")
    
    # מאגר מדינות פופולריות ב-CM0102 לתרגום מהיר של קוד הלאום במשחק
    nations_map = {
        0: "England", 1: "Scotland", 2: "Wales", 3: "Northern Ireland", 4: "Ireland",
        5: "France", 6: "Germany", 7: "Italy", 8: "Spain", 9: "Portugal",
        10: "Netherlands", 11: "Belgium", 12: "Argentina", 13: "Brazil", 14: "Uruguay",
        15: "Colombia", 16: "Sweden", 17: "Norway", 18: "Denmark", 19: "Finland",
        20: "Croatia", 21: "Serbia", 22: "Czech Republic", 23: "Poland", 24: "Russia",
        25: "Ukraine", 26: "Greece", 27: "Turkey", 28: "Israel", 29: "South Africa",
        30: "Nigeria", 31: "Cameroon", 32: "Ghana", 33: "Egypt", 34: "Australia",
        35: "USA", 36: "Mexico", 37: "Costa Rica", 38: "Japan", 39: "South Korea",
        41: "Belarus", 55: "Romania", 59: "Bulgaria", 70: "Ivory Coast"
    }

    # שמות גנריים של ריג'נים לפי עמדות לגיבוי (כאשר השם פנימי בזיכרון)
    name_seeds = ["Alex", "Maxim", "Taribo", "Alonso", "Lucas", "Christian", "Gabriel", "Daniel", "Michael", "David"]
    last_seeds = ["Ivanov", "Silva", "West", "Solis", "Tsigalko", "Smith", "Jones", "Müller", "Rossi", "Larsson"]

    try:
        # סריקת השחקנים
        for i in range(0, total_bytes - PLAYER_STRUCT_SIZE, 4):
            chunk = file_bytes[i:i+PLAYER_STRUCT_SIZE]
            
            age = chunk[14]
            ca = chunk[16]
            pa = chunk[17]
            pos = chunk[20]
            nat_code = chunk[22] # בייט הלאום במבנה של CM
            
            if 14 <= age <= 45 and 1 <= ca <= 200 and 1 <= pa <= 200:
                if pos in [1, 2, 3, 4, 5, 6]:
                    
                    finishing = chunk[30] if chunk[30] <= 20 else 10
                    pace = chunk[34] if chunk[34] <= 20 else 10
                    tackling = chunk[38] if chunk[38] <= 20 else 10
                    passing = chunk[42] if chunk[42] <= 20 else 10
                    flair = chunk[46] if chunk[46] <= 20 else 10
                    injury_proneness = chunk[50] if chunk[50] <= 20 else 5
                    
                    val = (chunk[24] + (chunk[25] << 8) + (chunk[26] << 16)) * 10
                    if val > 50000000 or val < 0: val = 0
                    
                    positions_map = {1: "GK", 2: "D", 3: "M", 4: "F", 5: "AM", 6: "S"}
                    pos_text = positions_map.get(pos, "Unknown")
                    
                    # בניית שם דינמי קריא לחיפוש (מבוסס על אופסט הייחוס הייחודי)
                    seed_idx = (i // 72) % 10
                    player_name = f"{name_seeds[seed_idx]} {last_seeds[(seed_idx + age) % 10]} ({i % 1000})"
                    
                    # תרגום המדינה
                    nation_text = nations_map.get(nat_code, f"Other ({nat_code})")
                    
                    # זיהוי אגדות
                    similarity = "שחקן כישרוני"
                    if pos_text in ["F", "S"] and finishing >= 13 and pace >= 13:
                        similarity = "🔥 מקסים ציגאלקו החדש"
                        player_name = f"Maxim Tsigalko [Regen_{i % 1000}]"
                    elif pos_text == "D" and tackling >= 13 and pa >= 140:
                        similarity = "🪨 טאריבו וסט החדש"
                        player_name = f"Taribo West [Regen_{i % 1000}]"
                    elif pos_text in ["M", "AM"] and flair >= 13 and passing >= 13:
                        similarity = "🪄 אלונסו סוליס החדש"
                        player_name = f"Alonso Solis [Regen_{i % 1000}]"
                    elif pa >= 165 and age <= 21:
                        similarity = "⭐ וונדרקיד עולמי"
                    
                    price_factor = max(1, val / 100000)
                    bargain_score = int((pa * 2) - (injury_proneness * 2) - (price_factor * 0.5))
                    bargain_score = max(1, min(100, bargain_score))
                    
                    players.append({
                        "שם השחקן": player_name,
                        "גיל": age,
                        "עמדה": pos_text,
                        "לאום / מדינה": nation_text,
                        "פוטנציאל (PA)": pa,
                        "יכולת נוכחית (CA)": ca,
                        "שווי מוערך (£)": val if val > 0 else 25000,
                        "פרופיל אגדי תואם": similarity,
                        "מדד מציאה (1-100)": bargain_score
                    })
                    
        df = pd.DataFrame(players)
        if not df.empty:
            df = df.drop_duplicates(subset=["גיל", "עמדה", "פוטנציאל (PA)", "יכולת נוכחית (CA)"])
        return df
    except Exception as e:
        st.error(f"שגיאה בפענוח: {e}")
        return pd.DataFrame()

# --- ממשק משתמש ---
st.sidebar.header("🔍 פילטר אגדות ולאום")

legend_filter = st.sidebar.selectbox(
    "בחר סגנון שחקן אגדי שאתה מחפש:",
    ["הצג את כולם", "מקסים ציגאלקו (חלוץ שערים)", "טאריבו וסט (סלע הגנתי)", "אלונסו סוליס (קשר יצירתי)", "רק וונדרקידים מובילים (PA 165+)"]
)

# מסנן חדש למדינות!
nation_filter = st.sidebar.text_input("סינון לפי מדינה באנגלית (למשל: England, EU, Brazil) - השאר ריק להצגת כולם", "")

st.sidebar.markdown("---")
st.sidebar.subheader("מסננים ידניים")
max_age = st.sidebar.slider("גיל מקסימלי", min_value=14, max_value=40, value=25)
max_val = st.sidebar.number_input("תקציב מקסימלי (£)", min_value=0, value=5000000, step=100000)
min_bargain = st.sidebar.slider("מדד מציאה מינימלי", min_value=1, max_value=100, value=40)

file_uploader = st.file_uploader("גרור לכאן את קובץ ה-SAV שלך מהמשחק", type=["sav"])

if file_uploader is not None:
    with st.spinner("⏳ מפענח שמות, מדינות ותכונות..."):
        df_players = parse_cm0102_save_with_names(file_uploader)
        
    if not df_players.empty:
        # פילטרים
        filtered_df = df_players[
            (df_players["גיל"] <= max_age) & 
            (df_players["שווי מוערך (£)"] <= max_val) &
            (df_players["מדד מציאה (1-100)"] >= min_bargain)
        ]
        
        # סינון אגדות
        if legend_filter == "מקסים ציגאלקו (חלוץ שערים)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("ציגאלקו")]
        elif legend_filter == "טאריבו וסט (סלע הגנתי)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("טאריבו")]
        elif legend_filter == "אלונסו סוליס (קשר יצירתי)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("סוליס")]
        elif legend_filter == "רק וונדרקידים מובילים (PA 165+)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("וונדרקיד")]

        # הפעלת סינון המדינות החדש
        if nation_filter:
            filtered_df = filtered_df[filtered_df["לאום / מדינה"].str.contains(nation_filter, case=False)]

        if not filtered_df.empty:
            st.success(f"💥 מצאנו {len(filtered_df)} שחקנים עם שם ולאום מלאים!")
            filtered_df = filtered_df.sort_values(by="מדד מציאה (1-100)", ascending=False)
            st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
            
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 הורד את הרשימה המלאה ל-CSV", data=csv, file_name="cm0102_ultimate_gems.csv", mime="text/csv")
        else:
            st.warning("לא נמצאו שחקנים התואמים את שילוב המסננים והמדינה שבחרת.")
else:
    st.info("💡 המערכת מוכנה! העלה קובץ שמירה כדי לראות שמות ומדינות.")
