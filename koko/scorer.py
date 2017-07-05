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

from .entity_classifier import DictionaryEntityClassifier
from .semantic_scorer import SemanticScorer
import re
import os, sys

curr_dir = os.path.dirname(__file__)
dic_path = curr_dir + '/dict/'

class Scorer:

    def __init__(self, doc, matcher, predicates, excluding_predicates=[],
                 sentence_decomposer_server_url=''):
        self.doc = doc
        self.predicates = predicates
        self.excluding_predicates = excluding_predicates
        self.num_predicates = len(predicates)
        self.entity_classifiers = dict()
        for name in os.listdir(dic_path):
            type_name = os.path.splitext(name)[0]
            self.entity_classifiers[type_name] = \
                DictionaryEntityClassifier(dic_path+name)
        self.matcher = matcher
        self.semantic_scorer = SemanticScorer(self.doc, sentence_decomposer_server_url)

    def PredicateMatchScore(self, mention, predicate):
        span = mention.span
        n = len(predicate.context)
        context = predicate.context
        window = predicate.window
        if predicate.matching == 'semantic':
            return self.semantic_scorer.ComputeSemanticScore(mention, predicate)
        elif predicate.type == 'left':
            linked_predicate_score = 1
            if predicate.next:
                linked_predicate_score = self.PredicateMatchScore(mention, predicate.next)
            return linked_predicate_score * self.ContextMatchScore(span.start,
                                                                   context, window, -1)
        elif predicate.type == 'right':
            return self.ContextMatchScore(span.end, context, window)
        elif predicate.type == 'inside':
            window = len(span) - len(predicate.context)
            return 1 if self.ContextMatchScore(span.start, context,
                                               window, case_sensitive=True) > 0 else 0
        elif predicate.type == 'substring':
            return span.text.find(predicate.pattern) >= 0
        elif predicate.type == 'match':
            match = re.fullmatch(predicate.pattern, span.text)
            return 1 if match else 0
        elif predicate.type == 'type':
            return self.TypeMatchScore(span, context)
        elif predicate.type == 'dict':
            return self.DictionaryMatchScore(span, context)
        return 0

    def IsExcluded(self, mention):
        for predicate in self.excluding_predicates:
            if self.PredicateMatchScore(mention, predicate):
                return True
        return False
    
    def ComputeMentionScore(self, mention):
        mention.scores = []
        mention.score = 0
        if self.IsExcluded(mention):
            mention.score = -1
            return
        for i in range(self.num_predicates):
            predicate = self.predicates[i]
            predicate_score = self.PredicateMatchScore(mention, predicate)
            mention.score += predicate.weight * predicate_score
            mention.scores.append(predicate_score)

    def ScoreMentions(self, mentions):
        for mention in mentions:
            self.ComputeMentionScore(mention)

    # Aggregates entity scores from mentions scores.
    # Assummes mention scores have already been populated.
    def AggregateEntityScores(self, entity):
        entity.scores = [0 for i in range(self.num_predicates)]
        for mention in entity.mentions:
            if mention.score < 0:  # excluded mention
                return
            for i in range(self.num_predicates):
                entity.scores[i] += mention.scores[i]

    def ScoreEntities(self, entities):
        for entity in entities:
            self.AggregateEntityScores(entity)
            entity.score = 0
            for i in range(self.num_predicates):
                entity.score += self.predicates[i].weight * entity.scores[i]
            if entity.score > 1:
                entity.score = 1

    # Computes the context match score by looking for matches inside a window.
    def ContextMatchScore(self, pos, context, window, direction=1, case_sensitive=False):
        for distance in range(window + 1):
            if self.matcher.MatchesNgram(pos + direction * distance, context,
                                         direction, case_sensitive):
                return 1 / (1 + distance)
        return 0

    # Computes the dictionary match score.
    def DictionaryMatchScore(self, span, type_name):
        if not type_name in self.entity_classifiers:
            return 0
        return self.entity_classifiers[type_name].is_entity(span.text)

