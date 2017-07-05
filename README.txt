KOKO - Extracting Entities with Limited Evidence
=================================================

Copyright 2017 Recruit Institute of Technology

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


INTRODUCTION
============

Information extraction is a fundamental step for obtaining structured
data from unstructured text.  A particular kind of information
extraction is entity extraction, which refers to the task of
extracting names of entities such as person, organizations, or
locations from text. KOKO is an information extraction system that
features the ability for users to specify at a high-level, what are
the properties of entities of interest through the use of semantic
descriptors, in addition to how to discover such entities through
patterns.  Entities are retrieved only when the aggregated evidence
across descriptors and patterns produce a sufficiently strong signal.

KOKO is a system for extracting entity mentions from natural language
text. It is using a declarative query language that allows one to use
a combination of cues (patterns, heuristics, or semantic query
phrases) to specify which entities should be extracted.


that specify
textual patterns to be matched by the entity text or by the context
around the entity mentions.

Here is a simple query that extracts cafe names:

select "Ents" from "doc.txt" if
       (str(x) contains "Cafe") or
		 (x ", a cafe")

This query specifies that we want to extract entities whose name
contains the string "Cafe" or that are followed by the string ", a
cafe" in the document "doc.txt".



INSTALLATION
============

After cloning the repository, install the KOKO package by running:

pip install --upgrade .

Then, load the word embedding model by running these commands:


cd biggorilla/packages/koko

./load_embedding_model.sh



To check that the KOKO package was successfully installed,
try running KOKO on the sample query provided in the "cafe.koko" file.

cd examples
python run_koko.py --query_file=cafe.koko


You may also output the query results in JSON. This option provides
additional provenance and scoring information for each entity in the result.



python run_koko.py --query_file=cafe.koko --output_format=json


By default, KOKO uses its built-in document parser, with a simple
heuristic for identifying entities (title-case strings). KOKO also
provides wrappers for other document parsers such as SpaCy
(https://spacy.io/) or the Google Cloud Natural Language API
(https://cloud.google.com/natural-language).

In order to use Spacy, you first need to download the English language model files:

python -m spacy.en.download

Then, you can use the SpaCy parser in KOKO as follws:

python run_koko.py --query_file=cafe.koko --doc_parser=spacy --output_format=json


To use Google Cloud API, you first need to set up your credentials by
following the instructions at:
https://developers.google.com/identity/protocols/application-default-credentials.

Then, assumming the environment variable GOOGLE_APPLICATION_CREDENTIALS is set, you can run:

python run_koko.py --query_file=cafe.koko --doc_parser=google --output_format=json


KOKO QUERY EXAMPLES
===================

Conditions:

- Entity name token containment:

  extract "Ents" x from "doc.txt" if
        (str(x) contains "Cafe")

- Entity name substring:

  extract "Ents" x from "doc.txt" if
        (str(x) mentions "afe")

- Entity name regular expression:

  extract "Ents" x from "doc.txt" if
        (str(x) matches "[Cc]afe")

- Strict left context:

  extract "Ents" x from "doc.txt" if
        ("introduce" x)

- Strict right context:

  extract "Ents" x from "doc.txt" if
        (x ", a cafe")

- Loose left context:

  extract "Ents" x from "doc.txt" if
        ("introduce" near x)

- Loose right context:

  extract "Ents" x from "doc.txt" if
        (x near "cafe")

- Semantic left context:

  extract "Ents" x from "doc.txt" if
        ("introducing cafe" ~ x) 

- Semantic right context:

  extract "Ents" x from "doc.txt" if
        (x ~ "serves coffee") 

