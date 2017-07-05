"""
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
"""

import sys
import logging
from optparse import OptionParser

# Parse commandline arguments
op = OptionParser()
op.add_option("--query_file",
              action="store", type="string", dest="query_file",
              help="Query file name.")
op.add_option("--doc_parser",
              action="store", type="string", dest="doc_parser",
              default="koko",
              help="Text parser: koko or spacy.")
op.add_option("--output_format",
              action="store", type="string", dest="output_format",
              default="text",
              help="Output format: text or json.")
op.add_option("--log_level",
              action="store", type="string", dest="log_level",
              default="info",
              help="Logging level: info, warning, error.")

(opts, args) = op.parse_args()
if len(args) > 0:
    logger.error("this script takes no arguments.")

# Set up logging
logging_level_dict = { 'info': logging.INFO,
                       'warning': logging.WARNING,
                       'error': logging.ERROR }
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging_level_dict[opts.log_level])
formatter = logging.Formatter('%(levelname)s %(asctime)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

with open(opts.query_file, 'r') as qfile:
    query = qfile.read()

# Process the KOKO query

from query_processor import QueryProcessor
processor = QueryProcessor(opts.doc_parser)
response = processor.ProcessQuery(query)

# Print the results
if opts.output_format == 'text':
    print("\nResults:\n")
    print("%s %s" % ("{:<50}".format("Entity name"), "Entity score"))
    print("================================================================")
    for entity in response.entities:
        print("%s %f" % ("{:<50}".format(entity.name), entity.score))
