import crypten
from crypten import mpc
import crypten.communicator as comm
import torch
import torch.distributed as dist
from torch.distributed import barrier   # Creates a "barrier", where parties have to wait until everyone reaches this step.
from math import sqrt
import os
import time
import pickle

# Ranks of each party
USER = 0
PARTY1 = 1
PARTY2 = 2

DEVICE = "cpu"
# DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# print("GPU Available:", torch.cuda.is_available())

def run_protocol(num_diagnoses, patients, output_folder, party1_input, list_notes, party2_input, lists_keywords, threshold):
    start = time.time()
    rank = get_rank()
    
    # Share the list of patients to the other parties, assuming they all know the patient IDs of the patients in question
    patients_list = distribute_patients(patients, USER)     #! Comment this out if we don't know the patient IDs yet and we can't share them
    # length_list_patients = get_length_results(patients, USER)     #! Use this if length of patients is unknown
    length_list_patients = len(patients_list)
    patient_results = create_results(num_diagnoses, patients, length_list_patients, USER)
    
    # Load the clinical note from party 1's file
    list_notes_embeddings = get_embeddings(party1_input, patients_list, list_notes, PARTY1)
    # list_notes_embeddings = get_embeddings(party1_input, list_notes, PARTY1)
    length_notes = get_length(list_notes_embeddings, PARTY1)
    encrypted_notes = load_party1_data(list_notes_embeddings, length_notes, PARTY1)
    
    # Load the keywords from party 2's file 
    list_keyword_embeddings = get_embeddings(party2_input, patients_list, lists_keywords, PARTY2)
    length_keywords = get_length(list_keyword_embeddings, PARTY2)
    encrypted_keywords = load_party2_data(list_keyword_embeddings, length_keywords, PARTY2)
    
    # Main MPC protocol
    list_diagnoses = []
    # Take each patient in the list of results
    for patient in range(len(patient_results)):
        patient_diagnoses = []
        # The index corresponds to the patient's note
        for diagnosis in range(len(patient_results[patient])):
            patient_diagnoses.append(patient_results[patient][diagnosis])
        list_diagnoses.append(patient_diagnoses)
    
    # Creates a list where each element is a list of tensors that represents each word in the patient's note
    list_notes = []
    for index in range(len(list_diagnoses)):
        notes_patient = []
        notes = encrypted_notes[index]
        for word_in_note in range(len(notes)):
            notes_patient.append(notes[word_in_note])
        list_notes.append(notes_patient)

    # Creates a list where each element is a list of tensors that represents each keyword for each possible diagnosis
    list_keywords = []
    for index in range(num_diagnoses):
        keywords_diseases = []
        keywords = encrypted_keywords[index]
        for keyword in range(len(keywords)):
            keywords_diseases.append(keywords[keyword])
        list_keywords.append(keywords_diseases)
    
    
    for patient in range(len(patients_list)):
        # break_flag = False
        print("Patient ID:", patients_list[patient])
        note = list_notes[patient]
        for diagnosis in range(len(list_keywords)):
            count = 0
            for keyword in list_keywords[diagnosis]:
                start_time_keyword = time.time()
                # If the keyword is not a list (keyword is a single encrypted tensor)
                if not isinstance(keyword, list):
                    for word in note:
                        euclidean_distance = (sum((keyword - word).pow(2))).sqrt()
                        match = crypten.where(euclidean_distance < threshold, 1, 0)
                        patient_results[patient][diagnosis] = crypten.where(match == 1, 1, patient_results[patient][diagnosis])
                # Keyword contains two substrings
                else:
                    match_indexes = []
                    for substring in range(len(keyword)):
                        index_match = 0
                        indexes = []
                        for word in range(len(note)):
                            euclidean_distance = (sum((keyword[substring] - note[word]).pow(2))).sqrt()
                            # Determine if there is a match, set match to the index of the word in the note, otherwise set it to -10
                            match = crypten.where(euclidean_distance < threshold, index_match, -10)
                            indexes.append(match)
                            index_match += 1
                        match_indexes.append(indexes)
                    # The first list represents the first substring in the keyword
                    first_word = match_indexes[0]
                    # Second substring in the keyword
                    second_word = match_indexes[1]
                    index = 0
                    while index < (len(first_word) - 1):
                        # If the difference in indexes between the first and secnod substrings is 1, this means they appeared back-to-back in the note, so patient has the diagnosis
                        patient_results[patient][diagnosis] = crypten.where(abs(first_word[index] - second_word[index+1]) == 1, 1, patient_results[patient][diagnosis])
                        index += 1
                count += 1
                print("Count keyword:", count)
                end_time_keyword = time.time()
                time_of_process_keyword = end_time_keyword - start_time_keyword
                print("Time for keyword:", round(time_of_process_keyword, 2), "seconds\n")
                
    #!##############################################################################################################
            #         stop = break_computation(patient_results[patient][diagnosis].get_plain_text(dst=USER), USER)
            #         print(stop)
            #         if stop == 1:
            #             break_flag = True
            #             break
            #     if break_flag:
            #         break
            # if break_flag:
            #     break
    #!##############################################################################################################
                    
    # # # Save the results on the User's device; can use it for a later computation(?)
    # # # crypten.save_from_party(results.get_plain_text(), user_input, src=USER)
    end = time.time()
    time_of_process = end - start
    print("Execution time:", round(time_of_process, 2), "seconds")
    final_results = get_plaintext_results(patient_results, USER)
    # write_results(final_results, patients, output_folder, USER)
    return final_results


