import math

def poisson_probability(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def calculate_all_markets(lambda_home, lambda_away, max_goals=8):
    p_home_win = 0.0
    p_draw = 0.0
    p_away_win = 0.0
    p_over_5_5 = 0.0
    p_btts = 0.0
    p_handicap_home = 0.0 # Dom gagne par 2 buts ou plus
    p_handicap_away = 0.0 # Ext gagne ou perd par 1 but

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
                
            # BTTS
            if h > 0 and a > 0:
                p_btts += prob
                
            # Handicap -1.5 (Dom) / +1.5 (Ext)
            if (h - a) > 1.5:
                p_handicap_home += prob
            if (a - h) > -1.5:
                p_handicap_away += prob

    # Vainqueur Final : On estime que si match nul à 60 min, c'est du 50/50 en OT
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
