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

import unittest
from koko.matcher import Matcher
from koko.test_document import TestDocument  

class MatcherTestCase(unittest.TestCase):
    def MatchTest(self, document, pos, phrase, direction=1, case_sensitive=False):
        doc = TestDocument(document)
        matcher = Matcher(doc)
        ngram = phrase.split(' ')
        self.assertTrue(matcher.MatchesNgram(pos, ngram, direction, case_sensitive))

    def test_match(self):
        self.MatchTest('This is Cafe Benz, a full service cafe.', 2, 'Cafe Benz',
                       case_sensitive=True)

    def test_match_ignore_case(self):
        self.MatchTest('This is Cafe Benz, a full service cafe.', 2, 'cafe benz')

    def test_match_beginning(self):
        self.MatchTest('This is Cafe Benz, a full service cafe.', 0, 'this is cafe benz ,')

    def test_match_end(self):
        self.MatchTest('This is Cafe Benz, a full service cafe.', 8, 'cafe .')

    def test_reverse_match(self):
        self.MatchTest('This is Cafe Benz, a full service cafe.', 4, 'Cafe Benz', -1,
        case_sensitive=True)

    def test_reverse_match_ignore_case(self):
        self.MatchTest('This is Cafe Benz, a full service cafe.', 4, 'cafe benz', -1)

    def test_reverse_match_beginning(self):
        self.MatchTest('This is Cafe Benz, a full service cafe.', 3, 'this is cafe', -1)

    def test_reverse_match_end(self):
        self.MatchTest('This is Cafe Benz, a full service cafe.', 10, 'cafe .', -1)

if __name__ == '__main__':
    unittest.main()
    
