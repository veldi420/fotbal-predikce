# fotbal_app_multi.py
# -------------------------------------------
# Moderní Streamlit UI pro fotbalové predikce
# Čte týmy z teams.json (formát: {"Premier League": ["Arsenal", ...], ...})
# Predikci dělá jednoduchá deterministická funkce (bez externích modelů),
# aby appka běžela i bez dalších závislostí.
# -------------------------------------------

import json
import math
import streamlit as st

# ============== PAGE SETUP & STYLY ==============
st.set_page_config(
    page_title="⚽ Fotbalové predikce",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Moderní (tmavý) vzhled
st.markdown("""
<style>
:root{
  --bg:#0f172a;          /* tmavé pozadí */
  --panel:#111827;       /* panely/karty */
  --muted:#94a3b8;       /* sekundární text */
  --primary:#22c55e;     /* zelená akční */
  --radius:18px;
}
html, body, [data-testid="stApp"]{
  background: radial-gradient(1200px 600px at 10% 0%, #0b1225 0%, var(--bg) 45%, #0b1225 100%) !important;
}
.block-container{padding-top:24px; padding-bottom:48px; max-width:1000px;}

h1,h2,h3{letter-spacing:.2px}
.big-title{
  font-size:clamp(26px, 4.2vw, 42px);
  font-weight:800; line-height:1.1;
  margin: 0 0 14px 0;
  background: linear-gradient(90deg,#e5e7eb, #9ae6b4);
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.sub{
  color:var(--muted); font-size:14px; margin-bottom:28px;
}
.card{
  background: linear-gradient(145deg, #0c142a, var(--panel));
  border:1px solid rgba(255,255,255,.06);
  border-radius:var(--radius);
  padding:18px 18px 14px; box-shadow: 0 10px 30px rgba(0,0,0,.35);
}
.select-label{font-weight:600; color:#e5e7eb; margin-bottom:6px;}
.run > button{
  width:100%; height:46px; font-weight:700; letter-spacing:.3px;
  background:linear-gradient(135deg, #16a34a, var(--primary)); color:white; border-radius:12px;
  border:1px solid rgba(255,255,255,.12);
}
.run > button:hover{filter:brightness(1.05)}
.badge{
  display:inline-flex; align-items:center; gap:8px;
  background:rgba(34,197,94,.12); color:#86efac; border:1px solid rgba(134,239,172,.25);
  padding:8px 12px; border-radius:999px; font-weight:700;
}
.metric{
  display:flex; gap:10px; align-items:center; color:#e2e8f0; font-size:22px; font-weight:700;
}
.metric small{color:var(--muted); font-weight:500; font-size:14px}
.footer{
  opacity:.75; color:var(--muted); font-size:12px; margin-top:26px; text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">⚽ Fotbalové predikce</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Vyber ligu a týmy. Na mobilu i desktopu. (Demo výpočet bez API)</div>', unsafe_allow_html=True)

# ============== DATA: TEAMS ==============
# Očekává soubor teams.json v rootu repozitáře:
# {
#   "Premier League": ["Arsenal","Manchester City",...],
#   "La Liga": ["Barcelona","Real Madrid",...],
#   ...
# }
@st.cache_data(show_spinner=False)
def load_teams():
    with open("teams.json", "r", encoding="utf-8") as f:
        return json.load(f)  # dict: liga -> list[str]

TEAMS_BY_LEAGUE = load_teams()
LEAGUES = list(TEAMS_BY_LEAGUE.keys())

def dedup(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            out.append(x); seen.add(x)
    return out

# ============== POMOCNÉ FUNKCE ==============

def deterministic_score(team_name: str, opponent_name: str) -> float:
    """
    Jednoduchý deterministický 'rating' z názvu týmu + soupeře
    => stabilní na každém běhu (nepoužívá random).
    Vrací číslo ~0.6 až ~3.4
    """
    def s(v: str) -> int:
        # stabilní hash bez saltů (součet kódů znaků)
        return sum(ord(c) for c in v.lower() if c.isalnum())
    base = 0.6 + ((s(team_name) * 1.7 + s(opponent_name) * 0.9) % 260) / 100.0
    # zkompresuj do rozumného intervalu
    return 0.6 + (base % 2.8)

def predict(home: str, away: str):
    """
    Vypočte odhad gólů a slovní tip (jen demo logika).
    """
    gh = deterministic_score(home, away)
    ga = deterministic_score(away, home) * 0.75

    # jemné zvýhodnění domácích
    gh += 0.25

    # zaokrouhlení na 1 desetinné místo
    gh = max(0.3, round(gh, 1))
    ga = max(0.3, round(ga, 1))

    if gh - ga > 0.35:
        tip = "Výhra domácích"
    elif ga - gh > 0.35:
        tip = "Výhra hostů"
    else:
        tip = "Remíza"
    return tip, gh, ga

# ============== UI ==============

# Sidebar (volitelně)
with st.sidebar:
    st.write("⚙️ **Nastavení**")
    st.caption("Výběr ligy ovlivní nabídku týmů.")

# Výběr ligy
st.markdown('<div class="card">', unsafe_allow_html=True)
col_l, col_r = st.columns([1,1])
with col_l:
    st.markdown('<div class="select-label">Liga</div>', unsafe_allow_html=True)
    league = st.selectbox("", LEAGUES, key="league")

# Seznam týmů pro danou ligu
teams = TEAMS_BY_LEAGUE.get(league, [])
teams = dedup(teams)

# Parametry z URL (moderní API)
qp = st.query_params
home_default = teams[0] if teams else ""
away_default = teams[1] if len(teams) > 1 else (teams[0] if teams else "")

if "home" in qp and qp["home"] in teams:
    home_default = qp["home"]
if "away" in qp and qp["away"] in teams:
    away_default = qp["away"]

# Výběr týmů
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="select-label">Domácí tým</div>', unsafe_allow_html=True)
    home_team = st.selectbox("", teams, index=teams.index(home_default) if home_default in teams else 0, key="home_team")
with c2:
    st.markdown('<div class="select-label">Hostující tým</div>', unsafe_allow_html=True)
    away_team = st.selectbox("", teams, index=teams.index(away_default) if away_default in teams else (1 if len(teams)>1 else 0), key="away_team")

# Ulož volby do URL
qp["home"] = home_team
qp["away"] = away_team

st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)
run = st.container()
with run:
    clicked = st.button("Spustit predikci", key="run", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)  # /card

# Výsledek
if clicked and home_team and away_team and home_team != away_team:
    tip, gh, ga = predict(home_team, away_team)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="badge">📊 Predikce: {tip}</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.markdown(f'<div class="metric">🏠 {home_team} <small>odhad gólů</small></div>', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin-top:4px; color:#e2e8f0'>{gh:.1f}</h3>", unsafe_allow_html=True)
    with r2:
        st.markdown(f'<div class="metric">🛫 {away_team} <small>odhad gólů</small></div>', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin-top:4px; color:#e2e8f0'>{ga:.1f}</h3>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # /card

elif clicked and home_team == away_team:
    st.warning("Vyber prosím **dva různé týmy**.")

# Patička
st.markdown('<div class="footer">© 2025 Fotbalové predikce – demo verze UI</div>', unsafe_allow_html=True)
