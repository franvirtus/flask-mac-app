from setuptools import setup, find_packages

# Il tuo script principale
APP = ["app_06_05.py"]      

# Cartelle di risorse da includere nel bundle
DATA_FILES = ["templates", "static"]

# Opzioni base per py2app
OPTIONS = {
    "argv_emulation": True
}

# Carica automaticamente le dipendenze da requirements.txt
with open("requirements.txt") as f:
    install_requires = [
        r.strip() for r in f
        if r.strip() and not r.startswith("#")
    ]

setup(
    name="LaTuaApp",                   # nome del tuo bundle
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
    install_requires=install_requires, # ecco tutte le librerie
    packages=find_packages(),          # se hai moduli interni
)
