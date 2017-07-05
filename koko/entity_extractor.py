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
from .parser import Parser
from .scorer import Scorer

import sys

class Entity:

    def __init__(self, span):
        self.span = span
        self.mentions = []
        self.score = 0.0
        self.scores = []
        self.name = span.text.replace('\n', ' ')

    def strip(self):
        del self.scores
        for mention in self.mentions:
            mention.strip()

class Mention:

    def __init__(self, span, sentence_index=-1):
        self.span = span
        self.sentence_index = sentence_index
        self.score = 0.0
        self.scores = []
        self.debug = ''

    def strip(self):
        del self.span
        del self.sentence_index
        del self.scores
        del self.debug


class EntityExtractor:

    def __init__(self, doc, testing=False):
        self.doc = doc
        assert self.doc.is_parsed
        self.error_msg = None
        self.testing = testing
        self.matcher = Matcher(self.doc)
        #print("Collecting set of document words")
        self.doc_words = set()
        for i in range(len(doc)):
            self.doc_words.add(doc[i].text.lower())

    def TopEntities(self, query):
        #print("Parse the query")
        parser = Parser(query, self.doc_words, testing=self.testing)
        if not parser.is_parsed:
            self.error_msg = parser.error_msg
            return []
        return self.TopEntitiesForParsedQuery(parser)
        
    def TopEntitiesForParsedQuery(self, parser):
        self.query_debug = parser.toString()
        spans = self.GetSpans(parser.etype)
        #print("GetMentionsFromSpans")
        #all_mentions = self.GetMentionsFromSpans(spans)
        all_mentions = self.JoinSpansAndSentences(spans)
        return self.TopEntitiesFromMentions(parser, all_mentions)
        
    def TopEntitiesFromMentions(self, parser, mentions):
        scorer = Scorer(self.doc, self.matcher,
                        parser.predicates,
                        parser.excluding_predicates,
                        parser.sentence_decomposer_server_url)
        #print("ScoreMentions")
        scorer.ScoreMentions(mentions)
        #print("FilterMentions")
        filtered_mentions = self.FilterMentions(mentions)
        #print("ClusterMentions")
        entities = self.ClusterMentions(filtered_mentions)
        #print("ScoreEntities")
        scorer.ScoreEntities(entities)
        filtered_entities = self.FilterEntities(entities, parser.threshold)
        #self.StripEntities(filtered_entities)
        return sorted(filtered_entities, key=lambda x: x.score, reverse=True)


    def GetSpans(self, etype):
        # Collect all spans of the given type
        spans = []
        if etype == "Ents":
            spans = self.doc.ents
        elif etype == "NPs":
            spans = self.doc.noun_chunks
        elif etype[:6] == "Ngrams":
            bounds = [int(x) for x in etype[7:-1].split(',')]
            for length in range(bounds[0], bounds[1] + 1):
                for i in range(len(self.doc)-length):
                    spans.append(self.doc[i:i+length])
        else:
            etype = etype.lower()
            for i in range(len(self.doc.ents)):
                if etype == "entity" or self.doc.ents[i].syntax_type == etype:
                    spans.append(self.doc.ents[i])
        return sorted(spans, key=lambda x: x.start, reverse=False)

    def GetMentionsFromSpans(self, spans):
        mentions = []
        for span in spans:
            si = self.GetSpanSentenceNumber(span)
            mention = Mention(span)
            mention.sentence_index = si
            mentions.append(mention)
        return mentions

    def JoinSpansAndSentences(self, spans):
        mentions = []
        sents = [sent for sent in self.doc.sents]
        si = 0
        i = 0
        while i < len(spans):
            #print(i, si)
            sent = sents[si]
            span = spans[i]
            #print(span.start, span.end, sent.start, sent.end)
            if sent.end <= span.start:
                si += 1
                continue
            if span.end <= sent.end:
                mentions.append(Mention(span, si))
            i += 1
        return mentions
    
    def FindAllMentions(self, spans):
        print("GenerateAllMentions")
        mentions = []
        print("Deduplicate ngrams")
        ngrams = set(Ngram(self.doc, span) for span in spans)
        ## This is very slow for large documents.
        for ngram in ngrams:
            print(' '.join(ngram.tokens()))
            n = len(ngram)
            si = -1
            for sent in self.doc.sents:
                si += 1
                for i in range(sent.start, sent.end - n):
                    if self.matcher.MatchesNgram(i, ngram.tokens()):
                        mentions.append(Mention(self.doc[i: i + n], si))
        return mentions

    def FilterMentions(self, mentions):
        return [mention for mention in mentions if mention.score > 0]

    def FilterEntities(self, entities, threshold):
        return [e for e in entities if e.score >= threshold]

    def StripEntities(self, entities):
        for e in entities:
            e.strip()

    def ClusterMentions(self, mentions):
        ent_dict = {}
        for mention in mentions:
            name = mention.span.text.lower()
            if name not in ent_dict:
                ent_dict[name] = Entity(mention.span)
            ent_dict[name].mentions.append(mention)
        return ent_dict.values()

    def GetSentence(self, mention):
        for sent in self.doc.sents:
            if mention.span.start >= sent.start and mention.span.end <= sent.end:
                return sent.text
        return "None"

    def GetSpanSentenceNumber(self, span):
        sentence_index = -1
        for sent in self.doc.sents:
            sentence_index += 1
            if span.start >= sent.start and span.end <= sent.end:
                return sentence_index
        return -1
    
    def GetSentenceNumber(self, mention):
        sentence_index = -1
        for sent in self.doc.sents:
            sentence_index += 1
            if mention.span.start >= sent.start and mention.span.end <= sent.end:
                return sentence_index
        return -1
