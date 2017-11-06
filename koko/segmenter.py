# -*- coding: utf-8 -*-
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


import string


class Segment:

    def __init__(self, text, row, col, start, end, append_to_previous):
        self.row = row
        self.col = col
        self.start = start
        self.end = end
        self.text = text[start:end]
        self.append_to_previous = append_to_previous

    def toString(self):
        return 'Line %d col %d start %d end %d: \'%s\'' % (self.row, self.col,
                                                           self.start, self.end, self.text)


class Segmenter:

    def __init__(self):
        pass

    @staticmethod
    def Segment(text):
        segments = []
        in_segment = False
        lines = text.splitlines(True)
        row = 0
        punctuation = set(string.punctuation) | \
                      set(['“', '”', '‘', '’'])
        number_punctuation = set(['.', ','])
        line_start = 0
        n = 0
        for i in range(len(lines)):
            row += 1
            line = lines[i]
            col = 0  # holds start of segment
            line_start += n
            n = len(line)

            for j in range(n):
                c = line[j]
                if c.isspace() and in_segment:
                    append_to_previous = segments and segments[-1].end == line_start + col
                    segments.append(
                        Segment(text, row, col, line_start + col, line_start + j,
                                append_to_previous))
                    append_to_previous = False
                    in_segment = False
                elif (j > 0 and line[j - 1].isdigit() and
                      c in number_punctuation and
                      j + 1 < n and line[j + 1].isdigit()):
                    pass
                elif c in punctuation:
                    if in_segment:
                        # terminate current segment
                        in_segment = False
                        append_to_previous = segments and segments[-1].end == line_start + col
                        segments.append(
                            Segment(text, row, col, line_start + col, line_start + j,
                                    append_to_previous))
                    # create new segment with the punctuation character
                    append_to_previous = segments and segments[-1].end == line_start + j
                    segments.append(
                        Segment(text, row, j, line_start + j, line_start + j + 1,
                                    append_to_previous))
                    in_segment = False
                elif not c.isspace() and not in_segment:
                    # mark start of new segment
                    # print('column %d char %s start segment' % (j, c))
                    col = j
                    in_segment = True
        if in_segment:
            append_to_previous = segments and segments[-1].end == line_start + col
            segments.append(
                Segment(text, row, col, line_start + col, line_start + j + 1,
                        append_to_previous))
        return segments


class SegmentedSpan:

    def __init__(self, doc, start, end, syntax_type=''):
        assert(start < len(doc) and start >= 0 and
               end <= len(doc) and end >= 0), \
               "Span %d:%d is out of the document range 0:%d." % (start, end, len(doc))
        self.doc = doc
        self.start = start
        self.end = end
        first_segment = doc.segments[start]
        last_segment = doc.segments[end - 1]
        self.row = first_segment.row
        self.col = first_segment.col
        self.start_char = first_segment.start
        self.end_char = last_segment.end
        self.segments = doc.segments[start:end]
        self.text = doc.text[first_segment.start:last_segment.end]
        self.type = "text"
        self.syntax_type = syntax_type

    def __len__(self):
        return self.end - self.start

    def __getitem__(self, x):
        if isinstance(x, slice):
            return SegmentedSpan(self.doc, self.start + x.start, self.start + x.stop)
        return self.segments[x]


class SegmentedDocument:

    def __init__(self, text):
        self.text = text
        self.segments = Segmenter.Segment(self.text)

    def __len__(self):
        return len(self.segments)

    def __getitem__(self, x):
        if isinstance(x, slice):
            return SegmentedSpan(self, x.start, x.stop)
        return SegmentedSpan(self, x, x + 1)[0]
