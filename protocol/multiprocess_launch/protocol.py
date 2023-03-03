import crypten
from crypten import mpc
import crypten.communicator as comm
import torch
from math import sqrt
import os
import time


def run_protocol(file_user, file_party1, file_party2, user_id, party1_id, party2_id, threshold, len_keywords, len_clinical_note):
    start = time.time()
    
    # Load the tensor that acts as the result that the user sees
    results = crypten.load_from_party(file_user, src=user_id)

    # Load the clinical note from party 1's file 
    list_words_note = []
    for i in range(len_clinical_note):
        clinical_note_word = crypten.load_from_party(preloaded=torch.load(file_party1)[i], src=party1_id)
        list_words_note.append(clinical_note_word)
    
    list_keywords = []
    # Load the keywords from party 2's file
    for i in range(len_keywords):
        keyword = crypten.load_from_party(preloaded=torch.load(file_party2)[i], src=party2_id)
        list_keywords.append(keyword)
    
    count = 0
    for keyword in list_keywords:
        for word in list_words_note:
            print(count)
            # Compute the euclidean distance between the two tensors
            euclidean_distance = (sum((keyword - word).pow(2))).sqrt()
        
            # Determine if there is a match, set match to 1 if there is, 0 otherwise
            match = crypten.where(euclidean_distance < threshold, 1, 0)
            
            # Flip the first bit to a 1 if there is a match, leave it as it is if there is no match
            results[0] = crypten.where(match == 1, 1, results[0])
        
            count += 1
            # Print the result to the user so that they can see it; Parties 1 and 2 do not see the result
            # rank = comm.get().get_rank()
            # crypten.print("\neuclidean distance:", euclidean_distance.get_plain_text(dst=user_id), in_order=True)
            # crypten.print("Result of the computation for user id %s:" % str(rank), results.get_plain_text(dst=user_id), in_order=True)
    
    # Save the results on the User's device; can use it for a later computation(?)
    crypten.save_from_party(results.get_plain_text(), file_user, src=user_id)
    end = time.time()
    time_of_process = end - start
    print("Execution time:", round(time_of_process, 2), "seconds")
    return results.get_plain_text(dst=user_id)
