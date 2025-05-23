from setuptools import setup

APP = ["app_06_05.py"]
DATA_FILES = ["templates", "static"]
OPTIONS = {
    # mantiene l’argv_emulation per le app GUI
    "argv_emulation": True,
    # includi qui tutti i moduli che py2app non rileva automaticamente
    "includes": [
        "flask",
        "jinja2",
        "pdf_generator_10_05",
        "specialists_config",
        "fpdf",         # se usi fpdf
        # aggiungi altri moduli “strani” che importi nel tuo script
    ],
    # se vuoi includere tutti i package sotto un namespace
    # "packages": ["your_package_name"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=[
        "Flask",
        "Jinja2",
        "fpdf",
        # inserisci qui tutte le tue dipendenze da pip
    ],
)
