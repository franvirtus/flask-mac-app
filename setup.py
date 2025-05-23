from setuptools import setup
from pathlib import Path

# Trova la cartella di questo file
HERE = Path(__file__).parent

# Leggi requirements.txt (uno per riga, ignora commenti e vuoti)
requirements = [
    r.strip()
    for r in (HERE / "requirements.txt").read_text().splitlines()
    if r.strip() and not r.startswith("#")
]

setup(
    # Sostituisci "app_06_05.py" col tuo script principale, se diverso
    app=["app_06_05.py"],

    # Metadata
    name="VirtusApp",
    version="0.1.0",

    # Dipendenze runtime
    install_requires=requirements,

    # Serve a py2app
    setup_requires=["py2app"],

    options={
        "py2app": {
            # Se ti serve emulare argv (utile per applicazioni GUI)
            "argv_emulation": True,

            # Forza l’inclusione di fpdf (o fpdf2)
            "includes": ["fpdf"],

            # DISABILITA la firma ad-hoc che fallisce sui runner GitHub
            "codesign_identity": "",
        }
    },
)
