import streamlit as st
from core.leagues import LEAGUES, list_markets, compute_points

st.set_page_config(page_title="HYPER-ICE 360", page_icon="🧊")

st.title("🧊 HYPER-ICE 360")
st.subheader("Moteur d'analyse Hockey sur Glace")

st.write("Bienvenue partenaire ! L'interface est maintenant connectée au cerveau du projet.")

st.divider()

# --- Choix de la ligue ---
ligue_id = st.selectbox("Choisis la ligue", list(LEAGUES.keys()))
ligue = LEAGUES[ligue_id]

# Affichage des infos de la ligue choisie
st.info(f"**{ligue.name}** ({ligue.country}) — Niveau de données : {ligue.capability}")

st.write("### Marchés disponibles :")
for marche in list_markets(ligue_id):
    st.write(f"- {marche}")

st.divider()

# --- Petit simulateur de points ---
st.write("### Simulateur de points au classement")
st.write("Rentre un score pour voir les points attribués selon la ligue :")

col1, col2 = st.columns(2)

with col1:
    st.write("**Équipe Domicile**")
    score_dom_60 = st.number_input("Buts à 60 min", min_value=0, value=2, key="dom_60")
    score_dom_fin = st.number_input("Buts Finaux (OT/SO)", min_value=0, value=3, key="dom_fin")

with col2:
    st.write("**Équipe Extérieur**")
    score_ext_60 = st.number_input("Buts à 60 min", min_value=0, value=2, key="ext_60")
    score_ext_fin = st.number_input("Buts Finaux (OT/SO)", min_value=0, value=2, key="ext_fin")

if st.button("Calculer les points"):
    try:
        pts_dom, pts_ext = compute_points(
            ligue_id, score_dom_60, score_ext_60, score_dom_fin, score_ext_fin
        )
        st.success(f"Résultat : Domicile **{pts_dom} pts** | Extérieur **{pts_ext} pts**")
    except Exception as e:
        st.error(f"Erreur : {e}")
