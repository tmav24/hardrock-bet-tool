"""
HardRock Bet Tool — Multi-API Hybrid Dashboard
Streamlit Cloud ready. Paste into app.py and deploy.
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# ──────────────────────────────────────────────
# PAGE CONFIG & THEME
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

/* Global */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: #0a0c10 !important;
    color: #e2e8f0 !important;
}

/* Header */
.hrb-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border-bottom: 2px solid #f59e0b;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    border-radius: 0 0 12px 12px;
}
.hrb-header h1 {
    font-size: 1.8rem;
    font-weight: 700;
    color: #f59e0b;
    margin: 0;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.hrb-header span {
    font-size: 0.8rem;
    color: #94a3b8;
    font-family: 'Share Tech Mono', monospace;
}

/* Metric cards */
.metric-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 0.5rem;
}
.metric-card .val {
    font-size: 2rem;
    font-weight: 700;
    color: #f59e0b;
    font-family: 'Share Tech Mono', monospace;
}
.metric-card .lbl {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Badges */
.badge-green  { background:#065f46; color:#6ee7b7; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:700; }
.badge-gold   { background:#78350f; color:#fcd34d; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:700; }
.badge-red    { background:#7f1d1d; color:#fca5a5; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:700; }
.badge-gray   { background:#1f2937; color:#94a3b8; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:700; }

/* Warning banner */
.blowout-warn {
    background: linear-gradient(90deg, #7f1d1d, #991b1b);
    border-left: 4px solid #ef4444;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-weight: 600;
    color: #fca5a5;
    font-size: 0.9rem;
}

/* Gold edge alert */
.edge-alert {
    background: linear-gradient(90deg, #78350f, #92400e);
    border-left: 4px solid #f59e0b;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    font-weight: 600;
    color: #fcd34d;
    font-size: 0.9rem;
}

/* Table — sticky first column */
.sticky-table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 10px;
    border: 1px solid #1f2937;
}
.sticky-table-wrapper table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.85rem;
}
.sticky-table-wrapper th {
    background: #1e293b;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 10px 14px;
    white-space: nowrap;
    position: sticky;
    top: 0;
    z-index: 2;
}
.sticky-table-wrapper td {
    padding: 10px 14px;
    border-bottom: 1px solid #1f2937;
    white-space: nowrap;
    color: #e2e8f0;
}
.sticky-table-wrapper tr:hover td { background: #1e293b; }
/* Sticky player name column */
.sticky-table-wrapper th:first-child,
.sticky-table-wrapper td:first-child {
    position: sticky;
    left: 0;
    background: #111827;
    z-index: 3;
    font-weight: 600;
    border-right: 2px solid #374151;
    min-width: 130px;
}
.sticky-table-wrapper th:first-child { background: #1e293b; z-index: 4; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1f2937;
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #f59e0b !important;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    letter-spacing: 1px;
}
div[data-testid="stSidebar"] .stButton button {
    background: #f59e0b;
    color: #0a0c10;
    font-weight: 700;
    border-radius: 8px;
    width: 100%;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    letter-spacing: 1px;
}

/* Streamlit overrides */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
}
.stToggle label { color: #e2e8f0 !important; }
div[data-testid="stMetric"] { background: #111827; border-radius: 10px; padding: 0.75rem; border: 1px solid #1f2937; }
div[data-testid="stMetricValue"] { color: #f59e0b !important; font-family: 'Share Tech Mono', monospace; }
.stSpinner > div { border-top-color: #f59e0b !important; }
hr { border-color: #1f2937 !important; }
.stTabs [data-baseweb="tab"] { color: #64748b; font-family: 'Rajdhani', sans-serif; font-weight: 600; font-size: 1rem; }
.stTabs [aria-selected="true"] { color: #f59e0b !important; border-bottom: 2px solid #f59e0b !important; }
.stAlert { border-radius: 10px !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# SECRETS
# ──────────────────────────────────────────────
TSDB_KEY   = st.secrets.get("THE_SPORTSDB_API_KEY", "")
ODDS_KEY   = st.secrets.get("THE_ODDS_API_KEY", "")
APIS_KEY   = st.secrets.get("API_SPORTS_API_KEY", "")
BDL_KEY    = st.secrets.get("BALLDONTLIE_API_KEY", "")

# ──────────────────────────────────────────────
# API HELPERS — with caching tiers
# ──────────────────────────────────────────────

@st.cache_data(ttl=15*60, show_spinner=False)
def fetch_odds(sport_key: str) -> list:
    """Fetch lines from The Odds API — 15-min cache."""
    if not ODDS_KEY:
        return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {
        "apiKey": ODDS_KEY,
        "regions": "us",
        "markets": "h2h,spreads,totals",
        "oddsFormat": "american",
        "bookmakers": "draftkings,fanduel,betmgm,hardrock,betonlineag,bovada",
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []

@st.cache_data(ttl=15*60, show_spinner=False)
def fetch_player_props(sport_key: str, player_name: str) -> list:
    """Fetch player props from The Odds API — 15-min cache."""
    if not ODDS_KEY:
        return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/events"
    try:
        r = requests.get(url, params={"apiKey": ODDS_KEY}, timeout=10)
        r.raise_for_status()
        events = r.json()
    except Exception:
        return []
    props = []
    for ev in events[:5]:  # limit to avoid rate hits
        eid = ev.get("id")
        purl = f"https://api.the-odds-api.com/v4/sports/{sport_key}/events/{eid}/odds"
        try:
            pr = requests.get(purl, params={
                "apiKey": ODDS_KEY,
                "markets": "player_points,player_rebounds,player_assists,player_threes,"
                           "player_hits,player_strikeouts,player_goals,player_shots",
                "oddsFormat": "american",
                "bookmakers": "hardrock,draftkings,fanduel",
            }, timeout=10)
            pr.raise_for_status()
            props.extend(pr.json().get("bookmakers", []))
            time.sleep(0.2)
        except Exception:
            pass
    return props

@st.cache_data(ttl=24*3600, show_spinner=False)
def fetch_player_last10_tsdb(player_id: str) -> list:
    """Fetch last 10 game logs from TheSportsDB Premium V2 — 24h cache."""
    if not TSDB_KEY:
        return []
    url = f"https://www.thesportsdb.com/api/v2/json/{TSDB_KEY}/playereventresults.php"
    try:
        r = requests.get(url, params={"id": player_id}, timeout=15)
        r.raise_for_status()
        data = r.json()
        results = data.get("results") or data.get("events") or []
        return results[:10]
    except Exception:
        return []

@st.cache_data(ttl=24*3600, show_spinner=False)
def search_player_tsdb(player_name: str) -> list:
    """Search player in TheSportsDB — 24h cache."""
    if not TSDB_KEY:
        return []
    url = f"https://www.thesportsdb.com/api/v2/json/{TSDB_KEY}/searchplayers.php"
    try:
        r = requests.get(url, params={"p": player_name}, timeout=10)
        r.raise_for_status()
        return r.json().get("player") or []
    except Exception:
        return []

@st.cache_data(ttl=7*24*3600, show_spinner=False)
def fetch_team_roster_tsdb(team_id: str) -> list:
    """Fetch full roster from TheSportsDB — 7-day cache."""
    if not TSDB_KEY:
        return []
    url = f"https://www.thesportsdb.com/api/v2/json/{TSDB_KEY}/lookup_all_players.php"
    try:
        r = requests.get(url, params={"id": team_id}, timeout=15)
        r.raise_for_status()
        return r.json().get("player") or []
    except Exception:
        return []

@st.cache_data(ttl=24*3600, show_spinner=False)
def fetch_player_stats_bdl(player_name: str) -> dict:
    """Fallback: NBA/MLB player stats from Balldontlie — 24h cache."""
    if not BDL_KEY:
        return {}
    headers = {"Authorization": BDL_KEY}
    try:
        r = requests.get(
            "https://api.balldontlie.io/v1/players",
            params={"search": player_name, "per_page": 1},
            headers=headers,
            timeout=10,
        )
        r.raise_for_status()
        players = r.json().get("data", [])
        if not players:
            return {}
        pid = players[0]["id"]
        sr = requests.get(
            "https://api.balldontlie.io/v1/season_averages",
            params={"player_ids[]": pid, "season": datetime.now().year - (1 if datetime.now().month < 8 else 0)},
            headers=headers,
            timeout=10,
        )
        sr.raise_for_status()
        avgs = sr.json().get("data", [])
        return avgs[0] if avgs else {}
    except Exception:
        return {}

@st.cache_data(ttl=15*60, show_spinner=False)
def fetch_live_scores_apisports(sport: str) -> list:
    """Live scores from API-Sports — 15-min cache."""
    if not APIS_KEY:
        return []
    sport_map = {"NBA": "basketball", "NFL": "american-football", "MLB": "baseball", "NHL": "hockey"}
    league_map = {"NBA": "12", "NFL": "1", "MLB": "1", "NHL": "57"}
    base = sport_map.get(sport, "basketball")
    league = league_map.get(sport, "12")
    url = f"https://v1.{base}.api-sports.io/games"
    headers = {"x-apisports-key": APIS_KEY}
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        r = requests.get(url, params={"date": today, "league": league}, headers=headers, timeout=10)
        r.raise_for_status()
        return r.json().get("response", [])
    except Exception:
        return []

@st.cache_data(ttl=7*24*3600, show_spinner=False)
def search_team_tsdb(team_name: str) -> list:
    if not TSDB_KEY:
        return []
    url = f"https://www.thesportsdb.com/api/v2/json/{TSDB_KEY}/searchteams.php"
    try:
        r = requests.get(url, params={"t": team_name}, timeout=10)
        r.raise_for_status()
        return r.json().get("teams") or []
    except Exception:
        return []

# ──────────────────────────────────────────────
# LOGIC HELPERS
# ──────────────────────────────────────────────

def american_to_decimal(odds: int) -> float:
    if odds >= 0:
        return round(1 + odds / 100, 4)
    return round(1 + 100 / abs(odds), 4)

def decimal_to_american(dec: float) -> int:
    if dec >= 2:
        return int((dec - 1) * 100)
    return int(-100 / (dec - 1))

def compute_hit_rate(game_logs: list, stat_field: str, line: float, excluded_players: list = None) -> dict:
    """
    Given last-N game logs, calculate hit rate for a player stat vs a line.
    Returns dict with hit_rate, avg, games_used.
    excluded_players: list of player names to filter out games where they played (future: lineup data).
    """
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

def get_market_median(bookmakers: list, market_key: str, team: str) -> float | None:
    """Calculate median line across all bookmakers for a given market and team."""
    prices = []
    for bk in bookmakers:
        for mkt in bk.get("markets", []):
            if mkt.get("key") != market_key:
                continue
            for out in mkt.get("outcomes", []):
                if out.get("name") == team:
                    prices.append(out.get("price", 0))
    if not prices:
        return None
    prices.sort()
    n = len(prices)
    mid = n // 2
    if n % 2 == 0:
        return round((prices[mid - 1] + prices[mid]) / 2, 1)
    return round(prices[mid], 1)

def get_hardrock_line(bookmakers: list, market_key: str, team: str) -> float | None:
    for bk in bookmakers:
        if "hardrock" not in bk.get("key", "").lower():
            continue
        for mkt in bk.get("markets", []):
            if mkt.get("key") != market_key:
                continue
            for out in mkt.get("outcomes", []):
                if out.get("name") == team:
                    return out.get("price")
    return None

def is_significant_edge(hr_line: float, median: float, market_key: str, threshold: float = 15.0) -> bool:
    """Return True if HardRock is off from median by threshold (American odds points)."""
    if hr_line is None or median is None:
        return False
    return abs(hr_line - median) >= threshold

def is_blowout_risk(sport: str, spread: float = None, moneyline: float = None) -> bool:
    if sport == "NBA" and spread is not None and abs(spread) > 12:
        return True
    if sport in ("MLB", "NHL") and moneyline is not None and moneyline < -250:
        return True
    return False

def build_hit_rate_badge(rate: float | None) -> str:
    if rate is None:
        return '<span class="badge-gray">N/A</span>'
    if rate >= 70:
        return f'<span class="badge-green">🟢 {rate}%</span>'
    if rate >= 55:
        return f'<span class="badge-gold">🟡 {rate}%</span>'
    return f'<span class="badge-red">🔴 {rate}%</span>'

def parlay_odds(american_odds_list: list[int]) -> int:
    if not american_odds_list:
        return 0
    decimal = 1.0
    for o in american_odds_list:
        decimal *= american_to_decimal(o)
    return decimal_to_american(decimal)

# ──────────────────────────────────────────────
# SPORT CONFIG
# ──────────────────────────────────────────────
SPORT_CONFIG = {
    "NBA": {
        "odds_key": "basketball_nba",
        "stat_fields": {"Points": "intPoints", "Rebounds": "intRebounds", "Assists": "intAssists", "3PM": "intThrees"},
        "stat_labels": {"intPoints": "PTS", "intRebounds": "REB", "intAssists": "AST", "intThrees": "3PM"},
        "default_lines": {"intPoints": 20.5, "intRebounds": 5.5, "intAssists": 4.5, "intThrees": 2.5},
    },
    "NFL": {
        "odds_key": "americanfootball_nfl",
        "stat_fields": {"Pass Yds": "intPassingYards", "Rush Yds": "intRushingYards", "Rec Yds": "intReceivingYards", "TDs": "intTouchdowns"},
        "stat_labels": {"intPassingYards": "PASS YDS", "intRushingYards": "RUSH YDS", "intReceivingYards": "REC YDS", "intTouchdowns": "TDs"},
        "default_lines": {"intPassingYards": 250.5, "intRushingYards": 65.5, "intReceivingYards": 55.5, "intTouchdowns": 1.5},
    },
    "MLB": {
        "odds_key": "baseball_mlb",
        "stat_fields": {"Hits": "intHits", "Strikeouts": "intStrikeouts", "RBIs": "intRBI", "HR": "intHomeRuns"},
        "stat_labels": {"intHits": "H", "intStrikeouts": "K", "intRBI": "RBI", "intHomeRuns": "HR"},
        "default_lines": {"intHits": 1.5, "intStrikeouts": 6.5, "intRBI": 1.5, "intHomeRuns": 0.5},
    },
    "NHL": {
        "odds_key": "icehockey_nhl",
        "stat_fields": {"Goals": "intGoals", "Shots": "intShots", "Points": "intPoints", "Assists": "intAssists"},
        "stat_labels": {"intGoals": "G", "intShots": "SOG", "intPoints": "PTS", "intAssists": "A"},
        "default_lines": {"intGoals": 0.5, "intShots": 3.5, "intPoints": 1.5, "intAssists": 0.5},
    },
}

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

    sport = st.selectbox("Sport", list(SPORT_CONFIG.keys()), index=0)
    cfg = SPORT_CONFIG[sport]

    green_light = st.toggle("🟢 Green Light (70%+ only)", value=False)

    st.markdown("---")
    st.markdown("### 🔍 Player Lookup")
    player_input = st.text_input("Player Name", placeholder="e.g. LeBron James")

    stat_option = st.selectbox("Stat", list(cfg["stat_fields"].keys()))
    stat_field  = cfg["stat_fields"][stat_option]
    default_line = cfg["default_lines"].get(stat_field, 10.5)
    line_val = st.number_input("Line (O/U)", value=default_line, step=0.5, format="%.1f")

    st.markdown("---")
    st.markdown("### 👥 Teammate Filter")
    team_name_filter = st.text_input("Team Name (for roster)", placeholder="e.g. Lakers")
    excluded_players = []
    if team_name_filter:
        with st.spinner("Loading roster..."):
            teams = search_team_tsdb(team_name_filter)
        if teams:
            team_id = teams[0].get("idTeam", "")
            roster = fetch_team_roster_tsdb(team_id)
            player_names = [p.get("strPlayer", "") for p in roster if p.get("strPlayer")]
            excluded_players = st.multiselect(
                "Exclude players (simulate absence)",
                options=player_names,
                help="Filter out games where these players were active.",
            )
        else:
            st.caption("No team found.")

    st.markdown("---")
    st.markdown("### 🎰 Parlay Calculator")
    parlay_legs = st.session_state.get("parlay_legs", [])

    if parlay_legs:
        for i, leg in enumerate(parlay_legs):
            st.markdown(f"**{i+1}.** {leg['name']} — `{leg['odds']:+d}`")
        total = parlay_odds([l["odds"] for l in parlay_legs])
        st.markdown(f"**Total Parlay Odds:** `{total:+d}`")
        implied_prob = round(100 / american_to_decimal(total), 1)
        st.markdown(f"**Implied Prob:** `{implied_prob}%`")
        if st.button("🗑️ Clear Parlay"):
            st.session_state["parlay_legs"] = []
            st.rerun()
    else:
        st.caption("No legs added yet. Use 'Add to Parlay' below.")

    st.markdown("---")
    if st.button("🔄 Refresh All Data"):
        st.cache_data.clear()
        st.rerun()

# ──────────────────────────────────────────────
# MAIN TABS
# ──────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Player Hit Rates", "📈 Lines & Edges", "📡 Live Scores"])

# ══════════════════════════════════════════════
# TAB 1: PLAYER HIT RATES
# ══════════════════════════════════════════════
with tab1:
    if not player_input:
        st.info("👈 Enter a player name in the sidebar to get started.")
    else:
        with st.spinner(f"Searching TheSportsDB for **{player_input}**..."):
            players_found = search_player_tsdb(player_input)

        if not players_found:
            # Fallback to Balldontlie
            st.warning("TheSportsDB returned no results — trying Balldontlie fallback...")
            bdl_stats = fetch_player_stats_bdl(player_input)
            if bdl_stats:
                st.success("✅ Balldontlie fallback data found.")
                st.json(bdl_stats)
            else:
                st.error("No player data found in any source. Check spelling.")
        else:
            player = players_found[0]
            pid    = player.get("idPlayer", "")
            pname  = player.get("strPlayer", player_input)
            pteam  = player.get("strTeam", "Unknown")
            ppos   = player.get("strPosition", "")
            pthumb = player.get("strThumb", "")

            # Player card
            col_img, col_info = st.columns([1, 4])
            with col_img:
                if pthumb:
                    st.image(pthumb, width=90)
            with col_info:
                st.markdown(f"### {pname}")
                st.markdown(f"**{pteam}** · {ppos}")
                if excluded_players:
                    st.markdown(f"🚫 Excluding teammates: {', '.join(excluded_players)}")

            st.markdown("---")

            with st.spinner("Pulling Last 10 game logs from TheSportsDB..."):
                game_logs = fetch_player_last10_tsdb(pid)

            if not game_logs:
                # Try Balldontlie as fallback
                st.warning("No game log data from TheSportsDB — checking Balldontlie...")
                bdl = fetch_player_stats_bdl(pname)
                if bdl:
                    st.info("Season averages from Balldontlie (no per-game logs available via free tier):")
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("PTS avg", bdl.get("pts", "N/A"))
                    col_b.metric("REB avg", bdl.get("reb", "N/A"))
                    col_c.metric("AST avg", bdl.get("ast", "N/A"))
                else:
                    st.error("No game log data available.")
            else:
                result = compute_hit_rate(game_logs, stat_field, line_val, excluded_players)
                hit_rate = result["hit_rate"]
                avg_val  = result["avg"]
                n_games  = result["games"]

                # Green light filter
                if green_light and (hit_rate is None or hit_rate < 70):
                    st.warning(f"🔒 Green Light active — {pname}'s {stat_option} hit rate ({hit_rate}%) is below 70%. Toggle off to view.")
                else:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Hit Rate", f"{hit_rate}%" if hit_rate else "N/A")
                    c2.metric("Avg", f"{avg_val}" if avg_val else "N/A")
                    c3.metric("Line", f"O {line_val}")
                    c4.metric("Games Sampled", n_games)

                    # Add to parlay button
                    if hit_rate and hit_rate >= 55:
                        synthetic_odds = -110 if hit_rate < 70 else -130
                        if st.button(f"➕ Add {pname} O{line_val} {stat_option} to Parlay"):
                            if "parlay_legs" not in st.session_state:
                                st.session_state["parlay_legs"] = []
                            st.session_state["parlay_legs"].append({
                                "name": f"{pname} O{line_val} {stat_option}",
                                "odds": synthetic_odds,
                            })
                            st.success("Added to parlay!")
                            st.rerun()

                    # Game log table
                    st.markdown("#### Last 10 Game Log")
                    rows = []
                    for g in game_logs:
                        val = g.get(stat_field)
                        try:
                            val_f = float(val)
                        except (TypeError, ValueError):
                            val_f = None
                        hit = "✅" if (val_f is not None and val_f >= line_val) else "❌"
                        rows.append({
                            "Date": g.get("dateEvent", "")[:10],
                            "Opponent": g.get("strAwayTeam", "") or g.get("strOpponent", ""),
                            stat_option: val_f,
                            f"O{line_val}?": hit,
                        })
                    if rows:
                        df = pd.DataFrame(rows)

                        # Build sticky HTML table
                        headers = "".join(f"<th>{c}</th>" for c in df.columns)
                        body = ""
                        for _, row in df.iterrows():
                            cells = ""
                            for col_name, v in row.items():
                                cells += f"<td>{v}</td>"
                            body += f"<tr>{cells}</tr>"
                        st.markdown(
                            f'<div class="sticky-table-wrapper"><table><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table></div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.caption("No parseable game log rows.")

                    # Full multi-stat scan
                    st.markdown("---")
                    st.markdown("#### Full Stat Scan (all available props)")
                    scan_rows = []
                    for stat_lbl, sf in cfg["stat_fields"].items():
                        dl = cfg["default_lines"].get(sf, 1.5)
                        r2 = compute_hit_rate(game_logs, sf, dl, excluded_players)
                        scan_rows.append({
                            "Stat": stat_lbl,
                            "Line": dl,
                            "Hit Rate": r2["hit_rate"],
                            "Avg": r2["avg"],
                            "Games": r2["games"],
                            "Badge": build_hit_rate_badge(r2["hit_rate"]),
                        })
                    scan_df = pd.DataFrame(scan_rows)
                    if green_light:
                        scan_df = scan_df[scan_df["Hit Rate"].apply(lambda x: x is not None and x >= 70)]

                    cols_show = ["Stat", "Line", "Badge", "Avg", "Games"]
                    headers2 = "".join(f"<th>{c}</th>" for c in cols_show)
                    body2 = ""
                    for _, row in scan_df.iterrows():
                        cells2 = (
                            f"<td><strong>{row['Stat']}</strong></td>"
                            f"<td>{row['Line']}</td>"
                            f"<td>{row['Badge']}</td>"
                            f"<td>{row['Avg']}</td>"
                            f"<td>{row['Games']}</td>"
                        )
                        body2 += f"<tr>{cells2}</tr>"
                    st.markdown(
                        f'<div class="sticky-table-wrapper"><table><thead><tr>{headers2}</tr></thead><tbody>{body2}</tbody></table></div>',
                        unsafe_allow_html=True,
                    )

# ══════════════════════════════════════════════
# TAB 2: LINES & EDGES
# ══════════════════════════════════════════════
with tab2:
    st.markdown("### 📈 Today's Lines — Hard Rock vs Market Median")

    with st.spinner("Fetching odds from The Odds API..."):
        odds_data = fetch_odds(cfg["odds_key"])

    if not odds_data:
        st.warning("No odds data returned. Check your Odds API key or quota.")
    else:
        edge_rows = []
        blowout_warnings = []

        for event in odds_data:
            home = event.get("home_team", "")
            away = event.get("away_team", "")
            bookmakers = event.get("bookmakers", [])
            commence = event.get("commence_time", "")[:16].replace("T", " ")

            for team in [home, away]:
                for market_key in ["h2h", "spreads"]:
                    hr_line = get_hardrock_line(bookmakers, market_key, team)
                    median  = get_market_median(bookmakers, market_key, team)
                    edge    = is_significant_edge(hr_line, median, market_key)

                    # Blowout checks
                    if market_key == "spreads" and sport == "NBA":
                        for bk in bookmakers:
                            for mkt in bk.get("markets", []):
                                if mkt.get("key") == "spreads":
                                    for out in mkt.get("outcomes", []):
                                        pt = out.get("point", 0)
                                        if is_blowout_risk("NBA", spread=pt):
                                            blowout_warnings.append(
                                                f"⚠️ Blowout Risk — {home} vs {away}: spread {pt:+.1f}"
                                            )
                    if market_key == "h2h" and sport in ("MLB", "NHL"):
                        if hr_line and is_blowout_risk(sport, moneyline=hr_line):
                            blowout_warnings.append(
                                f"⚠️ Heavy Favorite — {team} ML {hr_line:+d} ({sport})"
                            )

                    edge_rows.append({
                        "Time": commence,
                        "Matchup": f"{away} @ {home}",
                        "Team": team,
                        "Market": market_key.upper(),
                        "HardRock": hr_line,
                        "Median": median,
                        "Diff": round(hr_line - median, 1) if hr_line and median else None,
                        "Edge": edge,
                    })

        # Blowout warnings
        seen_bw = list(dict.fromkeys(blowout_warnings))  # dedupe
        for bw in seen_bw[:10]:
            st.markdown(f'<div class="blowout-warn">{bw}</div>', unsafe_allow_html=True)

        if not edge_rows:
            st.info("No line data to display.")
        else:
            df_edges = pd.DataFrame(edge_rows)

            # Build HTML table with gold highlight for edges
            cols_e = ["Time", "Matchup", "Team", "Market", "HardRock", "Median", "Diff", "Edge"]
            headers_e = "".join(f"<th>{c}</th>" for c in cols_e)
            body_e = ""
            for _, row in df_edges.iterrows():
                edge_flag = row.get("Edge", False)
                hr_disp = f"{int(row['HardRock']):+d}" if row['HardRock'] is not None else "—"
                med_disp = f"{int(row['Median']):+d}" if row['Median'] is not None else "—"
                diff_disp = f"{row['Diff']:+.1f}" if row['Diff'] is not None else "—"
                edge_disp = '<span class="badge-gold">🏅 EDGE</span>' if edge_flag else '<span class="badge-gray">—</span>'
                row_style = "background:#1c1507;" if edge_flag else ""
                body_e += (
                    f'<tr style="{row_style}">'
                    f"<td>{row['Time']}</td>"
                    f"<td>{row['Matchup']}</td>"
                    f"<td><strong>{row['Team']}</strong></td>"
                    f"<td>{row['Market']}</td>"
                    f"<td>{hr_disp}</td>"
                    f"<td>{med_disp}</td>"
                    f"<td>{diff_disp}</td>"
                    f"<td>{edge_disp}</td>"
                    f"</tr>"
                )
            st.markdown(
                f'<div class="sticky-table-wrapper"><table><thead><tr>{headers_e}</tr></thead><tbody>{body_e}</tbody></table></div>',
                unsafe_allow_html=True,
            )

            # Gold edge alerts summary
            edge_events = df_edges[df_edges["Edge"] == True]
            if not edge_events.empty:
                st.markdown("---")
                st.markdown("### 🏅 Market Edge Alerts")
                for _, er in edge_events.iterrows():
                    st.markdown(
                        f'<div class="edge-alert">📌 <strong>{er["Team"]}</strong> ({er["Market"]}) — '
                        f'HardRock: <strong>{int(er["HardRock"]) if er["HardRock"] else "—":+}</strong> '
                        f'vs Median: <strong>{int(er["Median"]) if er["Median"] else "—":+}</strong> '
                        f'(Δ {er["Diff"]:+.1f})</div>',
                        unsafe_allow_html=True,
                    )

# ══════════════════════════════════════════════
# TAB 3: LIVE SCORES
# ══════════════════════════════════════════════
with tab3:
    st.markdown(f"### 📡 Live & Today's {sport} Scores (API-Sports)")
    with st.spinner("Fetching live scores..."):
        live_games = fetch_live_scores_apisports(sport)

    if not live_games:
        st.info("No live or today's games found. API-Sports key may be missing or no games scheduled.")
    else:
        for game in live_games[:20]:
            g_home = game.get("teams", {}).get("home", {})
            g_away = game.get("teams", {}).get("away", {})
            sc     = game.get("scores", {})
            status = game.get("status", {}).get("long", "Scheduled")

            home_name  = g_home.get("name", "Home")
            away_name  = g_away.get("name", "Away")
            home_score = sc.get("home", {}).get("total", "—") if isinstance(sc.get("home"), dict) else sc.get("home", "—")
            away_score = sc.get("away", {}).get("total", "—") if isinstance(sc.get("away"), dict) else sc.get("away", "—")

            col_a, col_s, col_b = st.columns([3, 1, 3])
            with col_a:
                st.markdown(f"**{away_name}**")
            with col_s:
                st.markdown(f"**{away_score} — {home_score}**")
            with col_b:
                st.markdown(f"**{home_name}**")
            st.caption(f"Status: {status}")
            st.markdown("---")

# ──────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; color:#374151; font-size:0.75rem; margin-top:2rem; padding: 1rem;
     border-top: 1px solid #1f2937; font-family:'Share Tech Mono', monospace;">
  HardRock Bet Tool · Built with TheSportsDB · The Odds API · API-Sports · Balldontlie<br>
  ⚠️ For informational & entertainment purposes only. Please gamble responsibly.
</div>
""", unsafe_allow_html=True)
