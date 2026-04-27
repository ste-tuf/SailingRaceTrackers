# SailingRaceTrackers - Extraction et traitement de données du tracker Geovoile

[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/sebfournier95/SailingRaceTrackers/tree/v3.0.0)
![Mise à jour](https://img.shields.io/badge/dernière%20mise%20à%20jour-Avril%202026-green.svg)
![Statut](https://img.shields.io/badge/statut-production-brightgreen.svg)
[![Licence](https://img.shields.io/badge/licence-LGPL_v3-blue.svg)](/LICENCE)

## 📋 Description

**SailingRaceTrackers** est un système automatisé basé sur **Python** avec **Streamlit** pour la visualisation et le traitement de données de trackers GPS depuis la plateforme **Geovoile** pour les courses nautiques. Ce système permet de récupérer, décoder et analyser des trajectoires de bateaux en temps réel depuis le système cartographie Geovoile utilisé par les plus grandes courses océaniques, avec **mise à jour automatique via GitHub Actions**.

Le système s'articule autour de quatre piliers principaux :

- **Extraction automatisée** : Récupération périodique des positions depuis les serveurs Geovoile avec décodage propriétaire
- **Traitement et analyse** : Conversion, nettoyage et enrichissement
- **Automatisation GitHub Actions** : Exécution programmée, suivi continu et versioning automatique des données
- **Export multi-formats** : Génération de fichiers JSON structurés pour analyse et intégration

### Particularité technique

SailingRaceTrackers utilise une **interface Streamlit** pour la visualisation interactive des données de course, avec un backend Python pour le traitement et l'analyse des données Geovoile. Le système est conçu pour être exécuter localement ou déployé sur un serveur.

---

## 📑 Table des matières

### 🎯 Démarrage rapide
- [🌟 Fonctionnalités](#-fonctionnalités)
- [🗂️ Structure du projet](#️-structure-du-projet)
- [⚙️ Installation et utilisation](#️-installation-et-utilisation)

### 🔧 Aspects techniques
- [🔍 Détails techniques](#-détails-techniques)
- [✅ Tâches à suivre](#-tâches-à-suivre)

### 🤝 Communauté et collaboration
- [🤝 Contribuer au projet](#-contribuer-au-projet)
- [🐙 Bonnes pratiques Git](#-bonnes-pratiques-git)
- [🔒 Sécurité et confidentialité](#-sécurité-et-confidentialité)

### ℹ️ Informations légales
- [👥 Contributeurs](#-contributeurs)
- [📄 Licence](#-licence)
- [📞 Contact](#-contact)

---

## 🌟 Fonctionnalités

### Extraction de données Geovoile

- **Décodage propriétaire** : Implémentation du décodeur Geovoile (format `.hwx`) extrait depuis Chrome
- **Support multi-courses** : Compatible avec Vendée Globe, Transat Jacques Vabre, et autres courses utilisant Geovoile
- **Mise à jour automatique** : Scripts de téléchargement automatisés avec gestion des versions
- **Double format** : Récupération des configurations bateaux (`tracker_config.hwx`) et trajectoires (`tracker_tracks.hwx`)

### Traitement des données

- **Décompression et parsing** : Conversion des données binaires Geovoile en JSON lisible
- **Calculs nautiques** : Extraction de cap, vitesse, distance parcourue, DTF (Distance To Finish), DTL (Distance To Leader)
- **Historique complet** : Reconstruction des trajectoires complètes avec résolution temporelle fine
- **Métadonnées enrichies** : Informations de bateaux (nom, skipper, catégorie) depuis les fichiers de configuration

### Export et intégration

- **Format JSON structuré** : Données organisées par bateau avec métadonnées complètes
- **Trajectoires complètes** : Points GPS avec timestamps pour chaque bateau
- **Statistiques de course** : Classement, distances, vitesses moyennes
- **Extraction de métadonnées** : Notebooks Jupyter pour générer les informations bateaux utiles pour le sous-module servant à visualiser les traces des bateaux sur Windy

## 🗂️ Structure du projet

### Sur les branches de production (`prod-*`)

```
SailingRaceTrackers/
├── app.py                          # Application Streamlit (interface web)
├── python/                        # Package Python
│   ├── __init__.py               # Exports des modules
│   ├── extract_current_rankings.py # Extraction des classements
│   ├── sample_tracks_by_time.py   # Échantillonnage des trajectoires
│   ├── process_and_archive.py    # Archivage des données
│   └── utils.py                  # Utilitaires partagés
├── data/                         # Données de la course
│   ├── boats.json                # Données brutes des bateaux
│   ├── tracks.json              # Données des trajectoires
│   ├── boats_result.json        # Résultats traités finaux
│   ├── config.json             # Configuration de la course
│   └── processed/              # Archives traitées
├── pyproject.toml               # Configuration Python (dépendances)
├── uv.lock                    # Lock file uv
├── .streamlit/                # Configuration Streamlit
│   └── config.toml
└── README.md                 # Documentation
```
SailingRaceTrackers/
├── download-reports.js         # Script de téléchargement des données Geovoile
├── generate-result.js          # Script de génération des résultats traités
├── boats.json                  # Données brutes des bateaux (auto-généré)
├── tracks.json                 # Données des trajectoires (auto-généré)
├── boats_result.json           # Résultats traités finaux (auto-généré)
├── Notebook/                   # Notebooks Jupyter d'analyse
│   ├── Generate_BoatInfo.ipynb     # Extraction métadonnées bateaux
│   └── boatinfo_json_*.json        # Métadonnées par course (optionnel)
├── .github/                    # Configuration GitHub Actions
│   └── workflows/
│       └── generate-boats-result.yml  # Workflow d'automatisation
├── package.json                # Dépendances Node.js
├── package-lock.json           # Lock file des dépendances
├── .gitignore                  # Fichiers exclus du versioning
├── pyproject.toml              # Configuration du projet et dépendances
└── README.md                   # Documentation (ce fichier)

```

### Sur la branche master

La branche **`master`** contient uniquement :
- Ce fichier README avec la documentation complète
- Les templates de base pour créer de nouvelles branches de production
- Les exemples de configuration

### Architecture des branches

Le projet utilise une **architecture multi-branches** pour séparer les différentes courses :

```
master                           # Documentation et templates
├── prod-transatcafelor-2025   # Transat Jacques Vabre 2023 - Production active
├── prod-minitransat-2025      # Mini Transat 2025
├── prod-vg2024                # Vendée Globe 2024
├── prod-aucb-2024             # Arkea Ultim Challenge Brest 2024
└── prod-rab-2023              # Retour à la Base 2023
```

**Principes de l'architecture :**
- **Une branche = Une course** : Chaque course a sa propre branche de production
- **Scripts standardisés** : Tous les scripts utilisent les mêmes noms de fichiers (`download-reports.js`, `generate-result.js`)
- **Configuration par branche** : Seuls les paramètres (hostname, chemins) changent entre les branches
- **Données versionnées** : Les fichiers JSON sont committés automatiquement selon la fréquence définie dans le CRON du workflow
- **Historique complet** : Chaque commit représente un instant T de la course

> ⚠️ **Important** : Pour utiliser le tracker sur une course, basculez toujours vers la branche `prod-*` correspondante. La branche `master` ne contient que la documentation et les workflows des courses qu'on souhaite suivre.

## ⚙️ Installation et utilisation

### Prérequis

### Prérequis

#### Prérequis système

- **Python 3.13+** - Pour l'exécution de l'application Streamlit
- **uv** - Gestionnaire de packages Python moderne (recommandé)
- **Accès Internet** - Pour la récupération des données en temps réel

### Installation

#### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-username/SailingRaceTrackers.git
cd SailingRaceTrackers
```

#### 2. Installer les dépendances Python avec uv

```bash
# Installer uv si nécessaire (voir ci-dessous)
#Installer les dépendances
uv sync
```

### Utilisation

#### Mode 1 : Utilisation de l'application Streamlit (recommandé)

**Lancer l'application web :**

```bash
# Activer l'environnement (si nécessaire)
source .venv/bin/activate

# Lancer l'application Streamlit
streamlit run app.py
```

L'application Streamlit offre une interface interactive avec :
- **Classements en temps réel** : Tableau de bord des positions actuel
- **Visualisation des trajectoires** : Cartes interactives des parcours GPS
- **Analyse de course** : Graphiques d'évolution des performances
- **Archivage** : Traitement et generation d'archives

L'application est accessible à l'adresse `http://localhost:8501` par défaut.

#### Mode 2 : Utilisation en ligne de commande

Pour les opérations de traitement de données en lot :

```bash
# Extraire les classements actuels
python -c "from python import CurrentRankings; r = CurrentRankings(); print(r.load('data/boats.json'))"

# Échantillonner les trajectoires
python -c "from python import TrackSampler; s = TrackSampler(); print(s.sample_all_tracks())"

# Créer une archive
python -c "from python import ProcessAndArchive; p = ProcessAndArchive(); p.run('data/config.json', 'data/boats.json', 'data/tracks.json', 'data/processed')"
```

##### Courses disponibles

Les **implémentations fonctionnelles** se trouvent dans des **branches `prod-*` dédiées** :

| Course | Branche | Statut | GitHub Actions |
|--------|---------|--------|----------------|
| Transat Café l'Or 2025 | `prod-transatcafelor-2025` | 📦 Archivée | - |
| Mini Transat 2025 | `prod-minitransat-2025` | 📦 Archivée | - |
| Vendée Globe 2024 | `prod-vg2024` | 📦 Archivée | - |
| Arkea Ultim Challenge Brest 2024 | `prod-aucb-2024` | 📦 Archivée | - |
| Retour à la Base 2023 | `prod-rab-2023` | 📦 Archivée | - |

> **💡 Note** : Les branches archivées contiennent les données historiques complètes mais n'ont plus d'automatisation active.

#### Structure des données générées

##### Format `boats_result_*.json`

```json
{
  "result": {
    "123": {
      "sail": 123,
      "rank": 1,
      "heading": 245,
      "speed": 18.5,
      "timestamp": 1699012345,
      "lat_dec": 46.275,
      "lon_dec": -1.475,
      "24hour_heading": 240,
      "24hour_distance": 450.5,
      "dtf": 1234.5,
      "dtl": 0.0,
      "dtp": 45.2,
      "track": [
        [46.275, -1.475],
        [46.280, -1.480],
        ...
      ]
    }
  }
}
```

Champs disponibles :
- `sail` : Numéro de voile du bateau
- `rank` : Classement actuel
- `heading` : Cap actuel (degrés)
- `speed` : Vitesse actuelle (nœuds)
- `timestamp` : Timestamp Unix de dernière position
- `lat_dec`, `lon_dec` : Position GPS (degrés décimaux)
- `24hour_distance` : Distance parcourue sur 24h (milles nautiques)
- `dtf` : Distance to Finish (milles nautiques)
- `dtl` : Distance to Leader (milles nautiques)
- `dtp` : Distance to Predecessor (milles nautiques)
- `track` : Tableau de points GPS `[lat, lon]`

#### Extraction de métadonnées bateaux

Les notebooks Jupyter permettent d'extraire les informations détaillées des bateaux :

```bash
# Lancer Jupyter Lab
jupyter lab

# Ouvrir le notebook
# Notebook/Generate_BoatInfo.ipynb
```

Le notebook [`Generate_BoatInfo.ipynb`](Notebook/Generate_BoatInfo.ipynb) :
- Charge les fichiers de configuration depuis Dropbox
- Parse les données XML des bateaux
- Extrait nom du bateau, skippers, catégorie
- Génère les fichiers [`boatinfo_json_*.json`](Notebook/Generate_BoatInfo.ipynb:80)

Structure des fichiers `boatinfo_json`:

```json
{
  "123": {
    "boatName": "Biotherm",
    "skipperNames": "Paul_Meilhat",
    "category": "IMOCA"
  }
}
```

## 🔍 Détails techniques

### Algorithme de décodage Geovoile

Le module implémente le décodeur propriétaire Geovoile extrait depuis Chrome DevTools. L'algorithme utilise :

1. **XOR Shift RNG** : Générateur de nombres pseudo-aléatoires pour le déchiffrement
2. **Compression LZ77** : Décompression des trajectoires encodées
3. **Deltas cumulatifs** : Reconstruction des positions à partir de deltas

Le code de décodage se trouve dans la fonction [`UInt8Array()`](download-reports-VG.js:34-69) qui :
- Initialise le générateur aléatoire avec la première byte
- Décode la taille des données décompressées
- Applique l'algorithme de décompression LZ77
- Reconstruit le flux de données original

### Format des données Geovoile

#### `tracker_config.hwx`
Contient la configuration de la course :
- Liste des bateaux participants
- Métadonnées (nom, skipper, catégorie)
- Configuration du tracking

#### `tracker_tracks.hwx`
Contient les trajectoires encodées :
- Positions GPS sous forme de deltas
- Timestamps relatifs
- Indices de compression pour réduire la taille

### Reconstruction des trajectoires

Le script [`generate-result-VG.js`](generate-result-VG.js:33-48) reconstruit les trajectoires :

```javascript
// Point initial (coordonnées absolues)
const firstPoint = [
    (locForId[0][1] / 100000),
    (locForId[0][2] / 100000)
];

// Points suivants (deltas cumulés)
for (let j = 0; j < locForId.length - 1; j++) {
    lastLocDatetime += locForId[j + 1][0];  // Delta temps
    const transformedPoint = [
        (locForId[j + 1][1] / 100000) + track[j][0],  // Delta lat
        (locForId[j + 1][2] / 100000) + track[j][1]   // Delta lon
    ];
    track.push(transformedPoint);
}
```

## ✅ Tâches à suivre

Cette section liste les tâches de développement en cours, les améliorations prévues et les bugs identifiés.

### 🚧 Développement en cours

- [ ] Intégration d'un sous-module pour lancer un plugin Windy en local

### 🔮 Améliorations prévues

#### Traitement des données
- [ ] Calcul automatique des statistiques avancées (VMG, polaires)
- [ ] Détection et correction des anomalies de trajectoire
- [ ] Interpolation des points manquants
- [ ] Export vers format GPX pour compatibilité avec logiciels de navigation

#### Export et visualisation
- [ ] Export vers bases de données (InfluxDB, PostgreSQL)

### 🧪 Tests à ajouter

### 🐛 Bugs connus
- [ ] **Index des coordonnées GPS dans [`generate-result.js`](generate-result.js:51)** : La ligne `const trackDataArray = boatsData[i][31];` utilise un index fixe (31) qui peut varier selon la structure des données de chaque course Geovoile. Il est nécessaire d'analyser la structure du tableau `boatsData[i]` pour chaque nouvelle course et d'adapter l'index en conséquence pour capturer correctement les coordonnées GPS. Consultez les logs de débogage (lignes 32-47) pour identifier le bon index contenant les données de trajectoire.

### 🔄 Maintenance

- [ ] Mise à jour régulière des dépendances Node.js
- [ ] Mise à jour régulière des dépendances Python
- [ ] Mise à jour annuelle des [contributeurs](#-contributeurs) — ajout / modification des rôles
- [ ] Création d'une documentation dédiée (Sphinx ou pdoc) pour alléger ce fichier

> **Note** : Cette liste est maintenue activement. Les éléments cochés sont complétés, les nouveaux items sont ajoutés au fur et à mesure de l'évolution du projet.

## 🤝 Contribuer au projet

Nous accueillons avec plaisir les contributions de la communauté ! Que vous souhaitiez corriger un bug, améliorer la documentation, ou ajouter une nouvelle fonctionnalité, voici le processus à suivre.

### Processus de contribution via Fork

#### 1. Fork et configuration initiale

```bash
# 1. Forker le dépôt via l'interface GitHub
# Cliquer sur le bouton "Fork" en haut à droite de la page du projet

# 2. Cloner votre fork
git clone https://github.com/votre-username/SailingRaceTrackers.git
cd SailingRaceTrackers

# 3. Ajouter le dépôt original comme remote "upstream"
git remote add upstream https://github.com/sebfournier95/SailingRaceTrackers.git

# 4. Vérifier la configuration des remotes
git remote -v
# Vous devriez voir :
# origin    https://github.com/votre-username/SailingRaceTrackers.git (fetch)
# origin    https://github.com/votre-username/SailingRaceTrackers.git (push)
# upstream  https://github.com/sebfournier95/SailingRaceTrackers.git (fetch)
# upstream  https://github.com/sebfournier95/SailingRaceTrackers.git (push)
```

#### 2. Créer une branche de travail

```bash
# Mettre à jour votre fork avec les dernières modifications
git checkout master
git pull upstream master
git push origin master

# Créer une branche pour votre contribution
# Utilisez les préfixes selon le type de contribution :
# - feat/ pour une nouvelle fonctionnalité
# - fix/ pour une correction de bug
# - docs/ pour la documentation
# - refactor/ pour du refactoring
# - test/ pour des tests

git checkout -b feat/nom-descriptif-fonctionnalite
# ou
git checkout -b fix/description-bug
# ou
git checkout -b docs/amelioration-documentation
```

#### 3. Développer et tester

```bash
# Installer les dépendances si nécessaire
npm install

# Faire vos modifications
# ... éditer les fichiers ...

# Tester localement
node download-reports.js  # Si applicable
node generate-result.js   # Si applicable

# Commiter régulièrement avec des messages clairs
git add .
git commit -m "feat: description claire de la modification

- Détail 1
- Détail 2
- Détail 3"
```

Suivez les [conventions de commits](#types-de-commits) du projet :
- `feat:` pour les nouvelles fonctionnalités
- `fix:` pour les corrections de bugs
- `docs:` pour la documentation
- `refactor:` pour du refactoring
- `test:` pour les tests
- `chore:` pour la maintenance

#### 4. Soumettre votre Pull Request

```bash
# Pousser votre branche vers votre fork
git push origin feat/nom-descriptif-fonctionnalite

# Ensuite, sur GitHub :
# 1. Aller sur votre fork
# 2. Cliquer sur "Compare & pull request"
# 3. Remplir le template de PR avec :
#    - Description claire des changements
#    - Motivation de la contribution
#    - Tests effectués
#    - Captures d'écran si applicable
# 4. Soumettre la Pull Request
```

#### 5. Processus de revue

Une fois votre PR soumise :

1. **Revue automatique** : Les tests GitHub Actions s'exécuteront automatiquement
2. **Revue par les mainteneurs** : Un membre de l'équipe examinera votre code
3. **Discussion et ajustements** : Des modifications peuvent être demandées
4. **Validation et merge** : Une fois approuvée, votre PR sera mergée

Si des modifications sont demandées :

```bash
# Faire les modifications demandées
git add .
git commit -m "fix: correction selon les commentaires de la revue"
git push origin feat/nom-descriptif-fonctionnalite

# La PR sera automatiquement mise à jour
```

#### 6. Synchroniser votre fork après merge

```bash
# Une fois votre PR mergée, mettre à jour votre fork
git checkout master
git pull upstream master
git push origin master

# Supprimer la branche locale et distante (optionnel mais recommandé)
git branch -d feat/nom-descriptif-fonctionnalite
git push origin --delete feat/nom-descriptif-fonctionnalite
```

### Types de contributions acceptées

#### 🐛 Corrections de bugs
- Corrections de bugs dans les scripts de téléchargement ou de traitement
- Résolution de problèmes de compatibilité
- Amélioration de la gestion des erreurs

#### ✨ Nouvelles fonctionnalités
- Support de nouvelles courses Geovoile
- Nouveaux formats d'export (GPX, KML, CSV)
- Calculs nautiques avancés (VMG, polaires)
- Détection d'anomalies dans les trajectoires

#### 📚 Documentation
- Amélioration du README
- Ajout d'exemples d'utilisation
- Traduction de la documentation
- Correction de typos ou liens cassés

#### 🧪 Tests
- Ajout de tests unitaires
- Amélioration de la couverture de tests
- Tests d'intégration

#### 🎨 Optimisations
- Amélioration des performances
- Refactoring du code
- Optimisation des algorithmes de décodage

### Règles de contribution

#### Code de qualité
- ✅ Le code doit être **propre et bien commenté**
- ✅ Respecter le **style de code existant** (indentation, conventions de nommage)
- ✅ Ajouter des **commentaires explicatifs** pour la logique complexe
- ✅ Tester localement avant de soumettre

#### Commits
- ✅ Messages de commit **clairs et descriptifs**
- ✅ Suivre la convention [Conventional Commits](https://www.conventionalcommits.org/)
- ✅ Un commit = une modification logique cohérente
- ✅ Éviter les commits trop volumineux

#### Pull Requests
- ✅ Description **claire et complète** de la PR
- ✅ Référencer les issues concernées si applicable (`Fixes #123`)
- ✅ **Tests réussis** avant soumission
- ✅ PR de **taille raisonnable** (éviter les mega-PRs de 1000+ lignes)
- ✅ S'assurer que la branche est **à jour avec master**

#### Documentation
- ✅ Mettre à jour le **README** si nécessaire
- ✅ Documenter les **nouvelles fonctionnalités**
- ✅ Ajouter des **exemples d'utilisation**
- ✅ Commenter le code complexe

### Besoin d'aide ?

Si vous avez des questions ou besoin d'assistance :

1. **Issues GitHub** : Ouvrez une issue pour discuter d'une fonctionnalité avant de la développer
2. **Discussions** : Utilisez l'onglet Discussions pour les questions générales
3. **Contact** : Contactez [sebastien.fournier.95@gmail.com](mailto:sebastien.fournier.95@gmail.com)

### Code de conduite

En contribuant à ce projet, vous acceptez de :
- 🤝 Être respectueux et constructif dans vos interactions
- 💬 Communiquer de manière claire et professionnelle
- 🎯 Se concentrer sur ce qui est le mieux pour le projet
- 🌟 Accueillir les nouveaux contributeurs avec bienveillance

## 🐙 Bonnes pratiques Git

Ce projet suit un workflow Git structuré pour garantir la qualité du code et la stabilité des versions de production.

### Structure des branches

Le projet utilise un système de branches pour organiser le développement :

- **`master`** : Branche de production contenant uniquement le code stable et testé
- **`dev`** : Branche de développement où les nouvelles fonctionnalités sont intégrées
- **`feat-xxxxx`** : Branches de fonctionnalités pour le développement isolé de nouvelles fonctionnalités
- **`fix-xxxxx`** : Branches dédiées aux corrections de bugs
- **`docs-xxxxx`** : Branches pour les modifications de documentation
- **`prod-xxxxx`** : Branches de déploiement pour des projets spécifiques

### Types de commits

Le projet suit la convention [Conventional Commits](https://www.conventionalcommits.org/) pour structurer les messages de commit. Chaque commit doit commencer par un type suivi d'une description claire :

#### **`feat:`** Nouvelle fonctionnalité
Ajout d'une nouvelle fonctionnalité au code. Correspond à une incrémentation MINOR en versionnage sémantique.

**Exemples :**
```bash
feat: ajout du module d'analyse de densité pour les cachalots
feat: intégration du support des fichiers AIS pour les trajectoires
feat: implémentation du calcul de probabilité de collision multi-espèces
```

#### **`fix:`** Correction de bug
Correction d'un bug ou d'un comportement incorrect. Correspond à une incrémentation PATCH en versionnage sémantique.

**Exemples :**
```bash
fix: correction du calcul de distance pour les trajectoires circulaires
fix: résolution du problème d'encodage UTF-8 dans les fichiers GPX
fix: correction de la gestion des fuseaux horaires dans les données temporelles
```

#### **`docs:`** Documentation
Modifications concernant uniquement la documentation (README, commentaires, docstrings, etc.). N'affecte pas le code fonctionnel.

**Exemples :**
```bash
docs: mise à jour du guide d'installation avec les nouvelles dépendances
docs: ajout d'exemples d'utilisation du module de trajectoires
docs: correction des liens cassés dans le README
```

#### **`style:`** Formatage du code
Changements qui n'affectent pas le sens du code (espaces, formatage, points-virgules manquants, etc.).

**Exemples :**
```bash
style: application de black sur le module track.py
style: correction de l'indentation dans les fichiers Python
style: mise en conformité avec PEP 8 du module density.py
```

#### **`refactor:`** Refactorisation
Modification du code qui n'ajoute pas de fonctionnalité et ne corrige pas de bug. Améliore la structure interne du code.

**Exemples :**
```bash
refactor: réorganisation du module d'analyse en sous-modules
refactor: extraction de la logique de calcul dans une classe dédiée
refactor: simplification de la fonction de parsing des fichiers GPX
```

#### **`test:`** Ajout ou modification de tests
Ajout de tests manquants ou correction de tests existants.

**Exemples :**
```bash
test: ajout des tests unitaires pour le module density
test: correction des tests d'intégration pour l'analyse de collision
test: amélioration de la couverture de tests pour le module track
```

#### **`chore:`** Tâches de maintenance
Modifications qui ne concernent ni le code source ni les tests (mise à jour de dépendances, configuration, scripts de build, etc.).

**Exemples :**
```bash
chore: mise à jour des dépendances Python vers les dernières versions
chore: ajout de .gitignore pour les fichiers temporaires R
chore: configuration de pre-commit hooks pour le formatage automatique
```

### Workflow de développement

#### 1. Développement d'une nouvelle fonctionnalité

```bash
# Mettre à jour la branche dev
git checkout dev
git pull origin dev

# Créer une nouvelle branche de fonctionnalité
git checkout -b feat/nom-de-la-fonctionnalite

# Développer et commiter régulièrement
git add .
git commit -m "Description claire des modifications"

# Pousser la branche vers le dépôt distant
git push origin feat/nom-de-la-fonctionnalite
```

#### 2. Intégration d'une fonctionnalité

Après validation des tests unitaires :

```bash
# Mettre à jour dev avec les dernières modifications
git checkout dev
git pull origin dev

# Merger la fonctionnalité dans dev
git merge feat/nom-de-la-fonctionnalite

# Résoudre les conflits si nécessaire
# Tester l'intégration

# Pousser les modifications
git push origin dev
```

#### 3. Déploiement en production

```bash
# Mettre à jour master avec la dernière version de dev
git checkout master
git pull origin master

# Merger dev dans master
git merge dev

# IMPORTANT : Incrémenter la version dans README.md et pyproject.toml
# Suivre le versionnage sémantique : MAJOR.MINOR.PATCH
# - MAJOR : changements incompatibles avec les versions précédentes
# - MINOR : ajout de fonctionnalités rétrocompatibles
# - PATCH : corrections de bugs rétrocompatibles

# Exemple : 1.0.1 → 1.1.0 (nouvelle fonctionnalité)
#          1.1.0 → 2.0.0 (changement majeur)
#          1.1.0 → 1.1.1 (correction de bug)

# Créer un tag de version
git tag -a v1.1.0 -m "Version 1.1.0 : Description des changements"

# Pousser master et les tags
git push origin master
git push origin --tags
```

#### 4. Branches de production pour projets spécifiques

Les branches `prod-xxxxx` permettent d'utiliser la version la plus récente du code (depuis `master`) pour réaliser un projet spécifique sans polluer la branche dédiée au code stable. Elles peuvent également servir pour des correctifs urgents qui ne peuvent attendre le cycle normal de développement.

##### Cas d'usage : Projet spécifique

```bash
# Créer une branche de production depuis master
git checkout master
git pull origin master
git checkout -b prod/nom-du-projet

# Développer et adapter pour le projet
git add .
git commit -m "Feat: adaptation pour le projet X"

# Les modifications restent isolées dans cette branche
# Elles ne sont pas mergées dans master sauf si elles apportent
# une amélioration générique utile au projet principal
```

### Format des messages de commit

Utilisez des messages de commit clairs et descriptifs en respectant le format suivant :

```bash
# Format recommandé
git commit -m "type: description courte en minuscules

Description détaillée si nécessaire (optionnel)
- Point 1
- Point 2
- Point 3"
```

**Exemples complets :**

```bash
# Commit simple
git commit -m "feat: ajout du support des fichiers CSV pour les trajectoires"

# Commit avec description détaillée
git commit -m "fix: correction du calcul de distance

- Prise en compte de la courbure terrestre
- Amélioration de la précision pour les longues distances
- Ajout de tests unitaires pour valider la correction"
```

Pour plus de détails sur chaque type de commit, consultez la section [Types de commits](#types-de-commits) ci-dessus.

### Versionnage sémantique

Le projet suit la spécification [Semantic Versioning 2.0.0](https://semver.org/) :

- **Version format** : `MAJOR.MINOR.PATCH`
- **MAJOR** : Changements incompatibles de l'API
- **MINOR** : Ajout de fonctionnalités rétrocompatibles
- **PATCH** : Corrections de bugs rétrocompatibles

### 🔄 Processus de versionnage automatisé

Le versionnage est entièrement automatisé grâce à GitHub Actions.

Pour publier une nouvelle version :

1. **Faire un commit sur `master`** contenant dans le message un motif du type :

``` python 
Version vX.Y.Z : Description
```

2. Lors du push, le workflow :
- détecte automatiquement le numéro de version `X.Y.Z`
- met à jour tous les éléments liés à la version dans `README.md` :
  - badge de version (`version-2.0.1-blue.svg`)
  - badge "dernière mise à jour" basé sur la date du commit
  - lien vers le tag (`tree/v2.0.1)
- met à jour tous les éléments liés à la version dans `pyproject.toml`
- met à jour automatiquement uv.lock avec la commande `uv lock`
- génère un **tag annoté** `vX.Y.Z` à partir du message du commit
- pousse le commit mis à jour ainsi que le tag vers le dépôt

### 📌 À noter
- Aucun fichier n'a besoin d'être modifié manuellement pour changer de version.
- Le README du tag `vX.Y.Z` est toujours synchronisé avec celui de `master`.
- Le tag final suit systématiquement le format : `vMAJOR.MINOR.PATCH`.

## 🔒 Sécurité et confidentialité

### Données sensibles

Les scripts ne collectent ni ne transmettent aucune donnée personnelle. Seules les données publiquement disponibles sur les trackers officiels des courses sont téléchargées.

### Respect des conditions d'utilisation

Ce projet est conçu pour un usage personnel et éducatif.

### Recommandations d'usage

- **Limitez la fréquence** de téléchargement à 5-10 minutes minimum entre requêtes
- **N'utilisez pas les données** à des fins commerciales sans autorisation
- **Mentionnez toujours** la source des données (Geovoile) dans vos publications

## 👥 Contributeurs

| Nom                    | Rôle |
|------------------------|------|
| [globe-coder](https://github.com/globe-coder) | Développeur principal (Fork) |
| [ccyrille](https://github.com/ccyrille) | Contributeur (Fork) |
| [Bendrog](https://github.com/Bendrog) | Contributeur (Fork) |
| [sebfournier95](https://github.com/sebfournier95) | Développeur principal |

## 📄 Licence

Ce projet est distribué sous la licence **GNU Lesser General Public License v3.0**.

Voir le fichier [`LICENCE`](LICENCE) pour plus d'informations.

## 📞 Contact

Pour toute question ou assistance, contactez l'équipe de développement :

- **Sébastien Fournier** : [sebastien.fournier.95@gmail.com](mailto:sebastien.fournier.95@gmail.com)

---

**Développé avec ❤️ pour les passionnés des trackers de course**