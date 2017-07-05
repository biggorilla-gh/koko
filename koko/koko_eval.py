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
import spacy
from .test_document import TestDocument
import sys
from unidecode import unidecode

# main

if len(sys.argv) < 3:
    print("Usage: python koko.py query entities")
    exit()

query_file = sys.argv[1]
entities_file = sys.argv[2]


with open(query_file, 'r') as qfile:
    query = qfile.read()
# print("Query:\n%s" % query)

with open(entities_file, 'r') as efile:
    entities = set(efile.read().splitlines())

correct_entities = set()
for entity in entities:
    correct_entities.add(unidecode(entity).lower())


parser = Parser(query)
if not parser.is_parsed:
    print('Syntax error: ', parser.error_msg)
    exit()
    
#print("Rewritten query:\n", parser.toString())
        
with open(parser.document_name, 'r') as myfile:
    document = myfile.read()

print("Loading SpaCy English models...")
nlp = spacy.load('en')
print("Done loading models")
doc = nlp(document)
#doc = TestDocument(document)



extractor = EntityExtractor(doc, True)
results = extractor.TopEntities(query)

found_at_1 = set()

def matching_correct_entitity(entity):
    text = unidecode(entity.span.text).lower()
    for correct_entity in sorted(correct_entities):
        if correct_entity.startswith(text):
            return correct_entity
    return None

found_count = [0 for pred in parser.predicates]
correct_count = [0 for pred in parser.predicates]
found_entity_sets = [set() for pred in parser.predicates]
for entity in results:
    for p in range(len(parser.predicates)):
        if entity.scores[p]:
            found_count[p] += 1
            matching_entity = matching_correct_entitity(entity)
            if matching_entity:
                correct_count[p] += 1
                found_entity_sets[p].add(matching_entity)

for p in range(len(parser.predicates)):
    precision = correct_count[p] / (found_count[p] + 0.00001)
    recall = len(found_entity_sets[p]) / len(correct_entities)
    tp = correct_count[p]
    fp = found_count[p] - correct_count[p]
    print("%s pr:%6.2f re:%6.2f tp:%3d fp:%3d" % \
          ("{:<30}".format(parser.predicates[p].toString(False, False)),
           precision*100, recall*100, tp, fp))

print('Thresh\tRecall\tPrec\tF1')
for i in range(10, -1, -1):
    all_positives = 0
    true_positives = 0
    found_entities = set()
    threshold = i / 10.0
    for entity in results:
        if entity.score >= threshold:
            all_positives += 1
            matching_entity = matching_correct_entitity(entity)
            if matching_entity:
                true_positives += 1
                found_entities.add(matching_entity)
            
    precision = true_positives / (all_positives + 0.00001)
    recall = len(found_entities) / len(correct_entities)
    false_negatives = len(correct_entities) - len(found_entities)
    f1 = 2*((precision*recall)/(precision+recall + 0.00001))
    if i == 10:
        found_at_1 = found_entities
         
    print('%.3f\t%2.2f\t%2.2f\t%2.2f' % (threshold, recall*100, precision*100, f1*100))

    if i == 0:
        print('\ntp:%d fp:%d fn:%d found:%d all:%d' % (
            true_positives, all_positives - true_positives, false_negatives,
            len(found_entities), len(correct_entities) ))

"""
print('False negatives:')
for entity in correct_entities:
    if not entity in found_at_1:
        print(entity)
"""
