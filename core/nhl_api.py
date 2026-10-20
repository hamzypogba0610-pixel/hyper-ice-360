import requests

# Liste des 32 équipes de la NHL avec leur identifiant API
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
    """
    Va chercher les stats réelles de l'équipe sur l'API de la NHL.
    On utilise une API publique et gratuite.
    """
    try:
        # On appelle l'API des classements de la NHL
        url = "https://api-web.nhle.com/v1/standings/now"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # On cherche notre équipe dans la liste
        for team in data.get("standings", []):
            if team.get("teamAbbrev", {}).get("default") == team_code:
                # On calcule une approximation des buts attendus (xG) basée sur les buts marqués/encaissés
                # (Formule simplifiée pour le prototype)
                buts_marques = team.get("goalFor", 0)
                matchs_joues = team.get("gamesPlayed", 1)
                buts_encaisses = team.get("goalAgainst", 0)
                
                xg_moyen = buts_marques / matchs_joues if matchs_joues > 0 else 3.0
                xga_moyen = buts_encaisses / matchs_joues if matchs_joues > 0 else 3.0
                
                return {
                    "nom": team.get("teamName", {}).get("default", team_code),
                    "xg": round(xg_moyen, 2),
                    "xga": round(xga_moyen, 2),
                    "matchs": matchs_joues
                }
    except Exception as e:
        print(f"Erreur API : {e}")
        return None
    return None
