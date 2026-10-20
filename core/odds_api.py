import os
import requests
import streamlit as st

@st.cache_data(ttl=1800)  # Cache de 30 minutes pour actualiser plus souvent
def get_nhl_odds():
    """Va chercher les cotes réelles de la NHL sur The Odds API."""
    api_key = os.environ.get("ODDS_API_KEY")
    if not api_key:
        return {}

    url = f"https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/?apiKey={api_key}&regions=eu&markets=h2h&oddsFormat=decimal"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {}
            
        data = response.json()
        odds_dict = {}
        
        for game in data:
            home_team = game.get("home_team")
            away_team = game.get("away_team")
            match_key = f"{home_team} vs {away_team}"
            
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
        return {}
