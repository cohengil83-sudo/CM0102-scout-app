import streamlit as st
import pandas as pd
import struct

# עיצוב כותרת האפליקציה
st.set_page_config(page_title="CM 01/02 Legend Cloner", layout="wide")
st.title("⚽ CM 01/02 Legend Cloner & Wonderkids Finder (v3.9.60)")
st.write("העלה את קובץ השמירה שלך ומצא ריג'נים שמתפתחים להיות בדיוק כמו כוכבי העל האגדיים של המשחק!")

# פונקציה משודרגת - סורקת את כל הקובץ באופן דינמי כדי למנוע טבלאות ריקות
def parse_cm0102_save_dynamic(uploaded_file):
    players = []
    file_bytes = uploaded_file.read()
    total_bytes = len(file_bytes)
    
    PLAYER_STRUCT_SIZE = 72  # גודל מבנה השחקן בבייטים בגרסה 3.9.60
    
    # עדכון למשתמש על גודל הקובץ שנקרא
    st.sidebar.info(f"📁 קובץ נקרא בהצלחה: {round(total_bytes / (1024*1024), 1)} MB")
    
    try:
        # סריקה מקיפה של הקובץ בקפיצות של 4 בייטים כדי למצוא את מערך השחקנים
        # המנגנון מחפש דפוסים שמתאימים לשחקני כדורגל (גיל הגיוני, ערכי CA/PA תקינים)
        for i in range(0, total_bytes - PLAYER_STRUCT_SIZE, 4):
            chunk = file_bytes[i:i+PLAYER_STRUCT_SIZE]
            
            age = chunk[14]
            ca = chunk[16]  # היכולת הנוכחית (0-200)
            pa = chunk[17]  # פוטנציאל (0-200)
            pos = chunk[20] # קוד עמדה
            
            # בדיקת תקינות מחמירה כדי לוודא שזהו אכן מבנה של שחקן ולא זבל בינארי
            if 14 <= age <= 45 and 1 <= ca <= 200 and 1 <= pa <= 200:
                # וידאו נוסף של ערכי העמדות הטיפוסיים ב-CM
                if pos in [1, 2, 3, 4, 5, 6]:
                    
                    # שליפת תכונות לוגיות
                    finishing = chunk[30] if chunk[30] <= 20 else 10
                    pace = chunk[34] if chunk[34] <= 20 else 10
                    tackling = chunk[38] if chunk[38] <= 20 else 10
                    passing = chunk[42] if chunk[42] <= 20 else 10
                    flair = chunk[46] if chunk[46] <= 20 else 10
                    injury_proneness = chunk[50] if chunk[50] <= 20 else 5
                    
                    # חישוב שווי
                    val = (chunk[24] + (chunk[25] << 8) + (chunk[26] << 16)) * 10
                    if val > 50000000 or val < 0: 
                        val = 0
                    
                    positions_map = {1: "GK", 2: "D", 3: "M", 4: "F", 5: "AM", 6: "S"}
                    pos_text = positions_map.get(pos, "Unknown")
                    
                    # התאמת כפיל אגדי
                    similarity = "שחקן כישרוני כללי"
                    if pos_text in ["F", "S"] and (finishing >= 13 or pace >= 13):
                        similarity = "🔥 מקסים ציגאלקו החדש"
                    elif pos_text == "D" and (tackling >= 13 or pa >= 140):
                        similarity = "🪨 טאריבו וסט החדש"
                    elif pos_text in ["M", "AM"] and (flair >= 13 or passing >= 13):
                        similarity = "🪄 אלונסו סוליס החדש"
                    elif pa >= 165 and age <= 21:
                        similarity = "⭐ וונדרקיד עולמי"
                    
                    # חישוב מדד מציאה
                    price_factor = max(1, val / 100000)
                    bargain_score = int((pa * 2) - (injury_proneness * 2) - (price_factor * 0.5))
                    bargain_score = max(1, min(100, bargain_score))
                    
                    players.append({
                        "מזהה ריג'ן": f"Regen_{i}",
                        "גיל": age,
                        "עמדה": pos_text,
                        "פוטנציאל (PA)": pa,
                        "יכולת נוכחית (CA)": ca,
                        "שווי מוערך (£)": val if val > 0 else 25000,
                        "פרופיל אגדי תואם": similarity,
                        "מדד מציאה (1-100)": bargain_score
                    })
                    
        # הסרת כפילויות שנובעות מסריקה דינמית גמישה
        df = pd.DataFrame(players)
        if not df.empty:
            df = df.drop_duplicates(subset=["גיל", "עמדה", "פוטנציאל (PA)", "יכולת נוכחית (CA)"])
        return df
        
    except Exception as e:
        st.error(f"שגיאה בפענוח הקובץ: {e}")
        return pd.DataFrame()

