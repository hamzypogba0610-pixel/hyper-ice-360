import streamlit as st
from core.math_engine import calculate_all_markets, calculate_clv
from core.nhl_api import get_all_teams_stats
from core.odds_api import get_nhl_odds

def scan_matches(games, min_proba, markets_to_check):
    teams_stats = get_all_teams_stats()
    odds_data = get_nhl_odds()
    
    if not teams_stats:
        return []

    # Mémoire des cotes d'ouverture pour calculer le CLV
    if 'open_odds' not in st.session_state:
        st.session_state.open_odds = {}

    pepites = []

    for game in games:
        h_code = game.get("home_code")
        a_code = game.get("away_code")
        
        if h_code not in teams_stats or a_code not in teams_stats:
            continue
            
        st_h = teams_stats[h_code]
        st_a = teams_stats[a_code]
        
        # Formule magique (Attaque + Défense adverse) avec avantage domicile
        lam_h = ((st_h['attaque'] + st_a['defense']) / 2) * 1.05
        lam_a = ((st_a['attaque'] + st_h['defense']) / 2) * 0.95
        
        probs = calculate_all_markets(lam_h, lam_a)
        
        match_name = f"{st_h['nom']} vs {st_a['nom']}"
        
        book_cotes = odds_data.get(match_name, {})
        cote_1 = book_cotes.get("home", 0.0)
        cote_2 = book_cotes.get("away", 0.0)
        
        # Fonction utilitaire pour ajouter une pépite
        def add_pepite(marche, proba, cote):
            if cote > 0:
                # Gestion de la cote d'ouverture (Stockage au premier scan)
                cle_cote = f"{match_name}_{marche}"
                if cle_cote not in st.session_state.open_odds:
                    st.session_state.open_odds[cle_cote] = cote
                
                cote_ouv = st.session_state.open_odds[cle_cote]
                clv = calculate_clv(cote_ouv, cote)
                ev = (proba * cote) - 1
            else:
                cote_ouv = 0.0
                clv = 0.0
                ev = 0.0

            pepites.append({
                "match": match_name, 
                "marche": marche, 
                "proba": proba, 
                "cote": cote, 
                "cote_ouv": cote_ouv,
                "clv": clv,
                "ev": ev, 
                "lam_h": lam_h, 
                "lam_a": lam_a, 
                "h_code": h_code, 
                "a_code": a_code
            })

        # --- 1X2 ---
        if "1X2" in markets_to_check:
            if probs["1X2"][0] >= min_proba:
                add_pepite(f"Victoire {st_h['nom']}", probs["1X2"][0], cote_1)
            if probs["1X2"][2] >= min_proba:
                add_pepite(f"Victoire {st_a['nom']}", probs["1X2"][2], cote_2)
                
        # --- Vainqueur Final ---
        if "Final" in markets_to_check:
            if probs["final_1X2"][0] >= min_proba:
                add_pepite(f"Vainqueur Final {st_h['nom']}", probs["final_1X2"][0], cote_1)
            if probs["final_1X2"][1] >= min_proba:
                add_pepite(f"Vainqueur Final {st_a['nom']}", probs["final_1X2"][1], cote_2)

        # --- Over & BTTS ---
        if "Over" in markets_to_check and probs["over_5_5"] >= min_proba:
            add_pepite("Plus de 5.5 buts", probs["over_5_5"], 0.0)
        if "BTTS" in markets_to_check and probs["btts_yes"] >= min_proba:
            add_pepite("Les 2 marquent (Oui)", probs["btts_yes"], 0.0)

    # Tri par EV puis par CLV
    pepites = sorted(pepites, key=lambda x: (x["ev"], x["clv"], x["proba"]), reverse=True)
    return pepites
