import math

def poisson_probability(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def get_goal_matrix(lambda_home, lambda_away, max_goals=5):
    """Génère une matrice des scores possibles (de 0-0 à 5-5)."""
    matrix = []
    for h in range(max_goals + 1):
        row = []
        for a in range(max_goals + 1):
            prob = poisson_probability(h, lambda_home) * poisson_probability(a, lambda_away)
            row.append(prob * 100) # En pourcentage
        matrix.append(row)
    return matrix

def calculate_all_markets(lambda_home, lambda_away, max_goals=8):
    p_home_win = 0.0
    p_draw = 0.0
    p_away_win = 0.0
    p_over_5_5 = 0.0
    p_btts = 0.0
    p_handicap_home = 0.0
    p_handicap_away = 0.0

    for h in range(max_goals + 1):
        for a in range(max_goals + 1):
            prob = poisson_probability(h, lambda_home) * poisson_probability(a, lambda_away)
            
            if h > a: p_home_win += prob
            elif h == a: p_draw += prob
            else: p_away_win += prob
                
            if (h + a) > 5.5: p_over_5_5 += prob
            if h > 0 and a > 0: p_btts += prob
            if (h - a) > 1.5: p_handicap_home += prob
            if (a - h) > -1.5: p_handicap_away += prob

    p_final_home = p_home_win + (p_draw * 0.5)
    p_final_away = p_away_win + (p_draw * 0.5)

    return {
        "1X2": (p_home_win, p_draw, p_away_win),
        "final_1X2": (p_final_home, p_final_away),
        "over_5_5": p_over_5_5,
        "under_5_5": 1.0 - p_over_5_5,
        "btts_yes": p_btts,
        "btts_no": 1.0 - p_btts,
        "handicap_home": p_handicap_home,
        "handicap_away": p_handicap_away
    }

def get_naive_baseline(league_id):
    if league_id == "NHL":
        return calculate_all_markets(3.1, 2.9)
    elif league_id == "SHL":
        return calculate_all_markets(2.8, 2.5)
    else:
        return calculate_all_markets(2.6, 2.4)
