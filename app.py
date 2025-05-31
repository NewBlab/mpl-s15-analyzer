# MPL S15 Analyzer App: Champion, All-Star Team, MVP
import streamlit as st
import pandas as pd
import numpy as np

st.title("🏆 MPL S15 Data-Driven Awards App")

# Upload outside cached function
uploaded_file = st.file_uploader("Upload the MPL S15 Excel file", type=['xlsx'])

@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    return df

if uploaded_file:
    data = load_data(uploaded_file)

    # =========================
    # 1. Predict Champion
    # =========================
    st.header("🥇 Predicted Champion (Regular Season)")
    team_df = data[data['Team'].notna()].copy()
    team_df = team_df[team_df['Rank'].notna()].copy()
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
    player_df['Role'] = player_df['Role'].str.upper().str.strip()  # Normalize role names

    roles = ['EXP', 'JUNGLE', 'MID', 'GOLD', 'ROAM']
    all_star = {'first': [], 'second': []}

    # Use calculated KDA: (Kills + Assists) / max(Deaths, 1)
    player_df['Total Kills'] = pd.to_numeric(player_df['Total Kills'], errors='coerce')
    player_df['Total Assists'] = pd.to_numeric(player_df['Total Assists'], errors='coerce')
    player_df['Total Deaths'] = pd.to_numeric(player_df['Total Deaths'], errors='coerce')
    player_df['Calculated KDA'] = (player_df['Total Kills'] + player_df['Total Assists']) / player_df['Total Deaths'].replace(0, 1)

    for role in roles:
        role_players = player_df[player_df['Role'] == role].copy()
        role_players = role_players.dropna(subset=['Total Kills', 'Total Assists', 'Total Deaths'])

        # Prioritize first by total contributions, then KDA
        role_players = role_players.sort_values(
            by=['Total Kills', 'Total Assists', 'Total Deaths', 'Calculated KDA'],
            ascending=[False, False, True, False]
        )
        top2 = role_players.head(2)

        if len(top2) > 0:
            all_star['first'].append(top2.iloc[[0]])
        if len(top2) > 1:
            all_star['second'].append(top2.iloc[[1]])

    if all_star['first']:
        first_team = pd.concat(all_star['first'])
        st.subheader("⭐ 1st All-Star Team")
        st.dataframe(first_team[['Player', 'Team.1', 'Role', 'Total Kills', 'Total Assists', 'Total Deaths', 'Calculated KDA']])
    else:
        st.warning("Not enough data for 1st All-Star Team")

    if all_star['second']:
        second_team = pd.concat(all_star['second'])
        st.subheader("⭐ 2nd All-Star Team")
        st.dataframe(second_team[['Player', 'Team.1', 'Role', 'Total Kills', 'Total Assists', 'Total Deaths', 'Calculated KDA']])
    else:
        st.warning("Not enough data for 2nd All-Star Team")

    # =========================
    # 3. MVP Prediction
    # =========================
    st.header("🏅 Regular Season MVP Prediction")
    # Define MVP score as weighted: KDA * Kill Participation * Total Kills
    player_df['Kill Participation'] = pd.to_numeric(player_df['Kill Participation'], errors='coerce')
    player_df['MVP Score'] = player_df['Calculated KDA'] * player_df['Kill Participation'] * player_df['Total Kills']
    mvp = player_df.sort_values(by='MVP Score', ascending=False).head(1)

    if not mvp.empty:
        best = mvp.iloc[0]
        st.success(f"🏅 Predicted MVP: **{best['Player']}** from **{best['Team.1']}**")

    st.dataframe(mvp[['Player', 'Team.1', 'Role', 'Calculated KDA', 'Kill Participation', 'Total Kills', 'MVP Score']])
else:
    st.info("Please upload the MPL S15 Excel file to continue.")
