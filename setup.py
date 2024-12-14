from setuptools import setup, find_packages

setup(
    name="note_gen",
    packages=find_packages(),
    package_data={
        "models": ["py.typed"],
        "typings": ["*.pyi"],
    },
)
