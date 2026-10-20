import streamlit as st

st.set_page_config(page_title="HYPER-ICE 360", page_icon="🧊")
st.title("🧊 HYPER-ICE 360")
st.write("Bienvenue ! L'interface fonctionne.")

ligue = st.selectbox("Choisis la ligue", ["NHL", "SHL", "Liiga"])
st.write(f"Tu as choisi : {ligue}")

if st.button("Analyser"):
    st.success("Prêt pour les calculs !")
