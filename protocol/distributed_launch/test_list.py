import torch
import pickle
from math import sqrt
# import crypten
# crypten.init()

# diagnosis = [[[torch.tensor(0), torch.tensor(1)], [torch.tensor(1), torch.tensor(0)]], [[torch.tensor(1)], [torch.tensor(0)]]]

# patients = [torch.tensor([0, 0]), torch.tensor([0, 0])]

# diagnosis = [[[torch.tensor(0), torch.tensor(1)]]]

# patients = [torch.tensor([0])]

# for i in range(len(patients)):
#     test = patients[i]
#     for item in range(patients[i].size(dim=0)):
#         print(patients[i].size(dim=0))
#         print(patients[i][item])
#         for j in range(len(diagnosis[i][item])):
#             test3 = diagnosis[i][item][j]
#             print("Diagnosis", test3)
#             if diagnosis[i][item][j] == 1:
#                 patients[i][item] = diagnosis[i][item][j]
#             else:
#                 patients[i][item] = patients[i][item]
#     print("")

# print("TEST")
# print(patients)        

# test = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party1_unstructured/data/oa_patients_tensors/4.pt")
# print(type(test))
# for i in test:
#     print(type(i))
    
# print("\n")

# test2 = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party1_unstructured/list_test_embedding.pt")
# print(type(test2))
# for i in test2:
#     print(type(i))

# with open("/home/jovyan/mpc_use_case/three_party_mpc/protocol/list.pkl", 'rb') as f:
#     list = pickle.load(f)
#     print(len(list))


note = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party1_unstructured/data/oa_patients_tensors/159.pt")

knee_keywords = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party2_structured/data/convert_data_output/knee_keywords.pt")
hip_keywords = torch.load("/home/jovyan/mpc_use_case/three_party_mpc/party2_structured/data/convert_data_output/hip_keywords.pt")

print(len(note))
count = 0
for i in note:
    for j in knee_keywords:
        euclidean_distance = (sum((j - i).pow(2))).sqrt()
        # print(euclidean_distance)
        if euclidean_distance < 0.05:
            print(count)
            print("yes")
    count += 1
      
count = 0      
for i in note:
    for j in hip_keywords:
        euclidean_distance = (sum((j - i).pow(2))).sqrt()
        # print(euclidean_distance)
        if euclidean_distance < 0.05:
            print(count)
            print("yes2")
    count += 1