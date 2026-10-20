import streamlit as st
import pandas as pd
from core.leagues import LEAGUES, list_markets, compute_points
from core.math_engine import calculate_all_markets, get_naive_baseline, get_goal_matrix
from core.nhl_api import NHL_TEAMS, get_team_real_stats, get_team_last_games
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
    
    /* Style pour les logos */
    .team-logo { display: block; margin-left: auto; margin-right: auto; width: 80px; height: 80px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'historique' not in st.session_state:
    st.session_state.historique = []
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0

st.markdown('<p class="main-title">🏒 HYPER-ICE 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Moteur d\'analyse prédictive & Gestion des risques</p>', unsafe_allow_html=True)

tab_analyse, tab_historique = st.tabs(["🔍 Analyse du Match", "📜 Tracker de Paris & Bankroll"])

with tab_analyse:
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            ligue_id = st.selectbox("🏆 Compétition", list(LEAGUES.keys()))
            ligue = LEAGUES[ligue_id]
        with col2:
            date_match = st.date_input("📅 Date du match", datetime.date.today())
        with col3:
            st.write("Niveau données")
            st.info(f"**{ligue.capability}**")

        st.divider()

        st.subheader("⚔️ Confrontation")
        col_dom, col_ext = st.columns(2)
        xg_dom_auto = None
        xg_ext_auto = None
        stats_dom, stats_ext = None, None

        if ligue_id == "NHL":
            with col_dom:
                st.markdown("### 🏠 Domicile")
                equipe_dom = st.selectbox("Équipe Domicile", list(NHL_TEAMS.keys()), key="sel_dom")
                stats_dom = get_team_real_stats(NHL_TEAMS[equipe_dom])
                if stats_dom:
                    # Affichage du Logo
                    st.markdown(f'<img src="{stats_dom["logo"]}" class="team-logo">', unsafe_allow_html=True)
                    st.caption(f"⚔️ Attaque : {stats_dom['attaque']} buts/match")
                    st.caption(f"🛡️ Défense : {stats_dom['defense']} buts encaissés/match")
                    
                    # Forme récente (Le mini backtest visuel)
                    forme_dom = get_team_last_games(NHL_TEAMS[equipe_dom])
                    forme_str = " ".join(["🟢" if r == "V" else "🔴" for r in forme_dom])
                    st.caption(f"Forme (5 derniers) : {forme_str}")

            with col_ext:
                st.markdown("### ✈️ Extérieur")
                equipe_ext = st.selectbox("Équipe Extérieur", list(NHL_TEAMS.keys()), index=1, key="sel_ext")
                stats_ext = get_team_real_stats(NHL_TEAMS[equipe_ext])
                if stats_ext:
                    # Affichage du Logo
                    st.markdown(f'<img src="{stats_ext["logo"]}" class="team-logo">', unsafe_allow_html=True)
                    st.caption(f"⚔️ Attaque : {stats_ext['attaque']} buts/match")
                    st.caption(f"🛡️ Défense : {stats_ext['defense']} buts encaissés/match")
                    
                    # Forme récente
                    forme_ext = get_team_last_games(NHL_TEAMS[equipe_ext])
                    forme_str = " ".join(["🟢" if r == "V" else "🔴" for r in forme_ext])
                    st.caption(f"Forme (5 derniers) : {forme_str}")
        else:
            with col_dom:
                st.markdown("### 🏠 Domicile")
                equipe_dom = st.text_input("Nom de l'équipe", value="", placeholder="Ex: Färjestad BK", key="nom_dom")
            with col_ext:
                st.markdown("### ✈️ Extérieur")
                equipe_ext = st.text_input("Nom de l'équipe", value="", placeholder="Ex: Frölunda HC", key="nom_ext")

        st.divider()

        st.subheader("📊 Ajustement manuel (xG)")
        col_stat_dom, col_stat_ext = st.columns(2)
        with col_stat_dom:
            xg_dom = st.number_input("xG Domicile (Optionnel)", value=None, step=0.1, key="xg_dom", placeholder="Laisser vide pour l'auto")
        with col_stat_ext:
            xg_ext = st.number_input("xG Extérieur (Optionnel)", value=None, step=0.1, key="xg_ext", placeholder="Laisser vide pour l'auto")

        st.divider()

        st.subheader("💰 Cotes du Bookmaker (Optionnel)")
        c1, c2, c3 = st.columns(3)
        cote_dom = c1.number_input("1 (Dom)", min_value=1.01, value=None, step=0.01, key="c_dom", placeholder="2.10")
        cote_nul = c2.number_input("X (Nul)", min_value=1.01, value=None, step=0.01, key="c_nul", placeholder="4.20")
        cote_ext = c3.number_input("2 (Ext)", min_value=1.01, value=None, step=0.01, key="c_ext", placeholder="3.50")
        
        c4, c5 = st.columns(2)
        cote_final_dom = c4.number_input(f"Vainqueur Final {equipe_dom if equipe_dom else 'Dom'}", min_value=1.01, value=None, step=0.01, key="c_fdom", placeholder="1.80")
        cote_final_ext = c5.number_input(f"Vainqueur Final {equipe_ext if equipe_ext else 'Ext'}", min_value=1.01, value=None, step=0.01, key="c_fext", placeholder="2.00")
        
        c8, c9 = st.columns(2)
        cote_over = c8.number_input("Plus de 5.5 buts", min_value=1.01, value=None, step=0.01, key="c_over", placeholder="1.90")
        cote_under = c9.number_input("Moins de 5.5 buts", min_value=1.01, value=None, step=0.01, key="c_under", placeholder="1.90")

        c6, c7, c10 = st.columns(3)
        cote_h_dom = c6.number_input("Hand. -1.5 (Dom)", min_value=1.01, value=None, step=0.01, key="c_hdom", placeholder="2.50")
        cote_h_ext = c7.number_input("Hand. +1.5 (Ext)", min_value=1.01, value=None, step=0.01, key="c_hext", placeholder="1.50")
        cote_btts = c10.number_input("BTTS (Oui)", min_value=1.01, value=None, step=0.01, key="c_btts", placeholder="1.75")

        st.divider()

        if st.button("LANCER L'ANALYSE 🚀"):
            nom_dom = equipe_dom if equipe_dom else "Domicile"
            nom_ext = equipe_ext if equipe_ext else "Extérieur"
            
            if ligue_id == "NHL" and stats_dom and stats_ext and xg_dom is None:
                lam_dom = ((stats_dom['attaque'] + stats_ext['defense']) / 2) * 1.05
                lam_ext = ((stats_ext['attaque'] + stats_dom['defense']) / 2) * 0.95
            else:
                lam_dom = xg_dom if xg_dom is not None else 3.0
                lam_ext = xg_ext if xg_ext is not None else 2.7
            
            probs = calculate_all_markets(lam_dom, lam_ext)
            base_probs = get_naive_baseline(ligue_id)

            p_dom, p_nul, p_ext = probs["1X2"]
            pf_dom, pf_ext = probs["final_1X2"]
            b_dom, b_nul, b_ext = base_probs["1X2"]

            best_bet = None
            best_ev = 0
            def check_best(proba, cote, nom, prob_str):
                global best_bet, best_ev
                if cote and cote > 1.0:
                    ev = (proba * cote) - 1
                    if ev > best_ev:
                        best_ev = ev
                        best_bet = {"nom": nom, "cote": cote, "proba": prob_str}

            check_best(p_dom, cote_dom, f"Victoire {nom_dom}", f"{p_dom*100:.1f}%")
            check_best(p_nul, cote_nul, "Match Nul", f"{p_nul*100:.1f}%")
            check_best(p_ext, cote_ext, f"Victoire {nom_ext}", f"{p_ext*100:.1f}%")
            check_best(probs['over_5_5'], cote_over, "Plus de 5.5 buts", f"{probs['over_5_5']*100:.1f}%")
            check_best(probs['under_5_5'], cote_under, "Moins de 5.5 buts", f"{probs['under_5_5']*100:.1f}%")
            check_best(probs['btts_yes'], cote_btts, "BTTS Oui", f"{probs['btts_yes']*100:.1f}%")
            check_best(pf_dom, cote_final_dom, f"Vainqueur Final {nom_dom}", f"{pf_dom*100:.1f}%")
            check_best(pf_ext, cote_final_ext, f"Vainqueur Final {nom_ext}", f"{pf_ext*100:.1f}%")

            analyse_data = {
                "Date": str(date_match),
                "Match": f"{nom_dom} vs {nom_ext}",
                "Ligue": ligue_id,
                "xG Dom": round(lam_dom, 2),
                "xG Ext": round(lam_ext, 2),
                "Proba 1": f"{p_dom*100:.1f} %",
                "Proba 2": f"{p_ext*100:.1f} %",
                "Pari Conseillé": best_bet["nom"] if best_ev > 0 else "Aucun (pas de valeur)",
                "Cote": best_bet["cote"] if best_ev > 0 else 0.0,
                "Statut": "En attente",
                "Gain_Net": 0.0
            }
            st.session_state.historique.append(analyse_data)
            st.toast("Analyse sauvegardée dans le tracker !", icon="✅")

            st.subheader("🎯 Probabilités du Modèle")
            st.caption(f"xG calculés : {nom_dom} = {lam_dom:.2f} | {nom_ext} = {lam_ext:.2f}")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(label=f"Victoire {nom_dom}", value=f"{p_dom*100:.1f} %", delta=f"{(p_dom - b_dom)*100:+.1f}% vs Naïf")
            with c2:
                st.metric(label="Match Nul", value=f"{p_nul*100:.1f} %", delta=f"{(p_nul - b_nul)*100:+.1f}% vs Naïf")
            with c3:
                st.metric(label=f"Victoire {nom_ext}", value=f"{p_ext*100:.1f} %", delta=f"{(p_ext - b_ext)*100:+.1f}% vs Naïf")
            
            st.write("### 🎲 Matrice des Scores (Probabilités en %)")
            st.caption(f"Lignes = Buts {nom_dom} | Colonnes = Buts {nom_ext}")
            
            matrix_data = get_goal_matrix(lam_dom, lam_ext, max_goals=5)
            df_matrix = pd.DataFrame(matrix_data)
            df_matrix.index = [f"{i} buts" for i in range(6)]
            df_matrix.columns = [f"{i} buts" for i in range(6)]
            
            st.dataframe(df_matrix.style.format("{:.2f}"), use_container_width=True)

            if best_ev > 0:
                st.success(f"💎 **Meilleur Value Bet détecté :** {best_bet['nom']} à la cote {best_bet['cote']} (EV: +{best_ev*100:.1f}%)")

with tab_historique:
    st.subheader("💰 Gestion de Bankroll")
    
    col_bk1, col_bk2 = st.columns(2)
    col_bk1.metric("Bankroll Actuelle", f"{st.session_state.bankroll:.2f} €")
    
    profit = st.session_state.bankroll - 1000.0
    col_bk2.metric("Profit / Perte", f"{profit:+.2f} €", delta=f"{profit:.2f} €")

    st.divider()
    
    st.subheader("📜 Tes paris en cours et passés")
    
    if len(st.session_state.historique) == 0:
        st.info("Aucune analyse pour le moment. Va dans l'onglet Analyse !")
    else:
        df_hist = pd.DataFrame(st.session_state.historique)
        st.dataframe(df_hist[["Date", "Match", "Pari Conseillé", "Cote", "Statut", "Gain_Net"]], use_container_width=True)

        st.divider()
        st.write("**Mettre à jour un résultat ?**")
        
        matchs_en_attente = [i for i, m in enumerate(st.session_state.historique) if m["Statut"] == "En attente"]
        
        if matchs_en_attente:
            choix = st.selectbox("Choisis le match terminé", matchs_en_attente, format_func=lambda x: st.session_state.historique[x]["Match"])
            
            col_upd1, col_upd2 = st.columns(2)
            with col_upd1:
                if st.button("✅ Le pari est GAGNÉ"):
                    idx = choix
                    cote = st.session_state.historique[idx]["Cote"]
                    mise = 10.0 
                    gain = mise * (cote - 1)
                    
                    st.session_state.historique[idx]["Statut"] = "Gagné"
                    st.session_state.historique[idx]["Gain_Net"] = gain
                    st.session_state.bankroll += gain
                    st.rerun()
                    
            with col_upd2:
                if st.button("❌ Le pari est PERDU"):
                    idx = choix
                    mise = 10.0
                    
                    st.session_state.historique[idx]["Statut"] = "Perdu"
                    st.session_state.historique[idx]["Gain_Net"] = -mise
                    st.session_state.bankroll -= mise
                    st.rerun()
        else:
            st.success("Tous tes paris sont réglés !")
            
        if st.button("🗑️ Réinitialiser le tracker (Danger)"):
            st.session_state.historique = []
            st.session_state.bankroll = 1000.0
            st.rerun()
