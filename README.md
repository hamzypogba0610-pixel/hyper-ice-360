# HYPER-ICE 360

> *Une prédiction non calibrée est une opinion déguisée en chiffre.*

Moteur d'analyse et de prédiction des matchs de hockey sur glace.
**Ligues couvertes (V1)** : NHL, SHL, Liiga.

---

## Ce que ce projet est

Un moteur qui transforme des données de hockey en **probabilités calibrées** de résultats de marché, avec une **mesure honnête de sa propre performance**.

Trois principes non négociables :

1. **Probabilité estimée ≠ probabilité calibrée ≠ indicateur de valeur.** Ces trois notions ne sont jamais confondues.
2. **Aucune donnée manquante n'est inventée.** Une valeur absente est signalée, pas remplacée par zéro.
3. **Aucune prédiction n'utilise une information postérieure au match.** Le backtest rejoue le pipeline comme s'il était au jour J.

---

## Périmètre V1 (figé)

| Élément | Décision |
|---|---|
| Ligues | NHL, SHL, Liiga |
| Historique | 2 dernières saisons complètes par ligue |
| Marchés | 1X2 à 60 min, Over/Under, Handicap −1.5/+1.5, BTTS, Vainqueur final (incl. OT/SO) |
| Modèle NHL | Niveau A — Poisson + shrinkage + time decay + xG/GSAx |
| Modèle SHL/Liiga | Niveau B — Poisson + shrinkage + time decay + tirs en proxy |
| Repli | Niveau C — buts marqués/encaissés uniquement, toujours signalé |
| Calibration | Logistique par ligue (NHL) ou poolée (SHL+Liiga) |
| Baselines | Naïve **et** bookmaker (cotes Shin) |
| Métriques | Brier, log-loss, courbe de calibration, **CLV** |
| Staking | Kelly fractionnaire c=0.25, désactivé tant que CLV < 0 |
| Persistance | Turso (libSQL) |
| Déploiement | Render free + GitHub Actions |

**Hors V1 (quarantaine stricte)** : Dixon-Coles, GAMMA-X, Écologie du But, ensemble de modèles, calibration isotonic, temperature scaling, marchés par période, ligues supplémentaires.

---

## Sources de données

| Source | Ligues | Usage |
|---|---|---|
| NHL API | NHL | Calendrier, scores 60/OT/SO, boxscore |
| MoneyPuck (CSV) | NHL | xG, xGA, GSAx, tirs, PP/PK |
| shl.se | SHL | Calendrier, scores, boxscore, tirs |
| liiga.fi | Liiga | Calendrier, scores, boxscore, tirs |
| The Odds API | Les 3 | Cotes de clôture |
| Formulaire manuel | Les 3 | Gardien confirmé, absences |

---

## Critères de sortie V1

La V1 est terminée quand, sur **≥ 300 matchs hors échantillon par ligue** :

- [ ] Brier **< baseline naïve** sur les 3 ligues
- [ ] Log-loss **< baseline naïve** sur les 3 ligues
- [ ] Courbe de calibration **dans le cône à 95 %** sur les 3 ligues
- [ ] Marchés battus en NHL : **5/5**
- [ ] Marchés battus en SHL/Liiga : **≥ 3/5**
- [ ] CLV moyen calculable sur les 3 ligues
- [ ] Tous les tests verts, aucune régression

---

## Règles de settlement

| Marché | Inclut OT | Inclut SO | Nul possible | Push |
|---|---|---|---|---|
| 1X2_60 | Non | Non | **Oui** | Non |
| Over/Under | Non | Non | Non | **Oui** (ligne entière) |
| Handicap | Non | Non | Non | **Oui** (ligne entière) |
| BTTS | Non | Non | Non | Non |
| Vainqueur final | **Oui** | **Oui** | Non | Non |

---

## Feuille de route

| Étape | Contenu | Statut |
|---|---|---|
| S0 | `leagues.py` + tests settlement | En cours |
| S1 | Ingestion NHL + Turso | À venir |
| S2 | Poisson + Goal Matrix + OT | À venir |
| S3 | Baselines + métriques + backtest NHL | À venir |
| S4 | Calibration + rolling-origin NHL | À venir |
| S5 | Ingestion SHL + Liiga | À venir |
| S6 | Modèle Niveau B + backtest européen | À venir |
| S7 | Pooling SHL+Liiga | À venir |
| S8 | UI Streamlit + formulaire | À venir |
| S9 | 5 marchés + Kelly + GitHub Actions | À venir |
| S10 | Déploiement Render + release v1.0.0 | À venir |
