import streamlit as st
from core.leagues import LEAGUES, list_markets, compute_points
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
    # Ligne 1 : Ligue et Date
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

    # Ligne 2 : Les Équipes (Vides par défaut)
    st.subheader("⚔️ Confrontation")
    col_dom, col_ext = st.columns(2)
    
    with col_dom:
        st.markdown("### 🏠 Domicile")
        equipe_dom = st.text_input("Nom de l'équipe", value="", placeholder="Ex: Maple Leafs", key="nom_dom")
        
    with col_ext:
        st.markdown("### ✈️ Extérieur")
        equipe_ext = st.text_input("Nom de l'équipe", value="", placeholder="Ex: Canadiens", key="nom_ext")

    st.divider()

    # Ligne 3 : Statistiques (Vides par défaut)
    st.subheader("📊 Statistiques Avancées (Optionnel)")
    col_stat_dom, col_stat_ext = st.columns(2)
    
    with col_stat_dom:
        st.caption(f"Stats de l'équipe Domicile")
        xg_dom = st.number_input("xG (Buts attendus)", value=None, step=0.1, key="xg_dom", placeholder="Ex: 2.5")
        tirs_dom = st.number_input("Tirs au but", value=None, step=1, key="tirs_dom", placeholder="Ex: 30")
        
    with col_stat_ext:
        st.caption(f"Stats de l'équipe Extérieur")
        xg_ext = st.number_input("xG (Buts attendus)", value=None, step=0.1, key="xg_ext", placeholder="Ex: 1.8")
        tirs_ext = st.number_input("Tirs au but", value=None, step=1, key="tirs_ext", placeholder="Ex: 25")

    st.divider()

    # Ligne 4 : Le Simulateur (Vide par défaut)
    st.subheader("🧮 Simulateur de points (Test du moteur)")
    st.caption("Vérifie comment les règles de la ligue s'appliquent.")
    
    col_sim1, col_sim2 = st.columns(2)
    with col_sim1:
        score_dom_60 = st.number_input("Buts Dom (60 min)", min_value=0, value=None, key="sim_dom_60", placeholder="0")
        score_dom_fin = st.number_input("Buts Dom (Final)", min_value=0, value=None, key="sim_dom_fin", placeholder="0")
    with col_sim2:
        score_ext_60 = st.number_input("Buts Ext (60 min)", min_value=0, value=None, key="sim_ext_60", placeholder="0")
        score_ext_fin = st.number_input("Buts Ext (Final)", min_value=0, value=None, key="sim_ext_fin", placeholder="0")

    # Bouton d'action
    if st.button("LANCER L'ANALYSE 🚀"):
        
        # On remplace les champs vides par 0 pour éviter les erreurs
        v_dom_60 = score_dom_60 if score_dom_60 is not None else 0
        v_dom_fin = score_dom_fin if score_dom_fin is not None else 0
        v_ext_60 = score_ext_60 if score_ext_60 is not None else 0
        v_ext_fin = score_ext_fin if score_ext_fin is not None else 0
        
        nom_dom = equipe_dom if equipe_dom else "Équipe Domicile"
        nom_ext = equipe_ext if equipe_ext else "Équipe Extérieur"

        try:
            # Calcul des points
            pts_dom, pts_ext = compute_points(
                ligue_id, v_dom_60, v_ext_60, v_dom_fin, v_ext_fin
            )
            
            st.success(f"**Analyse terminée pour {nom_dom} vs {nom_ext} ({ligue.name})**")
            
            # Affichage des résultats
            res1, res2 = st.columns(2)
            res1.metric(label=f"Points {nom_dom}", value=f"{pts_dom} pts")
            res2.metric(label=f"Points {nom_ext}", value=f"{pts_ext} pts")
            
            st.info(f"ℹ️ Règles appliquées : Système {ligue.points_system} | Format OT : {ligue.ot_format}")
            
        except Exception as e:
            st.error(f"Erreur de calcul : {e}")
