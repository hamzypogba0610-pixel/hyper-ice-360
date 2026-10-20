import streamlit as st
from core.leagues import LEAGUES, list_markets, compute_points
from core.math_engine import calculate_all_markets
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="HYPER-ICE 360", page_icon="🏒", layout="wide")

# --- DESIGN CSS (Couleurs Hockey) ---
st.markdown("""
    <style>
    .stApp { background-color: #0A192F; }
    h1, h2, h3, h4, p, label { color: #E6F1FF !important; font-family: 'Helvetica Neue', sans-serif; }
    .main-title {
        color: #64FFDA !important; font-size: 3em; font-weight: 900;
        text-align: center; text-transform: uppercase; letter-spacing: 3px;
        text-shadow: 2px 2px 10px rgba(100, 255, 218, 0.3); margin-bottom: 0;
    }
    .sub-title { text-align: center; color: #8892B0 !important; font-size: 1.2em; margin-bottom: 2em; }
    .stButton>button {
        background-color: #64FFDA; color: #0A192F; font-weight: bold; font-size: 1.1em;
        border-radius: 8px; border: 2px solid #64FFDA; width: 100%; transition: 0.3s;
    }
    .stButton>button:hover { background-color: transparent; color: #64FFDA; }
    .stSelectbox, .stNumberInput, .stTextInput { background-color: #112240; border-radius: 8px; }
    hr { border-color: #233554; }
    </style>
""", unsafe_allow_html=True)

# --- EN-TÊTE ---
st.markdown('<p class="main-title">🏒 HYPER-ICE 360</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Moteur d\'analyse prédictive & Gestion des risques</p>', unsafe_allow_html=True)

# --- FORMULAIRE PRINCIPAL ---
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
    st.caption("Rentre les cotes pour voir si le modèle détecte une 'Value'.")
    
    # Ligne 1X2
    c1, c2, c3 = st.columns(3)
    cote_dom = c1.number_input(f"Cote 1 (Dom)", min_value=1.01, value=None, step=0.01, key="cote_dom", placeholder="Ex: 2.10")
    cote_nul = c2.number_input("Cote X (Nul)", min_value=1.01, value=None, step=0.01, key="cote_nul", placeholder="Ex: 4.20")
    cote_ext = c3.number_input(f"Cote 2 (Ext)", min_value=1.01, value=None, step=0.01, key="cote_ext", placeholder="Ex: 3.50")
    
    # Ligne Over/Under & BTTS
    c4, c5, c6 = st.columns(3)
    cote_over = c4.number_input("Cote + de 5.5 buts", min_value=1.01, value=None, step=0.01, key="cote_over", placeholder="Ex: 1.90")
    cote_under = c5.number_input("Cote - de 5.5 buts", min_value=1.01, value=None, step=0.01, key="cote_under", placeholder="Ex: 1.90")
    cote_btts = c6.number_input("Cote Les 2 marquent (Oui)", min_value=1.01, value=None, step=0.01, key="cote_btts", placeholder="Ex: 1.75")

    st.divider()

    if st.button("LANCER L'ANALYSE 🚀"):
        nom_dom = equipe_dom if equipe_dom else "Équipe Domicile"
        nom_ext = equipe_ext if equipe_ext else "Équipe Extérieur"
        
        lam_dom = xg_dom if xg_dom is not None else 3.0
        lam_ext = xg_ext if xg_ext is not None else 2.7
        
        # Appel du cerveau (qui renvoie maintenant un dictionnaire)
        probs = calculate_all_markets(lam_dom, lam_ext)
        
        p_dom, p_nul, p_ext = probs["1X2"]

        st.subheader("🎯 Probabilités du Modèle")
        st.write(f"*Basé sur xG : {nom_dom} = {lam_dom} | {nom_ext} = {lam_ext}*")
        
        # Affichage des probas
        prob1, prob2, prob3 = st.columns(3)
        prob1.metric(label=f"Victoire {nom_dom}", value=f"{p_dom*100:.1f} %")
        prob2.metric(label="Match Nul", value=f"{p_nul*100:.1f} %")
        prob3.metric(label=f"Victoire {nom_ext}", value=f"{p_ext*100:.1f} %")
        
        prob4, prob5, prob6 = st.columns(3)
        prob4.metric(label="+ de 5.5 buts", value=f"{probs['over_5_5']*100:.1f} %")
        prob5.metric(label="- de 5.5 buts", value=f"{probs['under_5_5']*100:.1f} %")
        prob6.metric(label="Les 2 marquent (Oui)", value=f"{probs['btts_yes']*100:.1f} %")

        st.divider()

        # --- DETECTION DE VALEUR ---
        if any([cote_dom, cote_nul, cote_ext, cote_over, cote_under, cote_btts]):
            st.subheader("💎 Analyse de la Valeur (Value Bet)")
            
            def calculer_valeur(proba, cote, nom_pari):
                if cote is None or cote <= 1.0:
                    return
                ev = (proba * cote) - 1
                kelly = ((proba * cote) - 1) / (cote - 1)
                mise = max(0.0, kelly * 0.25) * 100
                
                if ev > 0:
                    st.success(f"✅ **{nom_pari}** : Valeur ! (EV: +{ev*100:.1f}%) | Mise: {mise:.1f}% bankroll")
                else:
                    st.error(f"❌ **{nom_pari}** : Pas de valeur. (EV: {ev*100:.1f}%)")

            calculer_valeur(p_dom, cote_dom, f"Victoire {nom_dom}")
            calculer_valeur(p_nul, cote_nul, "Match Nul")
            calculer_valeur(p_ext, cote_ext, f"Victoire {nom_ext}")
            calculer_valeur(probs['over_5_5'], cote_over, "+ de 5.5 buts")
            calculer_valeur(probs['under_5_5'], cote_under, "- de 5.5 buts")
            calculer_valeur(probs['btts_yes'], cote_btts, "Les 2 marquent (Oui)")

    st.divider()

    with st.expander("🧮 Outil : Simulateur de points (Optionnel)"):
        col_sim1, col_sim2 = st.columns(2)
        with col_sim1:
            s_dom_60 = st.number_input("Buts Dom (60 min)", min_value=0, value=None, key="s_dom_60", placeholder="0")
            s_dom_fin = st.number_input("Buts Dom (Final)", min_value=0, value=None, key="s_dom_fin", placeholder="0")
        with col_sim2:
            s_ext_60 = st.number_input("Buts Ext (60 min)", min_value=0, value=None, key="s_ext_60", placeholder="0")
            s_ext_fin = st.number_input("Buts Ext (Final)", min_value=0, value=None, key="s_ext_fin", placeholder="0")
            
        if st.button("Calculer les points"):
            v_dom_60 = s_dom_60 or 0
            v_dom_fin = s_dom_fin or 0
            v_ext_60 = s_ext_60 or 0
            v_ext_fin = s_ext_fin or 0
            try:
                pts_dom, pts_ext = compute_points(ligue_id, v_dom_60, v_ext_60, v_dom_fin, v_ext_fin)
                st.success(f"**Points : Domicile {pts_dom} | Extérieur {pts_ext}**")
            except Exception as e:
                if "égalité" in str(e):
                    st.warning("⚠️ Un match ne peut pas finir sur un nul. Ajoute un but en OT/SO.")
                else:
                    st.error(f"Erreur : {e}")
