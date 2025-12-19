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
from joblib import Parallel, delayed
import re
import ast

## Pre-processing final dictionary before match

nlp = spacy.load('en_core_web_sm')

def pre_process(text):
    # text = text.replace("_", " ")
    if text == None or type(text) == float: return text
    texts_out = []
    new_text = []
    doc = nlp(text)  # Tokenizer
    for token in doc:
        if str(token) not in stopwords.words('english'):
            new_text.append(token.lemma_)
    final = " ".join(new_text)
    texts_out.append(final)

    if text.replace(" ", "").replace("  ", "") != texts_out[0].replace(" ", "").replace("  ", ""): 
        print(text + ' - ' + texts_out[0].replace(" ", "").replace("  ", ""))
    return texts_out[0].replace(" ", "").replace("  ", "")


def clean_k(text):
    if text == None or type(text) != float: return text.replace('_', ' ')

klist = pd.read_excel('nlp/keywords_list.xlsx')

klist['Keyword'] = klist['Keyword'].apply(lambda x: clean_k(x))

print(len(klist))
klist = klist[klist['Note']!='drop']
print(len(klist))

for i in range(1,len(klist.columns)-1):
    klist[f'co{i}'] = klist[f'co{i}'].apply(pre_process)
    klist[f'co{i}'] = klist[f'co{i}'].apply(lambda x: clean_k(x))


print(len(klist))
klist.drop_duplicates(subset=['Keyword', 'co1', 'co2', 'co3', 'co4', 'co5', 'co6'], inplace=True)
print(len(klist))
klist.to_csv('nlp/klist_final_ready.csv')



## Matching into patents' texts

df = pd.read_parquet('data/All_p_texts_lemma.parquet')

print(f'Total: {len(df):,}')
df = df[~df['full_text'].isna()]
df = df[df['full_text']!='']
df = df[df['full_text']!=' ']
df['full_text'] = df['full_text'].str.replace(' - nan', '')
df['full_text'] = df['full_text'].str.replace('nan - ', '')
df['full_text'] = df['full_text'].str.replace('nan', '')
print(f'After dropping missing: {len(df):,}')

gp= pd.read_parquet('data/GREEN_all.parquet')[['appln_id']]
print(f'GPs: {len(gp):,}')

# Select texts out of perimeter to check for false negatives
nonogp = df[~df['appln_id'].isin(gp['appln_id'])]
inv = pd.read_parquet(path + 'data/single_invetions_granted_after_2010.parquet')[['appln_id']]
nonogp = nonogp[nonogp['appln_id'].isin(inv['appln_id'])]
print(f'Non GP total: {len(nonogp):,}')

# Select traditional GPs to check for "true green"
df = df.merge(gp, on = 'appln_id', how='inner')
print(f'GP total: {len(nonogp):,}')
del gp


def count_occurrences(input_str, target_word):
    if input_str == None : return 0 

    # Convert both the input string and the target word to lowercase for case-insensitive comparison
    input_str_lower = input_str.lower()
    target_word_lower = target_word.lower()

    # Use regular expression to find word boundaries and count occurrences
    # this ensures that the target word is matched as a whole word and not as part of a larger word
    pattern = re.compile(r'\b' + re.escape(target_word_lower) + r'\b')
    count = len(re.findall(pattern, input_str_lower))

    return count


def clean_k(text):
    return text.replace('_', ' ')

klist['Keyword'] = klist['Keyword'].apply(lambda x: clean_k(x))
klist = klist[klist['Note']!='drop']

klist_cooc = klist.loc[klist['Note']=='co-occurrence'].drop(['Note'], axis=1)
klist_single = klist.loc[klist['Note']!='co-occurrence'].drop(['Note'], axis=1)

# Single expression match
matched_texts_single = pd.DataFrame()
matched_texts_single_nongp = pd.DataFrame()

# only green
for keyword in klist_single['Keyword']:
    temp_texts = df.copy()
    temp_texts['match'] = temp_texts['full_text'].apply(lambda x: count_occurrences(x, keyword))
    temp = temp_texts.loc[temp_texts['match'] != 0]
    if len(temp)==0:
        print(keyword)
    temp = temp[['appln_id', 'match']]
    temp['keyword'] = keyword
    matched_texts_single = pd.concat([matched_texts_single, temp])

