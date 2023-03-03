import argparse
import logging
import os
import time
import torch

from distributed_launcher_new import DistributedLauncher

parser = argparse.ArgumentParser(description="OA Affected Site Classification Using CrypTen")
parser.add_argument(
    "--world_size",
    type=int,
    default=3,
    help="The number of parties to launch the protocol. Each party has its own process."
)
parser.add_argument(
    "--rank",
    type=int,
    help="The rank of the current party in the computation. User=0, party1=1, party2=2."
)
parser.add_argument(
    "--address",
    type=str,
    help="Master IP address of the computation",
)
parser.add_argument(
    "--port",
    type=int,
    help="Master port",
)
parser.add_argument(
    "--backend",
    type=str,
    default="gloo",
    help="Backend for torhc.distributed, 'NCCL' or 'gloo'.",
)
parser.add_argument(
    "--num_diagnoses",
    default=2,
    type=int,
    help="Number of possible diagnoses that the user wants to identify",
)
parser.add_argument(
    "--patients",
    nargs='+',
    type=int,
    help="Lists of keywords to check against clinical notes",
)
parser.add_argument(
    "--output_folder",
    type=str,
    help="Decrypted output of the computation",
)
parser.add_argument(
    "--party1_input",
    type=str,
    help="Input file of party 1 (keywords)",
)
parser.add_argument(
    "--list_notes",
    nargs='+',
    type=str,
    help="Lists of patients to check against keywords",
)
parser.add_argument(
    "--party2_input",
    type=str,
    help="Input file of party 2 (clinical notes)",
)
parser.add_argument(
    "--lists_keywords",
    nargs='+',
    type=str,
    help="Lists of keywords to check against clinical notes",
)
parser.add_argument(
    "--threshold",
    default=0.05,
    type=float,
    help="Threshold for the string comparison",
)
parser.add_argument(
    "--distributed",
    default=True,
    action="store_true",
    help="Run example in distributed mode",
)

def _run_experiment(args):
    from protocol import run_protocol

    # Only Rank 0 will display logs.
    level = logging.INFO
    if "RANK" in os.environ and os.environ["RANK"] != "0":
       level = logging.CRITICAL
    logging.getLogger().setLevel(level)
    
    test = run_protocol(
        args.num_diagnoses,
        args.patients,
        args.output_folder,
        args.party1_input,
        args.list_notes,
        args.party2_input,
        args.lists_keywords,
        args.threshold,
    )
    print(test)
    



def main(run_experiment):
    args = parser.parse_args()
    
    if args.distributed:
        launcher = DistributedLauncher(args.world_size, args.rank, args.address, args.port, args.backend, run_experiment, args)
        launcher.start()
        #launcher.join()
        #launcher.terminate()
    else:
        run_experiment(args)


if __name__ == "__main__":
    main(_run_experiment)