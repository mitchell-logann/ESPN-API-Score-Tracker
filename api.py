import requests

BASE = "https://site.api.espn.com/apis/site/v2/sports/"

def getScoreboard(sport, league):
    url = f"{BASE}{sport}/{league}/scoreboard"
    response = requests.get(url)
    return requests.get(url).json()

def getTeamSchedule(sport, league, team_id):
    url = f"{BASE}{sport}/{league}/teams/{team_id}/schedule"
    return requests.get(url).json()

def getTeamInfo(sport, league, team_id):
    url = f"{BASE}{sport}/{league}/teams/{team_id}"
    return requests.get(url).json()