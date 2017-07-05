'''
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
'''

from .parser import Parser
from .entity_extractor import EntityExtractor
from .koko_document import KokoDocument
from .google_document import GoogleDocument
import logging
import spacy

logger = logging.getLogger()

class KokoResponse:
    
    def __init__(self, query, document, entities):
        self.query = query
        self.document = document
        self.entities = entities

class QueryProcessor:
    
    def __init__(self, document_parser='koko'):
        self.document_parser = document_parser
        if self.document_parser == 'spacy':
            logger.info("Loading SpaCy English models")
            self.nlp = spacy.load('en')
            logger.info("Done")

    def ProcessQuery(self, query, document=None):
        query_parser = Parser(query)
        if not query_parser.is_parsed:
            logger.error("Syntax error: %s" % query_parser.error_msg)
            return None
        print("Parsed query:", query_parser.toString())
        if not document:
            with open(query_parser.document_name, 'r') as myfile:
                document = myfile.read()
        if self.document_parser == 'koko':
            doc = KokoDocument(document)
        elif self.document_parser == 'spacy':
            doc = self.nlp(document)
        elif self.document_parser == 'google':
            doc = GoogleDocument(document)
        else:
            logger.error("Unknown parser: %s" % document_parser)
            return None
        extractor = EntityExtractor(doc)
        entities = extractor.TopEntitiesForParsedQuery(query_parser)
        return KokoResponse(query, document, entities)

