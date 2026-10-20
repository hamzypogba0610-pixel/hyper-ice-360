import requests

NHL_TEAMS = {
    "Anaheim Ducks": "ANA", "Boston Bruins": "BOS", "Buffalo Sabres": "BUF",
    "Calgary Flames": "CGY", "Carolina Hurricanes": "CAR", "Chicago Blackhawks": "CHI",
    "Colorado Avalanche": "COL", "Columbus Blue Jackets": "CBJ", "Dallas Stars": "DAL",
    "Detroit Red Wings": "DET", "Edmonton Oilers": "EDM", "Florida Panthers": "FLA",
    "Los Angeles Kings": "LAK", "Minnesota Wild": "MIN", "Montreal Canadiens": "MTL",
    "Nashville Predators": "NSH", "New Jersey Devils": "NJD", "New York Islanders": "NYI",
    "New York Rangers": "NYR", "Ottawa Senators": "OTT", "Philadelphia Flyers": "PHI",
    "Pittsburgh Penguins": "PIT", "San Jose Sharks": "SJS", "Seattle Kraken": "SEA",
    "St. Louis Blues": "STL", "Tampa Bay Lightning": "TBL", "Toronto Maple Leafs": "TOR",
    "Utah Hockey Club": "UTA", "Vancouver Canucks": "VAN", "Vegas Golden Knights": "VGK",
    "Washington Capitals": "WSH", "Winnipeg Jets": "WPG"
}

def get_team_real_stats(team_code):
    try:
        url = "https://api-web.nhle.com/v1/standings/now"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        for team in data.get("standings", []):
            if team.get("teamAbbrev", {}).get("default") == team_code:
                matchs_joues = team.get("gamesPlayed", 1)
                buts_marques = team.get("goalFor", 0)
                buts_encaisses = team.get("goalAgainst", 0)
                
                attaque = buts_marques / matchs_joues if matchs_joues > 0 else 3.0
                defense = buts_encaisses / matchs_joues if matchs_joues > 0 else 3.0
                
                return {
                    "nom": team.get("teamName", {}).get("default", team_code),
                    "attaque": round(attaque, 2),
                    "defense": round(defense, 2),
                    "matchs": matchs_joues,
                    "logo": f"https://assets.nhle.com/logos/nhl/svg/{team_code}_light.svg"
                }
    except Exception as e:
        print(f"Erreur API Stats : {e}")
        return None
    return None

def get_team_last_games(team_code, limit=5):
    """Récupère les 5 derniers résultats de l'équipe (V = Victoire, D = Défaite)."""
    try:
        url = f"https://api-web.nhle.com/v1/club-schedule-season/{team_code}/now"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        games = data.get("games", [])
        # On filtre les matchs terminés
        finished_games = [g for g in games if g.get("gameState") == "OFF"]
        
        # On prend les 5 derniers
        last_5 = finished_games[-limit:]
        results = []
        
        for g in last_5:
            home_team = g.get("homeTeam", {}).get("abbrev")
            away_team = g.get("awayTeam", {}).get("abbrev")
            home_score = g.get("homeTeam", {}).get("score", 0)
            away_score = g.get("awayTeam", {}).get("score", 0)
            
            if home_team == team_code:
                results.append("V" if home_score > away_score else "D")
            else:
                results.append("V" if away_score > home_score else "D")
                
        return results
    except Exception as e:
        print(f"Erreur API Forme : {e}")
        return []
