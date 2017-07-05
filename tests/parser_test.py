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
from koko.parser import Predicate, Parser


class ParserTestCase(unittest.TestCase):

    def ParseTest(self, query, etype, types, contexts,
                  matchings=[], weights=[], excluding_contexts=[],
                  next_types=None, next_contexts=None):
        parser = Parser(query, testing=True)
        if not parser.is_parsed:
            print("error: %s" % parser.error_msg)
        self.assertTrue(parser.is_parsed)
        n= len(parser.predicates)
        self.assertEqual(n, len(types))
        self.assertEqual(n, len(contexts))
        if weights:
            self.assertEqual(n, len(weights))
        if matchings:
            self.assertEqual(n, len(matchings))
        if next_types:
            self.assertEqual(n, len(next_types))
        if next_contexts:
            self.assertEqual(n, len(next_contexts))
        for i in range(n):
            predicate = parser.predicates[i]
            self.assertEqual(predicate.type, types[i])
            self.assertEqual(predicate.context, contexts[i])
            if weights:
                self.assertEqual(predicate.weight, weights[i])
            if matchings:
                self.assertEqual(predicate.matching, matchings[i])
        if excluding_contexts:
            self.assertEqual(len(parser.excluding_predicates), len(excluding_contexts))
            for i in range(len(parser.excluding_predicates)):
                self.assertEqual(parser.excluding_predicates[i].context,
                                 excluding_contexts[i])
        self.assertEqual(parser.etype, etype)

    def test_left_context(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if ("introducing" x)'
                       'with threshold 0.8',
                       "Ents",
                       ['left'],
                       [['introducing']])

    def test_right_context(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if (x "serves coffee")'
                       'with threshold 0.8',
                       "Ents",
                       ['right'],
                       [['serves', 'coffee']])

    def test_left_right_context(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if ("introducing" x ", a cafe")'
                       'with threshold 0.8',
                       "Ents",
                       ['left'],
                       [['introducing']],
                       next_types=['right'],
                       next_contexts=[', a cafe'])

    def test_contains(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if (str(x) contains "cafe")'
                       'with threshold 0.8',
                       "Ents",
                       ['inside'],
                       [['cafe']])

    def test_mentions(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if (str(x) mentions "cafe")'
                       'with threshold 0.8',
                       "Ents",
                       ['substring'],
                       [['cafe']])

    def test_semantic_left_context(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if ("introducing" ~ x)'
                       'with threshold 0.8',
                       "Ents",
                       ['left'],
                       [['introducing']],
                       ['semantic'])

    def test_semantic_right_context(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if (x ~ "has baristas")'
                       'with threshold 0.8',
                       "Ents",
                       ['right'],
                       [['has', 'baristas']],
                       ['semantic'])

    def test_semantic_inside_context(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if (str(x) contains ~ "cafe")'
                       'with threshold 0.8',
                       "Ents",
                       ['inside'],
                       [['cafe']],
                       ['semantic'])

    def test_dict(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if (str(x) in dict("Exercise"))'
                       'with threshold 0.8',
                       "Ents",
                       ['dict'],
                       ['Exercise'])

    def test_iterator_ents(self):
        self.ParseTest('extract "Ents" x from "doc.txt" if (str(x) in dict("Exercise"))'
                       'with threshold 0.8',
                       "Ents",
                       ['dict'],
                       ['Exercise'])

    def test_iterator_nps(self):
        self.ParseTest('extract "NPs" x from "doc.txt" if (str(x) in dict("Exercise"))'
                       'with threshold 0.8',
                       "NPs",
                       ['dict'],
                       ['Exercise'])

    def test_disjunction(self):
        self.ParseTest(
            """ extract "Ents" x from "doc.txt" if
                   (str(x) contains "cafe") or
                   (x "serves coffee") or
                   ("introducing" x)
                with threshold 0.8""",
            "Ents",
            ['inside', 'right', 'left'],
            [['cafe'], ['serves', 'coffee'], ['introducing']])

    def test_weights(self):
        self.ParseTest(
            """ extract "Ents" x from "doc.txt" if
                   (str(x) contains "cafe" {1}) or
                   (x "serves coffee" {2.5}) or
                   ("introducing" x {6.5})
                with threshold 0.8""",
            "Ents",
            ['inside', 'right', 'left'],
            [['cafe'], ['serves', 'coffee'], ['introducing']],
            weights = [1, 2.5, 6.5])

    def test_excluding(self):
        self.ParseTest(
            """ extract "Ents" x from "doc.txt" if
                   (str(x) contains "cafe") or
                   (x "serves coffee") or
                   ("introducing" x)
                with threshold 0.8
                excluding (str(x) contains "the") or (x "tea") or ("food court" near x)
            """,
            "Ents",
            ['inside', 'right', 'left'],
            [['cafe'], ['serves', 'coffee'], ['introducing']],
            excluding_contexts=[['the'], ['tea'], ['food', 'court']]
        )

    def test_syntax_error(self):
        parser = Parser(
            'select Ents(x) from "doc.txt" if (x "serves coffee") with threshold 0.8')
        self.assertFalse(parser.is_parsed)
        self.assertEqual(parser.error_msg, 'Syntax error at line 1 column 0:'
                                           ' unexpected token \'select\', expecting \'extract\'')

    def test_error_non_terminated_string(self):
        parser = Parser(
            'extract "Ents" x from "doc.txt" if (str(x) contains "cafe)')
        self.assertFalse(parser.is_parsed)
        self.assertEqual(
            parser.error_msg, 'At end of query: unexpected end of query, expecting \'"\'')

'''
    def test_etype_syntax_context(self):
        self.ParseTest('extract x:Entity from "doc.txt" if ("introducing" x)'
                       'with threshold 0.8',
                       "Entity",
                       ['left'],
                       [['introducing']])
'''

if __name__ == '__main__':
    unittest.main()
