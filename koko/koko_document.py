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

class KokoDocument(SegmentedDocument):

    def __init__(self, text):
        super().__init__(text)
        # Simple-minded sentence extraction.
        self.__PopulateSents()
        # Simple heuristic for entity extraction
        self.ents = self.__GetNgramsWithCapitalizedWords()
        # Noun chunks not implemented
        self.noun_chunks = self.ents
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

    def __GetMaximalNgrams2(self, condition):
        spans = []
        for sent in self.sents:
            prev = False
            for pos in range(sent.start, sent.end):
                curr = condition(pos)
                if curr != prev:
                    if curr:
                        start = pos
                    else:
                        spans.append(self[start:pos])
                        print("Inside entity: ", self[start:pos].text)
                        prev = curr
            if curr:
                spans.append(self[start:pos])
                print("End entity: ", self[start:pos].text)
        return spans

    # Extracts maximal ngrams with capitalized tokens.
    def __GetNgramsWithCapitalizedWords(self):
        return self.__GetMaximalNgrams(lambda pos: self[pos].text.istitle())

    def __PopulateSents(self):
        self.sents = []
        start = 0
        for pos in range(len(self)):
            if self[pos].text == '.' or pos == len(self) - 1 or \
               self[pos + 1].row != self[pos].row:
                end = pos + 1
                self.sents.append(self[start:end])
                start = end
