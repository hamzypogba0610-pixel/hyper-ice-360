import os
import requests
import streamlit as st

@st.cache_data(ttl=3600)  # On met en cache 1 heure pour économiser les crédits gratuits
def get_nhl_odds():
    """Va chercher les cotes réelles de la NHL sur The Odds API."""
    api_key = os.environ.get("ODDS_API_KEY")
    if not api_key:
        return {}

    # On cherche les cotes h2h (1X2) pour la NHL en Europe
    url = f"https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?apiKey={api_key}&regions=eu&markets=h2h&oddsFormat=decimal"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Erreur API Odds : {response.status_code}")
            return {}
            
        data = response.json()
        odds_dict = {}
        
        for game in data:
            home_team = game.get("home_team")
            away_team = game.get("away_team")
            match_key = f"{home_team} vs {away_team}"
            
            # On prend le premier bookmaker dispo pour simplifier
            bookmakers = game.get("bookmakers", [])
            if bookmakers:
                outcomes = bookmakers[0].get("markets", [])[0].get("outcomes", [])
                
                home_odds = 0.0
                away_odds = 0.0
                draw_odds = 0.0
                
                for o in outcomes:
                    if o["name"] == home_team: home_odds = o["price"]
                    elif o["name"] == away_team: away_odds = o["price"]
                    elif o["name"] == "Draw": draw_odds = o["price"]
                
                odds_dict[match_key] = {
                    "home": home_odds,
                    "away": away_odds,
                    "draw": draw_odds
                }
        return odds_dict
    except Exception as e:
        print(f"Erreur réseau Odds : {e}")
        return {}
