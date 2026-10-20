import math

def poisson_probability(k, lam):
    """Calcule la probabilité d'avoir exactement k buts avec une moyenne lam."""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def calculate_all_markets(lambda_home, lambda_away, max_goals=8):
    """Calcule toutes les probabilités des marchés à 60 min via la matrice de Poisson."""
    p_home_win = 0.0
    p_draw = 0.0
    p_away_win = 0.0
    p_over_5_5 = 0.0
    p_btts = 0.0

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson_probability(h, lambda_home) * poisson_probability(a, lambda_away)
            
            # 1X2
            if h > a:
                p_home_win += prob
            elif h == a:
                p_draw += prob
            else:
                p_away_win += prob
                
            # Over / Under 5.5
            if (h + a) > 5.5:
                p_over_5_5 += prob
                
            # BTTS (Les deux marquent)
            if h > 0 and a > 0:
                p_btts += prob

    return {
        "1X2": (p_home_win, p_draw, p_away_win),
        "over_5_5": p_over_5_5,
        "under_5_5": 1.0 - p_over_5_5,
        "btts_yes": p_btts,
        "btts_no": 1.0 - p_btts
    }
