import streamlit as st
from core.leagues import LEAGUES, list_markets, compute_points
from core.math_engine import calculate_all_markets, get_naive_baseline
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
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA MÉMOIRE (HISTORIQUE) ---
if 'historique' not in st.session_state:
    st.session_state.historique = []

st.markdown('<p class="main-title">🏒 HYPER-ICE 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Moteur d\'analyse prédictive & Gestion des risques</p>', unsafe_allow_html=True)

# --- ONGLETS ---
tab_analyse, tab_historique = st.tabs(["🔍 Analyse du Match", "📜 Historique des Prédictions"])

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
        with col_dom:
            st.markdown("### 🏠 Domicile")
            equipe_dom = st.text_input("Nom de l'équipe", value="", placeholder="Ex: Maple Leafs", key="nom_dom")
        with col_ext:
            st.markdown("### ✈️ Extérieur")
            equipe_ext = st.text_input("Nom de l'équipe", value="", placeholder="Ex: Canadiens", key="nom_ext")

        st.divider()

        st.subheader("📊 Statistiques (xG)")
        col_stat_dom, col_stat_ext = st.columns(2)
        with col_stat_dom:
            xg_dom = st.number_input("xG Domicile", value=None, step=0.1, key="xg_dom", placeholder="Ex: 2.5")
        with col_stat_ext:
            xg_ext = st.number_input("xG Extérieur", value=None, step=0.1, key="xg_ext", placeholder="Ex: 1.8")

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
            
            lam_dom = xg_dom if xg_dom is not None else 3.0
            lam_ext = xg_ext if xg_ext is not None else 2.7
            probs = calculate_all_markets(lam_dom, lam_ext)
            base_probs = get_naive_baseline(ligue_id)

            p_dom, p_nul, p_ext = probs["1X2"]
            pf_dom, pf_ext = probs["final_1X2"]
            b_dom, b_nul, b_ext = base_probs["1X2"]

            # --- SAUVEGARDE DANS L'HISTORIQUE ---
            analyse_data = {
                "Date": str(date_match),
                "Match": f"{nom_dom} vs {nom_ext}",
                "Ligue": ligue_id,
                "xG Dom": lam_dom,
                "xG Ext": lam_ext,
                "Proba 1": f"{p_dom*100:.1f} %",
                "Proba X": f"{p_nul*100:.1f} %",
                "Proba 2": f"{p_ext*100:.1f} %",
                "Over 5.5": f"{probs['over_5_5']*100:.1f} %"
            }
            st.session_state.historique.append(analyse_data)
            st.toast("Analyse sauvegardée dans l'historique !", icon="✅")

            st.subheader("🎯 Probabilités du Modèle vs Baseline Naïve")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric(label=f"Victoire {nom_dom}", value=f"{p_dom*100:.1f} %", delta=f"{(p_dom - b_dom)*100:+.1f}% vs Naïf")
            with c2:
                st.metric(label="Match Nul", value=f"{p_nul*100:.1f} %", delta=f"{(p_nul - b_nul)*100:+.1f}% vs Naïf")
            with c3:
                st.metric(label=f"Victoire {nom_ext}", value=f"{p_ext*100:.1f} %", delta=f"{(p_ext - b_ext)*100:+.1f}% vs Naïf")
            
            st.write("**Marché Vainqueur Final (incl. OT/SO)**")
            c4, c5 = st.columns(2)
            c4.metric(label=f"Vainqueur {nom_dom}", value=f"{pf_dom*100:.1f} %")
            c5.metric(label=f"Vainqueur {nom_ext}", value=f"{pf_ext*100:.1f} %")
            
            st.write("**Total Buts (60 minutes)**")
            c8, c9 = st.columns(2)
            c8.metric(label="Plus de 5.5 buts", value=f"{probs['over_5_5']*100:.1f} %")
            c9.metric(label="Moins de 5.5 buts", value=f"{probs['under_5_5']*100:.1f} %")
            
            st.write("**Handicap & BTTS (60 minutes)**")
            c6, c7, c10 = st.columns(3)
            c6.metric(label=f"Handicap -1.5 ({nom_dom})", value=f"{probs['handicap_home']*100:.1f} %")
            c7.metric(label=f"Handicap +1.5 ({nom_ext})", value=f"{probs['handicap_away']*100:.1f} %")
            c10.metric(label="Les 2 marquent (Oui)", value=f"{probs['btts_yes']*100:.1f} %")

            st.divider()

            if any([cote_dom, cote_nul, cote_ext, cote_final_dom, cote_final_ext, cote_h_dom, cote_h_ext, cote_over, cote_under, cote_btts]):
                st.subheader("💎 Analyse de la Valeur (Value Bet)")
                
                def calculer_valeur(proba, cote, nom_pari):
                    if cote is None or cote <= 1.0: return
                    ev = (proba * cote) - 1
                    kelly = ((proba * cote) - 1) / (cote - 1)
                    mise = max(0.0, kelly * 0.25) * 100
                    
                    if ev > 0:
                        st.success(f"✅ **{nom_pari}** : Valeur ! (EV: +{ev*100:.1f}%) | Mise: {mise:.1f}% bankroll")
                    else:
                        st.error(f"❌ **{nom_pari}** : Pas de valeur. (EV: {ev*100:.1f}%)")

                calculer_valeur(p_dom, cote_dom, f"Victoire {nom_dom} (60m)")
                calculer_valeur(p_nul, cote_nul, "Match Nul (60m)")
                calculer_valeur(p_ext, cote_ext, f"Victoire {nom_ext} (60m)")
                calculer_valeur(pf_dom, cote_final_dom, f"Vainqueur Final {nom_dom}")
                calculer_valeur(pf_ext, cote_final_ext, f"Vainqueur Final {nom_ext}")
                calculer_valeur(probs['handicap_home'], cote_h_dom, f"Handicap -1.5 {nom_dom}")
                calculer_valeur(probs['handicap_away'], cote_h_ext, f"Handicap +1.5 {nom_ext}")
                calculer_valeur(probs['over_5_5'], cote_over, "Plus de 5.5 buts")
                calculer_valeur(probs['under_5_5'], cote_under, "Moins de 5.5 buts")
                calculer_valeur(probs['btts_yes'], cote_btts, "Les 2 marquent (Oui)")

# --- ONGLET HISTORIQUE ---
with tab_historique:
    st.subheader("📜 Historique de tes analyses")
    if len(st.session_state.historique) == 0:
        st.info("Aucune analyse pour le moment. Lance une analyse dans le premier onglet !")
    else:
        if st.button("🗑️ Vider l'historique"):
            st.session_state.historique = []
            st.rerun()
        
        # Affichage sous forme de tableau
        st.dataframe(st.session_state.historique, use_container_width=True)
