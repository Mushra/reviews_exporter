# Review Exporter

Extraction de reviews et commentaires depuis Metacritic, Steam et YouTube, exportées en
JSON structuré (prêt pour analyse par des LLM : tendances, feedback récurrents presse/joueurs).

## Sources

- **Metacritic** : reviews presse et joueurs (API backend Metacritic).
- **Steam** : toutes les reviews d'un jeu via l'API publique `appreviews` (aucune clé requise).
- **YouTube** : commentaires de vidéos sélectionnées manuellement (URLs collées dans
  l'onglet YouTube), via l'API YouTube Data v3.

### Clé API YouTube

Ouvrir **⚙ Réglages** dans l'application et coller une clé API YouTube Data v3
(créée sur [console.cloud.google.com](https://console.cloud.google.com/)). Elle est
enregistrée localement dans `config.json` du dossier de données. Alternative :
définir la variable d'environnement `YOUTUBE_API_KEY` avant de lancer l'application.

**Ne jamais committer** de clé API ou le dossier `data/` - le `.gitignore` du projet
exclut déjà `data/` (créé automatiquement au premier lancement).

## Installation

Prérequis : Python 3.10+.

```bash
git clone https://github.com/Mushra/reviews_exporter.git
cd reviews_exporter
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Windows
# source .venv/bin/activate       # macOS/Linux
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Au premier lancement, l'app crée son propre dossier de données (par défaut sous
`%LOCALAPPDATA%\MetacriticReviewExporter\data` sur Windows, `~/.local/share/...`
sur Linux, `~/Library/Application Support/...` sur macOS) - aucune donnée du repo
n'est nécessaire pour démarrer.

Pour utiliser un dossier de données personnalisé :

```bash
$env:METACRITIC_EXPORT_DATA_DIR="C:/path/to/data"   # PowerShell
# export METACRITIC_EXPORT_DATA_DIR=/path/to/data   # bash
python main.py
```

## Build executable (Windows)

```powershell
./build_exe.ps1
```

## Release workflow

For a simple delivery to end users:

1. Commit your changes.
2. Create a version tag:

```powershell
./release.ps1 v0.1.1
```

3. Push the tag; GitHub Actions will build the Windows executable and publish it as a GitHub Release.
4. End users download the latest executable from the Releases page.

This gives you a clean path for updates: each new tag produces a new distributable binary.
