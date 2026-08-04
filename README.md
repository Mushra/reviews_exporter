# Metacritic Review Exporter

## Installation

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py
```

To use a custom data directory:

```bash
$env:METACRITIC_EXPORT_DATA_DIR="C:/path/to/data"
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
