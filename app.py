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

communes = sorted(donnees["commune"].dropna().unique())
communes_choisies = st.sidebar.multiselect(
    "Communes",
    options=communes,
    default=communes,
)

annees = sorted(donnees["annee"].dropna().unique())
annee_choisie = st.sidebar.selectbox(
    "Année",
    options=annees,
    index=annees.index(2025),
)

if not communes_choisies:
    st.warning("Choisissez au moins une commune pour afficher les données.")
    donnees_filtrees = donnees.iloc[0:0]
else:
    donnees_filtrees = donnees.loc[
        donnees["commune"].isin(communes_choisies)
        & (donnees["annee"] == annee_choisie)
    ]

st.write(f"{len(donnees_filtrees)} lignes pour les filtres sélectionnés.")
st.dataframe(donnees_filtrees.head(10), hide_index=True)
