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

import os, time
import operator
from collections import defaultdict
import numpy
from langdetect import detect
import progressbar
from .google_document import GoogleDocument
ROOT = os.path.abspath(os.path.dirname(__file__))

class QueryExpander(object):

    def __init__(self, lang, embedding_file_path=None, ontology_file_path=None):
        print('Creating QueryExpander for:', lang)
        self.lang = lang
        self.__embed_vectors = None
        self.__ontology_dict = None
        self.__load_embeding_model(embedding_file_path)
        self.__load_ontology_file(ontology_file_path)

    def __load_embeding_model(self, file_path, max_vocab_size=100000):
        self.__embed_vectors = dict()
        if not file_path:
            print('Embeddings file not provided')
            return
        if not os.path.exists(file_path):
            print('Embeddings file not found:', file_path)
            return
        
        print('Loading the embedding model from:', file_path)
        bar = progressbar.ProgressBar(max_value=max_vocab_size)
        with open(file_path, "r") as embed_f:
            for line in embed_f:
                try:
                    tab = line.rstrip().split()
                    word = tab[0].lower()
                    if not word in self.__embed_vectors:
                        vec = numpy.array(tab[1:], dtype=float)
                        self.__embed_vectors[word] = vec
                except ValueError:
                    continue
                bar.update(len(self.__embed_vectors))
                if len(self.__embed_vectors) == max_vocab_size:
                    bar.finish()
                    return


    def __load_ontology_file(self, file_path):
        self.__ontology_dict = defaultdict(set)
        if not file_path:
            print('Ontology file not provided')
            return
        
        if not os.path.exists(file_path):
            print('Ontology file not found:', file_path)
            return
        
        print('Loading ontology from:', file_path)
        with open(file_path, 'r') as ontology_f:
            for line in ontology_f:
                parent_word, child_word = line.rstrip().split('\t')
                self.__ontology_dict[parent_word].add(child_word)

    def __expand_word(self, word, topk=10, ontology_score=0.9):
        def _similarity(v1, v2):
            if v1.shape != v2.shape:
                return 0
            n2 = numpy.linalg.norm(v2)
            return float(numpy.dot(v1, v2) / n2)

        result = dict()
        result[word] = 1.0
        if self.__embed_vectors and word in self.__embed_vectors:
            word_vec = self.__embed_vectors[word]
            word_vec /= numpy.linalg.norm(word_vec)
            for cand_word, cand_vec in self.__embed_vectors.items():
                if cand_word.lower() == word.lower():
                    continue
                score = _similarity(word_vec, cand_vec)
                if cand_word in result:
                    result[cand_word] = max(score, result[cand_word])
                else:
                    result[cand_word] = score

        if word in self.__ontology_dict:
            for child_word in self.__ontology_dict[word]:
                if child_word in result:
                    result[child_word] = max(
                        ontology_score, result[child_word])
                else:
                    result[child_word] = ontology_score

        result = sorted(
            result.items(), key=operator.itemgetter(1,0), reverse=True)
        top_results = result[:min(len(result), topk)]
        return result[:min(len(result), topk)]

    def expand(self, context_tokens, wordset=None, threshold_score=0.5):
        result_list = []
        for pos, word in enumerate(context_tokens):
            word_score_pairs = self.__expand_word(word)
            next_result_list = []
            for word, score in word_score_pairs:
                if score < threshold_score:
                    continue
                if wordset and not word in wordset:
                    continue
                if pos == 0:
                    next_result_list.append(([word], score))
                    continue
                for tokens, phrase_score in result_list:
                    new_score = phrase_score * score
                    if new_score < threshold_score:
                        continue
                    next_result_list.append(
                        (tokens + [word], new_score))
            result_list = next_result_list
        result_list = sorted(
            result_list, key=operator.itemgetter(1), reverse=True)
        return result_list
       

def create_query_expanders(testing):
    if testing:
        query_expanders = {
            'en': QueryExpander('en')
        }
        return query_expanders
    
    print('Loading embedding models')
    en_embedding_file_path = ROOT + '/../embeddings/commoncrawl.840B.300d.txt'
    ontology_file_path = ROOT + '/../coffee_ontology.txt'
    ja_embedding_file_path = ROOT + '/../embeddings/japanese_noun_verb_embedding_vectors.txt'
    query_expanders = {
        'en': QueryExpander('en', en_embedding_file_path, ontology_file_path),
        'ja': QueryExpander('ja', ja_embedding_file_path)
    }
    print('Done loading embedding models')
    return query_expanders

def expand_phrase(query_expanders, tokens, wordset):
    phrase = " ".join(tokens)
    try:
        lang = detect(phrase)
    except Exception:
        lang = 'en'
    if not lang in query_expanders:
        return [(tokens, 1.0)]
    return query_expanders[lang].expand(tokens, wordset)

def tokenize_phrase(phrase):
    if len(phrase) == 0:
        return ['']
    try:
        lang = detect(phrase)
    except Exception:
        lang = 'en'

    if lang == 'ja':
        doc = GoogleDocument(phrase)
        tokens = [doc[i].text for i in range(len(doc))]
        #print('Japanese phrase tokens:', tokens)
    else:
        tokens = phrase.split()
    return tokens
