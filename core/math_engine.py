import math

def poisson_probability(k, lam):
    """Calcule la probabilité d'avoir exactement k buts avec une moyenne lam."""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def calculate_1x2_proba(lambda_home, lambda_away, max_goals=8):
    """Calcule les probabilités 1X2 à 60 minutes via la matrice de Poisson."""
    p_home_win = 0.0
    p_draw = 0.0
    p_away_win = 0.0

    # On calcule la probabilité pour chaque score possible (de 0-0 à 8-8)
    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson_probability(h, lambda_home) * poisson_probability(a, lambda_away)
            if h > a:
                p_home_win += prob
            elif h == a:
                p_draw += prob
            else:
                p_away_win += prob

    return p_home_win, p_draw, p_away_win
