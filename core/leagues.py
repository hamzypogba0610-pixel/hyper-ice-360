"""
HYPER-ICE 360 — Référentiel des ligues V1.

Trois ligues : NHL, SHL, Liiga.
Ce fichier ne contient AUCUNE logique de modélisation. Il définit :
  - la configuration des ligues (niveau de capacité, format OT, grille de points),
  - les règles de settlement des 5 marchés V1,
  - les accesseurs et la fonction de règlement.

RÈGLE : toute modification de ce fichier doit être accompagnée d'un passage
vert de tests/test_overtime_rules.py. Aucune exception.
"""

from dataclasses import dataclass
from typing import Literal, Optional


CapabilityLevel = Literal["A", "B", "C"]
OTFormat = Literal["3v3_5min_so", "4v4_5min_so", "5v5_20min_so"]
PointsSystem = Literal["2-2-1-0", "3-2-1-0"]
Side = Literal["home", "away", "draw", "over", "under", "yes", "no"]


@dataclass(frozen=True)
class MarketRule:
    key: str
    label: str
    includes_ot: bool
    includes_so: bool
    has_draw: bool
    push_rule: Optional[str]


@dataclass(frozen=True)
class League:
    id: str
    name: str
    country: str
    capability: CapabilityLevel
    ot_format: OTFormat
    points_system: PointsSystem
    shot_to_goal_rate: float
    markets: dict
    primary_source: str
    secondary_sources: tuple = ()
    odds_api_key: Optional[str] = None


_COMMON_MARKETS = {
    "1X2_60": MarketRule(
        key="1X2_60",
        label="1X2 à 60 minutes",
        includes_ot=False, includes_so=False,
        has_draw=True, push_rule=None,
    ),
    "over_under": MarketRule(
        key="over_under",
        label="Total de buts (60 min)",
        includes_ot=False, includes_so=False,
        has_draw=False, push_rule="integer_line",
    ),
    "handicap": MarketRule(
        key="handicap",
        label="Handicap de buts (60 min)",
        includes_ot=False, includes_so=False,
        has_draw=False, push_rule="integer_line",
    ),
    "btts": MarketRule(
        key="btts",
        label="Les deux équipes marquent (60 min)",
        includes_ot=False, includes_so=False,
        has_draw=False, push_rule=None,
    ),
    "final_winner": MarketRule(
        key="final_winner",
        label="Vainqueur du match (OT/SO inclus)",
        includes_ot=True, includes_so=True,
        has_draw=False, push_rule=None,
    ),
}


NHL = League(
    id="NHL",
    name="National Hockey League",
    country="US/CA",
    capability="A",
    ot_format="3v3_5min_so",
    points_system="2-2-1-0",
    shot_to_goal_rate=0.100,
    markets=_COMMON_MARKETS,
    primary_source="nhl_api",
    secondary_sources=("moneypuck",),
    odds_api_key="icehockey_nhl",
)

SHL = League(
    id="SHL",
    name="Swedish Hockey League",
    country="SE",
    capability="B",
    ot_format="3v3_5min_so",
    points_system="3-2-1-0",
    shot_to_goal_rate=0.095,
    markets=_COMMON_MARKETS,
    primary_source="shl_se",
    secondary_sources=(),
    odds_api_key="icehockey_sweden",
)

LIIGA = League(
    id="LIIGA",
    name="Liiga",
    country="FI",
    capability="B",
    ot_format="3v3_5min_so",
    points_system="3-2-1-0",
    shot_to_goal_rate=0.090,
    markets=_COMMON_MARKETS,
    primary_source="liiga_fi",
    secondary_sources=(),
    odds_api_key="icehockey_finland",
)


LEAGUES = {"NHL": NHL, "SHL": SHL, "LIIGA": LIIGA}


def get_league(league_id: str) -> League:
    try:
        return LEAGUES[league_id.upper()]
    except KeyError:
        raise ValueError(f"Ligue inconnue : {league_id!r}. Disponibles : {list(LEAGUES)}")


def get_market(league_id: str, market_key: str) -> MarketRule:
    league = get_league(league_id)
    try:
        return league.markets[market_key]
    except KeyError:
        raise ValueError(
            f"Marché {market_key!r} inconnu pour {league_id!r}. "
            f"Disponibles : {list(league.markets)}"
        )


def list_markets(league_id: str) -> list:
    return list(get_league(league_id).markets.keys())


def settle_market(
    league_id: str,
    market_key: str,
    home_60: int,
    away_60: int,
    home_final: Optional[int] = None,
    away_final: Optional[int] = None,
    line: Optional[float] = None,
    side: Optional[Side] = None,
) -> str:
    rule = get_market(league_id, market_key)

    if rule.includes_ot or rule.includes_so:
        if home_final is None or away_final is None:
            raise ValueError(
                f"Marché {market_key!r} inclut OT/SO : scores finaux obligatoires."
            )
        h, a = home_final, away_final
    else:
        h, a = home_60, away_60

    if market_key == "1X2_60":
        if side not in ("home", "away", "draw"):
            raise ValueError("1X2_60 : 'side' ∈ {'home','away','draw'}")
        if side == "home":
            return "win" if h > a else "lose"
        if side == "away":
            return "win" if h < a else "lose"
        return "win" if h == a else "lose"

    if market_key == "final_winner":
        if side not in ("home", "away"):
            raise ValueError("final_winner : 'side' ∈ {'home','away'}")
        if side == "home":
            return "win" if h > a else "lose"
        return "win" if h < a else "lose"

    if market_key == "over_under":
        if line is None or side not in ("over", "under"):
            raise ValueError("over_under : 'line' et 'side' obligatoires")
        total = h + a
        if total == line:
            return "push"
        return "win" if (total > line) == (side == "over") else "lose"

    if market_key == "handicap":
        if line is None or side not in ("home", "away"):
            raise ValueError("handicap : 'line' et 'side' obligatoires")
        margin = (h - a) + line if side == "home" else (a - h) + line
        if margin > 0:
            return "win"
        if margin < 0:
            return "lose"
        return "push"

    if market_key == "btts":
        if side not in ("yes", "no"):
            raise ValueError("btts : 'side' ∈ {'yes','no'}")
        both_scored = h > 0 and a > 0
        return "win" if both_scored == (side == "yes") else "lose"

    raise ValueError(f"Marché non géré : {market_key!r}")


def compute_points(
    league_id: str,
    home_60: int,
    away_60: int,
    home_final: int,
    away_final: int,
) -> tuple:
    system = get_league(league_id).points_system

    if home_60 > away_60:
        return (2, 0) if system == "2-2-1-0" else (3, 0)
    if home_60 < away_60:
        return (0, 2) if system == "2-2-1-0" else (0, 3)

    if home_final > away_final:
        return (2, 1)
    if home_final < away_final:
        return (1, 2)
    raise ValueError("Match ne peut pas se terminer à égalité après SO")
