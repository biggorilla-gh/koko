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

# encoding=utf8
# export FLASK_APP=demo.py
# python -m flask run
#

import spacy
from entity_extractor import EntityExtractor
from flask import Flask,render_template,request,url_for

app = Flask(__name__)

print("Loading SpaCy English models...")
nlp = spacy.load('en')
print("Done loading models")

@app.route('/')
def root():
    document = open('cafe.txt').read()
    query_str = """extract "Ents" x from "input.txt" if
                   (x "serves coffee" {0.5}) or
                   ("introducing" x {0.1}) or
                   (str(x) contains "coffee shop" {1}) or
                   (str(x) contains "cafe" {1})
               with threshold 0.8
            """

    return render_template('query.html',
                           document=document,
                           query=query_str)

@app.route('/query', methods=['POST', 'GET'])
def query():
    if request.method == 'POST':
        document = request.form['document']
        query_str = request.form['query']
        extractor = EntityExtractor(nlp(document), True)
        entities = extractor.TopEntities(query_str)
        return render_template('query.html',
                               document=document,
                               query=query_str,
                               entities=entities,
                               extractor=extractor)
    else:
        root()

with app.test_request_context():        
    url_for('static', filename='style.css')
