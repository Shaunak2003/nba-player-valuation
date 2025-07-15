import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

st.set_page_config(page_title="Stats", page_icon="📈")
st.title("📈 Stats Over Time")

@st.cache_data
def get_unique_players():
    df = pd.read_csv("../data/merged.csv")
    return sorted(df["Player"].dropna().unique())

unique_players = get_unique_players()
initial_selection = st.session_state.get("selected_player_name", "None")

selected_player = st.selectbox(
    "🔍 Search for a Player",
    options=["None"] + unique_players,
    index=unique_players.index(initial_selection) + 1 if initial_selection in unique_players else 0,
)

st.session_state["selected_player_name"] = selected_player

if selected_player == "None":
    st.info("Please select a player to view advanced stats.")
    st.stop()

found = players.find_players_by_full_name(selected_player)
if not found:
    st.warning("Player not found.")
    st.stop()

player_id = found[0]["id"]

try:
    career = playercareerstats.PlayerCareerStats(player_id=player_id)
    df_stats = career.get_data_frames()[0]
except Exception as e:
    st.error(f"Could not fetch stats: {e}")
    st.stop()


#print(df_stats)
# df_stats = df_stats.sort_values("TEAM_ABBREVIATION")
df_stats = df_stats.drop_duplicates(subset="SEASON_ID", keep="last")
#print(df_stats)

# df_stats["Season"] = df_stats["SEASON_ID"].str.replace("NBA", "").str.strip()

for stat in ["PTS", "REB", "AST", "STL", "BLK", "MIN"]:
    df_stats[f"{stat}_PG"] = df_stats[stat] / df_stats["GP"]

toggle_pg = st.radio("Display Mode", ["Season Totals", "Per-Game Averages"], horizontal=True)
suffix = "" if toggle_pg == "Season Totals" else "_PG"
title_suffix = "Total" if suffix == "" else "Per Game"

metrics = {
    "PTS": "Points",
    "REB": "Rebounds",
    "AST": "Assists",
    "STL": "Steals",
    "BLK": "Blocks",
    "MIN": "Minutes Played"
}

for stat, label in metrics.items():
    col_name = stat + suffix
    fig = px.line(
        df_stats,
        x="SEASON_ID",
        y=col_name,
        markers=True,
        title=f"{label} ({title_suffix}) per Season for {selected_player}"
    )
    fig.update_layout(xaxis_title="SEASON", yaxis_title=label)
    st.plotly_chart(fig, use_container_width=True)
