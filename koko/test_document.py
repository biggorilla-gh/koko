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

from .segmenter import SegmentedDocument


class TestSpan(object):

    def __init__(self, span_text, start_pos):
        self.text = span_text
        self.start_pos = start_pos


class TestDocument(SegmentedDocument):

    def __init__(self, text):
        super().__init__(text)
        # Poor man's entity extraction
        self.ents = self.__GetNgramsWithCapitalizedWords()
        # Fake noun phrase extraction
        self.noun_chunks = self.__GetNgramsWithLongWords(5)
        # Simple-minded sentence extraction.
        self.__PopulateSents()
        self.is_parsed = True

    def __GetMaximalNgrams(self, condition):
        spans = []
        prev = False
        for pos in range(len(self)):
            curr = condition(pos)
            if curr != prev:
                if curr:
                    start = pos
                else:
                    spans.append(self[start:pos])
                prev = curr
        return spans

    # Extracts maximal ngrams with tokens with at least k letters.
    def __GetNgramsWithLongWords(self, k):
        return self.__GetMaximalNgrams(lambda pos: len(self[pos].text) >= k)

    # Extracts maximal ngrams with capitalized tokens.
    def __GetNgramsWithCapitalizedWords(self):
        return self.__GetMaximalNgrams(lambda pos: self[pos].text.istitle())

    def __PopulateSents(self):
        self.sents = []
        start = 0
        for pos in range(len(self)):
            if self[pos].text == '.' or pos == len(self) - 1:
                end = pos + 1
                self.sents.append(self[start:end])
                start = end
