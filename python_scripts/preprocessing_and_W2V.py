import pandas as pd
import os
import numpy as np
import nltk
import nltk.corpus
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import spacy
import gensim
import gensim.corpora as corpora
from gensim.models import TfidfModel
import pyLDAvis
import pyLDAvis.gensim_models
import random
import re
import urllib
import bs4


## Pre-processing ##

df = pd.read_parquet('data/All_p_texts.parquet')

nlp = spacy.load('en_core_web_sm')

def lemmatize_abstracts(df, allowed_postags=["NOUN", "ADJ", "VERB", "ADV"]):
    texts_out = []
    for abstract in df['appln_abstract']:
        doc = nlp(abstract)  # Tokenizer
        new_text = []
        for token in doc:
            if token.pos_ in allowed_postags and str(token) not in stopwords.words('english'):
                new_text.append(token.lemma_)
        final = " ".join(new_text)
        texts_out.append(final)
    df['appln_abstract'] = texts_out
    return df

my_df = lemmatize_abstracts(df)
my_df.to_parquet('data/All_p_texts_lemma.parquet', engine='pyarrow')



## Word2Vec ##

gp= pd.read_parquet('data/GREEN_all.parquet')[['appln_id']]
print(f'GPs: {len(gp):,}')
df = my_df.merge(gp, on = 'appln_id', how='inner')
del gp, my_df

print(f'Total: {len(df):,}')
df = df[~df['full_text'].isna()]
df = df[df['full_text']!='']
df = df[df['full_text']!=' ']
print(f'After dropping missing: {len(df):,}')

df['full_text'] = df['full_text'].str.replace(' - nan', '')
df['full_text'] = df['full_text'].str.replace('nan - ', '')
df['full_text'] = df['full_text'].str.replace('nan', '')
df['lent'] = df['full_text'].apply(lambda x: len(x))
df = df[df['lent']>20]
df = df[['full_text']]
print(f'After cleaning and dropping short texts: {len(df):,}')


text___=list(df.full_text.apply(gensim.utils.simple_preprocess))

# Reopen the keywords list from the file
with open('klist_processed_gp.txt', 'r') as file:
    keywords = [line.strip() for line in file]

imposed_bigrams = []
for k in keywords:
    if "_" in k: imposed_bigrams.append(k)

# Automatic bigram and trigram detection
bigram_phrases = gensim.models.Phrases(text___, min_count=5, threshold=100)
trigram_phrases = gensim.models.Phrases(bigram_phrases[text___], threshold=100)

# Creating phrasers
bigram = gensim.models.phrases.Phraser(bigram_phrases)
trigram = gensim.models.phrases.Phraser(trigram_phrases)

for k in imposed_bigrams:
    trigram.phrasegrams[k] = float('inf')

# Functions to apply bigrams, trigrams, and additional bigrams
def make_bigrams(texts):
    return [bigram[doc] for doc in texts]

def make_trigrams(texts):
    return [trigram[bigram[doc]] for doc in texts]

# Applying the functions
data_bigrams = make_bigrams(text___)
data_bigrams_trigrams = make_trigrams(data_bigrams)

# Training the NN
model = gensim.models.Word2Vec(
    window = 2,
    min_count = 40,
    workers = 12,
    epochs = 5,
    vector_size = 450
)
model.build_vocab(data_bigrams, progress_per=1000)
model.train(data_bigrams, total_examples=model.corpus_count, epochs=model.epochs)



## Get suggested related keywords for dictionary expansion ##

def unpack(klist, final_list):
    for k in klist:
        final_list.append(k[0])
    return final_list

keywords_list = []
non_retrieved = []
for k in keywords_test:
    try:
        temp = model.wv.most_similar(k, topn=5)
        keywords_list = unpack(temp, keywords_list)
    except:
        non_retrieved.append(k)

keywords_list = list(set(keywords_list))
keywords_list___ = pd.DataFrame(keywords_list, columns=["Values"])
keywords_list___.to_excel("nlp/keywords_list.xlsx", index=False)