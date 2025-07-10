import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../data/merged.csv")
df = df.rename(columns={'2024-25': 'Salary'})

df['Salary'] = df['Salary'].replace(r'[\$,]', '', regex=True).astype(float)


df['MP'] = pd.to_numeric(df['MP'], errors='coerce')

df = df.dropna(subset=['Salary', 'MP', 'WS'])

df = df[(df['Salary'] > 0) & (df['MP'] > 0)]

df['Value_Index'] = df['WS'] / df['Salary']

st.sidebar.header("Filters")
position = st.sidebar.selectbox("Position", options=["All"] + sorted(df["Pos"].dropna().unique()))
min_minutes = st.sidebar.slider("Minimum Minutes Played", min_value=0, max_value=3000, value=500, step=100)

filtered_df = df[df["MP"] * df["G"] >= min_minutes]
if position != "All":
    filtered_df = filtered_df[filtered_df["Pos"].str.strip() == position]

st.title("NBA Player Value Dashboard")
st.markdown("2024-25 salaries vs performance metrics")

st.subheader("Salary vs Win Shares")
fig, ax = plt.subplots()
ax.scatter(filtered_df["WS"], filtered_df["Salary"], alpha=0.7)
ax.set_xlabel("Win Shares")
ax.set_ylabel("Salary ($M)")
ax.set_title("WS vs Salary")
st.pyplot(fig)

st.subheader("Top 10 Value Players (WS / Salary)")
top_value = filtered_df.sort_values("Value_Index", ascending=False).head(10)
st.dataframe(top_value[["Player", "Team", "Pos", "WS", "Salary", "Value_Index"]])
