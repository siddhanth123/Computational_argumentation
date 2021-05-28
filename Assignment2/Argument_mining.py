import sys
import numpy as np
import pandas as pd
import spacy
import nltk
import json
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

nlp = spacy.load("en_core_web_sm")

#Reading the training data and validation data
train_data_file = sys.argv[1]
val_data_file = sys.argv[2]

df_train = pd.read_json(train_data_file)
df_val = pd.read_json(val_data_file)

# Function: Pre-process the text(lower casing, lead/train space stripping,remove punctuations)
def PreprocessData(df):
    df['clean_text'] = df['text'].str.lower()
    df['clean_text'] = df['clean_text'].str.strip()
    df['clean_text'] = df['clean_text'].str.replace(r"http\S+",'')
    df['clean_text'] = df['clean_text'].str.replace('[^\w\s]','')
    return df

# Function: Linguistic Feature Extraction
def FeatureExtract(df):
    df['token_count'] = df['clean_text'].apply(lambda x: len(nlp(x)))

    md_exist_list = []  # modal verb
    verb_exist_list = []  # verb
    prp_exist_list = []  # personal pronouns
    vbp_exist_list = []  # verb non 3rd person
    adv_exist_list = []  # adverb
    conj_exist_list = []  # conjunction/preposition
    adj_exist_list = []  # adjective
    disc_exist_list = []  # discourse markers

    for text in df['clean_text']:
        doc = nlp(text)
        md_exist = 0
        verb_exist = 0
        prp_exist = 0
        vbp_exist = 0
        adv_exist = 0
        conj_exist = 0
        adj_exist = 0
        disc_exist = 0

        for token in doc:
            if token.tag_ == 'MD':
                md_exist = 1

            if token.pos_ == 'VERB':
                verb_exist = 1

            if token.tag_ == 'PRP':
                prp_exist = 1

            if token.tag_ == 'VBP':
                vbp_exist = 1

            if token.pos_ == 'ADV':
                adv_exist = 1

            if token.dep_ == 'prep':
                conj_exist = 1

            if token.pos_ == 'ADJ':
                adj_exist = 1

            if token.tag_ == 'IN' and token.pos_ != 'ADP':
                disc_exist = 1

        md_exist_list.append(md_exist)
        verb_exist_list.append(verb_exist)
        prp_exist_list.append(prp_exist)
        vbp_exist_list.append(vbp_exist)
        adv_exist_list.append(adv_exist)
        conj_exist_list.append(conj_exist)
        adj_exist_list.append(adj_exist)
        disc_exist_list.append(disc_exist)

    df['modal_exist'] = md_exist_list
    df['verb_exist'] = verb_exist_list
    df['prp_exist'] = prp_exist_list
    df['vbp_exist'] = vbp_exist_list
    df['adv_exist'] = adv_exist_list
    df['conj_exist'] = conj_exist_list
    df['adj_exist'] = adj_exist_list
    df['disc_exist'] = disc_exist_list
    return df


# Preprocess and feature extraction: Train and Val set
df_train = PreprocessData(df_train)
df_train = FeatureExtract(df_train)

df_val = PreprocessData(df_val)
df_val = FeatureExtract(df_val)


# Feature Extraction using Bag of Words(uni and bigrams): Train and Val set
vectorizer = CountVectorizer(ngram_range=(1,2))
feature_matrix_bow = vectorizer.fit_transform(df_train['clean_text'])

df_features_bow = pd.DataFrame(feature_matrix_bow.toarray())
df_features_text = df_train[["modal_exist","verb_exist","prp_exist","vbp_exist","adv_exist","conj_exist","adj_exist",
                             "disc_exist"]]
df_features = pd.concat([df_features_bow,df_features_text],axis = 1)

x_train = df_features.values
y_train = df_train['label'].values


# Transforming the Val/Test dataset with the vectorizer object

feature_matrix_bow_val = vectorizer.transform(df_val['clean_text'])

df_features_bow_val = pd.DataFrame(feature_matrix_bow_val.toarray())
df_features_text_val = df_val[["modal_exist","verb_exist","prp_exist","vbp_exist","adv_exist","conj_exist","adj_exist",
                              "disc_exist"]]
df_features_val = pd.concat([df_features_bow_val,df_features_text_val],axis = 1)

x_val = df_features_val.values
y_val = df_val['label'].values


#Actual training with the best hyperparameters combination¶
classifier = SVC(C=10.0, gamma=0.01)
# classifier = LogisticRegression(C = 20.0, penalty = 'l2',max_iter=1000)
classifier.fit(x_train,y_train)


predictions = classifier.predict(x_val)
print(metrics.f1_score(y_val,predictions))

# Extracting IDs -> Generating a dictionary -> Creating a JSON output file with predictions

val_data_id = df_val['id'].values
pred_val = dict(zip(val_data_id, predictions))

with open('pred_out.json', 'w') as fp:
    json.dump(pred_val,fp,default=str)


