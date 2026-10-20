import math

def poisson_probability(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def negative_binomial_probability(k, mu, r=4.5):
    """
    Loi Binomiale Négative (Gamma-Poisson).
    'r' est le paramètre de dispersion. r=4.5 est calibré pour le hockey (variance ~ 1.5x la moyenne).
    """
    if mu <= 0:
        return 1.0 if k == 0 else 0.0
    # Utilisation de lgamma pour calculer les factorielles de grands nombres sans erreur
    log_prob = (math.lgamma(k + r) - math.lgamma(r) - math.lgamma(k + 1) + 
                r * math.log(r / (r + mu)) + 
                k * math.log(mu / (r + mu)))
    return math.exp(log_prob)

def calibrate_probability(p, alpha=1.2, beta=0.05):
    """
    Calibration Sigmoid (Platt Scaling).
    Corrige l'excès de confiance du modèle. 
    Ramène légèrement les probas extrêmes vers le centre.
    """
    # Transformation logit
    if p <= 0: p = 0.001
    if p >= 1: p = 0.999
    logit = math.log(p / (1 - p))
    # Application de la sigmoïde calibrée
    p_cal = 1 / (1 + math.exp(-(alpha * logit + beta)))
    return p_cal

def get_goal_matrix(lambda_home, lambda_away, max_goals=5):
    matrix = []
    for h in range(max_goals + 1):
        row = []
        for a in range(max_goals + 1):
            # On utilise la Binomiale Négative au lieu de Poisson
            prob = negative_binomial_probability(h, lambda_home) * negative_binomial_probability(a, lambda_away)
            row.append(prob * 100)
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
            prob = negative_binomial_probability(h, lambda_home) * negative_binomial_probability(a, lambda_away)
            
            if h > a: p_home_win += prob
            elif h == a: p_draw += prob
            else: p_away_win += prob
                
            if (h + a) > 5.5: p_over_5_5 += prob
            if h > 0 and a > 0: p_btts += prob
            if (h - a) > 1.5: p_handicap_home += prob
            if (a - h) > -1.5: p_handicap_away += prob

    # Application de la calibration sur les marchés principaux
    p_home_win_cal = calibrate_probability(p_home_win)
    p_draw_cal = calibrate_probability(p_draw)
    p_away_win_cal = calibrate_probability(p_away_win)
    
    # On renormalise pour que la somme fasse 1 (car la calibration peut décaler un peu)
    total = p_home_win_cal + p_draw_cal + p_away_win_cal
    p_home_win_cal /= total
    p_draw_cal /= total
    p_away_win_cal /= total

    p_final_home = p_home_win_cal + (p_draw_cal * 0.5)
    p_final_away = p_away_win_cal + (p_draw_cal * 0.5)

    return {
        "1X2": (p_home_win_cal, p_draw_cal, p_away_win_cal),
        "final_1X2": (p_final_home, p_final_away),
        "over_5_5": calibrate_probability(p_over_5_5),
        "under_5_5": 1.0 - calibrate_probability(p_over_5_5),
        "btts_yes": calibrate_probability(p_btts),
        "btts_no": 1.0 - calibrate_probability(p_btts),
        "handicap_home": calibrate_probability(p_handicap_home),
        "handicap_away": calibrate_probability(p_handicap_away)
    }

def get_naive_baseline(league_id):
    if league_id == "NHL":
        return calculate_all_markets(3.1, 2.9)
    elif league_id == "SHL":
        return calculate_all_markets(2.8, 2.5)
    else:
        return calculate_all_markets(2.6, 2.4)

def calculate_clv(cote_ouverture, cote_fermeture):
    """
    Calcule le Closing Line Value (CLV).
    Un CLV positif signifie que la cote de fermeture a baissé (le marché a validé ton analyse).
    """
    if cote_ouverture is None or cote_fermeture is None or cote_ouverture <= 0 or cote_fermeture <= 0:
        return 0.0
    return (cote_ouverture / cote_fermeture) - 1
