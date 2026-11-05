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

if donnees_filtrees.empty:
    valeurs_indicateurs = ("—", "—", "—")
else:
    valeurs_indicateurs = (
        f"{donnees_filtrees['kwh'].sum() / 1_000_000:.2f} millions de kWh",
        f"{donnees_filtrees['kwh_par_abonne'].mean():.1f} kWh",
        f"{donnees_filtrees['heures_courant'].mean():.1f} heures",
    )

col_kwh, col_abonne, col_heures = st.columns(3)
col_kwh.metric("Consommation totale", valeurs_indicateurs[0])
col_abonne.metric("Consommation par abonné", valeurs_indicateurs[1])
col_heures.metric("Heures de courant par jour", valeurs_indicateurs[2])

st.dataframe(donnees_filtrees.head(10), hide_index=True)
