# GlobalShop Direct - Segmentation clients par RFM

Projet de clustering non supervisé sur les ventes d'un e-commerçant britannique. On range les clients dans 6 segments à partir de leur récence, leur fréquence et leur montant d'achat. Chaque segment reçoit une action marketing.

- **Simulateur Streamlit** : https://globalshop-radar-client.streamlit.app/
- **Dashboard Data Studio** : https://datastudio.google.com/reporting/28c64074-7fdb-4ab2-b672-5196f5004fd7

## Le contexte

GlobalShop Direct veut arrêter de traiter tous ses clients de la même façon. La question posée est simple. Qui sont nos clients et que doit-on faire pour chaque groupe ?

Le projet a été réalisé en binôme avec Zohair dans le cadre de la formation Data Analyst Simplon (brief Machine Learning non supervisé).

## Les données

Le dataset est **Online Retail** de l'UCI. Il contient les lignes de facture d'un détaillant en ligne du 1er décembre 2010 au 9 décembre 2011.

Il n'est pas dans le repo car il est trop lourd. Pour relancer le notebook.

1. Télécharger le fichier sur https://archive.ics.uci.edu/dataset/352/online+retail
2. Le placer dans le dossier `data/` sous le nom `Online_Retail.xlsx`

Après nettoyage il reste **4 321 clients**.

## La méthode

### Préparation des données

1. **Nettoyage.** Suppression des lignes sans identifiant client et des doublons. Suppression des codes qui ne sont pas des produits (frais de port, frais bancaires) et des prix à zéro. Une annulation totale est retirée avec l'achat d'origine. Un retour partiel est gardé en négatif pour obtenir un montant net.
2. **Variables RFM.** Une ligne par client avec la récence (jours depuis le dernier achat), la fréquence (nombre de commandes) et le montant net dépensé.
3. **Transformation.** Passage au log (`log1p`) pour limiter le poids des clients extrêmes puis standardisation des 3 variables. Sans cela le montant écraserait les deux autres.

### Modélisation

4. **K-Means.** Choix de K avec le coude et la silhouette puis test des paramètres (`init`, `n_init`, `max_iter`).
5. **CAH (Ward).** Le dendrogramme propose deux découpages. Celui à 6 clusters est gardé.
6. **Comparaison.** À 6 clusters K-Means a une meilleure silhouette que la CAH (0,314 contre 0,268) et des groupes plus équilibrés. Il sépare aussi les fidèles selon leur volume d'achat plutôt que selon "ont-ils acheté cette semaine". Il dépend moins du rush de Noël. **Le modèle final est K-Means à 6 clusters.**
7. **PCA** pour visualiser les clusters en 2D. Deux axes conservent 94 % de la variance.

## Les 6 segments

| Segment | Clients | Part des clients | Part du CA | Récence médiane | Fréquence médiane | Montant médian | Action recommandée |
|---|---|---|---|---|---|---|---|
| Champions | 316 | 7,3 % | 50,1 % | 5 jours | 15 | 5 675 £ | Programme VIP avec un interlocuteur dédié et un programme de parrainage |
| Fidèles | 634 | 14,7 % | 22,8 % | 32 jours | 6,5 | 2 461 £ | Programme de fidélité avec points et remises sur volume |
| Prometteurs | 656 | 15,2 % | 9,6 % | 10 jours | 4 | 1 016 £ | Recommandations personnalisées et avantage sur la prochaine commande |
| Occasionnels | 821 | 19,0 % | 3,1 % | 34 jours | 1 | 294 £ | Relance avec un code de réduction valable peu de temps |
| À risque | 929 | 21,5 % | 11,5 % | 94 jours | 2 | 825 £ | Campagne "vous nous manquez" avec une offre forte et une enquête de satisfaction |
| Perdus | 965 | 22,3 % | 2,9 % | 240 jours | 1 | 218 £ | Une seule campagne automatique peu coûteuse puis arrêt de l'investissement |

**À retenir.** Les 316 Champions représentent 7 % des clients mais la moitié du chiffre d'affaires. Les segments À risque et Perdus pèsent 44 % des clients pour 14 % du chiffre d'affaires.

## Contenu du repo

```
globalshop-rfm-clustering/
├── notebook/        Notebook complet (nettoyage, RFM, K-Means, CAH, PCA)
├── models/          Scaler, modèle K-Means et dictionnaires des segments (joblib)
├── streamlit/       Code du simulateur
├── dashboard/       Export PDF du dashboard Data Studio
├── presentation/    Diaporama de restitution (PDF)
├── data/            Dataset à placer ici (non versionné)
└── requirements.txt Dépendances du simulateur
```

## Relancer le projet

**Le simulateur en local.**

```bash
pip install -r requirements.txt
streamlit run streamlit/app.py
```

**Le notebook.** Il faut aussi `matplotlib`, `seaborn`, `scipy` et `openpyxl`.

```bash
pip install matplotlib seaborn scipy openpyxl jupyter
```

Placer ensuite `Online_Retail.xlsx` dans `data/` puis lancer `notebook/online_retail_clustering_rfm.ipynb` du début à la fin. Le notebook recrée les fichiers de `models/`.

## Auteurs

- Ludivine Thinet
- Zohair