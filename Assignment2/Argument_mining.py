
import numpy as np
import sys
import pandas as pd
import spacy
import nltk
import json
import re
from collections import Counter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn import metrics,naive_bayes

nlp = spacy.load("en_core_web_sm")

train_data_file = sys.argv[1]
val_data_file = sys.argv[2]

df_train = pd.read_json(train_data_file)
df_val = pd.read_json(val_data_file)


# display(df_train)

# %% md

### Function: Pre-process the text(lower casing, lead/train space stripping,remove punctuations)

# %%

def PreprocessData(df):
    df['clean_text'] = df['text'].str.lower()
    df['clean_text'] = df['clean_text'].str.strip()
    df['clean_text'] = df['clean_text'].str.replace('[^\w\s]', '')
    return df


# %% md

### Function: Linguistic Feature Extraction

# %%

def FeatureExtract(df):
    df['token_count'] = df['clean_text'].apply(lambda x: len(nlp(x)))

    md_exist_list = []  # modal verb
    verb_count_list = []  # verb
    prp_exist_list = []  # personal pronouns
    vbp_exist_list = []  # verb non 3rd person
    adv_exist_list = []  # adverb

    for text in df['clean_text']:
        doc = nlp(text)
        md_exist = 0
        verb_count = 0
        prp_exist = 0
        vbp_exist = 0
        adv_exist = 0

        for token in doc:
            if token.tag_ == 'MD':
                md_exist = 1

            if token.pos_ == 'VERB':
                verb_count = 1

            if token.tag_ == 'PRP':
                prp_exist = 1

            if token.tag_ == 'VBP':
                vbp_exist = 1

            if token.pos_ == 'ADV':
                adv_exist = 1

        md_exist_list.append(md_exist)
        verb_count_list.append(verb_count)
        prp_exist_list.append(prp_exist)
        vbp_exist_list.append(vbp_exist)
        adv_exist_list.append(adv_exist)

    df['modal_exist'] = md_exist_list
    df['verb_count'] = verb_count_list
    df['prp_exist'] = prp_exist_list
    df['vbp_exist'] = vbp_exist_list
    df['adv_exist'] = adv_exist_list
    return df


# %% md

### Preprocess and feature extraction: Train and Val set

# %%

df_train = PreprocessData(df_train)
df_train = FeatureExtract(df_train)

df_val = PreprocessData(df_val)
df_val = FeatureExtract(df_val)
#display(df_train)
# print("next \n")
#display(df_val)

# %%

# this code is for analying the features. Uncomment the second line to test different features

# display(df_train)
# df_train.loc[(df_train['adv_exist'] != 0) & (df_train['label'] == 1)]

# %%

# this part contains junk code for testing

text = "him personally believe had would feel death penalty should be abolished plays"
doc1 = nlp(text)
md_count = 0
for token in doc1:
    print(token.pos_, token.tag_)
    if token.tag_ == 'MD':
        md_count = md_count + 1

print(md_count)

spacy.explain('VBG')

# junk code ends here

# %% md

### Feature Extraction using Bag of Words(uni and bigrams): Train and Val set

# %%

vectorizer = CountVectorizer(ngram_range=(1, 2))
feature_matrix_bow = vectorizer.fit_transform(df_train['clean_text'])

df_features_bow = pd.DataFrame(feature_matrix_bow.toarray())
# df_features_text = df_train[["token_count","modal_exist","verb_count","prp_exist","vbp_exist","adv_exist"]]
df_features_text = df_train[["modal_exist", "verb_count", "prp_exist", "vbp_exist", "adv_exist"]]
df_features = pd.concat([df_features_bow, df_features_text], axis=1)

x_train = df_features.values
y_train = df_train['label'].values

# display(df_features)
# print(feature_matrix_bow.shape)
print(x_train.shape)
print(y_train.shape)

# %%

feature_matrix_bow_val = vectorizer.transform(df_val['clean_text'])

df_features_bow_val = pd.DataFrame(feature_matrix_bow_val.toarray())
# df_features_text_val = df_val[["token_count","modal_exist","verb_count","prp_exist","vbp_exist","adv_exist"]]
df_features_text_val = df_val[["modal_exist", "verb_count", "prp_exist", "vbp_exist", "adv_exist"]]
df_features_val = pd.concat([df_features_bow_val, df_features_text_val], axis=1)

x_val = df_features_val.values
y_val = df_val['label'].values
print(x_val.shape)
print(y_val.shape)

# %% md

### Classifer training and predict: Logisitc Regression

# %%

classifier = LogisticRegression(random_state=0, max_iter=1000)
classifier.fit(x_train, y_train)

# %%

predictions = classifier.predict(x_val)

# %%

metrics.f1_score(y_val, predictions)

# %%

print(predictions)

# %%

print(y_val)

# %%


