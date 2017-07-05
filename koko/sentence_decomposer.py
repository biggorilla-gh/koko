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

import json
import requests
from .koko_document import KokoDocument

class EntailedSentence:

    def __init__(self, doc, score):
        self.doc = doc
        self.score = score


class SentenceDecomposer:

    def __init__(self, server_url):
        self.server_url = server_url

    def decompose(self, doc):
        if not self.server_url:
            return [[EntailedSentence(doc, 1.0)]]
        
        r = requests.post(
            self.server_url, data={'document': doc.text.encode('utf-8')})

        if not r.text:  # Empty reply from server
            # Fall back to a single entailed sentence equal to the original text.
            return [[EntailedSentence(doc, 1.0)]]
    
        json_response = r.json()
        
        response = []
        for sentence_entry in json_response:
            entailed_sentences = []
            for entailed_sentence_entry in sentence_entry["entailment"]:
                entailed_sentence = entailed_sentence_entry[
                    "entailed_sentence"]
                score = entailed_sentence_entry["score"]
                doc = KokoDocument(entailed_sentence)
                entailed_sentences.append(EntailedSentence(doc, score))
            response.append(entailed_sentences)
        return response

