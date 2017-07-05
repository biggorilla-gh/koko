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

# Warning: the extracted entities and noun chunks are fake, using simple heuristics for extraction.

import unittest
from koko.test_document import TestDocument  

class TestDocumentTestCase(unittest.TestCase):
    def setUp(self):
        #           0 1    2     3      4    5    6        7 8   9   10   11   12    13     14  15 16
        document = 'I like Philz Coffee more than Starbucks, and way more than Peets Coffee and Tea.'
        self.doc = TestDocument(document)
    
    def test_len(self):
        self.assertEqual(len(self.doc), 17)

    def test_token(self):
        token = self.doc[3]
        self.assertEqual(token.start, 13)
        self.assertEqual(token.end, 19)
        self.assertEqual(token.text, 'Coffee')

    def test_span(self):
        span = self.doc[2:4]
        self.assertEqual(span.start, 2)
        self.assertEqual(span.end, 4)
        self.assertEqual(span.text, 'Philz Coffee')

    def test_span_text(self):
        span = self.doc[6:9]
        self.assertEqual(span.start, 6)
        self.assertEqual(span.end, 9)
        self.assertEqual(span.text, 'Starbucks, and')

    def test_ents(self):
        entities = [e.text for e in self.doc.ents]
        self.assertEqual(entities, ['I', 'Philz Coffee', 'Starbucks', 'Peets Coffee', 'Tea'])

    def test_noun_chunks(self):
        nps = [e.text for e in self.doc.noun_chunks]
        self.assertEqual(nps, ['Philz Coffee', 'Starbucks', 'Peets Coffee'])

    def test_sents(self):
        sents = self.doc.sents
        self.assertEqual(len(sents), 1)
        sent = sents[0]
        self.assertEqual(sent.start, 0)
        self.assertEqual(sent.end, len(self.doc))
        self.assertEqual(sent.text,
                         'I like Philz Coffee more than Starbucks, '
                         'and way more than Peets Coffee and Tea.')

if __name__ == '__main__':
    unittest.main()
