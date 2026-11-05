from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")


@st.cache_data
def charger_donnees():
    return pd.read_csv(DOSSIER / "consommation_propre.csv")


donnees = charger_donnees()
st.write(
    "Ces données couvrent 12 quartiers de quatre communes, de janvier 2024 à décembre 2025."
)
st.write(
    "Elles ont été nettoyées et enrichies avec les informations sur les quartiers et la météo."
)
st.write(f"Le fichier propre compte {len(donnees)} lignes.")
st.dataframe(donnees.head(10), hide_index=True)
