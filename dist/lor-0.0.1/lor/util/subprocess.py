# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Utilities for running separate subprocesses

Many of these functions wrap the python standard library's subprocess functions. The reason to use these functions
instead of the standard library's is because, in many cases:

- They handle signal capture (e.g. SIGINT), which is important when tasks are long-running and likely to be cancelled
  midway
- They stream the subprocess's output directly to the calling process's stdio, rather than collecting it into memory and
  dumping it after execution finishes: important for long-running tasks which output *a lot* of logging etc.
- Output streaming is handled functionally: downstream users don't need to worry about spawning threads etc.: they just
  write lambdas/functions to filter+reduce process outputs: important when a subprocess produces *a lot* of logging
  output (e.g. long-running Hadoop MR jobs) and you don't want to risk a memory leak.
"""
import subprocess
import sys
from threading import Thread

from luigi.contrib.external_program import ExternalProgramRunContext


def call(args):
    """Synchronously run the command described by args, returning an exit code integer once the subprocess exits.
    :param args: List of args, where the first arg is the application's name
    :return Exit code of the subprocess
    """

    exit_code, state = call_with_stdout_reducer(args, None, lambda state, last_line: None)
    return exit_code


def call_with_stdout_reducer(args, initial_reducer_state, output_reducer):
    exit_code, stdout_state, stderr_state = call_with_output_reducers(
        args,
        stdout_initial_state=initial_reducer_state,
        stdout_reducer=output_reducer)

    return exit_code, stdout_state


def call_with_output_reducers(args, stdout_initial_state=None, stdout_reducer=lambda: (), stderr_initial_state=None, stderr_reducer=lambda: ()):
    p = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

    with ExternalProgramRunContext(p):
        stdout_state_holder = __StateHolder(stdout_initial_state)
        stdout_thread = Thread(name="stdout", target=__split_pipe_via_reducer, args=(p.stdout, sys.stdout, stdout_state_holder, stdout_reducer,))
        stdout_thread.start()

        stderr_state_holder = __StateHolder(stderr_initial_state)
        stderr_thread = Thread(name="stderr", target=__split_pipe_via_reducer, args=(p.stderr, sys.stderr, stderr_state_holder, stderr_reducer,))
        stderr_thread.start()

        stdout_thread.join()
        stderr_thread.join()

        exit_code = p.wait()

        return exit_code, stdout_state_holder.state, stderr_state_holder.state


class __StateHolder:
    state = None

    def __init__(self, state):
        self.state = state


def __split_pipe_via_reducer(input_pipe, output_pipe, state_holder, reducer):
    line = input_pipe.readline()
    while len(line) > 0:
        decoded_line = line.decode("utf-8")

        output_pipe.write(decoded_line)
        output_pipe.flush()

        state_holder.state = reducer(state_holder.state, decoded_line.strip())

        line = input_pipe.readline()

    input_pipe.close()


def call_and_write_stdout_to_file(args, output_path):
    with open(output_path, "w") as stdout_file:
        p = subprocess.Popen(args, stdout=stdout_file)
        return p.wait()


def run_luigi_task(task_class, task_args):
    args = [
        "luigi",
        "--module",
        task_class.__module__,
        task_class.__name__,
        "--retcode-task-failed", "1",
        "--retcode-scheduling-error", "1",
        "--retcode-unhandled-exception", "1",
        "--retcode-missing-data", "1",
        "--retcode-not-run", "1",
    ]
    all_args = args + task_args

    return subprocess.call(all_args)
