from core.math_engine import calculate_all_markets
from core.nhl_api import get_all_teams_stats

def scan_matches(games, min_proba, markets_to_check):
    """
    Prend une liste de matchs et retourne ceux qui dépassent le seuil.
    """
    teams_stats = get_all_teams_stats()
    if not teams_stats:
        return []

    pépites = []

    for game in games:
        h_code = game.get("home_code")
        a_code = game.get("away_code")
        
        if h_code not in teams_stats or a_code not in teams_stats:
            continue
            
        st_h = teams_stats[h_code]
        st_a = teams_stats[a_code]
        
        # Formule magique : (Attaque + Défense adverse) / 2 * Avantage
        lam_h = ((st_h['attaque'] + st_a['defense']) / 2) * 1.05
        lam_a = ((st_a['attaque'] + st_h['defense']) / 2) * 0.95
        
        probs = calculate_all_markets(lam_h, lam_a)
        
        match_name = f"{st_h['nom']} vs {st_a['nom']}"
        
        # Vérification des marchés
        if "1X2" in markets_to_check:
            if probs["1X2"][0] >= min_proba:
                pépites.append({"match": match_name, "marche": f"Victoire {st_h['nom']}", "proba": probs["1X2"][0], "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})
            if probs["1X2"][2] >= min_proba:
                pépites.append({"match": match_name, "marche": f"Victoire {st_a['nom']}", "proba": probs["1X2"][2], "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})
                
        if "Final" in markets_to_check:
            if probs["final_1X2"][0] >= min_proba:
                pépites.append({"match": match_name, "marche": f"Vainqueur Final {st_h['nom']}", "proba": probs["final_1X2"][0], "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})
            if probs["final_1X2"][1] >= min_proba:
                pépites.append({"match": match_name, "marche": f"Vainqueur Final {st_a['nom']}", "proba": probs["final_1X2"][1], "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})

        if "Over" in markets_to_check and probs["over_5_5"] >= min_proba:
            pépites.append({"match": match_name, "marche": "Plus de 5.5 buts", "proba": probs["over_5_5"], "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})
            
        if "BTTS" in markets_to_check and probs["btts_yes"] >= min_proba:
            pépites.append({"match": match_name, "marche": "Les 2 marquent (Oui)", "proba": probs["btts_yes"], "lam_h": lam_h, "lam_a": lam_a, "h_code": h_code, "a_code": a_code})

    # On trie par probabilité décroissante
    pépites = sorted(pépites, key=lambda x: x["proba"], reverse=True)
    return pépites
