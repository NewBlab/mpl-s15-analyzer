# MPL S15 Analyzer App: Champion, All-Star Team, MVP
import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data

def load_data():
    file = st.file_uploader("Upload the MPL S15 Excel file", type=['xlsx'])
    if file:
        df = pd.read_excel(file)
        df.columns = df.columns.str.strip()
        return df
    return None

data = load_data()

if data is not None:
    st.title("🏆 MPL S15 Data-Driven Awards App")

    # =========================
    # 1. Predict Champion
    # =========================
    st.header("🥇 Predicted Champion (Regular Season)")
    team_df = data[data['Team'].notna()].copy()
    team_df = team_df[team_df['Rank '].notna()].copy()
    team_df.columns = team_df.columns.str.strip()
    top6 = team_df.nsmallest(6, 'Rank')
    champion_row = top6.loc[top6['Rank'] == 1]
    if not champion_row.empty:
        st.success(f"🏆 Predicted Champion: **{champion_row.iloc[0]['Team']}**")

    st.dataframe(top6[['Team', 'Rank', 'Match point', 'Net Game Win', 'Kills', 'Deaths', 'Assists']])

    # =========================
    # 2. All-Star Teams
    # =========================
    st.header("🌟 All-Star Teams (1st and 2nd)")
    player_df = data[data['Player'].notna()].copy()
    player_df.columns = player_df.columns.str.strip()

    roles = ['EXP', 'Jungle', 'Mid', 'Gold', 'Roam']
    all_star = []

    for role in roles:
        role_players = player_df[player_df['Role'] == role].copy()
        role_players = role_players.dropna(subset=['KDA Ratio'])
        role_players['KDA Ratio'] = pd.to_numeric(role_players['KDA Ratio'], errors='coerce')
        top2 = role_players.sort_values(by='KDA Ratio', ascending=False).head(2)
        all_star.append(top2)

    first_team = pd.concat([group.iloc[[0]] for group in all_star])
    second_team = pd.concat([group.iloc[[1]] for group in all_star])

    st.subheader("⭐ 1st All-Star Team")
    st.dataframe(first_team[['Player', 'Team.1', 'Role', 'KDA Ratio']])

    st.subheader("⭐ 2nd All-Star Team")
    st.dataframe(second_team[['Player', 'Team.1', 'Role', 'KDA Ratio']])

    # =========================
    # 3. MVP Prediction
    # =========================
    st.header("🏅 Regular Season MVP Prediction")
    # Define MVP score as weighted: KDA * Kill Participation * Games Played approximation
    player_df = player_df.copy()
    player_df['KDA Ratio'] = pd.to_numeric(player_df['KDA Ratio'], errors='coerce')
    player_df['Kill Participation'] = pd.to_numeric(player_df['Kill Participation'], errors='coerce')
    player_df['Total Kills'] = pd.to_numeric(player_df['Total Kills'], errors='coerce')

    player_df['MVP Score'] = player_df['KDA Ratio'] * player_df['Kill Participation'] * player_df['Total Kills']
    mvp = player_df.sort_values(by='MVP Score', ascending=False).head(1)

    if not mvp.empty:
        best = mvp.iloc[0]
        st.success(f"🏅 Predicted MVP: **{best['Player']}** from **{best['Team.1']}**")

    st.dataframe(mvp[['Player', 'Team.1', 'Role', 'KDA Ratio', 'Kill Participation', 'Total Kills', 'MVP Score']])
else:
    st.info("Please upload the MPL S15 Excel file to continue.")
