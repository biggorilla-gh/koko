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

from unidecode import unidecode

class Ngram:

    def __init__(self, doc, span):
        self.doc = doc
        self.span = span

    def tokens(self):
        return [self.doc[i].text.lower() for i in range(self.span.start, self.span.end)]

    def key(self):
        return self.span.text.lower()

    def __eq__(self, other):
        return self.key() == other.key()

    def __ne__(self, other):
        return self.key() != other.key()

    def __hash__(self):
        return hash(self.key())

    def __len__(self):
        return len(self.span)


class Matcher:

    def __init__(self, doc):
        self.doc = doc

    # Checks if the document token at position pos matches the j-th ngram token
    def TokenMatches(self, ngram, pos, j, case_sensitive=False):
        if pos < 0 or pos >= len(self.doc):
            return False
        return (self.doc[pos].text == ngram[j]) if case_sensitive else \
            (unidecode(self.doc[pos].text).lower() == unidecode(ngram[j]).lower())

    # Returns True if the document matches the ngram at position pos, False otherwise.
    # By default, direction = 1 to match at the right of pos, including the token at pos.
    # Use direction = -1 for matching at the left of pos, excluding the token
    # at pos.
    def MatchesNgram(self, pos, ngram, direction=1, case_sensitive=False):
        offset = 0 if direction > 0 else -1  # skip token at pos for reverse match
        for i in range(len(ngram)):
            j = offset + direction * i
            if not self.TokenMatches(ngram, pos + j, j, case_sensitive):
                return False
        return True

    def FindNgram(self, ngram):
        n = len(ngram)
        for pos in range(len(self.doc) - n + 1):
            if self.MatchesNgram(pos, ngram):
                return pos, pos + n
        return 0, 0
