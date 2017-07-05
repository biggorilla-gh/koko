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
from koko.entity_extractor import Mention, Entity
from koko.matcher import Matcher
from koko.parser import Predicate
from koko.scorer import Scorer
from koko.test_document import TestDocument


class ScorerTestCase(unittest.TestCase):

    def MentionScoreTest(self, document, phrase, predicates, expected_score=1):
        doc = TestDocument(document)
        matcher = Matcher(doc)
        scorer = Scorer(doc, matcher, predicates)
        mention = self.GetMention(doc, phrase)
        self.assertNotEqual(mention, None)
        scorer.ComputeMentionScore(mention)
        self.assertEqual(mention.score, expected_score)

    def GetMention(self, doc, phrase):
        ngram = phrase.split(' ')
        n = len(ngram)
        matcher = Matcher(doc)
        for si in range(len(doc.sents)):
                sent = doc.sents[si]
                for i in range(sent.start, sent.end - n):
                    if matcher.MatchesNgram(i, ngram):
                        return Mention(doc[i: i + len(ngram)], si)
        return None

    def test_left_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('left', ['this', 'is'])])

    def test_right_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('right', [',', 'a'])])

    def test_inside_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('inside', ['Cafe'])])

    def test_substring_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('substring', ['enz'])])

    def test_semantic_left_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('left', ['this', 'are'],
                                         matching='semantic',
                                         expanded_queries=[(['this', 'is'], 1.0)])])

    def text_semantic_right_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('right', [',', 'an'],
                                         matching='semantic',
                                         expanded_queries=[([',', 'a'], 1.0)])])

    def test_semantic_inside_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('inside', ['shop'],
                                         matching='semantic',
                                         expanded_queries=[(['cafe'], 1.0)])])

    def test_precedes_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('left', ['this'], 10)], 0.5)

    def test_follows_context(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [Predicate('right', ['cafe'], 10)], 0.2)

    def test_exercise(self):
        self.MentionScoreTest('I like figure skating.',
                              'figure skating',
                              [Predicate('dict', 'Exercise')])

    def test_location(self):
        self.MentionScoreTest('I work in Mountain View.',
                              'Mountain View',
                              [Predicate('dict', 'Location')])

    def test_multiple_predicates(self):
        self.MentionScoreTest('This is Cafe Benz, a full service cafe.',
                              'Cafe Benz',
                              [
                                  Predicate('left', ['this', 'is']),
                                  Predicate('right', [',', 'a']),
                                  Predicate('inside', ['Cafe'])
                              ],
                              3)

if __name__ == '__main__':
    unittest.main()
