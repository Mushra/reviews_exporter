$ErrorActionPreference = "Stop"

if (Test-Path ".venv\Scripts\python.exe") {
    $python = ".\.venv\Scripts\python.exe"
} else {
    $python = "python"
}

& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt pyinstaller

& $python -m PyInstaller --noconfirm --onefile --windowed --name "MetacriticReviewExporter" `
  main.py
