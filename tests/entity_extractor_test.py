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

# Unit tests for EntityExtractor

import unittest
from koko.entity_extractor import EntityExtractor
# Dependency injection: use TestDocument instead of the SpaCy document to avoid loading
# the SpaCy models.
# Warning: the extracted entities and noun chunks are fake, using simple heuristics.
from koko.test_document import TestDocument  

class EntityExtractorTestCase(unittest.TestCase):
    def QueryTest(self, document, query, expected_top_entities, expected_top_scores = None):
        doc = TestDocument(document)
        extractor = EntityExtractor(doc, testing=True)
        entities = extractor.TopEntities(query)
        n = len(entities)
        self.assertGreaterEqual(n, len(expected_top_entities))
        if expected_top_scores:
            self.assertEqual(len(expected_top_entities), len(expected_top_scores))
        for i in range(len(expected_top_entities)):
            curr_entity = entities[i]
            self.assertEqual(curr_entity.span.text, expected_top_entities[i])
            if expected_top_scores:
                self.assertAlmostEqual(curr_entity.score, expected_top_scores[i])

    def test_ents_left_context(self):
        self.QueryTest('Let me introduce Cafe Benz, a full service cafe '
                       'in the middle of the car dealership.'
                       'Sit on a soft leather couch in Cafe Benz.',
                       'extract "Ents" x from "doc.txt" if ("introduce" x)'
                       'with threshold 0.8',
                       ['Cafe Benz'])

    def test_ents_right_context(self):
        self.QueryTest('This is Cafe Benz, a full service cafe.',
                       'extract "Ents" x from "doc.txt" if (x ", a full service")'
                       'with threshold 0.8',
                       ['Cafe Benz'])

    def test_ents_semantic_right_context(self):
        self.QueryTest('this is Cafe Benz, a full service cafe.',
                       'extract "Ents" x from "doc.txt" if (x ~ "full service")'
                       'with threshold 0.8',
                       ['Cafe Benz'])

    def test_nps_left_context(self):
        self.QueryTest("Should we go to Starbucks or Philz Coffee this time?",
                       'extract "NPs" x from "doc.txt" if ("go to" x)'
                       'with threshold 0.8',
                       ['Starbucks'])

    def test_nps_inside_context(self):
        self.QueryTest('Philz Coffee is an American coffeehouse chain.',
                       'extract "NPs" x from "doc.txt" if (str(x) contains "Coffee")'
                       'with threshold 0.7',
                       ['Philz Coffee'])

    def test_nps_inside_context_score(self):
        self.QueryTest('Philz Coffee is an American coffeehouse chain.',
                       'extract "NPs" x from "doc.txt" if '
                       '        (str(x) contains "Coffee" {0.8}) or'
                       '        (str(x) contains "coffeehouse" {0.9})'
                       'with threshold 0.7',
                       ['American coffeehouse chain', 'Philz Coffee'],
                       [0.9, 0.8])

    def test_nps_substring_context(self):
        self.QueryTest('Philz Coffee is an American coffeehouse chain.',
                       'extract "NPs" x from "doc.txt" if (str(x) mentions "hilz")'
                       'with threshold 0.7',
                       ['Philz Coffee'])

    def test_ngrams_right_near_context(self):
        self.QueryTest('This is Cafe Benz, a full service cafe.',
                       '''
                       extract "Ngrams(1,2)" x from "doc.txt" if
                       (x near "a full service" {0.5}) or
                       ("is" x {0.5})
                       with threshold 0.5
                       excluding (str(x) contains ",")
                       ''',
                       ['Cafe Benz', 'Cafe'])

    def test_excluding(self):
        self.QueryTest('Philz Coffee is a coffeehouse chain with many stores in California.',
                       'extract "NPs" x from "doc.txt" if '
                       '        (str(x) contains "Coffee" {0.8}) or'
                       '        (str(x) contains "coffeehouse" {0.9}) or'
                       '        ("in" x) '
                       'with threshold 0.7 '
                       'excluding (str(x) matches "[a-z ]+") or (str(x) in dict("Location"))',
                       ['Philz Coffee'],
                       [0.8])

    def test_multiple_condition_score(self):
        self.QueryTest('Philz Coffee is an American coffeehouse chain.',
                       'extract "NPs" x from "doc.txt" if'
                       '        (x near "coffeehouse" {0.8}) or'
                       '        (str(x) contains "Coffee" {0.95})'
                       'with threshold 0.8',
                       ['Philz Coffee'],
                       [1.0])

    def test_nps_precedes_context_score(self):
        self.QueryTest('In 2003, Phil converted his corner store into Philz Coffee.',
                       'extract "NPs" x from "doc.txt" if ("store" near x {0.8})'
                       'with threshold 0.3',
                       ['Philz Coffee'],
                       [0.4])

    def test_nps_follows_context_score(self):
        self.QueryTest('Philz Coffee has great coffee.',
                       'extract "NPs" x from "doc.txt" if (x near "coffee" {0.9})'
                       'with threshold 0.2',
                       ['Philz Coffee'],
                       [0.3])

    def test_exercise_score(self):
        self.QueryTest('I like figure skating on TV.',
                       'extract "NPs" x from "doc.txt" if (str(x) in dict("Exercise") {0.99})'
                       'with threshold 0.8',
                       ['figure skating'],
                       [0.99])

'''
    def test_ents_etype_context(self):
        self.QueryTest('Let me introduce Cafe Benz, a full service cafe '
                       'in the middle of the car dealership.'
                       'Sit on a soft leather couch in Cafe Benz.',
                       'extract x:Entity from "doc.txt" if ("introduce" x)'
                       'with threshold 0.8',
                       ['Cafe Benz'])
'''

if __name__ == '__main__':
    unittest.main()

    