# Returns the rank of each party (0, 1, or 2)
def get_rank():
    return comm.get().get_rank()


# This function will break the for loop that checks if there is a match between the keywords and the words from the clinical
# notes.
def break_computation(result, rank_party):
    rank = get_rank()
    stop = torch.tensor(0)
    if rank == rank_party:
        if result == 1:
            stop = torch.tensor(1)
    barrier()
    dist.broadcast(stop, src=rank_party)   
    return stop


# This function distributes the patient list to the other parties. This is assuming they are allowed to see the patient IDs.
def distribute_patients(patients, rank_party):
    rank = get_rank()
    if rank == rank_party:
        length_tensor = torch.tensor([len(patients)])
    else:
        length_tensor = torch.tensor([0])
    barrier()
    dist.broadcast(length_tensor, src=rank_party)
    
    if rank == rank_party:
        # print(patients)
        patient_list = patients
    else:
        patient_list = [None] * length_tensor
    barrier()
    dist.broadcast_object_list(patient_list, src=rank_party)
    return patient_list

# This function loads the results tensor from the user, where we will store the results of the computation.
# While the user loads the true tensor, the other two parties generate a dummy tensor. The user sends shares of the
# encrypted tensor to the others so they all have a share of the results
def create_results(num_diagnoses, patients, length_list_patients, rank_party):
    results = []
    rank = get_rank()     
    for i in range(length_list_patients):  
        # Creates a tensor that has the number of possible diagnoses
        results_patient = torch.empty(num_diagnoses, device=DEVICE)
        results.append(crypten.cryptensor(results_patient, src=rank_party))
    return results


# This function gets the data from each input file of the party. The result is a list of lists of embeddings for the input party;
# the other two parties will have a list of dummy lists of embeddings
def get_embeddings(input_of_party, patients, list_of_elements, rank_party):
    list_embeddings_files = []
    rank = get_rank()
    if rank == rank_party:
        if os.path.exists(input_of_party):
            # Lists all files in the input directory
            list_of_files = os.listdir(input_of_party)
            if rank_party == PARTY1:
                for inputs in range(len(list_of_elements)):
                    patient_id = int(os.path.splitext(list_of_elements[inputs])[0])
                    for file_name in list_of_files:
                        # If the file is in the list of files and the patient ID corresponds to the correct note
                        if list_of_elements[inputs] == file_name and patient_id == patients[inputs]:
                            # Add the files to the list of embedding files, where we will load data from the file later on
                            list_embeddings_files.append(os.path.join(input_of_party, file_name))
            elif rank_party == PARTY2:
                for inputs in list_of_elements:
                    for file_name in list_of_files:
                        # If the file is in the list of files
                        if inputs == file_name:
                            # Add the files to the list of embedding files, where we will load data from the file later on
                            list_embeddings_files.append(os.path.join(input_of_party, file_name))
    barrier()
    return list_embeddings_files


# Gets the length of the input. For the user, gets the number of patients. For parties 1 and 2, gets the number of embeddings in
# the clinical notes and the list of keywords respectively.
def get_length_results(input_of_party, rank_party):
    length_tensor = torch.tensor([0])
    rank = get_rank()
    if rank == rank_party:
        # Store the number of patients in a tensor
        length_tensor = torch.tensor([len(input_of_party)])
    barrier()
    # The party with the actual input broadcasts the length of the input to the other parties
    dist.broadcast(length_tensor, src=rank_party)
    return length_tensor


