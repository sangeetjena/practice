"""
find summary board of icci world cup match:
input:
team1 | team2 | winner
IND | SL | IND
SL | AUS | AUS
SA | ENG | ENG
ENG | NZ | NZ
AUS | IND | IND


"""
import pandas as pd

match = pd.DataFrame({"team1": ["IND", "SL", "SA", "ENG", "AUS"],
                      "team2": ["SL", "AUS", "ENG", "NZ", "IND"],
                      "winner": ["IND", "AUS", "ENG", "NZ", "IND"]})
print(match)
total_team = pd.DataFrame(pd.concat([match["team1"], match["team2"]]))
total_team.columns=["teams"]
print(total_team)
total_played = total_team.groupby("teams").aggregate({"teams": "count"}).reset_index()
print(total_played)