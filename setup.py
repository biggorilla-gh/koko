from setuptools import setup, find_packages

setup(
    name="koko",
    version="0.1.0",
    packages=find_packages(),
    package_data={'koko': ['dict/*']},
    install_requires=[
        "google-api-python-client",
        "httplib2",
        "langdetect",
        "numpy",
        "progressbar2",
        "requests",
        "spacy",
        "unidecode",
    ],
)
