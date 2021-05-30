import sys
import numpy as np
import pandas as pd
import spacy
import json
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

# Loading the small english language model
nlp = spacy.load("en_core_web_sm")

#Reading the training data and validation data and storing them in dataframes
train_data_file = sys.argv[1]
val_data_file = sys.argv[2]

df_train = pd.read_json(train_data_file)
df_val = pd.read_json(val_data_file)

# Function: Pre-process the text
def PreprocessData(df):
    df['clean_text'] = df['text'].str.lower() #lowercase
    df['clean_text'] = df['clean_text'].str.strip() #striping lead trail spaces
    df['clean_text'] = df['clean_text'].str.replace(r"http\S+",'') #remove URLs
    df['clean_text'] = df['clean_text'].str.replace('[^\w\s]','') #remove punctuations and other special characters
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

    for text in df['clean_text']: #iterating through each text data point
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
            if token.tag_ == 'MD': #modal verb as a boolean feature
                md_exist = 1

            if token.pos_ == 'VERB': #action verbs as a boolean feature
                verb_exist = 1

            if token.tag_ == 'PRP': #personal pronouns as a boolean feature
                prp_exist = 1

            if token.tag_ == 'VBP': #third person present tense verbs as a boolean feature
                vbp_exist = 1

            if token.pos_ == 'ADV': #adverbs as a boolean feature
                adv_exist = 1

            if token.dep_ == 'prep': #prepositions as a boolean feature
                conj_exist = 1

            if token.pos_ == 'ADJ': #adjectives as a boolean feature
                adj_exist = 1

            if token.tag_ == 'IN' and token.pos_ != 'ADP': #discourse markers as a boolean feature
                disc_exist = 1

        # creating a list for each feature on each data point
        md_exist_list.append(md_exist)
        verb_exist_list.append(verb_exist)
        prp_exist_list.append(prp_exist)
        vbp_exist_list.append(vbp_exist)
        adv_exist_list.append(adv_exist)
        conj_exist_list.append(conj_exist)
        adj_exist_list.append(adj_exist)
        disc_exist_list.append(disc_exist)

    # creating features from the list
    df['modal_exist'] = md_exist_list
    df['verb_exist'] = verb_exist_list
    df['prp_exist'] = prp_exist_list
    df['vbp_exist'] = vbp_exist_list
    df['adv_exist'] = adv_exist_list
    df['conj_exist'] = conj_exist_list
    df['adj_exist'] = adj_exist_list
    df['disc_exist'] = disc_exist_list
    return df

print("Preprocessing and Feature extraction...\n")
# Preprocess and feature extraction: Train set
df_train = PreprocessData(df_train)
df_train = FeatureExtract(df_train)

# Preprocess and feature extraction: Val set
df_val = PreprocessData(df_val)
df_val = FeatureExtract(df_val)



# Feature Extraction using Bag of Words(uni and bigrams): TRAIN SET
vectorizer = CountVectorizer(ngram_range=(1,2))
feature_matrix_bow = vectorizer.fit_transform(df_train['clean_text'])

# creating a dataframe of n-gram features from sparse matrix
df_features_bow = pd.DataFrame(feature_matrix_bow.toarray())

# creating a dataframe of only the extracted linguistic features
df_features_text = df_train[["modal_exist","verb_exist","prp_exist","vbp_exist","adv_exist","conj_exist","adj_exist",
                             "disc_exist"]]

# concatenating n-gram features and extracted linguistic features to form final feature dataframe
df_features = pd.concat([df_features_bow,df_features_text],axis = 1)

# creating a feature matrix from dataframe(train set)
x_train = df_features.values

# creating ground truth array(train set)
y_train = df_train['label'].values

# Feature Extraction: VALIDATION SET

feature_matrix_bow_val = vectorizer.transform(df_val['clean_text'])

df_features_bow_val = pd.DataFrame(feature_matrix_bow_val.toarray())
df_features_text_val = df_val[["modal_exist","verb_exist","prp_exist","vbp_exist","adv_exist","conj_exist","adj_exist",
                              "disc_exist"]]
df_features_val = pd.concat([df_features_bow_val,df_features_text_val],axis = 1)

# creating feature matrix (val set)
x_val = df_features_val.values

# creating ground truth array(val set)
y_val = df_val['label'].values

print("Feature extraction complete\n")


#Actual training with the best hyperparameters combination¶
print("Starting training...\n")
classifier = SVC(C=10.0, gamma=0.01)
# classifier = LogisticRegression(C = 20.0, penalty = 'l2',max_iter=1000)
classifier.fit(x_train,y_train)
print("Training complete\n")


predictions = classifier.predict(x_val)
# print(metrics.f1_score(y_val,predictions))

# Extracting IDs -> Generating a dictionary -> Creating a JSON output file with predictions

val_data_id = df_val['id'].values
pred_val = dict(zip(val_data_id, predictions))

print("Generating predictions file for test/val data\n")

with open('prediction_out.json', 'w') as fp:
    json.dump(pred_val,fp,default=str)

print("File generation complete\n")