# This decrypts the results for the user only; parties 1 and 2 will not see the decrypted results
def get_plaintext_results(results, rank_party):
    final_results = []
    for i in results:
        final_results.append(i.get_plain_text(dst=rank_party))
    return final_results


# Gets the length of the input. For the user, gets the number of patients. For parties 1 and 2, gets the number of embeddings in
# the clinical notes and the list of keywords respectively.
def get_length(input_of_party, rank_party):
    list_of_lengths = []
    length_tensor = torch.tensor([0])
    rank = get_rank()
    
    # The correct party will store the true length of its input in a tensor, then broadcast it to the other parties
    if rank == rank_party:
        length_tensor = torch.tensor([len(input_of_party)])
    barrier()
    dist.broadcast(length_tensor, src=rank_party)
    
    # Now that they have the correct length of the input, the input party will generate the length of its lists of embeddings and
    # store them in another list. The other two parties will generate dummy tensors and store them in a list as well.
    for i in range(length_tensor.item()):
        if rank == rank_party:
            # Load the list of embeddings and store the length in a tensor
            length_embedding = torch.load(input_of_party[i])
            list_of_lengths.append(len(length_embedding))
        else:
            # Other parties create a dummy tensor as the length
            length_embedding = torch.tensor([0])
            list_of_lengths.append(len(length_embedding))
    barrier()
    # All parties convert their list into a tensor, and the correct party will broadcast its tensor to the other parties.
    # After this step, everyone will have the same tensor, that corresponds to the the lengths of the lists of input.
    # For party 1, this will be the length of each clinical note. For party 2, this will be the length of each list of keywords.
    tensor_lengths = torch.as_tensor(list_of_lengths)
    dist.broadcast(tensor_lengths, src=rank_party)
    return tensor_lengths


# This loads the input of a party. It encrypts each tensor and stores it into a list.
# Each input file will have a list of encrypted tensors for the computation
def load_party1_data(input_of_party, tensor_of_lengths, rank_party):
    list_encrypted_embeddings = []
    rank = get_rank()
    for item in range(len(tensor_of_lengths.tolist())):
        list_tensors = []
        if rank == rank_party:
            # Load the list of embeddings
            list_embeddings = torch.load(input_of_party[item])
        else:
            list_embeddings = []
        # Convert the length of the list of embeddings into a tensor, where the correct party will broadcast its length
        length_list_embeddings = torch.tensor([len(list_embeddings)])
        barrier()
        dist.broadcast(length_list_embeddings, src=rank_party)
        for i in range(length_list_embeddings.item()):
            if rank == rank_party:
                # Extract a tensor
                input_embedding = list_embeddings[i]
            else:
                # Other parties will create a dummy tensor
                input_embedding = torch.empty(1)
            barrier()
            # Encrypt the tensor and store it in the list of tensors
            list_tensors.append(crypten.cryptensor(input_embedding, src=rank_party, device=DEVICE, broadcast_size=True))
        # The encrypted tensors from the previous step are appended to this list, so that each "input file" has its own
        # list of embeddings
        list_encrypted_embeddings.append(list_tensors)
    return list_encrypted_embeddings


