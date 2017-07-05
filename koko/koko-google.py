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

from .entity_extractor import EntityExtractor
from .parser import Parser
from .google_document import GoogleDocument
import sys

def run(query_file):
    with open(query_file, 'r') as qfile:
        query = qfile.read()
    print("Query:\n%s" % query)

    parser = Parser(query)
    if not parser.is_parsed:
        print('Syntax error: ', parser.error_msg)
        return
    
    print("Rewritten query:\n", parser.toString())
        
    with open(parser.document_name, 'r') as myfile:
        document = myfile.read()
        
    extractor = EntityExtractor(GoogleDocument(document), True)
    entities = extractor.TopEntities(query)
    print("\nResults:\n")
    for entity in entities:
        print("%s\t%f" % (entity.span.text, entity.score))


# main

if len(sys.argv) < 2:
    print("Usage: python koko.py *.koko")
    exit()

query_files = sys.argv[1:]


for query_file in query_files:
    run(query_file)

    
