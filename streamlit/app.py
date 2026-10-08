from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Doit être la toute première commande Streamlit
st.set_page_config(page_title="Le radar client - GlobalShop Direct", page_icon="🛒", layout="wide")

# Dossier des fichiers sauvegardés par le notebook (app.py est dans streamlit/, models/ est à la racine du repo)
DOSSIER_MODELES = Path(__file__).resolve().parent.parent / "models"

# Palette Sauge et sable
SAUGE = "#6B8F71"
SAUGE_FONCE = "#2F3A32"
SABLE = "#D4A373"
FOND = "#F7F5F0"

# Une couleur par segment (sans rouge ni vert)
COULEURS_SEGMENTS = {
    "Champions": "#FFD700",
    "Fidèles": "#4682B4",
    "Prometteurs": "#800080",
    "Occasionnels": "#FF8C00",
    "À risque": "#000000",
    "Perdus": "#808080",
}

# Style de la page (fond, bandeau, cartes, bouton)
st.markdown(
    f"""
    <style>
        .stApp {{ background: {FOND}; }}
        .block-container {{ padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1000px; }}
        h1, h2, h3, label, p {{ color: {SAUGE_FONCE}; }}

        .bandeau {{
            background: linear-gradient(135deg, {SAUGE} 0%, #4F6F55 100%);
            border-radius: 14px; padding: 1.1rem 1.6rem; margin-bottom: 1rem;
        }}
        .bandeau h1 {{ color: #FFFFFF; margin: 0 0 0.3rem 0; padding: 0; font-size: 1.7rem; }}
        .bandeau p {{ color: #EEF3EC; margin: 0; font-size: 0.95rem; line-height: 1.4; }}
        .bandeau .pastille {{
            display: inline-block; background: {SABLE}; color: {SAUGE_FONCE};
            font-size: 0.78rem; font-weight: 700; letter-spacing: 0.04em;
            padding: 0.15rem 0.7rem; border-radius: 999px; margin-bottom: 0.5rem;
        }}

        .titre-section {{
            font-size: 0.85rem; font-weight: 700; letter-spacing: 0.06em;
            text-transform: uppercase; color: {SAUGE}; margin: 0.4rem 0 0.4rem 0;
        }}

        div[data-testid="stNumberInput"] div[data-baseweb="input"],
        div[data-testid="stNumberInput"] div[data-baseweb="input"] > div {{
            background: #FFFFFF; border-radius: 8px;
        }}
        div[data-testid="stNumberInput"] input {{
            background: #FFFFFF; color: {SAUGE_FONCE};
            -webkit-text-fill-color: {SAUGE_FONCE}; font-weight: 600;
        }}
        /* On masque les boutons + et - : on tape directement la valeur */
        [data-testid="stNumberInputStepUp"],
        [data-testid="stNumberInputStepDown"] {{ display: none; }}

        div.stButton > button {{
            background: {SAUGE}; color: #FFFFFF; border: none; border-radius: 10px;
            padding: 0.65rem 1.6rem; font-weight: 600; font-size: 1rem;
        }}
        div.stButton > button:hover {{ background: #587A5E; color: #FFFFFF; }}

        .carte {{
            background: #FFFFFF; border-radius: 14px; padding: 1.4rem 1.7rem;
            margin-top: 0.4rem; box-shadow: 0 2px 10px rgba(47, 58, 50, 0.08);
        }}
        .carte-vide {{
            border: 2px dashed #C9D3C6; border-radius: 14px; padding: 2.4rem 1.5rem;
            text-align: center; color: #6F7B72; margin-top: 0.4rem;
        }}
        .carte .etiquette {{ margin: 0; color: #6F7B72; font-size: 0.9rem; }}
        .carte .segment {{ margin: 0.1rem 0 1rem 0; font-size: 2.4rem; font-weight: 800; color: {SAUGE_FONCE}; }}
        .carte .action {{
            background: {FOND}; border-radius: 10px; padding: 0.9rem 1.1rem;
            margin: 0; color: {SAUGE_FONCE}; line-height: 1.5;
        }}
        .carte .action b {{ color: {SAUGE}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def charger_modeles():
    scaler = joblib.load(DOSSIER_MODELES / "scaler.joblib")
    modele = joblib.load(DOSSIER_MODELES / "kmeans_final.joblib")
    dicos = joblib.load(DOSSIER_MODELES / "segments.joblib")
    return scaler, modele, dicos


scaler, modele, dicos = charger_modeles()

# Bandeau d'en-tête
st.markdown(
    """
    <div class="bandeau">
        <span class="pastille">SEGMENTATION RFM</span>
        <h1>Le radar client de GlobalShop Direct</h1>
        <p>Renseignez l'historique d'un client. Le modèle le range dans l'un des 6 segments
        et propose l'action marketing adaptée.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Saisies à gauche et résultat à droite
gauche, droite = st.columns([1, 1.1], gap="large")

with gauche:
    st.markdown('<p class="titre-section">Historique du client</p>', unsafe_allow_html=True)
    recence = st.number_input("Récence (jours)", min_value=1, step=1,
                              help="Nombre de jours depuis le dernier achat")
    frequence = st.number_input("Fréquence (commandes)", min_value=1, step=1,
                                help="Nombre de commandes passées")
    montant = st.number_input("Montant (£)", min_value=0.01, step=10.0,
                              help="Total net dépensé, annulations déduites")
    lancer = st.button("Trouver le segment", type="primary")

with droite:
    st.markdown('<p class="titre-section">Résultat</p>', unsafe_allow_html=True)
    if lancer:
        # Même chemin que dans le notebook : log1p, standardisation, prédiction
        client = pd.DataFrame({"recence": [recence], "frequence": [frequence], "montant": [montant]})
        client_log = np.log1p(client)
        client_standardise = pd.DataFrame(scaler.transform(client_log), columns=client.columns)
        cluster = modele.predict(client_standardise)[0]

        segment = dicos["noms_segments"][cluster]
        action = dicos["actions_segments"][segment]
        couleur = COULEURS_SEGMENTS.get(segment, SAUGE)

        # Carte de résultat : bande de la couleur du segment à gauche
        st.markdown(
            f"""
            <div class="carte" style="border-left: 10px solid {couleur};">
                <p class="etiquette">Ce client appartient au segment</p>
                <p class="segment">{segment}</p>
                <p class="action"><b>Action recommandée</b><br>{action}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="carte-vide">Le segment du client apparaîtra ici.</div>',
            unsafe_allow_html=True,
        )