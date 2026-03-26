"""
HardRock Bet Tool — Multi-API Hybrid Dashboard
Streamlit Cloud ready. Paste into app.py and deploy.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import math

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="HardRock Bet Tool",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — Dark / Mobile-First / Galaxy Optimized
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #0a0c10 !important;
    color: #e2e8f0 !important;
}
.hrb-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-bottom: 2px solid #f59e0b;
    padding: 1rem 1.5rem;
    display: flex; align-items: center; gap: 1rem;
    margin-bottom: 1rem;
    border-radius: 0 0 12px 12px;
}
.hrb-header h1 { font-size:1.8rem; font-weight:700; color:#f59e0b; margin:0; letter-spacing:2px; text-transform:uppercase; }
.hrb-header span { font-size:0.8rem; color:#94a3b8; font-family:'Share Tech Mono',monospace; }
.badge-green { background:#065f46; color:#6ee7b7; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:700; }
.badge-gold  { background:#78350f; color:#fcd34d; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:700; }
.badge-red   { background:#7f1d1d; color:#fca5a5; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:700; }
.badge-gray  { background:#1f2937; color:#94a3b8; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:700; }
.edge-alert   { background:linear-gradient(90deg,#78350f,#92400e); border-left:4px solid #f59e0b; border-radius:8px; padding:.75rem 1rem; margin:.5rem 0; font-weight:600; color:#fcd34d; font-size:.9rem; }
.sticky-table-wrapper { overflow-x:auto; -webkit-overflow-scrolling:touch; border-radius:10px; border:1px solid #1f2937; }
.sticky-table-wrapper table { border-collapse:collapse; width:100%; font-size:.85rem; }
.sticky-table-wrapper th { background:#1e293b; color:#94a3b8; text-transform:uppercase; letter-spacing:.5px; padding:10px 14px; white-space:nowrap; position:sticky; top:0; z-index:2; }
.sticky-table-wrapper td { padding:10px 14px; border-bottom:1px solid #1f2937; white-space:nowrap; color:#e2e8f0; }
.sticky-table-wrapper tr:hover td { background:#1e293b; }
.sticky-table-wrapper th:first-child,
.sticky-table-wrapper td:first-child { position:sticky; left:0; background:#111827; z-index:3; font-weight:600; border-right:2px solid #374151; min-width:130px; }
.sticky-table-wrapper th:first-child { background:#1e293b; z-index:4; }
[data-testid="stSidebar"] { background:#0d1117 !important; border-right:1px solid #1f2937; }
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color:#f59e0b !important; font-family:'Rajdhani',sans-serif; font-weight:700; letter-spacing:1px; }
div[data-testid="stSidebar"] .stButton button { background:#f59e0b; color:#0a0c10; font-weight:700; border-radius:8px; width:100%; font-family:'Rajdhani',sans-serif; font-size:1rem; letter-spacing:1px; }
.stSelectbox>div>div,.stMultiSelect>div>div { background:#111827 !important; border:1px solid #374151 !important; border-radius:8px !important; color:#e2e8f0 !important; }
div[data-testid="stMetric"] { background:#111827; border-radius:10px; padding:.75rem; border:1px solid #1f2937; }
div[data-testid="stMetricValue"] { color:#f59e0b !important; font-family:'Share Tech Mono',monospace; }
hr { border-color:#1f2937 !important; }
.stTabs [data-baseweb="tab"] { color:#64748b; font-family:'Rajdhani',sans-serif; font-weight:600; font-size:1rem; }
.stTabs [aria-selected="true"] { color:#f59e0b !important; border-bottom:2px solid #f59e0b !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SECRETS
# ──────────────────────────────────────────────
def _secret(key: str, default: str = "") -> str:
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return default

TSDB_KEY     = _secret("THE_SPORTSDB_API_KEY")
ODDS_KEY     = _secret("THE_ODDS_API_KEY")
APIS_KEY     = _secret("API_SPORTS_API_KEY")
BDL_KEY      = _secret("BALLDONTLIE_API_KEY")
ODDS_REGIONS = _secret("REGIONS", "us,us2")

with st.expander("🔑 API Key Status", expanded=False):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("TheSportsDB", "✅ Set" if TSDB_KEY else "❌ Missing")
    c2.metric("The Odds API", "✅ Set" if ODDS_KEY else "❌ Missing")
    c3.metric("API-Sports",  "✅ Set" if APIS_KEY else "❌ Missing")
    c4.metric("Balldontlie", "✅ Set" if BDL_KEY  else "❌ Missing")
    if c5.button("🗑️ Clear Cache", help="Force-clears all cached API responses"):
        st.cache_data.clear()
        st.rerun()

# ──────────────────────────────────────────────
# FULL SPORT CONFIG
# ──────────────────────────────────────────────
SPORT_CONFIG = {
    "NBA": {
        "odds_key": "basketball_nba",
        "apisports_base": "basketball", "apisports_league": "12",
        "stat_fields": {"Points":"intPoints","Rebounds":"intRebounds","Assists":"intAssists","3PM":"intThrees","Steals":"intSteals","Blocks":"intBlocks"},
        "default_lines": {"intPoints":20.5,"intRebounds":5.5,"intAssists":4.5,"intThrees":2.5,"intSteals":1.5,"intBlocks":1.5},
        "blowout_rule": ("spread", 12),
    },
    "NFL": {
        "odds_key": "americanfootball_nfl",
        "apisports_base": "american-football", "apisports_league": "1",
        "stat_fields": {"Pass Yds":"intPassingYards","Rush Yds":"intRushingYards","Rec Yds":"intReceivingYards","TDs":"intTouchdowns","Receptions":"intReceptions","INTs":"intInterceptions"},
        "default_lines": {"intPassingYards":250.5,"intRushingYards":65.5,"intReceivingYards":55.5,"intTouchdowns":1.5,"intReceptions":5.5,"intInterceptions":0.5},
        "blowout_rule": ("spread", 14),
    },
    "MLB": {
        "odds_key": "baseball_mlb",
        "apisports_base": "baseball", "apisports_league": "1",
        "stat_fields": {"Hits":"intHits","Strikeouts":"intStrikeouts","RBIs":"intRBI","HR":"intHomeRuns","Walks":"intWalks","Runs":"intRuns"},
        "default_lines": {"intHits":1.5,"intStrikeouts":6.5,"intRBI":1.5,"intHomeRuns":0.5,"intWalks":0.5,"intRuns":0.5},
        "blowout_rule": ("ml", -250),
    },
    "NHL": {
        "odds_key": "icehockey_nhl",
        "apisports_base": "hockey", "apisports_league": "57",
        "stat_fields": {"Goals":"intGoals","Shots":"intShots","Points":"intPoints","Assists":"intAssists","Saves":"intSaves","PIM":"intPenaltyMinutes"},
        "default_lines": {"intGoals":0.5,"intShots":3.5,"intPoints":1.5,"intAssists":0.5,"intSaves":25.5,"intPenaltyMinutes":0.5},
        "blowout_rule": ("ml", -250),
    },
    "NCAAF": {
        "odds_key": "americanfootball_ncaaf",
        "apisports_base": "american-football", "apisports_league": "2",
        "stat_fields": {"Pass Yds":"intPassingYards","Rush Yds":"intRushingYards","TDs":"intTouchdowns","Rec Yds":"intReceivingYards"},
        "default_lines": {"intPassingYards":220.5,"intRushingYards":75.5,"intTouchdowns":1.5,"intReceivingYards":50.5},
        "blowout_rule": ("spread", 17),
    },
    "NCAAB": {
        "odds_key": "basketball_ncaab",
        "apisports_base": "basketball", "apisports_league": "116",
        "stat_fields": {"Points":"intPoints","Rebounds":"intRebounds","Assists":"intAssists","3PM":"intThrees"},
        "default_lines": {"intPoints":15.5,"intRebounds":5.5,"intAssists":3.5,"intThrees":2.5},
        "blowout_rule": ("spread", 15),
    },
    "NCAAW Basketball": {
        "odds_key": "basketball_ncaaw",
        "apisports_base": "basketball", "apisports_league": "117",
        "stat_fields": {"Points":"intPoints","Rebounds":"intRebounds","Assists":"intAssists"},
        "default_lines": {"intPoints":15.5,"intRebounds":6.5,"intAssists":3.5},
        "blowout_rule": ("spread", 15),
    },
    "CFL": {
        "odds_key": "americanfootball_cfl",
        "apisports_base": "american-football", "apisports_league": "3",
        "stat_fields": {"Pass Yds":"intPassingYards","Rush Yds":"intRushingYards","TDs":"intTouchdowns"},
        "default_lines": {"intPassingYards":250.5,"intRushingYards":55.5,"intTouchdowns":1.5},
        "blowout_rule": ("spread", 14),
    },
    "XFL": {
        "odds_key": "americanfootball_xfl",
        "apisports_base": "american-football", "apisports_league": "4",
        "stat_fields": {"Pass Yds":"intPassingYards","TDs":"intTouchdowns"},
        "default_lines": {"intPassingYards":200.5,"intTouchdowns":1.5},
        "blowout_rule": ("spread", 14),
    },
    "WNBA": {
        "odds_key": "basketball_wnba",
        "apisports_base": "basketball", "apisports_league": "13",
        "stat_fields": {"Points":"intPoints","Rebounds":"intRebounds","Assists":"intAssists"},
        "default_lines": {"intPoints":14.5,"intRebounds":5.5,"intAssists":3.5},
        "blowout_rule": ("spread", 12),
    },
    "NBA G League": {
        "odds_key": "basketball_nba_dleague",
        "apisports_base": "basketball", "apisports_league": "14",
        "stat_fields": {"Points":"intPoints","Rebounds":"intRebounds","Assists":"intAssists"},
        "default_lines": {"intPoints":18.5,"intRebounds":5.5,"intAssists":4.5},
        "blowout_rule": ("spread", 12),
    },
    "EPL": {
        "odds_key": "soccer_epl",
        "apisports_base": "football", "apisports_league": "39",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots","Yellow Cards":"intYellowCards"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5,"intYellowCards":0.5},
        "blowout_rule": ("ml", -400),
    },
    "La Liga": {
        "odds_key": "soccer_spain_la_liga",
        "apisports_base": "football", "apisports_league": "140",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "Bundesliga": {
        "odds_key": "soccer_germany_bundesliga",
        "apisports_base": "football", "apisports_league": "78",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "Serie A": {
        "odds_key": "soccer_italy_serie_a",
        "apisports_base": "football", "apisports_league": "135",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "Ligue 1": {
        "odds_key": "soccer_france_ligue_one",
        "apisports_base": "football", "apisports_league": "61",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "MLS": {
        "odds_key": "soccer_usa_mls",
        "apisports_base": "football", "apisports_league": "253",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "Champions League": {
        "odds_key": "soccer_uefa_champs_league",
        "apisports_base": "football", "apisports_league": "2",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "Europa League": {
        "odds_key": "soccer_uefa_europa_league",
        "apisports_base": "football", "apisports_league": "3",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "Eredivisie": {
        "odds_key": "soccer_netherlands_eredivisie",
        "apisports_base": "football", "apisports_league": "88",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "Primeira Liga": {
        "odds_key": "soccer_portugal_primeira_liga",
        "apisports_base": "football", "apisports_league": "94",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "Brasileirao": {
        "odds_key": "soccer_brazil_campeonato",
        "apisports_base": "football", "apisports_league": "71",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5},
        "blowout_rule": ("ml", -400),
    },
    "Liga MX": {
        "odds_key": "soccer_mexico_ligamx",
        "apisports_base": "football", "apisports_league": "262",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5},
        "blowout_rule": ("ml", -400),
    },
    "Argentine Primera": {
        "odds_key": "soccer_argentina_primera_division",
        "apisports_base": "football", "apisports_league": "128",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5},
        "blowout_rule": ("ml", -400),
    },
    "FIFA World Cup": {
        "odds_key": "soccer_fifa_world_cup",
        "apisports_base": "football", "apisports_league": "1",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Shots":"intShots"},
        "default_lines": {"intGoals":0.5,"intAssists":0.5,"intShots":2.5},
        "blowout_rule": ("ml", -400),
    },
    "ATP Tennis": {
        "odds_key": "tennis_atp_french_open",
        "apisports_base": "tennis", "apisports_league": "1",
        "stat_fields": {"Aces":"intAces","Double Faults":"intDoubleFaults","Games Won":"intGamesWon"},
        "default_lines": {"intAces":5.5,"intDoubleFaults":3.5,"intGamesWon":20.5},
        "blowout_rule": ("ml", -500),
    },
    "WTA Tennis": {
        "odds_key": "tennis_wta_french_open",
        "apisports_base": "tennis", "apisports_league": "2",
        "stat_fields": {"Aces":"intAces","Double Faults":"intDoubleFaults","Games Won":"intGamesWon"},
        "default_lines": {"intAces":3.5,"intDoubleFaults":3.5,"intGamesWon":18.5},
        "blowout_rule": ("ml", -500),
    },
    "PGA Tour": {
        "odds_key": "golf_pga_championship",
        "apisports_base": "golf", "apisports_league": "1",
        "stat_fields": {"Score":"intScore","Birdies":"intBirdies","Eagles":"intEagles"},
        "default_lines": {"intScore":-3.5,"intBirdies":4.5,"intEagles":0.5},
        "blowout_rule": ("ml", -600),
    },
    "European Tour (Golf)": {
        "odds_key": "golf_european_tour",
        "apisports_base": "golf", "apisports_league": "2",
        "stat_fields": {"Score":"intScore","Birdies":"intBirdies"},
        "default_lines": {"intScore":-2.5,"intBirdies":4.5},
        "blowout_rule": ("ml", -600),
    },
    "Masters Tournament": {
        "odds_key": "golf_masters_tournament_winner",
        "apisports_base": "golf", "apisports_league": "1",
        "stat_fields": {"Score":"intScore","Birdies":"intBirdies"},
        "default_lines": {"intScore":-5.5,"intBirdies":5.5},
        "blowout_rule": ("ml", -600),
    },
    "UFC / MMA": {
        "odds_key": "mma_mixed_martial_arts",
        "apisports_base": "mma", "apisports_league": "1",
        "stat_fields": {"Sig Strikes":"intStrikes","Takedowns":"intTakedowns"},
        "default_lines": {"intStrikes":50.5,"intTakedowns":1.5},
        "blowout_rule": ("ml", -400),
    },
    "Boxing": {
        "odds_key": "boxing_boxing",
        "apisports_base": "boxing", "apisports_league": "1",
        "stat_fields": {"Punches Landed":"intPunchesLanded","Knockdowns":"intKnockdowns"},
        "default_lines": {"intPunchesLanded":60.5,"intKnockdowns":0.5},
        "blowout_rule": ("ml", -500),
    },
    "Formula 1": {
        "odds_key": "motorsport_formula_one",
        "apisports_base": "formula-1", "apisports_league": "1",
        "stat_fields": {"Finish Pos":"intPosition","Points":"intPoints"},
        "default_lines": {"intPosition":5.5,"intPoints":8.5},
        "blowout_rule": ("ml", -600),
    },
    "NASCAR Cup": {
        "odds_key": "motorsport_nascar_cup_series",
        "apisports_base": "nascar", "apisports_league": "1",
        "stat_fields": {"Finish Pos":"intPosition","Laps Led":"intLapsLed"},
        "default_lines": {"intPosition":10.5,"intLapsLed":20.5},
        "blowout_rule": ("ml", -600),
    },
    "Rugby Union — Six Nations": {
        "odds_key": "rugbyunion_six_nations",
        "apisports_base": "rugby", "apisports_league": "17",
        "stat_fields": {"Tries":"intTries","Conversions":"intConversions"},
        "default_lines": {"intTries":0.5,"intConversions":0.5},
        "blowout_rule": ("spread", 20),
    },
    "NRL Rugby League": {
        "odds_key": "rugbyleague_nrl",
        "apisports_base": "rugby", "apisports_league": "1",
        "stat_fields": {"Tries":"intTries","Tackles":"intTackles"},
        "default_lines": {"intTries":0.5,"intTackles":20.5},
        "blowout_rule": ("spread", 20),
    },
    "AFL": {
        "odds_key": "aussierules_afl",
        "apisports_base": "afl", "apisports_league": "1",
        "stat_fields": {"Disposals":"intDisposals","Goals":"intGoals","Marks":"intMarks"},
        "default_lines": {"intDisposals":22.5,"intGoals":1.5,"intMarks":5.5},
        "blowout_rule": ("spread", 25),
    },
    "Cricket — IPL": {
        "odds_key": "cricket_ipl",
        "apisports_base": "cricket", "apisports_league": "1",
        "stat_fields": {"Runs":"intRuns","Wickets":"intWickets","Fours":"intFours","Sixes":"intSixes"},
        "default_lines": {"intRuns":30.5,"intWickets":1.5,"intFours":3.5,"intSixes":1.5},
        "blowout_rule": ("ml", -400),
    },
    "Cricket — Test": {
        "odds_key": "cricket_test_match",
        "apisports_base": "cricket", "apisports_league": "2",
        "stat_fields": {"Runs":"intRuns","Wickets":"intWickets"},
        "default_lines": {"intRuns":40.5,"intWickets":2.5},
        "blowout_rule": ("ml", -400),
    },
    "CS2 (Counter-Strike)": {
        "odds_key": "esports_cs2",
        "apisports_base": None, "apisports_league": None,
        "stat_fields": {"Kills":"intKills","Deaths":"intDeaths","Assists":"intAssists"},
        "default_lines": {"intKills":15.5,"intDeaths":12.5,"intAssists":5.5},
        "blowout_rule": ("spread", 10),
    },
    "League of Legends": {
        "odds_key": "esports_lol",
        "apisports_base": None, "apisports_league": None,
        "stat_fields": {"Kills":"intKills","Deaths":"intDeaths","Assists":"intAssists"},
        "default_lines": {"intKills":3.5,"intDeaths":3.5,"intAssists":7.5},
        "blowout_rule": ("spread", 10),
    },
    "Dota 2": {
        "odds_key": "esports_dota2",
        "apisports_base": None, "apisports_league": None,
        "stat_fields": {"Kills":"intKills","Deaths":"intDeaths","Assists":"intAssists"},
        "default_lines": {"intKills":5.5,"intDeaths":5.5,"intAssists":8.5},
        "blowout_rule": ("spread", 10),
    },
    "Valorant": {
        "odds_key": "esports_valorant",
        "apisports_base": None, "apisports_league": None,
        "stat_fields": {"Kills":"intKills","Deaths":"intDeaths","Assists":"intAssists"},
        "default_lines": {"intKills":17.5,"intDeaths":14.5,"intAssists":5.5},
        "blowout_rule": ("spread", 10),
    },
    "Table Tennis": {
        "odds_key": "tabletennis_tt_cup",
        "apisports_base": "table-tennis", "apisports_league": "1",
        "stat_fields": {"Points Won":"intPointsWon"},
        "default_lines": {"intPointsWon":40.5},
        "blowout_rule": ("ml", -500),
    },
    "Volleyball — WVL": {
        "odds_key": "volleyball_womens_world_championship",
        "apisports_base": "volleyball", "apisports_league": "1",
        "stat_fields": {"Kills":"intKills","Aces":"intAces","Blocks":"intBlocks"},
        "default_lines": {"intKills":10.5,"intAces":1.5,"intBlocks":1.5},
        "blowout_rule": ("spread", 10),
    },
    "Handball — EHF": {
        "odds_key": "handball_ehf_champions_league",
        "apisports_base": "handball", "apisports_league": "1",
        "stat_fields": {"Goals":"intGoals","Assists":"intAssists","Saves":"intSaves"},
        "default_lines": {"intGoals":5.5,"intAssists":3.5,"intSaves":6.5},
        "blowout_rule": ("spread", 10),
    },
}

SPORT_NAMES = sorted(SPORT_CONFIG.keys())

# ──────────────────────────────────────────────
# SESSION STATE INIT
# ──────────────────────────────────────────────
for _k, _v in {
    "active_player": "",
    "active_stat": "",
    "active_line": 0.0,
    "player_results": None,
    "game_logs": None,
    "log_source": None,
    "active_team": "",
    "roster_list": [],
    "excluded_players": [],
    "parlay_legs": [],
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ──────────────────────────────────────────────
# TSDB STAT KEY NORMALIZER
# Maps every known TheSportsDB stat key variant → our internal intXxx keys
# ──────────────────────────────────────────────
_TSDB_STAT_NORMALIZE = {
    # ── Basketball ──────────────────────────────
    "intPointsScored":     "intPoints",
    "intScore":            "intPoints",
    "intReboundsTotal":    "intRebounds",
    "intRebounds":         "intRebounds",
    "intAssistsTotal":     "intAssists",
    "intAssists":          "intAssists",
    "int3PointsMade":      "intThrees",
    "intThreesMade":       "intThrees",
    "intThreesScored":     "intThrees",
    "intThrees":           "intThrees",
    "intStealsTotal":      "intSteals",
    "intSteals":           "intSteals",
    "intBlocksTotal":      "intBlocks",
    "intBlocks":           "intBlocks",
    # ── American Football ────────────────────────
    "intPassingYards":     "intPassingYards",
    "intRushingYards":     "intRushingYards",
    "intReceivingYards":   "intReceivingYards",
    "intTouchdownsTotal":  "intTouchdowns",
    "intTouchdowns":       "intTouchdowns",
    "intReceptionsTotal":  "intReceptions",
    "intReceptions":       "intReceptions",
    "intInterceptions":    "intInterceptions",
    # ── Baseball ─────────────────────────────────
    "intHitsTotal":        "intHits",
    "intHits":             "intHits",
    "intStrikeouts":       "intStrikeouts",
    "intHomeRuns":         "intHomeRuns",
    "intRBI":              "intRBI",
    "intWalks":            "intWalks",
    "intRuns":             "intRuns",
    # ── Hockey ───────────────────────────────────
    "intGoalsTotal":       "intGoals",
    "intGoals":            "intGoals",
    "intShotsTotal":       "intShots",
    "intShots":            "intShots",
    "intSavesTotal":       "intSaves",
    "intSaves":            "intSaves",
    "intPenaltyMinutes":   "intPenaltyMinutes",
    "intPoints":           "intPoints",
    # ── Soccer ───────────────────────────────────
    "intYellowCards":      "intYellowCards",
    "intRedCards":         "intRedCards",
}


def _normalize_tsdb_game(raw: dict) -> dict:
    """
    Remap TheSportsDB raw stat keys → our internal intXxx keys.
    Preserves date and opponent fields for display.
    """
    out = {}
    for k, v in raw.items():
        mapped = _TSDB_STAT_NORMALIZE.get(k, k)
        out[mapped] = v

    # Normalize date field
    for date_key in ("dateEvent", "strDate", "strTimestamp", "date"):
        if raw.get(date_key):
            out["dateEvent"] = str(raw[date_key])[:10]
            break
    if "dateEvent" not in out:
        out["dateEvent"] = ""

    # Normalize opponent field
    for opp_key in ("strOpponent", "strAwayTeam", "strHomeTeam", "strTeam", "opponent"):
        if raw.get(opp_key):
            out["strOpponent"] = raw[opp_key]
            break
    if "strOpponent" not in out:
        out["strOpponent"] = ""

    return out


def _has_numeric_stats(game: dict) -> bool:
    """Return True if game dict has at least one intXxx key with a numeric value."""
    for k, v in game.items():
        if not k.startswith("int"):
            continue
        try:
            f = float(v)
            if not math.isnan(f):
                return True
        except (TypeError, ValueError):
            pass
    return False


# ──────────────────────────────────────────────
# API HELPERS
# ──────────────────────────────────────────────

@st.cache_data(ttl=15*60, show_spinner=False)
def fetch_odds(sport_key: str, api_key: str, regions: str) -> tuple:
    if not api_key or not sport_key:
        return [], "Missing API key or sport key.", None
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american",
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        quota_remaining = r.headers.get("x-requests-remaining", "?")
        if r.status_code == 401:
            return [], "❌ 401 Unauthorized — Odds API key rejected.", quota_remaining
        if r.status_code == 422:
            return [], f"❌ 422 — sport key {sport_key!r} invalid or off-season.", quota_remaining
        if r.status_code == 429:
            return [], "❌ 429 Rate limit / quota exhausted.", quota_remaining
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get("message"):
            return [], f"❌ API error: {data['message']}", quota_remaining
        return data if isinstance(data, list) else [], None, quota_remaining
    except requests.exceptions.Timeout:
        return [], "❌ Request timed out.", None
    except Exception as e:
        return [], f"❌ Unexpected error: {e}", None


def _tsdb_get(url: str, params: dict, tsdb_key: str):
    """
    TheSportsDB unified request helper.
    V2 endpoints: key goes in X-API-KEY header (NOT in the URL path).
    V1 endpoints: key is already embedded in the URL path by the caller.
    Returns parsed JSON dict or None on failure.
    """
    headers = {}
    if "/api/v2/" in url:
        headers["X-API-KEY"] = tsdb_key
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


@st.cache_data(ttl=24*3600, show_spinner=False)
def search_player_tsdb(player_name: str, tsdb_key: str) -> list:
    """
    Search TheSportsDB. V2 key in header, V1 key in URL path.
    Tries Title Case, original casing, and last-name-only as fallback.
    """
    if not tsdb_key:
        return []
    cleaned = player_name.strip()
    name_variants = list(dict.fromkeys(filter(None, [
        cleaned.title(),
        cleaned,
        cleaned.split()[-1].title() if " " in cleaned else None,
    ])))
    for name_attempt in name_variants:
        for url in [
            "https://www.thesportsdb.com/api/v2/json/searchplayers.php",
            f"https://www.thesportsdb.com/api/v1/json/{tsdb_key}/searchplayers.php",
        ]:
            data = _tsdb_get(url, {"p": name_attempt}, tsdb_key)
            if data:
                result = data.get("player") or []
                if result:
                    return result
    return []


@st.cache_data(ttl=24*3600, show_spinner=False)
def fetch_player_gamelogs_bdl(player_name: str, bdl_key: str, sport: str) -> list:
    """
    Balldontlie per-game stats — primary game log source for NBA and MLB.
    Returns list of dicts with normalized intXxx stat keys.
    """
    if not bdl_key:
        return []

    # Only NBA and MLB are supported by Balldontlie
    if sport not in ("NBA", "MLB", "NCAAB", "WNBA", "NBA G League"):
        return []

    headers = {"Authorization": bdl_key}

    try:
        # Step 1: find player ID
        r = requests.get(
            "https://api.balldontlie.io/v1/players",
            params={"search": player_name, "per_page": 5},
            headers=headers, timeout=10,
        )
        r.raise_for_status()
        players = r.json().get("data", [])
        if not players:
            return []
        pid = players[0]["id"]

        # Step 2: fetch recent game stats
        # Use current season — NBA season year = calendar year the season ends in
        now = datetime.now()
        season = now.year if now.month >= 9 else now.year - 1

        sr = requests.get(
            "https://api.balldontlie.io/v1/stats",
            params={
                "player_ids[]": pid,
                "seasons[]": season,
                "per_page": 15,
            },
            headers=headers, timeout=10,
        )
        sr.raise_for_status()
        raw_stats = sr.json().get("data", [])

        if not raw_stats:
            # Try prior season if current returns nothing (e.g. early in season)
            sr2 = requests.get(
                "https://api.balldontlie.io/v1/stats",
                params={
                    "player_ids[]": pid,
                    "seasons[]": season - 1,
                    "per_page": 15,
                },
                headers=headers, timeout=10,
            )
            sr2.raise_for_status()
            raw_stats = sr2.json().get("data", [])

        if not raw_stats:
            return []

        # Step 3: normalize to intXxx format
        # BDL stat keys: pts, reb, ast, stl, blk, fgm, fga, fg3m, fg3a, ftm, fta,
        #                oreb, dreb, turnover, min
        bdl_map = {
            "pts":      "intPoints",
            "reb":      "intRebounds",
            "ast":      "intAssists",
            "stl":      "intSteals",
            "blk":      "intBlocks",
            "fg3m":     "intThrees",
            "turnover": "intTurnovers",
        }

        normalized = []
        for entry in raw_stats:
            game_info = entry.get("game", {})
            date      = game_info.get("date", "")[:10]
            home_team = entry.get("team", {}).get("abbreviation", "")
            g = {"dateEvent": date, "strOpponent": home_team}
            for bdl_key_name, int_key in bdl_map.items():
                val = entry.get(bdl_key_name)
                if val is not None:
                    try:
                        g[int_key] = float(val)
                    except (TypeError, ValueError):
                        pass
            if _has_numeric_stats(g):
                normalized.append(g)

        # Sort by date descending, return last 10
        normalized.sort(key=lambda x: x.get("dateEvent", ""), reverse=True)
        return normalized[:10]

    except Exception:
        return []


@st.cache_data(ttl=7*24*3600, show_spinner=False)
def fetch_team_roster_tsdb(team_id: str, tsdb_key: str) -> list:
    if not tsdb_key:
        return []
    data = _tsdb_get(
        "https://www.thesportsdb.com/api/v2/json/lookup_all_players.php",
        {"id": team_id}, tsdb_key
    )
    if data:
        return data.get("player") or []
    # V1 fallback
    data = _tsdb_get(
        f"https://www.thesportsdb.com/api/v1/json/{tsdb_key}/lookup_all_players.php",
        {"id": team_id}, tsdb_key
    )
    return data.get("player") or [] if data else []


@st.cache_data(ttl=7*24*3600, show_spinner=False)
def search_team_tsdb(team_name: str, tsdb_key: str) -> list:
    if not tsdb_key:
        return []
    data = _tsdb_get(
        "https://www.thesportsdb.com/api/v2/json/searchteams.php",
        {"t": team_name}, tsdb_key
    )
    if data:
        return data.get("teams") or []
    data = _tsdb_get(
        f"https://www.thesportsdb.com/api/v1/json/{tsdb_key}/searchteams.php",
        {"t": team_name}, tsdb_key
    )
    return data.get("teams") or [] if data else []


@st.cache_data(ttl=24*3600, show_spinner=False)
def fetch_player_stats_espn(player_name: str) -> list:
    """
    ESPN public API fallback — no key required.
    Searches ESPN athlete lookup then pulls recent game log.
    Returns list of dicts with normalized intXxx stat keys.
    """
    try:
        search_url = "https://site.api.espn.com/apis/common/v3/search"
        sr = requests.get(search_url, params={"query": player_name, "limit": 5, "type": "athlete"}, timeout=10)
        if sr.status_code != 200:
            return []
        results = sr.json().get("results", [])
        athlete_id = None
        sport_path = None
        for res in results:
            for item in res.get("contents", []):
                if item.get("type") == "athlete":
                    athlete_id = item.get("id")
                    desc = (item.get("description") or "").lower()
                    if "basketball" in desc or "nba" in desc:
                        sport_path = "basketball/nba"
                    elif "football" in desc or "nfl" in desc:
                        sport_path = "football/nfl"
                    elif "baseball" in desc or "mlb" in desc:
                        sport_path = "baseball/mlb"
                    elif "hockey" in desc or "nhl" in desc:
                        sport_path = "hockey/nhl"
                    else:
                        sport_path = "basketball/nba"
                    break
            if athlete_id:
                break

        if not athlete_id or not sport_path:
            return []

        # ESPN season label = the ENDING year of the season.
        # NBA/NHL 2024-25 → season=2025. New season starts ~October.
        # NFL 2024 → season=2024. New season starts ~September.
        # MLB 2025 → season=2025. New season starts ~March/April.
        now = datetime.now()
        if sport_path in ("basketball/nba", "hockey/nhl"):
            espn_season = str(now.year) if now.month >= 10 else str(now.year - 1 if now.month < 7 else now.year)
        elif sport_path == "football/nfl":
            espn_season = str(now.year) if now.month >= 9 else str(now.year - 1)
        else:
            espn_season = str(now.year)
        log_url = f"https://site.web.api.espn.com/apis/common/v3/sports/{sport_path}/athletes/{athlete_id}/gamelog"
        lr = requests.get(log_url, params={"season": espn_season}, timeout=10)
        if lr.status_code != 200:
            return []
        log_data = lr.json()

        label_map = {
            "PTS": "intPoints", "REB": "intRebounds", "AST": "intAssists",
            "3PM": "intThrees", "STL": "intSteals", "BLK": "intBlocks",
            "PY":  "intPassingYards", "RY": "intRushingYards", "REC": "intReceivingYards",
            "TD":  "intTouchdowns",  "H":  "intHits",  "SO": "intStrikeouts",
            "RBI": "intRBI", "HR": "intHomeRuns", "G": "intGoals", "A": "intAssists",
            "S":   "intShots", "SV": "intSaves",
        }

        stat_rows = []
        for stype in log_data.get("seasonTypes", []):
            for cat in stype.get("categories", []):
                labels = cat.get("labels", [])
                for event_stat in cat.get("events", []):
                    stat_rows.append({
                        "labels": labels,
                        "stats":  event_stat.get("stats", []),
                    })

        normalized = []
        for row in stat_rows[:10]:
            game = {"dateEvent": "", "strOpponent": ""}
            for i, lbl in enumerate(row["labels"]):
                mapped = label_map.get(lbl, f"int{lbl}")
                if i < len(row["stats"]):
                    try:
                        game[mapped] = float(row["stats"][i])
                    except (ValueError, TypeError):
                        pass
            if _has_numeric_stats(game):
                normalized.append(game)

        return normalized[:10]
    except Exception:
        return []


@st.cache_data(ttl=24*3600, show_spinner=False)
def fetch_player_season_avg_bdl(player_name: str, bdl_key: str) -> dict:
    """Balldontlie season averages — used only as last-resort display fallback."""
    if not bdl_key:
        return {}
    headers = {"Authorization": bdl_key}
    try:
        r = requests.get(
            "https://api.balldontlie.io/v1/players",
            params={"search": player_name, "per_page": 1},
            headers=headers, timeout=10,
        )
        r.raise_for_status()
        players = r.json().get("data", [])
        if not players:
            return {}
        pid = players[0]["id"]
        now = datetime.now()
        season = now.year if now.month >= 9 else now.year - 1
        sr = requests.get(
            "https://api.balldontlie.io/v1/season_averages",
            params={"player_ids[]": pid, "season": season},
            headers=headers, timeout=10,
        )
        sr.raise_for_status()
        avgs = sr.json().get("data", [])
        return avgs[0] if avgs else {}
    except Exception:
        return {}


@st.cache_data(ttl=15*60, show_spinner=False)
def fetch_live_scores_apisports(apisports_base: str, apisports_league: str, apis_key: str) -> list:
    if not apis_key or not apisports_base or not apisports_league:
        return []
    url = f"https://v1.{apisports_base}.api-sports.io/games"
    headers = {"x-apisports-key": apis_key, "x-rapidapi-key": apis_key}
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        r = requests.get(url, params={"date": today, "league": apisports_league}, headers=headers, timeout=15)
        if r.status_code in (401, 403):
            return [{"_error": f"API-Sports auth failed ({r.status_code})"}]
        r.raise_for_status()
        return r.json().get("response", [])
    except Exception as e:
        return [{"_error": str(e)}]


# ──────────────────────────────────────────────
# LOGIC HELPERS
# ──────────────────────────────────────────────

def american_to_decimal(odds: int) -> float:
    if odds >= 0:
        return round(1 + odds / 100, 4)
    return round(1 + 100 / abs(odds), 4)

def decimal_to_american(dec: float) -> int:
    if dec <= 1.0:
        return 0
    if dec >= 2:
        return int((dec - 1) * 100)
    return int(-100 / (dec - 1))

def parlay_odds(american_odds_list: list) -> int:
    if not american_odds_list:
        return 0
    decimal = 1.0
    for o in american_odds_list:
        decimal *= american_to_decimal(o)
    return decimal_to_american(decimal)

def compute_hit_rate(game_logs: list, stat_field: str, line: float) -> dict:
    if not game_logs:
        return {"hit_rate": None, "avg": None, "games": 0}
    vals = []
    for g in game_logs:
        val = g.get(stat_field)
        if val is not None:
            try:
                vals.append(float(val))
            except (ValueError, TypeError):
                pass
    if not vals:
        return {"hit_rate": None, "avg": None, "games": 0}
    hits = sum(1 for v in vals if v >= line)
    return {
        "hit_rate": round(hits / len(vals) * 100, 1),
        "avg": round(sum(vals) / len(vals), 1),
        "games": len(vals),
    }

def get_market_median(bookmakers: list, market_key: str, team: str):
    prices = []
    for bk in bookmakers:
        # Exclude Hard Rock from the market median so the comparison is fair
        bk_key = bk.get("key", "").lower()
        if "hardrock" in bk_key or "hard_rock" in bk_key:
            continue
        for mkt in bk.get("markets", []):
            if mkt.get("key") != market_key:
                continue
            for out in mkt.get("outcomes", []):
                if out.get("name") == team:
                    prices.append(out.get("price", 0))
    if not prices:
        return None
    prices.sort()
    n, mid = len(prices), len(prices) // 2
    return round((prices[mid-1]+prices[mid])/2 if n % 2 == 0 else prices[mid], 1)

HARDROCK_KEYS = {"hardrock", "hardrock_bet", "hardrock_us", "hard_rock", "hardrock_sportsbook", "hardrockbet", "hardrockbet_az"}

def get_hardrock_line(bookmakers: list, market_key: str, team: str):
    for bk in bookmakers:
        bk_key = bk.get("key", "").lower()
        if not (bk_key in HARDROCK_KEYS or "hardrock" in bk_key or "hard_rock" in bk_key):
            continue
        for mkt in bk.get("markets", []):
            if mkt.get("key") != market_key:
                continue
            for out in mkt.get("outcomes", []):
                if out.get("name") == team:
                    return out.get("price")
    return None

def is_significant_edge(hr, median, market_key: str = "h2h") -> bool:
    if hr is None or median is None:
        return False
    if isinstance(hr, float) and math.isnan(hr): return False
    if isinstance(median, float) and math.isnan(median): return False
    diff = abs(hr - median)
    if market_key in ("spreads", "totals"):
        return diff >= 0.5
    base = abs(median) if median != 0 else 1
    return diff >= max(20, base * 0.08)

def safe_odds_int(val) -> str:
    try:
        if val is None: return "—"
        if isinstance(val, float) and math.isnan(val): return "—"
        return f"{int(val):+d}"
    except (TypeError, ValueError):
        return "—"

def safe_float(val) -> str:
    try:
        if val is None: return "—"
        if isinstance(val, float) and math.isnan(val): return "—"
        return f"{val:+.1f}"
    except (TypeError, ValueError):
        return "—"

def build_hit_rate_badge(rate) -> str:
    if rate is None:
        return '<span class="badge-gray">N/A</span>'
    if rate >= 70:
        return f'<span class="badge-green">🟢 {rate}%</span>'
    if rate >= 55:
        return f'<span class="badge-gold">🟡 {rate}%</span>'
    return f'<span class="badge-red">🔴 {rate}%</span>'

def _html_escape(val) -> str:
    s = str(val)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def make_sticky_table(df: pd.DataFrame) -> str:
    headers = "".join(f"<th>{_html_escape(c)}</th>" for c in df.columns)
    body = ""
    for _, row in df.iterrows():
        cells = "".join(
            # Don't escape badge HTML — it's intentional markup
            f"<td>{v}</td>" if isinstance(v, str) and v.startswith("<span") else f"<td>{_html_escape(v)}</td>"
            for v in row
        )
        body += f"<tr>{cells}</tr>"
    return (
        f'<div class="sticky-table-wrapper">'
        f'<table><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table>'
        f'</div>'
    )

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown(f"""
<div class="hrb-header">
  <div>
    <h1>🪨 HardRock Bet Tool</h1>
    <span>LIVE DASHBOARD &nbsp;·&nbsp; {datetime.now().strftime("%b %d, %Y %I:%M %p")}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Controls")

    sport = st.selectbox("Sport", SPORT_NAMES, index=SPORT_NAMES.index("NBA"))
    cfg   = SPORT_CONFIG[sport]

    green_light = st.toggle("🟢 Green Light (70%+ only)", value=False)

    st.markdown("---")
    st.markdown("### 🔍 Player Lookup")

    player_input = st.text_input("Player Name", placeholder="e.g. LeBron James", key="txt_player")
    stat_option  = st.selectbox("Stat", list(cfg["stat_fields"].keys()), key="sel_stat")
    stat_field   = cfg["stat_fields"][stat_option]
    default_line = float(cfg["default_lines"].get(stat_field, 1.5))
    line_val     = st.number_input("Line (O/U)", value=default_line, step=0.5, format="%.1f", key="num_line")

    if st.button("🔎 Apply — Look Up Player", key="btn_lookup"):
        if player_input.strip():
            pname_input = player_input.strip()
            st.session_state["active_player"]  = pname_input
            st.session_state["active_stat"]    = stat_field
            st.session_state["active_line"]    = line_val

            # Step 1: TSDB for player profile/photo only
            with st.spinner(f"Looking up {pname_input}..."):
                found = search_player_tsdb(pname_input, TSDB_KEY.strip())
            st.session_state["player_results"] = found

            # Step 2: Game logs — BDL first (NBA/MLB), ESPN fallback for others
            with st.spinner("Fetching game logs..."):
                logs = fetch_player_gamelogs_bdl(pname_input, BDL_KEY.strip(), sport)
                log_source = "Balldontlie" if logs else None

                if not logs:
                    logs = fetch_player_stats_espn(pname_input)
                    log_source = "ESPN" if logs else None

            st.session_state["game_logs"]   = logs
            st.session_state["log_source"]  = log_source
        else:
            st.warning("Enter a player name first.")

    st.markdown("---")
    st.markdown("### 👥 Teammate Filter")

    team_name_filter = st.text_input("Team Name (for roster)", placeholder="e.g. Lakers", key="txt_team")

    if st.button("📋 Apply — Load Roster", key="btn_roster"):
        if team_name_filter.strip():
            with st.spinner(f"Searching for {team_name_filter}..."):
                teams_found = search_team_tsdb(team_name_filter.strip(), TSDB_KEY.strip())
            if teams_found:
                team_id = teams_found[0].get("idTeam", "")
                with st.spinner("Loading full roster..."):
                    roster = fetch_team_roster_tsdb(team_id, TSDB_KEY.strip())
                st.session_state["roster_list"] = [
                    p.get("strPlayer","") for p in roster if p.get("strPlayer","")
                ]
                st.session_state["active_team"] = teams_found[0].get("strTeam", team_name_filter)
                st.session_state["excluded_players"] = []
            else:
                st.session_state["roster_list"] = []
                st.session_state["active_team"] = ""
                st.warning("No team found — check spelling.")
        else:
            st.warning("Enter a team name first.")

    roster_list = st.session_state.get("roster_list", [])
    if roster_list:
        st.caption(f"✅ Roster loaded: **{st.session_state.get('active_team','')}** ({len(roster_list)} players)")
        excl = st.multiselect(
            "Exclude players (simulate absence)",
            options=roster_list,
            default=st.session_state.get("excluded_players", []),
            key="ms_exclude",
        )
        st.session_state["excluded_players"] = excl
    else:
        excl = []

    st.markdown("---")
    st.markdown("### 🎰 Parlay Calculator")
    parlay_legs = st.session_state.get("parlay_legs", [])
    if parlay_legs:
        for i, leg in enumerate(parlay_legs):
            st.markdown(f"**{i+1}.** {leg['name']} — `{leg['odds']:+d}`")
        total = parlay_odds([l["odds"] for l in parlay_legs])
        impl  = round(100 / american_to_decimal(total), 1)
        st.metric("Total Odds", f"{total:+d}", f"Implied {impl}%")
        if st.button("🗑️ Clear Parlay"):
            st.session_state["parlay_legs"] = []
            st.rerun()
    else:
        st.caption("No legs yet. Use '➕ Add to Parlay' in the main panel.")

    st.markdown("---")
    if st.button("🔄 Refresh All Data"):
        st.cache_data.clear()
        st.rerun()

