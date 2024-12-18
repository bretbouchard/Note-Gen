from setuptools import setup, find_packages

setup(
    name="note_gen",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "models": ["py.typed"],
        "typings": ["*.pyi"],
    },
)