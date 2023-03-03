import torch
from math import sqrt

test = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party1_unstructured/list_test_embedding.pt")   # hip

test2 = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party1_unstructured/list2_test_embedding.pt") # osteoarthritis, knee

test3 = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party2_structured/test_folder/knee.pt")   # knee
print(test3)

test4 = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party2_structured/test_folder/hip.pt")    # hip
# print(test4)

for i in test:
    for j in test3:
        euclidean_distance = (sum((i - j).pow(2))).sqrt()
        print("test 1:", euclidean_distance)
        
for i in test:
    for j in test4:
        euclidean_distance = (sum((i - j).pow(2))).sqrt()
        print("test 2:", euclidean_distance)

for i in test2:
    for j in test3:
        euclidean_distance = (sum((i - j).pow(2))).sqrt()
        print("test 3:", euclidean_distance)
        
for i in test2:
    for j in test4:
        euclidean_distance = (sum((i - j).pow(2))).sqrt()
        print("test 4:", euclidean_distance)