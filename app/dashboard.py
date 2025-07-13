
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from graphs.salary_vs_ws import salary_ws_graph
from graphs.ws_vs_usage import ws_usage_graph
from graphs.tov_vs_ast import tov_ast_graph

df = pd.read_csv("../data/merged.csv")
df = df.rename(columns={'2024-25': 'Salary'})
df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).astype(float)
df['MP'] = pd.to_numeric(df['MP'], errors='coerce')
df['G'] = pd.to_numeric(df['G'], errors='coerce')
df['USG%'] = pd.to_numeric(df['USG%'], errors='coerce')
df = df.dropna(subset=['Salary', 'MP', 'WS', 'G'])
df = df[(df['Salary'] > 0) & (df['MP'] > 0) & (df['G'] > 0)]
df['Total_MP'] = df['MP'] * df['G']

df['Value_Index'] = df['WS'] / df['Salary']
df['Usage_Index'] = df['WS'] / df['USG%']
df['Possession_Control'] = df['AST'] / df['TOV']

position = st.sidebar.selectbox("Position", options=["All"] + sorted(df["Pos"].dropna().unique()))
min_minutes = st.sidebar.slider("Minimum Minutes Played", min_value=0, max_value=3000, value=500, step=100)
unique_players = sorted(df["Player"].dropna().unique())
selected_player = st.sidebar.selectbox("Search and Select Player", options=["None"] + unique_players)
graph_option = st.sidebar.selectbox("Select Graph", options=[
    "Salary vs Win Shares",
    "Win Shares vs Usage Rate",
    "Turnovers vs Assists"
])

filtered_df = df[df["Total_MP"] >= min_minutes]
if position != "All":
    filtered_df = filtered_df[filtered_df["Pos"].str.strip() == position]

highlight_df = pd.DataFrame()
if selected_player and selected_player != "None":
    highlight_df = filtered_df[filtered_df["Player"].str.contains(selected_player, case=False, na=False)]

st.title("NBA Player Value Dashboard")
st.text(f"📊 Total players displayed: {len(filtered_df)}")

if not highlight_df.empty:
    selected_player = highlight_df.iloc[0]["Player"]
    found = players.find_players_by_full_name(selected_player)
    if found:
        player_id = found[0]["id"]
        try:
            career = playercareerstats.PlayerCareerStats(player_id=player_id)
            df_stats = career.get_data_frames()[0]

            total_gp = df_stats["GP"].sum()
            total_min = df_stats["MIN"].sum()
            total_pts = df_stats["PTS"].sum()
            total_reb = df_stats["REB"].sum()
            total_ast = df_stats["AST"].sum()
            total_stl = df_stats["STL"].sum()
            total_blk = df_stats["BLK"].sum()

            mpg = total_min / total_gp
            ppg = total_pts / total_gp
            rpg = total_reb / total_gp
            apg = total_ast / total_gp
            spg = total_stl / total_gp
            bpg = total_blk / total_gp

            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png", width=220)
            with col2:
                st.markdown(f"**{selected_player} - Career Averages**")
                st.markdown(f"""
                - **Games Played (GP):** {int(total_gp)}
                - **Minutes per Game (MPG):** {mpg:.1f}
                - **Points per Game (PPG):** {ppg:.1f}
                - **Rebounds per Game (RPG):** {rpg:.1f}
                - **Assists per Game (APG):** {apg:.1f}
                - **Steals per Game (SPG):** {spg:.1f}
                - **Blocks per Game (BPG):** {bpg:.1f}
                """)
        except Exception as e:
            st.warning(f"Stats not available for {selected_player}. Error: {str(e)}")
    else:
        st.info("Headshot not available.")

if graph_option == "Salary vs Win Shares":
    fig = salary_ws_graph(filtered_df, df, highlight_df)
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Top 10 Value Players (WS / Salary)")
    top_value = filtered_df.sort_values("Value_Index", ascending=False).head(10)
    st.dataframe(top_value[["Player", "Team", "Pos", "WS", "Salary", "Value_Index", "Total_MP"]])

elif graph_option == "Win Shares vs Usage Rate":
    fig = ws_usage_graph(filtered_df, df, highlight_df)
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Top 10 by Usage-WS Ratio")
    top_value = filtered_df.sort_values("Usage_Index", ascending=False).head(10)
    st.dataframe(top_value[["Player", "Team", "Pos", "WS", "USG%", "Usage_Index", "Total_MP"]])

elif graph_option == "Turnovers vs Assists":
    fig = tov_ast_graph(filtered_df, df, highlight_df)
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Top 10 by AST/TOV Ratio")
    top_value = filtered_df.sort_values("Possession_Control", ascending=False).head(10)
    st.dataframe(top_value[["Player", "Team", "Pos", "AST", "TOV", "Possession_Control", "Total_MP"]])