# ──────────────────────────────────────────────
# MAIN TABS
# ──────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Player Hit Rates", "📈 Lines & Edges", "📡 Live Scores"])

# ══════════════════════════════════════════════
# TAB 1 — PLAYER HIT RATES
# ══════════════════════════════════════════════
with tab1:
    player_results = st.session_state.get("player_results")
    game_logs      = st.session_state.get("game_logs")
    active_player  = st.session_state.get("active_player", "")
    active_stat    = st.session_state.get("active_stat", "")
    active_line    = st.session_state.get("active_line", 0.0)
    log_source     = st.session_state.get("log_source", None)
    excl           = st.session_state.get("excluded_players", [])

    stat_label = stat_option
    for lbl, sf in cfg["stat_fields"].items():
        if sf == active_stat:
            stat_label = lbl
            break

    if player_results is None and not game_logs:
        st.info("👈 Enter a player name & stat in the sidebar, then click **Apply — Look Up Player**.")

    else:
        # ── Player header ────────────────────────────────────────────────────
        pname  = active_player
        pteam  = ""
        ppos   = ""
        pthumb = ""
        if player_results:
            p      = player_results[0]
            pname  = p.get("strPlayer", active_player)
            pteam  = p.get("strTeam", "")
            ppos   = p.get("strPosition", "")
            pthumb = p.get("strThumb", "")

        col_img, col_info = st.columns([1, 4])
        with col_img:
            if pthumb:
                st.image(pthumb, width=90)
        with col_info:
            st.markdown(f"### {pname}")
            if pteam or ppos:
                st.markdown(f"**{pteam}** · {ppos} · {sport}")
            if log_source:
                st.caption(f"📊 Stats sourced from **{log_source}**")
            if excl:
                st.markdown(f"🚫 Excluding: {', '.join(excl)}")

        st.markdown("---")

        # ── No game logs — try season averages as last resort ────────────────
        if not game_logs or not any(_has_numeric_stats(g) for g in game_logs):
            bdl = fetch_player_season_avg_bdl(pname, BDL_KEY.strip())
            if bdl:
                st.info("📊 Showing **season averages** from Balldontlie (no per-game log available for this sport/player).")
                ca, cb, cc, cd = st.columns(4)
                ca.metric("PTS avg", bdl.get("pts", "N/A"))
                cb.metric("REB avg", bdl.get("reb", "N/A"))
                cc.metric("AST avg", bdl.get("ast", "N/A"))
                cd.metric("MIN avg", bdl.get("min", "N/A"))
            else:
                st.error(f"No game log data found for **{pname}**. "
                         "For NBA players use the exact full name (e.g. 'Jaylen Brown'). "
                         "Non-NBA sports use ESPN fallback — player may be inactive or name may differ.")

        # ── Game logs available — show hit rates ─────────────────────────────
        else:
            result   = compute_hit_rate(game_logs, active_stat, active_line)
            hit_rate = result["hit_rate"]
            avg_val  = result["avg"]
            n_games  = result["games"]

            if green_light and (hit_rate is None or hit_rate < 70):
                st.warning(
                    f"🔒 Green Light active — {pname} {stat_label} hit rate "
                    f"({hit_rate}%) is below 70%. Toggle off to view."
                )
            else:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Hit Rate", f"{hit_rate}%" if hit_rate is not None else "N/A")
                c2.metric("Avg", str(avg_val) if avg_val is not None else "N/A")
                c3.metric("Line", f"O {active_line}")
                c4.metric("Games Sampled", n_games)

                if hit_rate and hit_rate >= 55:
                    synthetic_odds = -130 if hit_rate >= 70 else -110
                    if st.button(f"➕ Add {pname} O{active_line} {stat_label} to Parlay"):
                        st.session_state["parlay_legs"].append({
                            "name": f"{pname} O{active_line} {stat_label}",
                            "odds": synthetic_odds,
                        })
                        st.success("Added to parlay!")
                        st.rerun()

                # Game log table
                st.markdown("#### Last 10 Game Log")
                rows = []
                for g in game_logs:
                    val = g.get(active_stat)
                    try:
                        val_f = float(val)
                    except (TypeError, ValueError):
                        val_f = None
                    rows.append({
                        "Date":     g.get("dateEvent", "")[:10],
                        "Opponent": g.get("strOpponent", ""),
                        stat_label: val_f if val_f is not None else "—",
                        f"O{active_line}?": "✅" if (val_f is not None and val_f >= active_line) else "❌",
                    })
                if rows:
                    st.markdown(make_sticky_table(pd.DataFrame(rows)), unsafe_allow_html=True)
                else:
                    st.caption("No parseable game log rows.")

                # Full stat scan
                st.markdown("---")
                st.markdown(f"#### Full {sport} Stat Scan")
                scan_rows = []
                for lbl, sf in cfg["stat_fields"].items():
                    dl = cfg["default_lines"].get(sf, 1.5)
                    r2 = compute_hit_rate(game_logs, sf, dl)
                    scan_rows.append({
                        "Player": pname,
                        "Stat":   lbl,
                        "Line":   dl,
                        "Badge":  build_hit_rate_badge(r2["hit_rate"]),
                        "Avg":    r2["avg"] if r2["avg"] is not None else "—",
                        "Games":  r2["games"],
                    })
                scan_df = pd.DataFrame(scan_rows)
                if green_light:
                    scan_df = scan_df[scan_df["Badge"].str.contains("🟢")]
                if not scan_df.empty:
                    st.markdown(make_sticky_table(scan_df), unsafe_allow_html=True)
                else:
                    st.info("No props at 70%+ with Green Light active.")

