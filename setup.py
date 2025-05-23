from setuptools import setup
from pathlib import Path

HERE = Path(__file__).parent

# leggo le dipendenze riga per riga, ignorando commenti e righe vuote
requirements = [
    r.strip() for r in (HERE / "requirements.txt").read_text().splitlines()
    if r.strip() and not r.startswith("#")
]

setup(
    app=["app_06_05.py"],          # o il tuo script principale
    name="VirtusApp",              # nome a piacere
    version="0.1.0",
    install_requires=requirements, # <-- qui passo fpdf2 (o fpdf)
    setup_requires=["py2app"],
    options={
        "py2app": {
            "argv_emulation": True,
            "includes": ["fpdf"],  # se usi 'fpdf2' qui rimane comunque "fpdf"
        }
    },
)
