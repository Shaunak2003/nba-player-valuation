import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

st.set_page_config(page_title="Advanced Stats", page_icon="📈")

# Title
st.title("📈 Advanced Stats Over Time")

# Session-state backed search bar
@st.cache_data
def get_unique_players():
    df = pd.read_csv("../data/merged.csv")
    return sorted(df["Player"].dropna().unique())

unique_players = get_unique_players()

if "selected_player" not in st.session_state:
    st.session_state["selected_player"] = "None"

selected_player = st.selectbox(
    "🔍 Search for a Player",
    options=["None"] + unique_players,
    index=unique_players.index(st.session_state["selected_player"]) if st.session_state["selected_player"] in unique_players else 0,
)

# Sync to session state
st.session_state["selected_player"] = selected_player

# Skip if "None"
if selected_player == "None":
    st.info("Please select a player to view advanced stats.")
    st.stop()

# Lookup player ID
found = players.find_players_by_full_name(selected_player)
if not found:
    st.warning("Player not found.")
    st.stop()

player_id = found[0]["id"]

# Get career stats
try:
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df_stats = career.get_data_frames()[0]
except Exception as e:
    st.error(f"Could not fetch stats: {e}")
    st.stop()

# Format season labels to full years
def format_season_label(season_str):
    start, end = season_str.split("-")
    start_year = int("20" + start) if int(start) <= 25 else int("19" + start)
    end_year = int("20" + end) if int(end) <= 25 else int("19" + end)
    return f"{start_year}-{end_year}"

df_stats["SEASON"] = df_stats["SEASON_ID"].apply(lambda x: format_season_label(x.split(" ")[1]))

# Toggle between per-game and total stats
v
