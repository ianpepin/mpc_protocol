#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pickle
import torch
import gensim
from gensim.models import KeyedVectors
import os
import pandas as pd
import csv
import fasttext
import sys
import torch
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import string
import re
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import unidecode
from natsort import natsorted
import time


# In[5]:


# Paths of different files used in this script
vectors_filename = "/home/jovyan/embeddings/BioWordVec_PubMed_MIMICIII_d200.vec.bin"
model_filename = "/home/jovyan/embeddings/BioWordVec_PubMed_MIMICIII_d200.bin"

deid_notes_path = "/home/jovyan/mpc_use_case/crypten_unstructured_data/data/deidentified_notes"
oa_patients_combined_notes = "/home/jovyan/mpc_use_case/crypten_unstructured_data/data/oa_patients_notes/oa_patients"
other_patients_combined_notes = "/home/jovyan/mpc_use_case/crypten_unstructured_data/data/other_patients_notes"

oa_patients_tensors = "/home/jovyan/mpc_use_case/crypten_unstructured_data/data/oa_patients_tensors"


# In[6]:


# Loads the word embeddings from the vector binary file
bioword_vector = KeyedVectors.load_word2vec_format(vectors_filename, binary=True)
print("Vectors loaded")


# In[7]:


# Loads the BioWordVec model, which we can use to generate embeddings for OOV words
bioword_model = fasttext.load_model(model_filename)
print("Model loaded")


# In[8]:


print("\nProcessing patients and their notes based on their diagnosis")

# Fetching demographic_no for all patients from the filename of notes
files = natsorted(os.listdir(deid_notes_path))
all_demographic_nos_notes = set()
# This is a list that contains the note IDs for each patient
for file in files:
    # print(file)
    demographic_no = int(file.split("-")[1].split(".")[0])
    all_demographic_nos_notes.add(demographic_no)
    
list_of_files = [[] for _ in range(len(all_demographic_nos_notes))]
for file in files:
    demographic_no = int(file.split("-")[1].split(".")[0])
    note_id = int(file.split("-")[0].split(".")[0])
    # Add the note ID to the list of notes for the patient
    list_of_files[demographic_no-1].append(note_id)
print("Number of patients having patient notes:", len(all_demographic_nos_notes))

# print(list_of_files


# In[9]:


