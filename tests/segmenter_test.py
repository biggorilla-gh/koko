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

import unittest
from koko.segmenter import Segmenter, SegmentedDocument

class SegmenterTestCase(unittest.TestCase):
                                   #            1         2
    def test_segment_query(self):  #  012345678901234567890123456
        segments = Segmenter.Segment('extract x from "doc.txt" if\n' +
                                          '  (str(x) contains "cafe")\n')

        expected_values = ['extract', 'x', 'from', '"', 'doc', '.', 'txt', '"', 'if',
                           '(', 'str', '(', 'x', ')', 'contains', '"', 'cafe', '"', ')']
        expected_rows = [1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
        expected_cols = [0, 8, 10, 15, 16, 19, 20, 23, 25, 2, 3, 6, 7, 8, 10, 19, 20, 24, 25]
        self.assertEqual(len(segments), len(expected_values))
        self.assertEqual(len(segments), len(expected_rows))
        self.assertEqual(len(segments), len(expected_cols))
        for i in range(len(segments)):
            self.assertEqual(segments[i].text, expected_values[i], 'token %d' % i)
            self.assertEqual(segments[i].row, expected_rows[i], 'token %d' % i)
            self.assertEqual(segments[i].col, expected_cols[i], 'token %d' % i)

    def test_segment_float(self):
        segments = Segmenter.Segment('Pi=3.14')
        expected_values = ['Pi', '=', '3.14']
        self.assertEqual(len(segments), len(expected_values))
        for i in range(len(segments)):
            self.assertEqual(segments[i].text, expected_values[i], 'token %d' % i)

    def test_segmented_document(self):
        #                        0 1    2  3    4       5  678  9  10  11    12   13    14 15  16
        doc = SegmentedDocument('I woke up this morning at 7:50 am and drove 3.14 miles to work.')
        self.assertEqual(len(doc), 17)
        self.assertEqual(doc[4].text, 'morning')
        self.assertEqual(doc[12].text, '3.14')
        time_span = doc[6:10]
        time_span.type = "time"
        self.assertEqual(time_span.text, '7:50 am')
        self.assertEqual(doc[6].text, '7')
        self.assertEqual(doc[7].text, ':')
        self.assertEqual(doc[8].text, '50')
        
            
if __name__ == '__main__':
    unittest.main()

