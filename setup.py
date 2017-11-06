"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'google-api-python-client',
    'httplib2',
    'langdetect',
    'numpy',
    'progressbar2',
    'requests',
    'spacy',
    'unidecode',
]

setup(
    name='pykoko',
    version='0.0.1',
    description="KOKO is an easy-to-use entity extraction tool",
    long_description=readme,
    author="BigGorilla Team",
    author_email='thebiggorilla.team@gmail.com',
    url='https://github.com/biggorilla-gh/koko',
    packages=find_packages(include=['koko']),
    package_data={'koko': ['koko/dict/*', 'koko/ontologies/*']},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='koko entity extraction',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
)