# This function loads the keywords from party 2. Since keywords may contain multiple words (e.g., "knee pain"), we have to account for that as well.
# The function returns a list where each sub-list contains the secret shares of the keywords. If the keyword is made up of multiple words, the element
# in the list_encrypted_keywords variable will be a list that contains the secret shares of each word in the keyword.
def load_party2_data(input_of_party, tensor_of_lengths, rank_party):
    list_encrypted_embeddings = []
    rank = get_rank()
    for item in range(len(tensor_of_lengths.tolist())):
        list_tensors = []
        if rank == rank_party:
            # Load the list of embeddings
            list_embeddings = torch.load(input_of_party[item])
        else:
            list_embeddings = []
        # Convert the length of the list of embeddings into a tensor, where the correct party will broadcast its length
        length_list_embeddings = torch.tensor([len(list_embeddings)])
        barrier()
        # The length of the list of keywords is broadcast to every party through a tensor
        dist.broadcast(length_list_embeddings, src=rank_party)
        
        # This block counts the number of embeddings for each keyword (whether the keyword consists of one word or multiple words)
        list_number_embeddings = []
        for i in range(length_list_embeddings.item()):
            if rank == rank_party:
                # Extract a tensor
                input_embedding = list_embeddings[i]
                # If the keyword is a list of embeddings (more than one word)
                if isinstance(input_embedding, list):
                    list_number_embeddings.append(len(input_embedding))
                else:
                    list_number_embeddings.append(1)
            else:
                # Other parties will create a dummy tensor
                input_embedding = torch.empty(1)
                list_number_embeddings.append(len(input_embedding))
        barrier()
        tensor_list_num_embeddings = torch.tensor(list_number_embeddings)
        # This tensor, that represents how many words are in each keyword, is broadcast to all parties
        dist.broadcast(tensor_list_num_embeddings, src=rank_party)
    
        for index in range(len(tensor_list_num_embeddings.tolist())):
            index_value = tensor_list_num_embeddings[index]
            # If the keyword only has one element
            if index_value.item() == 1:
                if rank == rank_party:
                    # Extract a tensor
                    input_embedding = list_embeddings[index]
                else:
                    # Other parties will create a dummy tensor
                    input_embedding = torch.empty(1)
                barrier()
                # Encrypt the tensor and store it in the list of tensors
                list_tensors.append(crypten.cryptensor(input_embedding, src=rank_party, device=DEVICE, broadcast_size=True))
            else:
                # If the tensor has 2 or more elements
                input_embedding_list = []
                for index_embedding in range(index_value.item()):
                    if rank == rank_party:
                        # Extract a tensor
                        input_embedding = list_embeddings[index][index_embedding]
                        # print(input_embedding)
                    else:
                        # Other parties will create a dummy tensor
                        input_embedding = torch.empty(1)
                    barrier()
                    # Encrypt each tensor that corresponds to a word in the keyword, and store it in a list
                    input_embedding_list.append(crypten.cryptensor(input_embedding, src=rank_party, device=DEVICE, broadcast_size=True))
                barrier()
                # Append this list to the rest of the tensors
                list_tensors.append(input_embedding_list)
        list_encrypted_embeddings.append(list_tensors)
    return list_encrypted_embeddings

# Writes the results of the computation to a file on the user's device. Other parties generate a temporary file and write
# dummy data to it, but they dop not get the result
# def write_results(results, patients, output_"folder, rank_party):
#     rank = get_rank()
#     try:
#         # Extract all results from the list of results, and write them for each patient in the input patient list of the user
#         for i in range(len(results)):
#             if rank == rank_party:
#                 patient_id = patients[i]
#                 result = results[i].tolist()
#                 for number in range(len(result)):
#                     if result[number] == 1.0:
#                         result[number] = 1
#                     else:
#                         result[number] = 0
#                 results_to_write = "Patient " + str(patient_id) + " diagnosis: " + str(result) + "\n"
#             # Parties 1 and 2 will simply write "None" for each iteration of the for loop
#             else:
#                 results_to_write = b"None"
#             barrier()
#             output_file.write(results_to_write)
#     finally:
#         barrier()
#         print("Done")


# Writes the results of the computation to a file on the user's device. Other parties generate a temporary file and write
# dummy data to it, but they dop not get the result
# def write_results(results, patients, output_folder, rank_party):
#     rank = get_rank()
#     if rank == rank_party:
#         # User creates a new file in the folder to write the results in
#         if os.path.exists(output_folder):
#             filename = "results - " + time.strftime('%Y-%m-%d %H:%M:%S') + ".txt"
#             path = os.path.join(output_folder, filename)
#             output_file = open(path, 'w')
#     else:
#         # Parties 1 and 2 generate a temporary file
#         output_file = tempfile.NamedTemporaryFile()
#     try:
#         # Extract all results from the list of results, and write them for each patient in the input patient list of the user
#         for i in range(len(results)):
#             if rank == rank_party:
#                 patient_id = patients[i]
#                 result = results[i].tolist()
#                 for number in range(len(result)):
#                     if result[number] == 1.0:
#                         result[number] = 1
#                     else:
#                         result[number] = 0
#                 results_to_write = "Patient " + str(patient_id) + " diagnosis: " + str(result) + "\n"
#             # Parties 1 and 2 will simply write "None" for each iteration of the for loop
#             else:
#                 results_to_write = b"None"
#             barrier()
#             output_file.write(results_to_write)
#     finally:
#         barrier()
#         output_file.close()