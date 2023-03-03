import argparse
import logging
import os
import time
import torch

from multiprocess_launcher import MultiProcessLauncher
from protocol import run_protocol

# Function that checks whether the string corresponds to a valid path or not.
# This is used in the arguments passed to the command that executes the protocol
def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)



# Creates the arguments for the command that runs the protocol using multiple processes
parser = argparse.ArgumentParser(description="3PC protocol for OA Affected Site Classifcation")
parser.add_argument(
    "--world_size", type=int, default=3, help="The number of parties to launch. Each party acts as its own process",
)
#! MIGHT HAVE TO CHANGE THE DEFAULT VALUES FOR THE FILE NAMES!!!!!!!!!!!
parser.add_argument(
    "--file_user", default="", type=str, help="File where we store the results of the computation",
)
parser.add_argument(
    "--file_party1", default="", type=str, help="File that contains the clinical note"
)
parser.add_argument(
    "--file_party2", default="", type=str, help="File that contains the keywords"
)

parser.add_argument("--user_id", default=0, type=int, help="User's ID in the computation")
parser.add_argument("--party1_id", default=1, help="Party1's ID in the computation")
parser.add_argument("--party2_id", default=2, help="Party2's ID in the computation")

parser.add_argument(
    "--threshold", default=0.05, type=float, help="Threshold for the string comparison",
)
parser.add_argument(
    "--multiprocess", default=True, action="store_true", help="Run example in multiprocess mode",
)
parser.add_argument("--len_keywords", default=0, type=int)
parser.add_argument("--len_clinical_note", default=0, type=int)


def _run_experiment(args):
    
    level = logging.INFO
    if "RANK" in os.environ and os.environ["RANK"] != "0":
        level = logging.CRITICAL
    logging.getLogger().setLevel(level)
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s",
    )
    
    args.file_user = "/home/jovyan/mpc_use_case/three_party_mpc/user/data/results_of_protocol.pt"
    
    args.file_party1 = "/home/jovyan/mpc_use_case/three_party_mpc/party1_unstructured/data/oa_patients_tensors/4.pt"
    
    args.file_party2 = "/home/jovyan/mpc_use_case/three_party_mpc/party2_structured/data/convert_data_output/knee_keywords.pt"
    
    args.len_keywords = len(torch.load(args.file_party2))
    
    args.len_clinical_note = len(torch.load(args.file_party1))
    
    test = run_protocol(args.file_user, args.file_party1, args.file_party2, args.user_id,
                        args.party1_id, args.party2_id, args.threshold, args.len_keywords, args.len_clinical_note)
    if test != None:
        test = test.tolist()
    print("The result of the computation is:", test)

def main(run_experiment):
    #! DELETE THIS - THIS IS JUST TO RESET THE RESULTS AFTER EACH EXECUTION
    reset = torch.Tensor([0, 0, 0, 0])
    torch.save(reset, "/home/jovyan/mpc_use_case/three_party_mpc/user/data/results_of_protocol.pt")
    print(reset)
    #!---------------------------------------------------------------------
    
    args = parser.parse_args()
    if args.multiprocess:
        launcher = MultiProcessLauncher(args.world_size, run_experiment, args)
        launcher.start()
        launcher.join()
        launcher.terminate()
    else:
        run_experiment(args)


if __name__ == "__main__":
    main(_run_experiment)