# KOKO - Extracting Entities with Limited Evidence

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

## Installation

After cloning the repository, install the KOKO package (optionally in
a separate virtual environment) by running:

```
pip install --upgrade .
```


Then, load the word embedding model by running these commands:

```
./load_embedding_model.sh
ln -s ./embeddings examples/

```

## Running KOKO

To check that the KOKO package was successfully installed,
try running KOKO on the sample query provided in the "cafe.koko" file.
```
cd examples
python run_koko.py --query_file=cafe.koko
```

By default, KOKO uses its built-in document parser, with a simple
heuristic for identifying entities (title-case strings). KOKO also
provides wrappers for other document parsers such as SpaCy
(https://spacy.io/) or the Google Cloud Natural Language API
(https://cloud.google.com/natural-language).

In order to use Spacy, you first need to download the English language model files:
```
python -m spacy.en.download
```
Then, you can use the SpaCy parser in KOKO as follws:
```
python run_koko.py --query_file=cafe.koko --doc_parser=spacy
```

To use Google Cloud API, you first need to set up your credentials by
following the instructions at:
https://developers.google.com/identity/protocols/application-default-credentials.

Then, assumming the environment variable GOOGLE_APPLICATION_CREDENTIALS is set, you can run:
```
python run_koko.py --query_file=cafe.koko --doc_parser=google 
```

## Query Examples


- Entity name token containment:

```
  extract "Ents" x from "doc.txt" if
        (str(x) contains "Cafe")
```

- Entity name substring:

```
  extract "Ents" x from "doc.txt" if
        (str(x) mentions "afe")
```

- Entity name regular expression:

```
  extract "Ents" x from "doc.txt" if
        (str(x) matches "[Cc]afe")
```

- Strict left context:

```
  extract "Ents" x from "doc.txt" if
        ("introduce" x)
```

- Strict right context:

```
  extract "Ents" x from "doc.txt" if
        (x ", a cafe")
```

- Loose left context:

```
  extract "Ents" x from "doc.txt" if
        ("introduce" near x)
```

- Loose right context:

```
  extract "Ents" x from "doc.txt" if
        (x near "cafe")
```

- Semantic left context:

```
  extract "Ents" x from "doc.txt" if
        ("introducing cafe" ~ x) 
```

- Semantic right context:

```
  extract "Ents" x from "doc.txt" if
        (x ~ "serves coffee") 
```

