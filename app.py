import streamlit as st
import pandas as pd
from core.leagues import LEAGUES, list_markets, compute_points
from core.math_engine import (calculate_all_markets, get_naive_baseline, get_goal_matrix, 
                              calculate_brier_score, calculate_log_loss)
from core.nhl_api import NHL_TEAMS, get_all_teams_stats, get_team_last_games, get_upcoming_games
from core.europe_teams import SHL_TEAMS, LIIGA_TEAMS
from core.scanner import scan_matches
import datetime

st.set_page_config(page_title="HYPER-ICE 360", page_icon="🏒", layout="wide")

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
    .ev-positive { color: #64FFDA; font-weight: bold; font-size: 1.2em; }
    .ev-negative { color: #FF6B6B; font-weight: bold; }
    .clv-positive { color: #FFD700; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 1. INITIALISATION DE LA MÉMOIRE ---
if 'historique' not in st.session_state: st.session_state.historique = []
if 'bankroll' not in st.session_state: st.session_state.bankroll = 1000.0
if 'current_page' not in st.session_state: st.session_state.current_page = "🎯 Scanner Automatique"
if 'open_odds' not in st.session_state: st.session_state.open_odds = {}

# --- 2. TRANSFERT DES CIBLES ---
if 'target_dom' in st.session_state:
    st.session_state.team_dom = st.session_state.target_dom
    del st.session_state.target_dom
if 'target_ext' in st.session_state:
    st.session_state.team_ext = st.session_state.target_ext
    del st.session_state.target_ext

# --- 3. FONCTIONS MAGIQUES (Callbacks) ---
def switch_to_analysis(h_code, a_code):
    st.session_state.current_page = "🔍 Analyse Manuelle"
    st.session_state.target_dom = [k for k, v in NHL_TEAMS.items() if v == h_code][0]
    st.session_state.target_ext = [k for k, v in NHL_TEAMS.items() if v == a_code][0]
    st.rerun()

def add_to_tracker(match, marche, proba, cote):
    for p in st.session_state.historique:
        if p["Match"] == match and p["Marche"] == marche:
            st.toast("⚠️ Ce pari est déjà dans ton tracker !", icon="⚠️")
            return
    nouveau_pari = {
        "Date": str(datetime.date.today()),
        "Match": match,
        "Marche": marche,
        "Proba": round(proba * 100, 1),
        "Cote": cote,
        "Statut": "En attente",
        "Gain_Net": 0.0
    }
    st.session_state.historique.append(nouveau_pari)
    st.toast("✅ Pari ajouté au tracker !", icon="📌")

st.markdown('<p class="main-title">🏒 HYPER-ICE 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Moteur d\'analyse prédictive & Gestion des risques</p>', unsafe_allow_html=True)

# --- 4. MENU DE NAVIGATION ---
pages = ["🎯 Scanner Automatique", "🔍 Analyse Manuelle", "📜 Tracker & Bankroll"]
index_actuel = pages.index(st.session_state.current_page)

choix_menu = st.radio("Navigation", pages, index=index_actuel, horizontal=True, label_visibility="collapsed")
if choix_menu != st.session_state.current_page:
    st.session_state.current_page = choix_menu
    st.rerun()

navigation = st.session_state.current_page
st.divider()

# ==========================================
# PAGE 1 : SCANNER
# ==========================================
if navigation == "🎯 Scanner Automatique":
    st.subheader("🎯 Chasseur de Pépites & Cotes Réelles")
    
    col_scan1, col_scan2 = st.columns(2)
    with col_scan1:
        horizon = st.slider("Horizon (jours)", 1, 7, 3)
        seuil = st.slider("Seuil de probabilité minimum (%)", 50, 85, 60) / 100.0
    with col_scan2:
        st.write("Marchés à scanner :")
        m_1x2 = st.checkbox("1X2 (60 min)", value=True)
        m_final = st.checkbox("Vainqueur Final (OT/SO)", value=True)
        
    markets_to_check = []
    if m_1x2: markets_to_check.append("1X2")
    if m_final: markets_to_check.append("Final")

    if st.button("🚀 LANCER LE SCAN", type="primary"):
        with st.spinner("Radar en cours..."):
            upcoming = get_upcoming_games(horizon)
            if not upcoming:
                st.warning("Aucun match trouvé.")
            else:
                pepites = scan_matches(upcoming, seuil, markets_to_check)
                st.write(f"**{len(upcoming)} matchs scannés** | **{len(pepites)} pépites trouvées**")
                
                for p in pepites:
                    with st.container():
                        colA, colB, colC, colD = st.columns([3, 2, 1, 1])
                        with colA:
                            st.write(f"**{p['match']}**")
                            st.caption(f"{p['marche']}")
                        with colB:
                            st.metric(label="Proba", value=f"{p['proba']*100:.1f}%")
                            if p['cote'] > 0:
                                st.markdown(f"Cote: **{p['cote']}** | EV: {p['ev']*100:+.1f}%")
                        with colC:
                            st.button("🔍", key=f"btn_ana_{p['match']}_{p['marche']}", 
                                      on_click=switch_to_analysis, args=(p["h_code"], p["a_code"]), help="Analyser en détail")
                        with colD:
                            if p['cote'] > 0:
                                st.button("📌", key=f"btn_sw_{p['match']}_{p['marche']}", 
                                          on_click=add_to_tracker, args=(p['match'], p['marche'], p['proba'], p['cote']), help="Ajouter au tracker")
                        st.divider()

# ==========================================
# PAGE 2 : ANALYSE MANUELLE
# ==========================================
elif navigation == "🔍 Analyse Manuelle":
    ligue_id = st.selectbox("🏆 Compétition", list(LEAGUES.keys()))
    st.divider()
    with st.container():
        col1, col2 = st.columns(2)
        
        if ligue_id == "NHL":
            default_home = 0
            default_away = 1
            with col1:
                equipe_dom = st.selectbox("🏠 Équipe Domicile", list(NHL_TEAMS.keys()), index=default_home, key="team_dom")
                stats_dom = get_all_teams_stats().get(NHL_TEAMS[equipe_dom])
                if stats_dom:
                    st.markdown(f'<img src="{stats_dom["logo"]}" class="team-logo">', unsafe_allow_html=True)
                    st.caption(f"⚔️ {stats_dom['attaque']:.2f} buts/match | 🛡️ {stats_dom['defense']:.2f} encaissés")
                    forme = get_team_last_games(NHL_TEAMS[equipe_dom])
                    st.caption("Forme : " + " ".join(["🟢" if r == "V" else "🔴" for r in forme]))
            with col2:
                equipe_ext = st.selectbox("✈️ Équipe Extérieur", list(NHL_TEAMS.keys()), index=default_away, key="team_ext")
                stats_ext = get_all_teams_stats().get(NHL_TEAMS[equipe_ext])
                if stats_ext:
                    st.markdown(f'<img src="{stats_ext["logo"]}" class="team-logo">', unsafe_allow_html=True)
                    st.caption(f"⚔️ {stats_ext['attaque']:.2f} buts/match | 🛡️ {stats_ext['defense']:.2f} encaissés")
                    forme = get_team_last_games(NHL_TEAMS[equipe_ext])
                    st.caption("Forme : " + " ".join(["🟢" if r == "V" else "🔴" for r in forme]))

        elif ligue_id == "SHL":
            with col1:
                equipe_dom = st.selectbox("🏠 Équipe Domicile", list(SHL_TEAMS.keys()))
                att_dom = st.number_input("Attaque (buts/match)", value=SHL_TEAMS[equipe_dom]["attaque"], step=0.1)
                def_dom = st.number_input("Défense (encaissés/match)", value=SHL_TEAMS[equipe_dom]["defense"], step=0.1)
            with col2:
                equipe_ext = st.selectbox("✈️ Équipe Extérieur", list(SHL_TEAMS.keys()), index=1)
                att_ext = st.number_input("Attaque (buts/match)", value=SHL_TEAMS[equipe_ext]["attaque"], step=0.1)
                def_ext = st.number_input("Défense (encaissés/match)", value=SHL_TEAMS[equipe_ext]["defense"], step=0.1)
            stats_dom = {"attaque": att_dom, "defense": def_dom}
            stats_ext = {"attaque": att_ext, "defense": def_ext}

        elif ligue_id == "LIIGA":
            with col1:
                equipe_dom = st.selectbox("🏠 Équipe Domicile", list(LIIGA_TEAMS.keys()))
                att_dom = st.number_input("Attaque (buts/match)", value=LIIGA_TEAMS[equipe_dom]["attaque"], step=0.1)
                def_dom = st.number_input("Défense (encaissés/match)", value=LIIGA_TEAMS[equipe_dom]["defense"], step=0.1)
            with col2:
                equipe_ext = st.selectbox("✈️ Équipe Extérieur", list(LIIGA_TEAMS.keys()), index=1)
                att_ext = st.number_input("Attaque (buts/match)", value=LIIGA_TEAMS[equipe_ext]["attaque"], step=0.1)
                def_ext = st.number_input("Défense (encaissés/match)", value=LIIGA_TEAMS[equipe_ext]["defense"], step=0.1)
            stats_dom = {"attaque": att_dom, "defense": def_dom}
            stats_ext = {"attaque": att_ext, "defense": def_ext}

        st.divider()
        st.subheader("💰 Cotes (Optionnel)")
        c1, c2, c3 = st.columns(3)
        cote_dom = c1.number_input("1 (Dom)", min_value=1.01, value=None, step=0.01)
        cote_nul = c2.number_input("X (Nul)", min_value=1.01, value=None, step=0.01)
        cote_ext = c3.number_input("2 (Ext)", min_value=1.01, value=None, step=0.01)

        if st.button("LANCER L'ANALYSE DÉTAILLÉE 🚀", use_container_width=True):
            lam_dom = ((stats_dom['attaque'] + stats_ext['defense']) / 2) * 1.05
            lam_ext = ((stats_ext['attaque'] + stats_dom['defense']) / 2) * 0.95
            probs = calculate_all_markets(lam_dom, lam_ext)
            
            st.subheader("🎯 Probabilités")
            st.caption(f"xG calculés : {equipe_dom} = {lam_dom:.2f} | {equipe_ext} = {lam_ext:.2f}")
            
            st.write("### 🎲 Matrice des Scores")
            matrix_data = get_goal_matrix(lam_dom, lam_ext)
            df_matrix = pd.DataFrame(matrix_data).style.format("{:.2f}")
            st.dataframe(df_matrix, use_container_width=True)
            
            if cote_dom and (probs['1X2'][0] * cote_dom) - 1 > 0:
                st.success(f"💎 VALUE DÉTECTÉE sur Victoire {equipe_dom} !")
            if cote_ext and (probs['1X2'][2] * cote_ext) - 1 > 0:
                st.success(f"💎 VALUE DÉTECTÉE sur Victoire {equipe_ext} !")

# ==========================================
# PAGE 3 : TRACKER & BANKROLL
# ==========================================
elif navigation == "📜 Tracker & Bankroll":
    st.subheader("📊 Tableau de Bord de Performance")
    
    brier = calculate_brier_score(st.session_state.historique)
    logloss = calculate_log_loss(st.session_state.historique)
    profit = st.session_state.bankroll - 1000.0
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("💰 Bankroll", f"{st.session_state.bankroll:.2f} €", f"{profit:+.2f} €")
    m2.metric("🎯 Brier Score", f"{brier:.3f}", help="Plus proche de 0 = Meilleur. (0.25 = Hasard)")
    m3.metric("📉 Log-Loss", f"{logloss:.3f}", help="Plus bas = Mieux.")
    
    total_regles = len([p for p in st.session_state.historique if p["Statut"] in ["Gagné", "Perdu"]])
    reussite = len([p for p in st.session_state.historique if p["Statut"] == "Gagné"]) / total_regles * 100 if total_regles > 0 else 0
    m4.metric("🏆 Taux Réussite", f"{reussite:.1f} %")

    st.divider()
    
    if len(st.session_state.historique) == 0:
        st.info("Aucun pari. Utilise le Scanner pour en ajouter !")
    else:
        df_hist = pd.DataFrame(st.session_state.historique)
        st.dataframe(df_hist[["Date", "Match", "Marche", "Proba", "Cote", "Statut", "Gain_Net"]], use_container_width=True)

        st.divider()
        st.write("**Mettre à jour les résultats :**")
        
        matchs_en_attente = [i for i, m in enumerate(st.session_state.historique) if m["Statut"] == "En attente"]
        
        if matchs_en_attente:
            choix = st.selectbox("Choisis le match à régler", matchs_en_attente, 
                                 format_func=lambda x: f"{st.session_state.historique[x]['Match']} - {st.session_state.historique[x]['Marche']}")
            
            col_upd1, col_upd2 = st.columns(2)
            with col_upd1:
                if st.button("✅ GAGNÉ"):
                    idx = choix
                    cote = st.session_state.historique[idx]["Cote"]
                    mise = 10.0 
                    gain = mise * (cote - 1)
                    st.session_state.historique[idx]["Statut"] = "Gagné"
                    st.session_state.historique[idx]["Gain_Net"] = gain
                    st.session_state.bankroll += gain
                    st.rerun()
            with col_upd2:
                if st.button("❌ PERDU"):
                    idx = choix
                    mise = 10.0
                    st.session_state.historique[idx]["Statut"] = "Perdu"
                    st.session_state.historique[idx]["Gain_Net"] = -mise
                    st.session_state.bankroll -= mise
                    st.rerun()
