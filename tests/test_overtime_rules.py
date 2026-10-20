"""
Tests de non-régression pour core/leagues.py.

Ces tests vérifient que :
  - les 3 ligues existent avec les bonnes capacités,
  - les 5 marchés sont présents partout,
  - les grilles de points NHL (2-2-1-0) et SHL/Liiga (3-2-1-0) sont correctes,
  - les 5 règles de settlement sont respectées.

RÈGLE : ces tests doivent passer AVANT tout commit qui modifie core/leagues.py.
"""

import pytest
from core.leagues import (
    LEAGUES, get_league, get_market, settle_market, compute_points,
)


# ---------------------------------------------------------------------------
# Structure : les 3 ligues et les 5 marchés
# ---------------------------------------------------------------------------

def test_three_leagues_present():
    assert set(LEAGUES.keys()) == {"NHL", "SHL", "LIIGA"}


def test_capability_levels():
    assert get_league("NHL").capability == "A"
    assert get_league("SHL").capability == "B"
    assert get_league("LIIGA").capability == "B"


def test_all_leagues_have_five_markets():
    expected = {"1X2_60", "over_under", "handicap", "btts", "final_winner"}
    for lid in LEAGUES:
        assert set(get_league(lid).markets.keys()) == expected


def test_unknown_league_raises():
    with pytest.raises(ValueError):
        get_league("KHL")


def test_unknown_market_raises():
    with pytest.raises(ValueError):
        get_market("NHL", "marche_inconnu")


# ---------------------------------------------------------------------------
# Grille de points NHL (2-2-1-0)
# ---------------------------------------------------------------------------

def test_points_nhl_victoire_60min():
    assert compute_points("NHL", 3, 1, 3, 1) == (2, 0)


def test_points_nhl_victoire_ot():
    assert compute_points("NHL", 2, 2, 3, 2) == (2, 1)


def test_points_nhl_defaite_ot():
    assert compute_points("NHL", 2, 2, 2, 3) == (1, 2)


def test_points_nhl_victoire_so():
    assert compute_points("NHL", 1, 1, 2, 1) == (2, 1)


# ---------------------------------------------------------------------------
# Grille de points SHL et Liiga (3-2-1-0)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("league_id", ["SHL", "LIIGA"])
def test_points_europeen_victoire_60min(league_id):
    assert compute_points(league_id, 4, 0, 4, 0) == (3, 0)


@pytest.mark.parametrize("league_id", ["SHL", "LIIGA"])
def test_points_europeen_victoire_ot(league_id):
    assert compute_points(league_id, 2, 2, 3, 2) == (2, 1)


@pytest.mark.parametrize("league_id", ["SHL", "LIIGA"])
def test_points_europeen_defaite_ot(league_id):
    assert compute_points(league_id, 2, 2, 2, 3) == (1, 2)


# ---------------------------------------------------------------------------
# Règle 1 : 1X2_60 — OT/SO exclus, nul possible
# ---------------------------------------------------------------------------

def test_1x2_60_nul_est_gagnant():
    assert settle_market("NHL", "1X2_60", 2, 2, 3, 2, side="draw") == "win"


def test_1x2_60_domicile_perd_si_nul_a_60():
    assert settle_market("NHL", "1X2_60", 2, 2, 3, 2, side="home") == "lose"


def test_1x2_60_ignore_ot():
    assert settle_market("NHL", "1X2_60", 2, 1, 3, 1, side="home") == "win"


def test_1x2_60_side_invalide():
    with pytest.raises(ValueError):
        settle_market("NHL", "1X2_60", 2, 1, side="over")


# ---------------------------------------------------------------------------
# Règle 2 : Over/Under — push sur ligne entière
# ---------------------------------------------------------------------------

def test_over_under_push_ligne_entiere_over():
    assert settle_market("NHL", "over_under", 4, 2, line=6, side="over") == "push"


def test_over_under_push_ligne_entiere_under():
    assert settle_market("NHL", "over_under", 4, 2, line=6, side="under") == "push"


def test_over_under_demi_ligne_pas_de_push():
    assert settle_market("NHL", "over_under", 4, 2, line=5.5, side="over") == "win"
    assert settle_market("NHL", "over_under", 3, 2, line=5.5, side="under") == "win"


def test_over_under_sans_ligne_leve_erreur():
    with pytest.raises(ValueError):
        settle_market("NHL", "over_under", 4, 2, side="over")


# ---------------------------------------------------------------------------
# Règle 3 : Handicap — pas de push sur demi-ligne
# ---------------------------------------------------------------------------

def test_handicap_home_moins_1_5_gagne():
    assert settle_market("NHL", "handicap", 3, 1, line=-1.5, side="home") == "win"


def test_handicap_home_moins_1_5_perd():
    assert settle_market("NHL", "handicap", 2, 1, line=-1.5, side="home") == "lose"


def test_handicap_away_plus_1_5_perd():
    assert settle_market("NHL", "handicap", 3, 1, line=1.5, side="away") == "lose"


def test_handicap_away_plus_1_5_gagne():
    assert settle_market("NHL", "handicap", 2, 1, line=1.5, side="away") == "win"


def test_handicap_sans_ligne_leve_erreur():
    with pytest.raises(ValueError):
        settle_market("NHL", "handicap", 3, 1, side="home")


# ---------------------------------------------------------------------------
# Règle 4 : BTTS — uniquement sur les 60 minutes
# ---------------------------------------------------------------------------

def test_btts_oui_gagne_si_les_deux_marquent_60min():
    assert settle_market("NHL", "btts", 1, 1, 1, 2, side="yes") == "win"


def test_btts_non_gagne_si_0_0_a_60_min():
    assert settle_market("NHL", "btts", 0, 0, 1, 0, side="no") == "win"


def test_btts_oui_perd_si_0_0_a_60_min():
    assert settle_market("NHL", "btts", 0, 0, 1, 0, side="yes") == "lose"


def test_btts_ignore_les_buts_en_ot():
    # 0-0 à 60 min, 1-0 en OT : BTTS "oui" perd car les 60 min ne comptent pas l'OT
    assert settle_market("NHL", "btts", 0, 0, 1, 0, side="yes") == "lose"


# ---------------------------------------------------------------------------
# Règle 5 : Vainqueur final — inclut OT/SO, pas de nul
# ---------------------------------------------------------------------------

def test_final_winner_inclut_ot():
    assert settle_market("NHL", "final_winner", 2, 2, 3, 2, side="home") == "win"
    assert settle_market("NHL", "final_winner", 2, 2, 3, 2, side="away") == "lose"


def test_final_winner_requiert_scores_finaux():
    with pytest.raises(ValueError):
        settle_market("NHL", "final_winner", 2, 2, side="home")


def test_final_winner_side_invalide():
    with pytest.raises(ValueError):
        settle_market("NHL", "final_winner", 2, 1, 3, 1, side="draw")


# ---------------------------------------------------------------------------
# Invariants cross-ligues : les mêmes règles s'appliquent partout
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("league_id", ["NHL", "SHL", "LIIGA"])
def test_settlement_identique_sur_les_3_ligues(league_id):
    # 1-1 à 60 min, 2-1 en OT
    assert settle_market(league_id, "1X2_60", 1, 1, 2, 1, side="draw") == "win"
    assert settle_market(league_id, "final_winner", 1, 1, 2, 1, side="home") == "win"
    assert settle_market(league_id, "btts", 1, 1, 2, 1, side="yes") == "win"
    assert settle_market(league_id, "over_under", 1, 1, line=2, side="over") == "push"