#! -----------------------------------------------------------------------------------------
#TODO Structured data
#! -----------------------------------------------------------------------------------------
all_demographic_nos_dxresearch = set()
oa_patients = set()
# Convert txt to csv
with open('/home/jovyan/mpc_use_case/structured_data/DxResearch.txt', 'r') as in_file:
    stripped = (line.strip() for line in in_file)
    lines = (line.split(",") for line in stripped if line)
    with open('/home/jovyan/mpc_use_case/structured_data/DxResearch.csv', 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerows(lines)

#! -----------------------------------------------------------------------------------------
#TODO Structured Data
#! -----------------------------------------------------------------------------------------
# Fetching demographic_no of total patients and OA patients from the DxResearch table
df = pd.read_csv("/home/jovyan/mpc_use_case/structured_data/DxResearch.csv")
# df.head()
for index, row in df.iterrows():
    no = row['demographic_no']
    all_demographic_nos_dxresearch.add(no)
    if row['dxresearch_code'] == 715:
        oa_patients.add(no)
print("\nNumber of patients listed with disease code:", len(all_demographic_nos_dxresearch))
print("Number of patients listed in disease code table as having OA:", len(oa_patients))

#! -----------------------------------------------------------------------------------------
#TODO Where PSI comes in
#! -----------------------------------------------------------------------------------------
# Deducting the demographic_no of OA patients having notes
oa_patients_with_notes = oa_patients.intersection(all_demographic_nos_notes)
#print("Number of patients having OA and notes:", len(oa_patients_with_notes))
print("Patient IDs:", sorted(oa_patients_with_notes))


# In[17]:


# This function combines all the notes from all patients and moves the combined notes to another folder.
# The notes are separated by whether the patients have OA or not
def combine_files(files, oa_patients_with_notes, notes_folder, new_folder_name, flag):
    for file in files:
        demographic_no = file.split("-")[1].split(".")[0]
        # for id_number in all_demographic_nos_notes:
        #     if id_number == int(demographic_no):
        if flag == 0:
            if int(demographic_no) not in oa_patients_with_notes:
                with open(os.path.join(notes_folder, file), 'r') as fr:
                    text = fr.read()
                    fr.close()
                if not os.path.exists(new_folder_name):
                    os.makedirs(new_folder_name)
                with open(new_folder_name + '/' + demographic_no + ".txt", "a") as fw:
                    fw.write(text)
                    fw.write("\n")
                    fw.close()
        else:
            if int(demographic_no) in oa_patients_with_notes:
                with open(os.path.join(notes_folder, file), 'r') as fr:
                    text = fr.read()
                    fr.close()
                if not os.path.exists(new_folder_name):
                    os.makedirs(new_folder_name)
                with open(new_folder_name + '/' + demographic_no + ".txt", "a") as fw:
                    fw.write(text)
                    fw.write("\n")
                    fw.close()
                        
# combine_files(files, oa_patients_with_notes, deid_notes_path, other_patients_combined_notes, flag=0)
# combine_files(files, oa_patients_with_notes, deid_notes_path, oa_patients_combined_notes, flag=1)


# In[11]:


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


# In[12]:


# This function is used to preprocess a clinical note. It removes any undesired symbols and stopwords, so that only words remain in the note
def preprocess(txt):
    BAD_SYMBOLS_RE = re.compile('[0-9a-z #+_]')
    remove_digits = str.maketrans('', '', string.digits)
    p = re.compile("[" + re.escape(string.punctuation) + "]")
    txt = txt.lower()
    #txt = BAD_SYMBOLS_RE.sub('', txt)
    txt = txt.translate(remove_digits)
    txt = p.sub("", txt)
    txt = unidecode.unidecode(txt)
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(txt)
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words and len(w) > 1:
            # stem_w = ps.stem(w)
            filtered_sentence.append(w)
    # return " ".join(filtered_sentence)
    return filtered_sentence


# In[13]:


# Convert the word embeddings into tensors
def create_tensors(embeddings):
    tensors = []
    for key in embeddings:
        tensor = torch.Tensor(embeddings[key])
        tensors.append(tensor)
    return tensors


# In[15]:


# This function creates pickle files that can be retrieved later in the MPC protocol
def create_file(filename, tensors):
    with open(filename, 'wb') as f:
        torch.save(tensors, f)


# In[16]:


# For each patient, taking all the combined notes, extracting the words, then creating embeddings for each word
# After the embeddings are created, we can create CrypTen tensors and stored the tensors into a file for later use
oa_files = natsorted(os.listdir(oa_patients_combined_notes))
all_tensors = []
notes_embeddings = []

# For each patient in the folder
for notes_file in oa_files:
    oa_demographic_no = int(notes_file.split(".")[0])
    # print(oa_demographic_no)
    with open(os.path.join(oa_patients_combined_notes, notes_file), 'r') as fr:
        note_data = fr.read()
        fr.close()
    # Preprocess the note
    preprocessed_note = preprocess(note_data)
    # Create an embedding for each word
    embeddings = create_embeddings(preprocessed_note)
    # notes_embeddings.append(embeddings)
    note_tensors = create_tensors(embeddings)
    # all_tensors.append(note_tensors)
    # Save the tensors to a file    ** Might have to do this in the protocol itself
    create_file(os.path.join(oa_patients_tensors, str(oa_demographic_no) + ".pt"), note_tensors)
    # create_file(os.path.join(oa_patients_tensors, str(oa_demographic_no) + ".pkl"), note_tensors)
    print(oa_demographic_no)
    print(len(preprocessed_note))
    print(len(note_tensors))
    print("\n")

