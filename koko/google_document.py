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

import sys
import json
import hashlib
import httplib2
import os
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from .segmenter import SegmentedDocument, Segment, SegmentedSpan

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './google_APIconfig.json'
        
class GoogleDocument(SegmentedDocument):

    def __init__(self, text):
        # super().__init__(text)
        self.text = text
        self.chunks = self.split_doc(self.text)
        self.chunk_syntax_responses = []
        # print(self.text)
        self.populate_tokens()
        self.populate_offset_to_pos_maps()
        self.populate_sents()
        self.populate_ents()
        self.is_parsed = True

    def populate_tokens(self):
        #print("populate_tokens")
        self.segments = []
        chunk_offset = 0
        i = 0
        for chunk in self.chunks:
            #print("chunk", i, ":", len(chunk), "chars")
            response = self.analyze_chunk_syntax(chunk)
            self.chunk_syntax_responses.append(response)
            self.segments += self.get_segments(response['tokens'], chunk_offset)
            chunk_offset += len(chunk)
            i += 1
        #for s in self.segments:
        #    print("Segment: [%d, %d) = %s" % (s.start, s.end, s.text))

    def populate_offset_to_pos_maps(self):
        pos = -1
        self.beginOffset2pos = {}
        self.endOffset2pos = {}
        for segment in self.segments:
            pos += 1
            start = segment.start
            end = segment.end
            self.beginOffset2pos[start] = pos
            self.endOffset2pos[end] = pos + 1
        
    def populate_sents(self):
        #print("populate_sents")
        self.sents = []
        chunk_offset = 0
        i = 0
        for chunk in self.chunks:
            #print("chunk", i, ":", len(chunk), "chars")
            response = self.chunk_syntax_responses[i]
            self.sents += self.get_resolved_spans(response['sentences'], chunk_offset)
            chunk_offset += len(chunk)
            i += 1
        
    def populate_ents(self):
        #print("populate_ents")
        self.ents = []
        self.ents_etype = []
        chunk_offset = 0
        i = 0
        for chunk in self.chunks:
            #print("chunk", i, ":", len(chunk), "chars")
            response = self.analyze_chunk_entities(chunk)
            for entity in response['entities']:
                self.ents += self.get_resolved_spans(entity['mentions'], chunk_offset, entity['type'].lower())
            chunk_offset += len(chunk)
            i += 1
            
        self.noun_chunks = self.ents

    def get_segments(self, objs, chunk_offset=0):
        segments = []
        for obj in objs:
            span = obj['text']
            beginOffset = chunk_offset + span['beginOffset']
            text = span['content']
            endOffset = beginOffset + len(text)
            prevSegmentEndOffset = -1 if not segments else segments[-1].end
            segments.append(Segment(self.text, 0, beginOffset, \
                                         beginOffset, endOffset, beginOffset==prevSegmentEndOffset))
        return segments
            
    def get_resolved_spans(self, objs, chunk_offset=0, syntax_type=''):
        spans = []
        for obj in objs:
            span = obj['text']
            beginOffset = chunk_offset + span['beginOffset']
            text = span['content']
            endOffset = beginOffset + len(text)
            resolved_span = self.resolve_span(beginOffset, endOffset, syntax_type)
            if resolved_span:
                spans.append(resolved_span)
        return spans
    
    def resolve_span(self, beginOffset, endOffset, syntax_type):
        if not beginOffset in self.beginOffset2pos:
            print('Misaligned begin offset: %d' % beginOffset)
            return None
        start = self.beginOffset2pos[beginOffset]
        if not endOffset in self.endOffset2pos:
            print('Misaligned end offset: %d' % endOffset)
            return None
        end = self.endOffset2pos[endOffset]
        #print("Span: [%d, %d) = %s" % (start, end, self[start:end].text))
        return SegmentedSpan(self, start, end, syntax_type)
        
    def get_service(self):
        credentials = GoogleCredentials.get_application_default()
        scoped_credentials = credentials.create_scoped(
            ['https://www.googleapis.com/auth/cloud-platform'])
        http = httplib2.Http()
        scoped_credentials.authorize(http)
        return discovery.build('language', 'v1beta1', http=http)

    def lookup_cached_response(self, method, text):
        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
        file_path = 'cache/'+method+'.'+md5
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r') as myfile:
            data = myfile.read()
        #print("Returning cached response for", method, md5)
        return json.loads(data)

    def cache_response(self, method, text, response):
        if not os.path.exists('cache'):
            os.makedirs('cache')
        md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
        file_path = 'cache/'+method+'.'+md5
        with open(file_path, 'w') as myfile:
            myfile.write(json.dumps(response, indent=4, separators=(',', ': ')))
        #print("Caching response for", method, md5)
        
    def analyze_chunk_entities(self, chunk, encoding='UTF16'):
        response = self.lookup_cached_response('analyzeEntities', chunk)
        if response:
            return response
        body = {
            'document': {
                'type': 'PLAIN_TEXT',
                'content': chunk,
            },
            'encodingType': encoding,
        }
        service = self.get_service()
        request = service.documents().analyzeEntities(body=body)
        response = request.execute()
        self.cache_response('analyzeEntities', chunk, response)
        return response

    def analyze_chunk_syntax(self, chunk, encoding='UTF16'):
        response = self.lookup_cached_response('analyzeSyntax', chunk)
        if response:
            return response
        body = {
            'document': {
                'type': 'PLAIN_TEXT',
                'content': chunk,
            },
            'encodingType': encoding,
        }
        service = self.get_service()
        request = service.documents().analyzeSyntax(body=body)
        response = request.execute()
        #print(json.dumps(response, indent=4, separators=(',', ': ')))
        self.cache_response('analyzeSyntax', chunk, response)
        return response

    def split_doc(self, text, max_chunk_size=30000):
        if len(text) <= max_chunk_size:
            return [text]
        pos = text[:max_chunk_size].rfind('\n\n')
        if pos == -1:
            print("Couldn't split at paragraph, trying at end of line")
            pos = text[:max_chunk_size].rfind('\n')
        if pos == -1:
            print("Couldn't split at line, trying at end of word")
            pos = text[:max_chunk_size].rfind(' ')
        if pos == -1:
            pos = len(text)
            print("Couldn't find a suitable split point")
        return [text[:pos+1]] + self.split_doc(text[pos+1:], max_chunk_size)
        
        
