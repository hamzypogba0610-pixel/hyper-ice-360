import streamlit as st
import pandas as pd
from core.leagues import LEAGUES, list_markets, compute_points
from core.math_engine import calculate_all_markets, get_naive_baseline, get_goal_matrix
from core.nhl_api import NHL_TEAMS, get_all_teams_stats, get_team_last_games, get_upcoming_games
from core.scanner import scan_matches
import datetime

st.set_page_config(page_title="HYPER-ICE 360", page_icon="🏒", layout="wide")

# CSS
st.markdown("""
    <style>
    .stApp { background-color: #0A192F; }
    h1, h2, h3, h4, p, label { color: #E6F1FF !important; font-family: 'Helvetica Neue', sans-serif; }
    .main-title { color: #64FFDA !important; font-size: 3em; font-weight: 900; text-align: center; text-transform: uppercase; letter-spacing: 3px; text-shadow: 2px 2px 10px rgba(100, 255, 218, 0.3); margin-bottom: 0; }
    .sub-title { text-align: center; color: #8892B0 !important; font-size: 1.2em; margin-bottom: 2em; }
    .stButton>button { background-color: #64FFDA; color: #0A192F; font-weight: bold; font-size: 1.1em; border-radius: 8px; border: 2px solid #64FFDA; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background-color: transparent; color: #64FFDA; }
    .stSelectbox, .stNumberInput, .stTextInput { background-color: #112240; border-radius: 8px; }
    hr { border-color: #233554; }
    .team-logo { display: block; margin-left: auto; margin-right: auto; width: 80px; height: 80px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# Mémoire
if 'historique' not in st.session_state: st.session_state.historique = []
if 'bankroll' not in st.session_state: st.session_state.bankroll = 1000.0
if 'selected_match' not in st.session_state: st.session_state.selected_match = None

st.markdown('<p class="main-title">🏒 HYPER-ICE 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Moteur d\'analyse prédictive & Gestion des risques</p>', unsafe_allow_html=True)

# 3 ONGLETS
tab_scanner, tab_analyse, tab_historique = st.tabs(["🎯 Scanner Automatique", "🔍 Analyse Manuelle", "📜 Tracker & Bankroll"])

# ==========================================
# ONGLET 1 : SCANNER
# ==========================================
with tab_scanner:
    st.subheader("🎯 Chasseur de Pépites")
    st.write("Le scanner analyse tous les matchs à venir et filtre selon tes critères.")
    
    col_scan1, col_scan2 = st.columns(2)
    with col_scan1:
        horizon = st.slider("Horizon (jours)", 1, 7, 3)
        seuil = st.slider("Seuil de probabilité minimum (%)", 50, 85, 60) / 100.0
    with col_scan2:
        st.write("Marchés à scanner :")
        m_1x2 = st.checkbox("1X2 (60 min)", value=True)
        m_final = st.checkbox("Vainqueur Final (OT/SO)", value=True)
        m_over = st.checkbox("Over 5.5 buts", value=False)
        m_btts = st.checkbox("BTTS (Oui)", value=False)
        
    markets_to_check = []
    if m_1x2: markets_to_check.append("1X2")
    if m_final: markets_to_check.append("Final")
    if m_over: markets_to_check.append("Over")
    if m_btts: markets_to_check.append("BTTS")

    if st.button("🚀 LANCER LE SCAN", type="primary"):
        with st.spinner("Radar en cours... Analyse des données NHL..."):
            upcoming = get_upcoming_games(horizon)
            if not upcoming:
                st.warning("Aucun match trouvé sur cette période (ou API indisponible).")
            else:
                pepites = scan_matches(upcoming, seuil, markets_to_check)
                
                st.write(f"**{len(upcoming)} matchs scannés** | **{len(pepites)} pépites trouvées**")
                
                if len(pepites) == 0:
                    st.info("Aucun match ne passe ton seuil. Baisse le seuil ou élargis l'horizon.")
                else:
                    for p in pepites:
                        with st.container():
                            colA, colB, colC = st.columns([3, 2, 1])
                            with colA:
                                st.write(f"**{p['match']}**")
                                st.caption(f"Marché : {p['marche']}")
                            with colB:
                                st.metric(label="Probabilité", value=f"{p['proba']*100:.1f}%")
                                cote_juste = 1 / p['proba']
                                st.caption(f"Cote juste : {cote_juste:.2f}")
                            with colC:
                                # Bouton magique pour envoyer vers l'analyse
                                if st.button("Analyser", key=f"btn_{p['match']}_{p['marche']}"):
                                    st.session_state.selected_match = {
                                        "home": p["h_code"],
                                        "away": p["a_code"],
                                        "lam_h": p["lam_h"],
                                        "lam_a": p["lam_a"]
                                    }
                                    st.success("Match sélectionné ! Va dans l'onglet 'Analyse Manuelle'.")
                            st.divider()

# ==========================================
# ONGLET 2 : ANALYSE MANUELLE
# ==========================================
with tab_analyse:
    # Pré-remplissage si on vient du scanner
    default_home = list(NHL_TEAMS.keys()).index([k for k, v in NHL_TEAMS.items() if v == st.session_state.selected_match["home"]][0]) if st.session_state.selected_match else 0
    default_away = list(NHL_TEAMS.keys()).index([k for k, v in NHL_TEAMS.items() if v == st.session_state.selected_match["away"]][0]) if st.session_state.selected_match else 1

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            equipe_dom = st.selectbox("🏠 Équipe Domicile", list(NHL_TEAMS.keys()), index=default_home, key="sel_dom")
            stats_dom = get_all_teams_stats().get(NHL_TEAMS[equipe_dom])
            if stats_dom:
                st.markdown(f'<img src="{stats_dom["logo"]}" class="team-logo">', unsafe_allow_html=True)
                st.caption(f"⚔️ {stats_dom['attaque']} buts/match | 🛡️ {stats_dom['defense']} encaissés")
                forme_dom = get_team_last_games(NHL_TEAMS[equipe_dom])
                st.caption("Forme : " + " ".join(["🟢" if r == "V" else "🔴" for r in forme_dom]))
        with col2:
            equipe_ext = st.selectbox("✈️ Équipe Extérieur", list(NHL_TEAMS.keys()), index=default_away, key="sel_ext")
            stats_ext = get_all_teams_stats().get(NHL_TEAMS[equipe_ext])
            if stats_ext:
                st.markdown(f'<img src="{stats_ext["logo"]}" class="team-logo">', unsafe_allow_html=True)
                st.caption(f"⚔️ {stats_ext['attaque']} buts/match | 🛡️ {stats_ext['defense']} encaissés")
                forme_ext = get_team_last_games(NHL_TEAMS[equipe_ext])
                st.caption("Forme : " + " ".join(["🟢" if r == "V" else "🔴" for r in forme_ext]))

        st.divider()
        
        # Affichage des cotes
        st.subheader("💰 Cotes (Optionnel)")
        c1, c2, c3 = st.columns(3)
        cote_dom = c1.number_input("1 (Dom)", min_value=1.01, value=None, step=0.01)
        cote_nul = c2.number_input("X (Nul)", min_value=1.01, value=None, step=0.01)
        cote_ext = c3.number_input("2 (Ext)", min_value=1.01, value=None, step=0.01)

        if st.button("LANCER L'ANALYSE DÉTAILLÉE 🚀"):
            # Calculs
            lam_dom = ((stats_dom['attaque'] + stats_ext['defense']) / 2) * 1.05
            lam_ext = ((stats_ext['attaque'] + stats_dom['defense']) / 2) * 0.95
            probs = calculate_all_markets(lam_dom, lam_ext)
            
            st.subheader("🎯 Probabilités")
            st.caption(f"xG calculés : {equipe_dom} = {lam_dom:.2f} | {equipe_ext} = {lam_ext:.2f}")
            
            # Matrice
            st.write("### 🎲 Matrice des Scores")
            matrix_data = get_goal_matrix(lam_dom, lam_ext)
            df_matrix = pd.DataFrame(matrix_data).style.format("{:.2f}")
            st.dataframe(df_matrix, use_container_width=True)
            
            # Value Bet
            if cote_dom and (probs['1X2'][0] * cote_dom) - 1 > 0:
                st.success(f"💎 VALUE DÉTECTÉE sur Victoire {equipe_dom} ! (Proba: {probs['1X2'][0]*100:.1f}%, Cote: {cote_dom})")

# ==========================================
# ONGLET 3 : HISTORIQUE & BANKROLL
# ==========================================
with tab_historique:
    st.subheader("💰 Bankroll & Paris")
    st.metric("Bankroll Actuelle", f"{st.session_state.bankroll:.2f} €")
    
    if len(st.session_state.historique) > 0:
        st.dataframe(pd.DataFrame(st.session_state.historique), use_container_width=True)
    else:
        st.info("L'historique est vide.")
