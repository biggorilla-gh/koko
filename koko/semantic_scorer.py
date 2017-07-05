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

from .matcher import Matcher, Ngram
from .sentence_decomposer import SentenceDecomposer

class SemanticScorer(object):

    def __init__(self, doc, sentence_decomposer_server_url = ''):
        self.doc = doc
        self.sentence_wordsets = []
        self.sentences = []
        self.entailed_sentences = []
        self.sentence_decomposer_server_url = sentence_decomposer_server_url
        for sent in doc.sents:
            wordset = set()
            for word in sent:
                wordset.add(word.text.lower())
            self.sentence_wordsets.append(wordset)
            self.sentences.append(sent)
            self.entailed_sentences.append([])

    def PruneExpandedQueries(self, sentence_index, expanded_queries):
        valid_expanded_queries = []
        for (expanded_tokens, query_score) in expanded_queries:
            valid = True
            for token in expanded_tokens:
                if token not in self.sentence_wordsets[sentence_index]:
                    valid = False
                    break
            if valid:
                valid_expanded_queries.append((expanded_tokens, query_score))
        return valid_expanded_queries

    def ComputeSemanticScore(self, mention, predicate):
        ngram = Ngram(self.doc, mention.span).tokens()
        maximum_score = 0.0
        sentence_index = mention.sentence_index
        valid_expanded_queries = self.PruneExpandedQueries(sentence_index,
                                                           predicate.expanded_queries)
        if not valid_expanded_queries:
            return 0.0
        
        if predicate.type == 'inside':
            matcher = Matcher(self.doc)
            for (expanded_tokens, query_score) in valid_expanded_queries:
                if query_score <= maximum_score:
                    continue
                for pos in range(mention.span.start, \
                                 mention.span.end - len(expanded_tokens) + 1):
                    if matcher.MatchesNgram(pos, expanded_tokens):
                        maximum_score = query_score
            return maximum_score
        elif predicate.type == 'substring':
            for (expanded_tokens, query_score) in valid_expanded_queries:
                if query_score <= maximum_score:
                    continue
                if mention.span.text.lower().find(' '.join(expanded_tokens)) >= 0:
                    maximum_score = query_score
            return maximum_score
        

        entailed_sentences = self.entailed_sentences[sentence_index]  # look up in cache
        if not entailed_sentences:
            # lazy decomposition
            sentence = self.sentences[sentence_index]
            # print('Requesting entailed sentences for: %s' % sentence)
            
            decomposer = SentenceDecomposer(self.sentence_decomposer_server_url)
            entailed_sentences = decomposer.decompose(sentence)
            self.entailed_sentences[sentence_index] = entailed_sentences  # cache the result

        for entailed_sentence_list in entailed_sentences:
            for entailed_sentence in entailed_sentence_list:
                if entailed_sentence.score <= maximum_score:
                    continue
                matcher = Matcher(entailed_sentence.doc)
                start, end = matcher.FindNgram(ngram)
                if start == end:
                    continue
                for (expanded_tokens, query_score) in valid_expanded_queries:
                    score = query_score * entailed_sentence.score
                    if score <= maximum_score:
                        continue
                    sent = entailed_sentence.doc
                    sequence = sent[0:start]
                    if predicate.type == 'right':
                        if end == len(sent):
                            continue
                        sequence = sent[end:len(sent)]
                    if self.SubsequenceMatch(sequence, expanded_tokens):
                        maximum_score = score
                        mention.debug = '%s : %s' % (' '.join(expanded_tokens),
                                                     entailed_sentence.doc.text)
        return maximum_score

    def SubsequenceMatch(self, sequence, pattern):
        start = 0
        end = len(sequence)
        for token in pattern:
            found = False
            for pos in range(start, end):
                if sequence[pos].text.lower() == token.lower():
                    found = True
                    start = pos + 1
                    break
            if not found:
                return False
        return True