# ══════════════════════════════════════════════
# TAB 2 — LINES & EDGES
# ══════════════════════════════════════════════
with tab2:
    st.markdown(f"### 📈 {sport} Lines — Hard Rock vs Market Median")
    odds_key = cfg.get("odds_key", "")

    if not odds_key:
        st.warning(f"No Odds API key configured for {sport}.")
    else:
        with st.spinner("Fetching lines from The Odds API..."):
            odds_data, odds_error, quota_left = fetch_odds(odds_key, ODDS_KEY.strip(), ODDS_REGIONS.strip())

        diag_col1, diag_col2 = st.columns(2)
        diag_col1.caption(f"📊 Requests remaining (Odds API): **{quota_left}**")

        if odds_error:
            st.error(odds_error)
            st.stop()
        elif not odds_data:
            st.info(f"✅ Odds API connected (quota left: {quota_left}). No upcoming/live {sport} events found — sport may be off-season or between rounds.")
            st.stop()
        else:
            all_bk_keys = sorted({bk.get("key","") for ev in odds_data for bk in ev.get("bookmakers",[])})
            hr_present = any(k for k in all_bk_keys if "hardrock" in k or "hard_rock" in k)
            diag_col2.caption(
                f"📚 Books in response: `{'`, `'.join(all_bk_keys) or 'none'}`  "
                f"{'✅ Hard Rock found' if hr_present else '⚠️ Hard Rock NOT in response'}"
            )
            if not hr_present:
                st.warning(
                    "Hard Rock Bet is not in this Odds API response. "
                    "Hard Rock is only available in FL, NJ, OH, IN, PA, TN, VA, and AZ. "
                    "The table will still show the Market Median from all other books."
                )

            edge_rows = []
            for event in odds_data:
                home       = event.get("home_team", "")
                away       = event.get("away_team", "")
                bookmakers = event.get("bookmakers", [])
                commence   = event.get("commence_time","")[:16].replace("T"," ")

                for team in [home, away]:
                    for market_key in ["h2h", "spreads"]:
                        hr_line = get_hardrock_line(bookmakers, market_key, team)
                        median  = get_market_median(bookmakers, market_key, team)
                        edge    = is_significant_edge(hr_line, median, market_key)
                        edge_rows.append({
                            "Time":    commence,
                            "Matchup": f"{away} @ {home}",
                            "Team":    team,
                            "Market":  market_key.upper(),
                            "HardRock": hr_line,
                            "Median":   median,
                            "Diff":     round(hr_line - median, 1) if (hr_line is not None and median is not None) else None,
                            "Edge":     edge,
                        })

            if edge_rows:
                df_edges = pd.DataFrame(edge_rows)
                headers_e = "".join(f"<th>{c}</th>" for c in ["Time","Matchup","Team","Market","HardRock","Median","Diff","Edge"])
                body_e = ""
                for _, row in df_edges.iterrows():
                    ef    = row.get("Edge", False)
                    hr_d  = safe_odds_int(row["HardRock"])
                    med_d = safe_odds_int(row["Median"])
                    dif_d = safe_float(row["Diff"])
                    edg_d = '<span class="badge-gold">🏅 EDGE</span>' if ef else '<span class="badge-gray">—</span>'
                    rs    = "background:#1c1507;" if ef else ""
                    body_e += (
                        f'<tr style="{rs}">'
                        f"<td>{row['Time']}</td><td>{row['Matchup']}</td>"
                        f"<td><strong>{row['Team']}</strong></td><td>{row['Market']}</td>"
                        f"<td>{hr_d}</td><td>{med_d}</td><td>{dif_d}</td><td>{edg_d}</td></tr>"
                    )
                st.markdown(
                    f'<div class="sticky-table-wrapper"><table><thead><tr>{headers_e}</tr></thead>'
                    f'<tbody>{body_e}</tbody></table></div>',
                    unsafe_allow_html=True,
                )

                edge_events = df_edges[df_edges["Edge"] == True]
                if not edge_events.empty:
                    st.markdown("---")
                    st.markdown("### 🏅 Market Edge Alerts")
                    for _, er in edge_events.iterrows():
                        hr_v  = safe_odds_int(er["HardRock"])
                        med_v = safe_odds_int(er["Median"])
                        st.markdown(
                            f'<div class="edge-alert">📌 <strong>{er["Team"]}</strong> ({er["Market"]}) — '
                            f'HardRock: <strong>{hr_v}</strong> vs Median: <strong>{med_v}</strong> '
                            f'(Δ {safe_float(er["Diff"])})</div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No line data to display.")

# ══════════════════════════════════════════════
# TAB 3 — LIVE SCORES
# ══════════════════════════════════════════════
with tab3:
    apisports_base   = cfg.get("apisports_base")
    apisports_league = cfg.get("apisports_league")
    st.markdown(f"### 📡 Live & Today's {sport} Scores (API-Sports)")

    if not apisports_base:
        st.info(f"Live scores via API-Sports are not available for **{sport}**.")
    else:
        with st.spinner("Fetching live scores..."):
            live_games = fetch_live_scores_apisports(apisports_base, apisports_league, APIS_KEY.strip())

        if live_games and live_games[0].get("_error"):
            st.error(f"API-Sports error: {live_games[0]['_error']}")
        elif not live_games:
            st.info(f"No {sport} games found for today ({datetime.now().strftime('%b %d')}). Check back on a game day.")
        else:
            st.caption(f"Showing {len(live_games)} game(s) for today")
            for game in live_games[:20]:
                g_home = game.get("teams",{}).get("home",{})
                g_away = game.get("teams",{}).get("away",{})
                sc     = game.get("scores",{})
                status = game.get("status",{}).get("long","Scheduled")
                home_name  = g_home.get("name","Home")
                away_name  = g_away.get("name","Away")
                home_score = sc.get("home",{}).get("total","—") if isinstance(sc.get("home"),dict) else sc.get("home","—")
                away_score = sc.get("away",{}).get("total","—") if isinstance(sc.get("away"),dict) else sc.get("away","—")
                col_a, col_s, col_b = st.columns([3,1,3])
                with col_a: st.markdown(f"**{away_name}**")
                with col_s: st.markdown(f"**{away_score} — {home_score}**")
                with col_b: st.markdown(f"**{home_name}**")
                st.caption(f"Status: {status}")
                st.markdown("---")

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;color:#374151;font-size:.75rem;margin-top:2rem;padding:1rem;
     border-top:1px solid #1f2937;font-family:'Share Tech Mono',monospace;">
  HardRock Bet Tool · TheSportsDB · The Odds API · API-Sports · Balldontlie<br>
  ⚠️ For informational & entertainment purposes only. Please gamble responsibly.
</div>
""", unsafe_allow_html=True)
