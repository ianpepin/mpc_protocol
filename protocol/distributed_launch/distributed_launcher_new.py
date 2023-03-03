#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import logging
import multiprocessing
import os
import uuid

import crypten

import torch


class DistributedLauncher:

    # run_process_fn will be run in subprocesses.
    def __init__(self, world_size, rank, address, port, backend, run_process_fn, fn_args=None):
        multiprocessing.set_start_method("spawn")

        # Specify necessary environmental variables for torch.distributed
        env = os.environ.copy()
        env["RENDEZVOUS"] = "env://"
        # env["RENDEZVOUS"] = "file:///tmp/crypten-rendezvous-{}".format(uuid.uuid1())
        env["WORLD_SIZE"] = str(world_size)
        env["RANK"] = str(rank)
        env["MASTER_ADDR"] = address
        env["MASTER_PORT"] = str(port)
        
        self.processes = []
        
        # prepare process for the current rank
        process_name = "process " + str(rank)
        process = multiprocessing.Process(
            target=self.__class__._run_process,
            name=process_name,
            args=(rank, world_size, env, run_process_fn, fn_args),
        )
        self.processes.append(process)

        if crypten.mpc.ttp_required():
            ttp_process = multiprocessing.Process(
                target=self.__class__._run_process,
                name="TTP",
                args=(
                    world_size,
                    world_size,
                    env,
                    crypten.mpc.provider.TTPServer,
                    None,
                ),
            )
            self.processes.append(ttp_process)

    @classmethod
    def _run_process(cls, rank, world_size, env, run_process_fn, fn_args):
        for env_key, env_value in env.items():
            os.environ[env_key] = env_value
        os.environ["RANK"] = str(rank)
        orig_logging_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.INFO)
        crypten.init()
        logging.getLogger().setLevel(orig_logging_level)
        
        # #! Resetting the results before each execution, delete this once protocol is fully implemented!!!!!!!!!!!!!!!!
        # if rank == 0:
        #     new_results = torch.empty(4)
        #     torch.save(new_results, "/home/jovyan/mpc_use_case/three_party_mpc/user/data/results_of_protocol.pt")
        # #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            
        if fn_args is None:
            run_process_fn()
        else:
            run_process_fn(fn_args)

    def start(self):
        for process in self.processes:
            process.start()

    def join(self):
        for process in self.processes:
            process.join()
            assert (
                process.exitcode == 0
            ), f"{process.name} has non-zero exit code {process.exitcode}"

    def terminate(self):
        for process in self.processes:
            process.terminate()
