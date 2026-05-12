import pandas as pd

def get_all_teams(df):
    teams = sorted(df["batting_team"].dropna().unique().tolist())
    return teams

def get_all_players(df):
    players = sorted(df["batter"].dropna().unique().tolist())
    return players

def get_all_seasons(df):
    seasons = sorted(df["season"].dropna().unique().tolist(), reverse=True)
    return seasons

def top_run_scorers(df, top_n=10):
    runs = df.groupby("batter")["runs_batter"].sum().reset_index()
    runs.columns = ["player", "total_runs"]
    runs = runs.sort_values("total_runs", ascending=False).head(top_n)
    return runs

def top_wicket_takers(df, top_n=10):
    wickets_df = df[df["wicket_kind"].notna() & (df["wicket_kind"] != "run out")]
    wickets = wickets_df.groupby("bowler").size().reset_index(name="wickets")
    wickets = wickets.sort_values("wickets", ascending=False).head(top_n)
    return wickets

def player_batting_stats(df, player_name):
    player_df = df[df["batter"] == player_name]
    total_runs = player_df["runs_batter"].sum()
    matches = player_df["match_id"].nunique()
    fours = player_df[player_df["runs_batter"] == 4].shape[0]
    sixes = player_df[player_df["runs_batter"] == 6].shape[0]
    avg = round(total_runs / matches, 2) if matches > 0 else 0
    return {
        "Total Runs": total_runs,
        "Matches": matches,
        "Average": avg,
        "Fours": fours,
        "Sixes": sixes
    }

def head_to_head(df, team1, team2):
    h2h = df[
        ((df["batting_team"] == team1) | (df["batting_team"] == team2)) &
        ((df["bowling_team"] == team1) | (df["bowling_team"] == team2))
    ]
    matches = h2h.drop_duplicates(subset=["match_id"])[["match_id", "match_won_by"]]
    results = matches["match_won_by"].value_counts().reset_index()
    results.columns = ["team", "wins"]
    return results