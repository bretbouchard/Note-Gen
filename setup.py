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
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "mypy>=1.0",
        ],
    },
    python_requires=">=3.8",
)