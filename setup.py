from setuptools import setup

APP = ["app_06_05.py"]
DATA_FILES = ["templates", "static"]
OPTIONS = {"argv_emulation": True}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