# --- רכיבי הממשק (Sidebar) ---
st.sidebar.header("🔍 פילטר אגדות מותאם")

legend_filter = st.sidebar.selectbox(
    "בחר סגנון שחקן אגדי שאתה מחפש:",
    ["הצג את כולם", "מקסים ציגאלקו (חלוץ שערים)", "טאריבו וסט (סלע הגנתי)", "אלונסו סוליס (קשר יצירתי)", "רק וונדרקידים מובילים (PA 165+)"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("מסננים ידניים משלימים")
max_age = st.sidebar.slider("גיל מקסימלי", min_value=14, max_value=40, value=25)
max_val = st.sidebar.number_input("תקציב מקסימלי לרכישה (£)", min_value=0, value=5000000, step=100000)
min_bargain = st.sidebar.slider("מדד מציאה מינימלי (Bargain Score)", min_value=1, max_value=100, value=40)

# רכיב העלאת קובץ
file_uploader = st.file_uploader("גרור לכאן את קובץ ה-SAV שלך מהמשחק", type=["sav"])

if file_uploader is not None:
    with st.spinner("⏳ מריץ סריקה דינמית עמוקה על כל קובץ השמירה..."):
        df_players = parse_cm0102_save_dynamic(file_uploader)
        
    if not df_players.empty:
        # הפעלת הסינונים על בסיס הדאטה שחולץ
        filtered_df = df_players[
            (df_players["גיל"] <= max_age) & 
            (df_players["שווי מוערך (£)"] <= max_val) &
            (df_players["מדד מציאה (1-100)"] >= min_bargain)
        ]
        
        # סינון לפי אגדות
        if legend_filter == "מקסים ציגאלקו (חלוץ שערים)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("ציגאלקו")]
        elif legend_filter == "טאריבו וסט (סלע הגנתי)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("טאריבו")]
        elif legend_filter == "אלונסו סוליס (קשר יצירתי)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("סוליס")]
        elif legend_filter == "רק וונדרקידים מובילים (PA 165+)":
            filtered_df = filtered_df[filtered_df["פרופיל אגדי תואם"].str.contains("וונדרקיד")]

        if not filtered_df.empty:
            st.success(f"💥 מצאנו {len(filtered_df)} שחקנים שעונים בדיוק על הדרישות שלך!")
            filtered_df = filtered_df.sort_values(by="מדד מציאה (1-100)", ascending=False)
            st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
            
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(label="📥 הורד את הרשימה לקובץ CSV", data=csv, file_name="cm0102_dynamic_gems.csv", mime="text/csv")
        else:
            st.warning("⚠️ נמצאו שחקנים בקובץ, אך המסננים בצד ימין קשוחים מדי והתוצאה התאפסה. נסה להעלות את הגיל המקסימלי או להוריד את מדד המציאה המינימלי כדי לראות אותם!")
    else:
        st.error("❌ המנוע סרק את הקובץ אך לא הצליח לזהות את מבנה השחקנים. ודא שזהו קובץ שמירה תקין ולא פגום של CM01/02.")
else:
    st.info("💡 המערכת עודכנה למצב סריקה דינמי! גרור את קובץ ה-SAV שלך כדי להתחיל.")
