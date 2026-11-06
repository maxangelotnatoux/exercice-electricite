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

donnees_analyse = donnees.loc[donnees["commune"].isin(communes_choisies)]
st.caption(
    "Les analyses des onglets couvrent 2024 et 2025; le filtre Année s'applique "
    "aux indicateurs et au tableau ci-dessous."
)
onglet_quartiers, onglet_evolution, onglet_courant, onglet_coupures, onglet_records = (
    st.tabs(
        [
            "Par quartier",
            "Évolution",
            "Chaleur ou courant ?",
            "Coupures",
            "Relevés records",
        ]
    )
)

with onglet_quartiers:
    if donnees_analyse.empty:
        st.info("Sélectionnez au moins une commune pour afficher cette analyse.")
    else:
        classement = (
            donnees_analyse.groupby("quartier")["kwh_par_abonne"]
            .mean()
            .sort_values(ascending=False)
            .rename("kWh par abonné")
        )
        moyennes_type = donnees_analyse.groupby("type")["kwh_par_abonne"].mean()
        st.bar_chart(classement)
        if {"Commercial", "Résidentiel"}.issubset(moyennes_type.index):
            st.write(
                f"En moyenne, les quartiers commerciaux consomment "
                f"{moyennes_type['Commercial']:.1f} kWh par abonné, contre "
                f"{moyennes_type['Résidentiel']:.1f} kWh dans les quartiers "
                f"résidentiels. En tête : {classement.index[0]} "
                f"({classement.iloc[0]:.1f} kWh par abonné)."
            )
        else:
            st.write(
                f"En tête du classement : {classement.index[0]} "
                f"({classement.iloc[0]:.1f} kWh par abonné)."
            )

with onglet_evolution:
    if donnees_analyse.empty:
        st.info("Sélectionnez au moins une commune pour afficher cette analyse.")
    else:
        consommation_mensuelle = (
            donnees_analyse.groupby(["mois", "commune"])
            .agg(kwh_total=("kwh", "sum"), abonnes=("abonnes", "sum"))
            .assign(kwh_par_abonne=lambda df: df["kwh_total"] / df["abonnes"])
            .reset_index()
            .pivot(index="mois", columns="commune", values="kwh_par_abonne")
        )
        st.line_chart(consommation_mensuelle)

        totaux_annuels = donnees_analyse.pivot_table(
            index="commune", columns="annee", values="kwh", aggfunc="sum"
        )
        if {2024, 2025}.issubset(totaux_annuels.columns):
            hausses = (
                (totaux_annuels[2025] / totaux_annuels[2024] - 1) * 100
            ).sort_values(ascending=False)
            commune_max = hausses.index[0]
            st.write(
                f"La hausse la plus forte est à {commune_max} "
                f"({totaux_annuels.loc[commune_max, 2024] / 1_000_000:.2f} à "
                f"{totaux_annuels.loc[commune_max, 2025] / 1_000_000:.2f} "
                f"millions de kWh, soit +{hausses.iloc[0]:.1f} %)."
            )

with onglet_courant:
    residentiel = donnees_analyse.loc[donnees_analyse["type"] == "Résidentiel"]
    if residentiel.empty:
        st.info("Aucune donnée résidentielle pour les communes sélectionnées.")
    else:
        st.scatter_chart(
            residentiel,
            x="heures_courant",
            y="kwh_par_abonne",
        )
        correlation_heures = residentiel["kwh_par_abonne"].corr(
            residentiel["heures_courant"]
        )
        correlation_temperature = residentiel["kwh_par_abonne"].corr(
            residentiel["temperature_c"]
        )
        st.write(
            f"Dans les quartiers résidentiels, la corrélation est de "
            f"{correlation_heures:.2f} avec les heures de courant et de "
            f"{correlation_temperature:.2f} avec la température."
        )

with onglet_coupures:
    if donnees_analyse.empty:
        st.info("Sélectionnez au moins une commune pour afficher cette analyse.")
    else:
        heures_par_commune = donnees_analyse.groupby("commune")[
            "heures_courant"
        ].median()
        st.bar_chart(heures_par_commune.rename("Médiane d'heures par jour"))
        moins_de_huit_heures = donnees_analyse.loc[
            (donnees_analyse["annee"] == 2025)
            & (donnees_analyse["heures_courant"] < 8)
        ]
        phrase_coupures = (
            f"En 2025, {len(moins_de_huit_heures)} relevés indiquent moins de "
            "8 heures de courant par jour."
        )
        if "Cap-Haïtien" in heures_par_commune.index:
            phrase_coupures = (
                f"La médiane à Cap-Haïtien est de "
                f"{heures_par_commune['Cap-Haïtien']:.1f} heures par jour. "
                + phrase_coupures
            )
        st.write(phrase_coupures)
        if not moins_de_huit_heures.empty:
            st.dataframe(
                moins_de_huit_heures[
                    ["mois", "quartier", "heures_courant"]
                ],
                hide_index=True,
            )

with onglet_records:
    if donnees_analyse.empty:
        st.info("Sélectionnez au moins une commune pour afficher cette analyse.")
    else:
        records = donnees_analyse.nlargest(3, "kwh").copy()
        records["relevé"] = records["quartier"] + " — " + records["mois"]
        st.bar_chart(records.set_index("relevé")["kwh"])
        premier = records.iloc[0]
        st.write(
            f"Le relevé le plus élevé est celui de {premier['quartier']} "
            f"({premier['mois']}) : {premier['kwh']:.0f} kWh."
        )

st.dataframe(donnees_filtrees.head(10), hide_index=True)
