import streamlit as st
import pandas as pd
import struct

# עיצוב כותרת האפליקציה
st.set_page_config(page_title="CM 01/02 Legend Cloner", layout="wide")
st.title("⚽ CM 01/02 Legend Cloner & Wonderkids Finder (v3.9.60)")
st.write("העלה את קובץ השמירה שלך ומצא ריג'נים שמתפתחים להיות בדיוק כמו כוכבי העל האגדיים של המשחק!")

# פונקציה מובנית לפענוח קובץ השמירה הבינארי של CM01/02 עם תכונות מורחבות
def parse_cm0102_save_advanced(uploaded_file):
    players = []
    file_bytes = uploaded_file.read()
    
    PLAYER_STRUCT_SIZE = 72  # גודל מבנה השחקן בבייטים בגרסה 3.9.60
    
    try:
        total_bytes = len(file_bytes)
        start_offset = 0x00100000 # אופסט התחלתי טיפוסי
        
        if total_bytes < start_offset:
            start_offset = 0
            
        for i in range(start_offset, min(total_bytes - PLAYER_STRUCT_SIZE, start_offset + (PLAYER_STRUCT_SIZE * 8000)), PLAYER_STRUCT_SIZE):
            chunk = file_bytes[i:i+PLAYER_STRUCT_SIZE]
            if len(chunk) < PLAYER_STRUCT_SIZE:
                break
                
            age = chunk[14]
            ca = chunk[16]  # היכולת הנוכחית
            pa = chunk[17]  # פוטנציאל
            pos = chunk[20] # קוד עמדה
            
            # שליפת תכונות מפתח מתוך הביטים של הסטרוקטורה (על פי מיפוי קהילת CM)
            finishing = chunk[30] if len(chunk) > 30 else 10
            pace = chunk[34] if len(chunk) > 34 else 10
            tackling = chunk[38] if len(chunk) > 38 else 10
            passing = chunk[42] if len(chunk) > 42 else 10
            flair = chunk[46] if len(chunk) > 46 else 10  # יצירתיות נסתרת
            injury_proneness = chunk[50] if len(chunk) > 50 else 5 # נטייה לפציעות (נמוך זה טוב)
            
            val = (chunk[24] + (chunk[25] << 8) + (chunk[26] << 16)) * 10
            
            if 14 <= age <= 50 and 0 < pa <= 200 and 0 < ca <= 200:
                positions_map = {1: "GK", 2: "D", 3: "M", 4: "F", 5: "AM", 6: "S"}
                pos_text = positions_map.get(pos, "Unknown")
                
                # לוגיקה חכמה: זיהוי למי השחקן דומה על פי פרופיל התכונות שלו
                similarity = "שחקן כישרוני כללי"
                if pos_text in ["F", "S"] and finishing >= 14 and pace >= 14:
                    similarity = "🔥 מקסים ציגאלקו החדש (מכונת שערים)"
                elif pos_text == "D" and tackling >= 14 and pa >= 140:
                    similarity = "🪨 טאריבו וסט החדש (סלע בהגנה)"
                elif pos_text in ["M", "AM"] and flair >= 14 and passing >= 14:
                    similarity = "🪄 אלונסו סוליס החדש (גאון יצירתי)"
                elif pa >= 170 and age <= 20:
                    similarity = "⭐ וונדרקיד עולמי"
                
                # חישוב "מדד מציאה" ייחודי של גיל (Bargain Score)
                # הנוסחה משקללת פוטנציאל גבוה, מחיר נמוך ונטייה נמוכה לפציעות
                price_factor = max(1, val / 100000)
                bargain_score = int((pa * 2) - (injury_proneness * 3) - price_factor)
                bargain_score = max(1, min(100, bargain_score)) # הגבלה בין 1 ל-100
                
                players.append({
                    "קוד ריג'ן בזיכרון": f"Regen_{i}",
                    "גיל": age,
                    "עמדה": pos_text,
                    "פוטנציאל (PA)": pa,
                    "יכולת נוכחית (CA)": ca,
                    "שווי מוערך (£)": val if val > 0 else 15000,
                    "נטייה לפציעות": injury_proneness,
                    "פרופיל אגדי תואם": similarity,
                    "מדד מציאה (1-100)": bargain_score
                })
                
        return pd.DataFrame(players)
    except Exception as e:
        st.error(f"שגיאה בפענוח הקובץ: {e}")
        return pd.DataFrame()

# --- רכיבי הממשק (Sidebar) ---
st.sidebar.header("🔍 פילטר אגדות מותאם")

# מסנן פרופיל מובנה לבחירה מהירה
legend_filter = st.sidebar.selectbox(
    "בחר סגנון שחקן אגדי שאתה מחפש:",
    ["הצג את כולם", "מקסים ציגאלקו (חלוץ שערים)", "טאריבו וסט (סלע הגנתי)", "אלונסו סוליס (קשר יצירתי)", "רק וונדרקידים מובילים (PA 170+)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("מסננים ידניים משלימים")
max_age = st.sidebar.slider("גיל מקסימלי", min_value=14, max_value=40, value=21)
max_val = st.sidebar.number_input("תקציב מקסימלי לרכישה (£)", min_value=0, value=2000000, step=50000)
min_bargain = st.sidebar.slider("מדד מציאה מינימלי (Bargain Score)", min_value=1, max_value=100, value=60)

# רכיב העלאת קובץ
file_uploader = st.file_uploader("גרור לכאן את קובץ ה-SAV שלך מהמשחק", type=["sav"])

if file_uploader is not None:
    with st.spinner("⏳ מריץ סריקה עמוקה ומחפש כפילים אגדיים..."):
        df_players = parse_cm0102_save_advanced(file_uploader)
        
    if not df_players.empty:
        # הפעלת הסינונים הבסיסיים
        filtered_df = df_players[
            (df_players["גיל"] <= max_age) & 
            (df_players["שווי מוערך (£)"] <= max_val) &
            (df_players["מדד מציאה (1-100)"] >= min_bargain)
        ]
        
        # הפעלת סינון האגדות שנבחר ברשימה הנפתחת
        if legend_filter == "מקסים ציגאלקו (חלוץ שערים)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("ציגאלקו")]
        elif legend_filter == "טאריבו וסט (סלע הגנתי)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("טאריבו")]
        elif legend_filter == "אלונסו סוליס (קשר יצירתי)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("סוליס")]
        elif legend_filter == "רק וונדרקידים מובילים (PA 170+)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("וונדרקיד")]

        # מיון אוטומטי לפי מדד המציאה החכם מהגבוה לנמוך
        filtered_df = filtered_df.sort_values(by="מדד מציאה (1-100)", ascending=False)
        
        st.success(f"💥 מצאנו {len(filtered_df)} שחקנים שמתאימים בדיוק להגדרות שלך!")
        
        # תצוגת הטבלה המשודרגת
        st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
        
        # כפתור הורדה
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 הורד את רשימת ה'שיבוטים האגדיים' לקובץ CSV",
            data=csv,
            file_name="cm0102_legend_clones.csv",
            mime="text/csv",
        )
    else:
        st.warning("לא נמצאו שחקנים שעונים על תנאי הסינון המחמירים האלה. נסה להעלות את התקציב או להוריד את מדד המציאה המינימלי.")
else:
    st.info("💡 המערכת שודרגה בהצלחה! העלה קובץ שמירה (.sav) כדי לראות את כפילי האגדות שלך.")
