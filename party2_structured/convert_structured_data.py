#!/usr/bin/env python
# coding: utf-8

# In[1]:


# from collections import Counter
import pickle
import torch
import numpy as np
# import codecs
import gensim
# import time
from gensim.models import KeyedVectors
import os
import pandas as pd
import csv
import fasttext
import sys
import torch
import crypten
crypten.init()


# In[2]:


vectors_filename = "/home/jovyan/embeddings/BioWordVec_PubMed_MIMICIII_d200.vec.bin"
model_filename = "/home/jovyan/embeddings/BioWordVec_PubMed_MIMICIII_d200.bin"

#! Remove this path once I implement PSI
deid_notes_path = "/home/jovyan/mpc_use_case/unstructured_data/deidentified_notes"

knee_keywords_output = "/home/jovyan/mpc_use_case/three_party_mpc/party2_structured/data/convert_data_output/knee_keywords.pt"
hip_keywords_output = "/home/jovyan/mpc_use_case/three_party_mpc/party2_structured/data/convert_data_output/hip_keywords.pt"


# In[3]:


bioword_vector = KeyedVectors.load_word2vec_format(vectors_filename, binary=True)
print("Vectors loaded")


# In[4]:


bioword_model = fasttext.load_model(model_filename)
print("Model loaded")


# In[5]:


#! -----------------------------------------------------------------------------------------
#TODO Untructured data - Remove after
#! -----------------------------------------------------------------------------------------
print("\nProcessing patients and their notes based on their diagnosis")

# Fetching demographic_no for all patients from the filename of notes
files = os.listdir(deid_notes_path)
all_demographic_nos_notes = set()
oa_patients = set()
for file in files:
    demographic_no = int(file.split("-")[1].split(".")[0])
    all_demographic_nos_notes.add(demographic_no)
print("Number of patients having patient notes:", len(all_demographic_nos_notes))


# In[6]:


all_demographic_nos_dxresearch = set()
oa_patients = set()

# Convert txt to csv
with open('/home/jovyan/mpc_use_case/structured_data/DxResearch.txt', 'r') as in_file:
    stripped = (line.strip() for line in in_file)
    lines = (line.split(",") for line in stripped if line)
    with open('/home/jovyan/mpc_use_case/prototype/oaTypes/DxResearch.csv', 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerows(lines)

# Fetching demographic_no of total patients and OA patients from the DxResearch table
df = pd.read_csv("/home/jovyan/mpc_use_case/prototype/oaTypes/DxResearch.csv")
# df.head()
for index, row in df.iterrows():
    no = row['demographic_no']
    all_demographic_nos_dxresearch.add(no)
    if row['dxresearch_code'] == 715:
        oa_patients.add(no)
print("\nNumber of patients listed with disease code:", len(all_demographic_nos_dxresearch))
print("Number of patients listed in disease code table as having OA:", len(oa_patients))


# In[7]:


#! -----------------------------------------------------------------------------------------
#TODO Where PSI comes in
#! -----------------------------------------------------------------------------------------
# Deducting the demographic_no of OA patients having notes
oa_patients_with_notes = oa_patients.intersection(all_demographic_nos_notes)
#print("Number of patients having OA and notes:", len(oa_patients_with_notes))
print("Patient IDs:", sorted(oa_patients_with_notes))


# In[8]:


# Lists that contain keywords that we can look for in the clinical notes
knee_oa_substrings = ['knee pain', 'pain knee', 'knee oa', 'oa knee', 'osteoarthrities knee', 'knee osteoarthritis', 
                      'kneepain', 'painknee', 'kneeoa', 'oaknee', 'osteoarthritiesknee', 'kneeosteoarthritis']
hip_oa_substrings = ['hip pain', 'pain hip', 'hip oa', 'oa hip', 'osteoarthrities hip', 'hip osteoarthritis',
                     'hippain', 'painhip', 'hipoa', 'oahip', 'osteoarthritieship', 'hiposteoarthritis']

# knee_oa_substrings = ['kneepain', 'painknee', 'kneeoa', 'oaknee', 'osteoarthritiesknee', 'kneeosteoarthritis']
# hip_oa_substrings = ['hip pain', 'pain hip', 'hip oa', 'oa hip', 'osteoarthrities hip', 'hip osteoarthritis',
#                      'hippain', 'painhip', 'hipoa', 'oahip', 'osteoarthritieship', 'hiposteoarthritis']


# In[9]:


# This adds every individual word into a new list, and splits up strings that contain more than one word so that their
# individual words can be added to the list. The new list contains unique individual words that are found in any of the original
# strings. Returns a dictionary of individual words and their associated embeddings
def create_embeddings(substrings):  
    vectors = {}
    single_words =[]
    for i in substrings:
        if len(i.split()) == 1:
            single_words.append(i)
        else:
            two_words = i.split()
            for word in two_words:
                if word not in single_words:
                    single_words.append(word)
    for word in single_words:
        # print(word)
        try:
            word_array = bioword_vector[word]
        # If the word does not have an embedding already, we use the model to create one for it
        except:
            word_array = bioword_model.get_word_vector(word)
        vectors[word] = word_array
    return vectors

knee_oa_embeddings = create_embeddings(knee_oa_substrings)
hip_oa_embeddings = create_embeddings(hip_oa_substrings)

print(knee_oa_embeddings.keys())
print(hip_oa_embeddings.keys())
    
# print(np.sqrt(np.sum(np.square(knee_oa_embeddings['oa'] - hip_oa_embeddings['oa']))))


# In[11]:


# Convert the word embeddings into CrypTen tensors, save the encrypted tensors to a file for future use
def create_tensors(list_embeddings):
    tensors = []
    for key in list_embeddings:
        # print(list_embeddings[key])
        tensor = torch.Tensor(list_embeddings[key])
        # encrypted_tensor = crypten.cryptensor(tensor)
        # tensors.append(encrypted_tensor)
        tensors.append(tensor)
    return tensors

knee_oa_tensors = create_tensors(knee_oa_embeddings)
hip_oa_tensors = create_tensors(hip_oa_embeddings)


# In[12]:


# This function creates pickle files that can be retrieved later in the MPC protocol
def create_file(filename, tensors):
    with open(filename, 'wb') as f:
        torch.save(tensors, f)
    
create_file(knee_keywords_output, knee_oa_tensors)
create_file(hip_keywords_output, hip_oa_tensors)

