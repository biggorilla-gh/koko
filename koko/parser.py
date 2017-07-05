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
###
# Parser for KOQL.
# Example query in KOQL:
#
#   extract NPs(x) from input.txt if
#             (x ~ "serves coffee" {0.5}) or (x ~ "has baristas" {0.5}) or
#             (x near "coffee" {3.5}) or ("check out" near x {2}) or
#             (x ", a cafe" {1}) or
#             (type(x) is "Exercises" {2}) or
#             (str(x) contains "Cafe" {1}) or (str(x) contains "Roasters" {1})
#   with threshold 0.8
###


from .segmenter import SegmentedDocument
from .query_expander import create_query_expanders, tokenize_phrase, expand_phrase

query_expanders = None

class Predicate:
    # type: what type of maching (left, right, inside, type, semantic)
    # context: what phrase to look for
    # window: how far to look for context (max number of tokens to skip)
    # weight: score multiplier
    # matching: syntactic or semantic
    # expanded_queries: a set of expanded queries through query expansion

    def __init__(self, type, context, window=0, weight = 1,
                 matching ='syntactic', expanded_queries = [], pattern=''):
        self.type = type
        self.context = context
        self.window = window
        self.weight = weight
        self.matching = matching
        self.expanded_queries = expanded_queries
        self.pattern = pattern
        self.next = None

    def toString(self, rewritten = True, weight = True):
        context = '"' + ' '.join(self.context) + '"'
        if rewritten and self.expanded_queries:
            context = ''
            for (tokens, score) in self.expanded_queries:
                if context:
                    context += ' or \n'
                context += '"%s" (%.2f)' % (tokens, score)
        
        near = ' near' if self.window else ''
        tilde = ' ~' if self.matching == 'semantic' else ''
        s = '('
        if self.type == 'left':
            s += context + near + tilde + ' x'
            if self.next:
                s += ' and ' + self.next.toString()
        elif self.type == 'right':
            s += 'x' + near + tilde + ' ' + context
        elif self.type == 'inside':
            s += 'str(x) contains ' + context
        elif self.type == 'substring':
            s += 'str(x) mentions ' + context
        elif self.type == 'match':
            s += 'str(x) matches ' + context
        if weight and self.weight != 1:
            s += ' { %.2f }' % self.weight
        s += ')'
        return s


