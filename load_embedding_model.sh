#!/bin/bash
set -eux

EMBEDDING_DIRECTORY_PATH=./embeddings
COMMONCRAWL_EMBEDDING_FILE_PATH=${EMBEDDING_DIRECTORY_PATH}/commoncrawl.840B.300d.txt

# In default setting, this demo script downloads word embedding files and ontology files
# Word embeddings are trained from "CommonCrawl Corpus (840B tokens, 2.2M vocab, cased, 300d vectors, 2.03 GB)."
# In detail, please check Glove site [[ http://nlp.stanford.edu/projects/glove/ ]]

# Check the existence of model directory. If not exist, create the directory.
if [ ! -d ${EMBEDDING_DIRECTORY_PATH} ]; then
    mkdir -p ${EMBEDDING_DIRECTORY_PATH}
fi

# Check the existence of commoncrawl embedding file. If not exist, download the embedding model file from glove website.
if [ ! -e ${COMMONCRAWL_EMBEDDING_FILE_PATH} ]; then
    if hash wget 2> /dev/null; then
        wget https://nlp.stanford.edu/data/glove.840B.300d.zip
    else
        curl -O https://nlp.stanford.edu/data/glove.840B.300d.zip
    fi

    tar zxvf glove.840B.300d.zip
    mv glove.840B.300d.txt ${COMMONCRAWL_EMBEDDING_FILE_PATH}
    rm glove.840B.300d.zip
fi