# all the rest
for keyword in klist_single['Keyword']:
    temp_texts = nonogp.copy()
    temp_texts['match'] = temp_texts['full_text'].apply(lambda x: count_occurrences(x, keyword))
    temp = temp_texts.loc[temp_texts['match'] != 0]
    if len(temp)==0:
        print(keyword)
    temp = temp[['appln_id', 'match']]
    temp['keyword'] = keyword
    matched_texts_single_nongp = pd.concat([matched_texts_single_nongp, temp])


# Co-occurrences match
lista = []
# iterate through rows of the dataframe
for index, row in klist_cooc.iterrows(): 
    for i in range(1,len(klist_cooc.columns)-1):
        temp_list = []
        if type(row[f'co{i}']) != float: # drop NAN
            temp_list.append(row['Keyword']) # main keyword
            multi_term_list = row[f'co{i}'].split('&') # co-occurence
            for term in multi_term_list:
                temp_list.append(term.lower())
        if len(temp_list) > 0: lista.append(temp_list)

# Convert each pair to a frozenset (order doesn't matter) and check for duplicates
seen = set()
duplicates = []

for pair in lista:
    pair_set = frozenset(pair)
    if pair_set in seen:
        duplicates.append(pair)
    else:
        seen.add(pair_set)

print(f'Keywords before dropping duplicates: {len(lista)}')
for i in duplicates:
    lista.remove(i)
print(f'Keywords after dropping duplicates: {len(lista)}')


def find_word_positions(text, keyword):
    """Finds the positions of all occurrences of a multi-word keyword in a text."""
    words = text.split()
    keyword_words = keyword.split()
    keyword_length = len(keyword_words)
    
    positions = []
    for i in range(len(words) - keyword_length + 1):
        if words[i:i + keyword_length] == keyword_words:
            positions.append(i)
    return positions


def count_proximity_matches(positions_list, max_distance=20):
    """Counts how many times all keywords are within max_distance words of each other."""
    if not positions_list or any(len(positions) == 0 for positions in positions_list):
        return 0

    count = 0
    for i, pos in enumerate(positions_list[0]):
        if all(any(abs(pos - other_pos) <= max_distance for other_pos in other_positions)
               for other_positions in positions_list[1:]):
            count += 1
    return count


matched_texts_cooc = pd.DataFrame()
matched_texts_cooc_nongp = pd.DataFrame()

# only green
for combination in lista:
    temp_texts = df.copy()
    positions_list = []
    
    for keyword in combination:
        temp_texts[f'{keyword}_positions'] = temp_texts['full_text'].apply(lambda x: find_word_positions(x, keyword))
        positions_list.append(temp_texts[f'{keyword}_positions'].values)

    temp_texts['match'] = temp_texts.apply(lambda row: count_proximity_matches([row[f'{kw}_positions'] for kw in combination]), axis=1)
    temp = temp_texts.loc[temp_texts['match'] > 0]  # Filter only texts with at least one match
    
    temp = temp[['appln_id', 'match']]
    temp['keyword'] = f'{combination}'
    matched_texts_cooc = pd.concat([matched_texts_cooc, temp])

# all the rest
for combination in lista:
    temp_texts = nonogp.copy()
    positions_list = []
    
    for keyword in combination:
        temp_texts[f'{keyword}_positions'] = temp_texts['full_text'].apply(lambda x: find_word_positions(x, keyword))
        positions_list.append(temp_texts[f'{keyword}_positions'].values)

    temp_texts['match'] = temp_texts.apply(lambda row: count_proximity_matches([row[f'{kw}_positions'] for kw in combination]), axis=1)
    temp = temp_texts.loc[temp_texts['match'] > 0]  # Filter only texts with at least one match
    
    temp = temp[['appln_id', 'match']]
    temp['keyword'] = f'{combination}'
    matched_texts_cooc_nongp = pd.concat([matched_texts_cooc_nongp, temp])




# Merge results

match = pd.concat([matched_texts_single, matched_texts_cooc])
match_nongp = pd.concat([matched_texts_single_nongp, matched_texts_cooc_nongp])

del matched_texts_single, matched_texts_single_nongp, matched_texts_cooc, matched_texts_cooc_nongp, df, nonogp

match.drop_duplicates(subset = 'appln_id', inplace=True)
match = match [['appln_id']]
match_nongp.drop_duplicates(subset = 'appln_id', inplace=True)
match_nongp = match_nongp [['appln_id']]


match.to_parquet('data/match_true_green.parquet', engine='pyarrow')

match_nongp = pd.concat([match, match_nongp])
match_nongp.drop_duplicates(subset = 'appln_id', inplace=True)
match_nongp.to_parquet('data/match_true_green_all.parquet', engine='pyarrow')