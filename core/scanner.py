from core.math_engine import calculate_all_markets
from core.nhl_api import get_all_teams_stats
from core.odds_api import get_nhl_odds

def scan_matches(games, min_proba, markets_to_check):
    teams_stats = get_all_teams_stats()
    odds_data = get_nhl_odds() # On récupère les cotes réelles
    
    if not teams_stats:
        return []

    pepites = []

    for game in games:
        h_code = game.get("home_code")
        a_code = game.get("away_code")
        
        if h_code not in teams_stats or a_code not in teams_stats:
            continue
            
        st_h = teams_stats[h_code]
        st_a = teams_stats[a_code]
        
        # Formule magique
        lam_h = ((st_h['attaque'] + st_a['defense']) / 2) * 1.05
        lam_a = ((st_a['attaque'] + st_h['defense']) / 2) * 0.95
        
        probs = calculate_all_markets(lam_h, lam_a)
        
        match_name = f"{st_h['nom']} vs {st_a['nom']}"
        
        # On regarde si on a les cotes pour ce match précis
        book_cotes = odds_data.get(match_name, {})
        cote_1 = book_cotes.get("home", 0.0)
        cote_2 = book_cotes.get("away", 0.0)
        
        # --- 1X2 ---
        if "1X2" in markets_to_check:
            if probs["1X2"][0] >= min_proba:
                ev = (probs["1X2"][0] * cote_1) - 1 if cote_1 > 0 else 0
                pepites.append({"match": match_name, "marche": f"Victoire {st_h['nom']}", "proba": probs["1X2"][0], "cote": cote_1, "ev": ev, "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})
            if probs["1X2"][2] >= min_proba:
                ev = (probs["1X2"][2] * cote_2) - 1 if cote_2 > 0 else 0
                pepites.append({"match": match_name, "marche": f"Victoire {st_a['nom']}", "proba": probs["1X2"][2], "cote": cote_2, "ev": ev, "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})
                
        # --- Vainqueur Final ---
        if "Final" in markets_to_check:
            if probs["final_1X2"][0] >= min_proba:
                ev = (probs["final_1X2"][0] * cote_1) - 1 if cote_1 > 0 else 0
                pepites.append({"match": match_name, "marche": f"Vainqueur Final {st_h['nom']}", "proba": probs["final_1X2"][0], "cote": cote_1, "ev": ev, "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})
            if probs["final_1X2"][1] >= min_proba:
                ev = (probs["final_1X2"][1] * cote_2) - 1 if cote_2 > 0 else 0
                pepites.append({"match": match_name, "marche": f"Vainqueur Final {st_a['nom']}", "proba": probs["final_1X2"][1], "cote": cote_2, "ev": ev, "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})

        # --- Over ---
        if "Over" in markets_to_check and probs["over_5_5"] >= min_proba:
            # L'API gère parfois mal le Over/Under, on met 0.0 pour l'instant
            pepites.append({"match": match_name, "marche": "Plus de 5.5 buts", "proba": probs["over_5_5"], "cote": 0.0, "ev": 0.0, "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})
            
        # --- BTTS ---
        if "BTTS" in markets_to_check and probs["btts_yes"] >= min_proba:
            pepites.append({"match": match_name, "marche": "Les 2 marquent (Oui)", "proba": probs["btts_yes"], "cote": 0.0, "ev": 0.0, "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})

    # On trie : d'abord les plus grosses Values (EV), puis par probabilité
    pepites = sorted(pepites, key=lambda x: (x["ev"], x["proba"]), reverse=True)
    return pepites
