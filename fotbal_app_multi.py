import streamlit as st
import json
from stripe_checkout import paywall_ui

st.set_page_config(page_title="⚽ Fotbalové predikce", page_icon="⚽", layout="wide")

# Načteme data týmů
with open("teams.json", "r", encoding="utf-8") as f:
    TEAMS = json.load(f)

def protected_content():
    st.success("✅ Máte aktivní předplatné – plný přístup k predikcím!")

    league = st.selectbox("Vyber ligu:", list(TEAMS.keys()))
    teams = list(TEAMS[league].keys())

    col1, col2 = st.columns(2)
    with col1:
        home = st.selectbox("Domácí tým", teams)
    with col2:
        away = st.selectbox("Hostující tým", [t for t in teams if t != home])

    if st.button("Spustit predikci"):
        home_data = TEAMS[league][home]
        away_data = TEAMS[league][away]
        # jednoduchý model
        home_score = home_data["avg_goals_for"] * home_data["home_strength"]
        away_score = away_data["avg_goals_for"] * away_data["away_strength"]

        if home_score > away_score:
            pred = f"🏠 Výhra domácích ({home})"
        elif away_score > home_score:
            pred = f"✈️ Výhra hostů ({away})"
        else:
            pred = "🤝 Remíza"

        st.metric("Predikce", pred)
        st.write(f"Odhad gólů: {home_score:.1f} – {away_score:.1f}")

# Paywall – voláme hlavní obsah jen při aktivním předplatném
paywall_ui(protected_content)
