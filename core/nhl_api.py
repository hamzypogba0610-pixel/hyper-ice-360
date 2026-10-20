import requests
import streamlit as st
import datetime

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

@st.cache_data(ttl=3600)
def get_team_last_games(team_code, limit=5):
    """Récupère les 5 derniers résultats de l'équipe (V = Victoire, D = Défaite)."""
    try:
        url = f"https://api-web.nhle.com/v1/club-schedule-season/{team_code}/now"
        response = requests.get(url, timeout=10)
        data = response.json()
        finished = [g for g in data.get("games", []) if g.get("gameState") == "OFF"]
        results = []
        for g in finished[-limit:]:
            is_home = g.get("homeTeam", {}).get("abbrev") == team_code
            h_score = g.get("homeTeam", {}).get("score", 0)
            a_score = g.get("awayTeam", {}).get("score", 0)
            if is_home:
                results.append("V" if h_score > a_score else "D")
            else:
                results.append("V" if a_score > h_score else "D")
        return results
    except:
        return []

@st.cache_data(ttl=3600)
def get_all_teams_stats():
    """
    Récupère les stats et applique le Strength of Schedule (SOS).
    Les stats des équipes qui gagnent sont validées, les stats des équipes faibles sont lissées vers la moyenne.
    """
    try:
        url = "https://api-web.nhle.com/v1/standings/now"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # PASSE 1 : On calcule un "Rating" de base pour chaque équipe (basé sur le % de victoires)
        ratings_bruts = {}
        stats_brutes = {}
        
        for team in data.get("standings", []):
            code = team.get("teamAbbrev", {}).get("default")
            if code in NHL_TEAMS.values():
                matchs = team.get("gamesPlayed", 1)
                buts_pour = team.get("goalFor", 0)
                buts_contre = team.get("goalAgainst", 0)
                victoires = team.get("wins", 0)
                
                win_pct = victoires / matchs if matchs > 0 else 0.5
                ratings_bruts[code] = win_pct
                
                stats_brutes[code] = {
                    "nom": team.get("teamName", {}).get("default", code),
                    "attaque_brute": buts_pour / matchs if matchs > 0 else 3.0,
                    "defense_brute": buts_contre / matchs if matchs > 0 else 3.0,
                    "logo": f"https://assets.nhle.com/logos/nhl/svg/{code}_light.svg"
                }

        # PASSE 2 : Ajustement SOS (Strength of Schedule)
        teams_stats = {}
        moyenne_ligue_att = sum(s["attaque_brute"] for s in stats_brutes.values()) / len(stats_brutes)
        moyenne_ligue_def = sum(s["defense_brute"] for s in stats_brutes.values()) / len(stats_brutes)

        for code, stats in stats_brutes.items():
            rating = ratings_bruts[code]
            
            # Formule : Un poids fort pour les bonnes équipes, lissage vers la moyenne pour les faibles
            poids_equipe = 0.6 + (rating * 0.4) # Entre 0.6 et 1.0
            
            att_ajustee = (stats["attaque_brute"] * poids_equipe) + (moyenne_ligue_att * (1 - poids_equipe))
            def_ajustee = (stats["defense_brute"] * poids_equipe) + (moyenne_ligue_def * (1 - poids_equipe))
            
            # On récupère le momentum (forme) pour l'ajuster
            forme = get_team_last_games(code)
            momentum = 0
            if len(forme) > 0:
                momentum = (forme.count("V") - forme.count("D")) / len(forme)
            
            # Ajustement final avec le momentum (+/- 5%)
            att_finale = att_ajustee * (1 + (momentum * 0.05))
            def_finale = def_ajustee * (1 - (momentum * 0.05))
            
            teams_stats[code] = {
                "nom": stats["nom"],
                "attaque": att_finale,
                "defense": def_finale,
                "rating": rating,
                "logo": stats["logo"]
            }
            
        return teams_stats
    except Exception as e:
        print(f"Erreur API Stats : {e}")
        return {}

@st.cache_data(ttl=1800)
def get_upcoming_games(days_ahead=3):
    games = []
    today = datetime.date.today()
    for i in range(days_ahead + 1):
        date_str = (today + datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        try:
            url = f"https://api-web.nhle.com/v1/schedule/{date_str}"
            response = requests.get(url, timeout=10)
            data = response.json()
            for day in data.get("gameWeek", []):
                if day.get("date") == date_str:
                    for game in day.get("games", []):
                        if game.get("gameState") in ["FUT", "PRE"]:
                            games.append({
                                "date": date_str,
                                "home_code": game.get("homeTeam", {}).get("abbrev"),
                                "away_code": game.get("awayTeam", {}).get("abbrev"),
                            })
        except Exception as e:
            print(f"Erreur calendrier {date_str}: {e}")
    return games
