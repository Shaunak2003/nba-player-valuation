import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

df = pd.read_csv("../data/merged.csv")
df = df.rename(columns={'2024-25': 'Salary'})

df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).astype(float)
df['MP'] = pd.to_numeric(df['MP'], errors='coerce')
df['G'] = pd.to_numeric(df['G'], errors='coerce')

df = df.dropna(subset=['Salary', 'MP', 'WS'])
df = df[(df['Salary'] > 0) & (df['MP'] > 0) & (df['G'] > 0)]

df['Total_MP'] = df['MP'] * df['G']
df['Value_Index'] = df['WS'] / df['Salary']

st.sidebar.header("Filters")
position = st.sidebar.selectbox("Position", options=["All"] + sorted(df["Pos"].dropna().unique()))
min_minutes = st.sidebar.slider("Minimum Minutes Played", min_value=0, max_value=3000, value=500, step=100)

filtered_df = df[df["Total_MP"] >= min_minutes]
if position != "All":
    filtered_df = filtered_df[filtered_df["Pos"].str.strip() == position]

st.text(f"📊 Total players displayed: {len(filtered_df)}")
st.title("NBA Player Value Dashboard")
st.markdown("2024-25 salaries vs performance metrics")

st.subheader("Salary vs Win Shares (Click Points for Player Info)")
fig = px.scatter(
    filtered_df,
    x="WS",
    y="Salary",
    hover_name="Player",
    hover_data=["Team", "Pos", "Total_MP", "Value_Index"],
    title="Win Shares vs Salary (Interactive)"
)
fig.update_traces(marker=dict(size=10, opacity=0.7))
fig.update_layout(height=600)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 10 Value Players (WS / Salary)")
top_value = filtered_df.sort_values("Value_Index", ascending=False).head(10)
st.dataframe(top_value[["Player", "Team", "Pos", "WS", "Salary", "Value_Index", "Total_MP"]])