class Parser:

    def __init__(self, query, wordset=None, testing=False):
        self.query = query
        self.wordset = wordset
        self.document_name = ''
        self.sentence_decomposer_server_url = ''
        self.predicates = []
        self.excluding_predicates = []
        self.threshold = 0
        self.lines = []
        self.curr_pos = 0
        self.error_msg = ''
        global query_expanders 
        if not query_expanders:
            query_expanders = create_query_expanders(testing)
        self.is_parsed = self.Parse(query)

    def toString(self):
        s = 'extract "%s" %s from "%s" if\n\t%s   \nwith threshold %.2f\n' % (
                   self.document_name,
                   self.etype,
                   self.variable_name,
                   ' or\n\t'.join([p.toString() for p in self.predicates]),
                   self.threshold )
        if self.excluding_predicates:
            s += 'excluding\n\t%s\n' % '\n\t'.join([p.toString()
                                                  for p in self.excluding_predicates])
        if self.sentence_decomposer_server_url:
            s += 'using sentence decomposition server "%s"\n' % self.sentence_decomposer_server_url
        return s

    def AtEnd(self):
        return self.curr_pos >= len(self.query_doc)

    def CurrToken(self):
        return self.query_doc[self.curr_pos]

    def Advance(self):
        if self.curr_pos < len(self.query_doc):
            self.curr_pos += 1

    def Rewind(self):
        if self.curr_pos > 0:
            self.curr_pos -= 1
            
    def Parse(self, query):
        self.lines = query.split('\n')
        self.query_doc = SegmentedDocument(query)
        try:
            self.Query()
        except AssertionError as error:
            if self.AtEnd():
                self.error_msg = "At end of query: %s" % error
            else:
                curr_token = self.CurrToken()
                self.error_msg = "Syntax error at line %d column %d: %s" % (curr_token.row,
                                                                            curr_token.col,
                                                                            error)
            return False
        return True

    # Asserts the current token has a given value, and consumes it
    def Literal(self, literal):
        assert(not self.AtEnd()), "unexpected end of query, expecting '%s'" % literal

        assert(self.Match(literal)), "unexpected token '%s', expecting '%s'" % (self.CurrToken().text,
                                                                                literal)
        self.Advance()

    # Compares the current token to a given value, but doesn't consume it
    def Match(self, literal):
        if self.AtEnd():
            return False
        return self.CurrToken().text.lower() == literal

    def Query(self):
        self.Literal("extract")
        #Determine the syntax
        if self.Match('"'):
            self.etype = self.QuotedString()[0]
            self.VariableDefinition()
        else:
            self.VariableDefinition()
            self.Literal(":")
            self.VariableType()
        self.Literal("from")
        self.DocumentName()
        self.Literal("if")
        self.Condition()
        while not self.AtEnd():
            if self.Match('with'):
                self.Threshold()
            elif self.Match('excluding'):
                self.Advance()
                self.ExcludingCondition()
            elif self.Match('using'):
                self.UsingDecompositionServer()

    def DocumentName(self):
        self.document_name = self.QuotedString()[0]

    def VariableDefinition(self):
        #assert(self.CurrToken().isidentifier()), "expecting identifier"
        self.variable_name = self.CurrToken().text
        self.Advance()
        
    def VariableType(self):
        self.etype = self.CurrToken().text
        self.Advance()

    def VariableReference(self):
        self.Literal(self.variable_name)

    def QuotedString(self):
        self.Literal('"')
        start = self.curr_pos
        while not self.AtEnd() and not self.Match('"'):
            self.Advance()
        end = self.curr_pos
        self.Literal('"')
        start_token = self.query_doc[start]
        char_start = start_token.start
        end_token = self.query_doc[end]
        char_end = end_token.start
        text = self.query[char_start:char_end]
        return tokenize_phrase(text)

    def Weight(self):
        self.Literal('{')
        start = self.curr_pos
        while not self.AtEnd() and not self.Match('}'):
            self.Advance()
        end = self.curr_pos
        self.Literal('}')
        return float(self.query_doc[start:end].text)

    def Condition(self):
        self.Literal('(')
        predicate = self.Predicate()
        if self.Match('{'):
            weight = self.Weight()
            predicate.weight = weight
        self.Literal(')')
        self.predicates.append(predicate)        
        if self.Match('or'):
            self.Advance()
            self.Condition()

    def ExcludingCondition(self):
        self.Literal('(')
        predicate = self.Predicate()
        if self.Match('{'):
            weight = self.Weight()
            predicate.weight = weight
        self.Literal(')')
        self.excluding_predicates.append(predicate)        
        if self.Match('or'):
            self.Advance()
            self.ExcludingCondition()

    def Threshold(self):
        self.Literal('with')
        self.Literal('threshold')
        self.threshold = float(self.CurrToken().text)
        self.Advance()

    def UsingDecompositionServer(self):
        self.Literal('using')
        self.Literal('sentence')
        self.Literal('decomposition')
        self.sentence_decomposer_server_url = 'http://koko-demo.com:8000'
        if self.Match('server'):
            self.Advance()
            url_tokens = self.QuotedString()
            self.sentence_decomposer_server_url = ''.join(url_tokens)

    def Predicate(self):
        predicate = None
        if self.Match('"'):  # left context predicate such as: "introducing" x
            predicate = self.LeftPredicate()
        elif self.Match('str'):  # contains predicate such as: str(x) contains "cafe"
            predicate = self.InsidePredicate()
        elif self.Match('type'):   # type(x) is "Exercise"
            predicate = self.TypePredicate()
        # right context predicate such as: x ", a cafe"
        elif self.Match(self.variable_name):
            predicate = self.RightPredicate()
        else:
            assert(False), "unexpected token '%s'" % self.CurrToken().text
        global query_expanders
        if predicate.matching == 'semantic':
            predicate.expanded_queries = expand_phrase(
                query_expanders, predicate.context, self.wordset)
        return predicate

    def LeftPredicate(self):
        context = self.QuotedString()
        type = 'left'
        matching='syntactic'
        window = 0
        if self.Match('~'):
            self.Advance()
            matching = 'semantic'
        elif self.Match('near'):  # proximity context predicate such as: "coffee" near x
            self.Advance()
            window = 10
        self.VariableReference()
        predicate = Predicate(type, context, window, matching=matching)
        if not self.Match(')') and not self.Match('{') :
            self.Rewind()
            predicate.next = self.Predicate()
        return predicate

    def RightPredicate(self):
        self.VariableReference()
        type = 'right'
        matching='syntactic'
        window = 0
        if self.Match('~'):
            self.Advance()
            matching = 'semantic'  # semantic context predicate such as: x ~ "had baristas"
        elif self.Match('near'):
            self.Advance()  # proximity context predicate such as: x near "coffee"
            window = 10
        context = self.QuotedString()
        return Predicate(type, context, window, matching=matching)

    def InsidePredicate(self):
        self.Literal('str')
        self.Literal('(')
        self.VariableReference()
        self.Literal(')')
        type = 'inside'
        matching='syntactic'
        if self.Match('contains'):
            self.Advance()
        elif self.Match('mentions'):
            self.Advance()
            type='substring'
        elif self.Match('matches'):
            self.Advance()
            type='match'
        elif self.Match('in'):
            self.Advance()
            self.Literal('dict')
            self.Literal('(')
            context = self.QuotedString()[0]
            self.Literal(')')
            return Predicate('dict', context)
        if self.Match('~'):
            self.Advance()
            matching = 'semantic'
        context = self.QuotedString()
        pattern = ' '.join(context)
        return Predicate(type, context, matching=matching, pattern=pattern)

    def TypePredicate(self):
        self.Literal('type')
        self.Literal('(')
        self.VariableReference()
        self.Literal(')')
        self.Literal('is')
        context = self.QuotedString()[0]
        return Predicate('type', context)
