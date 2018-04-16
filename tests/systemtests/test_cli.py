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
import io
import os
import unittest

import lor._paths
import lor.util.subprocess
from lor.test import TemporaryWorkspace, TemporaryEnv


def run_cli(args):
    with TemporaryEnv():
        # CI might be running from a non-standard dir, so need to setup the python path correctly
        # before launching off a subprocess
        os.environ["PYTHONPATH"] = os.path.normpath(os.path.join(os.path.dirname(__file__), "../.."))
        cli_command = lor._paths.lor_path("lor")
        all_args = ["python3", cli_command] + args

        exit_code, stdout_builder, stderr_builder = lor.util.subprocess.call_with_output_reducers(
            all_args,
            stdout_initial_state=io.StringIO(),
            stdout_reducer=__append_to_builder,
            stderr_initial_state=io.StringIO(),
            stderr_reducer=__append_to_builder)

        stdout = stdout_builder.getvalue()
        stdout_builder.close()
        stderr = stderr_builder.getvalue()
        stderr_builder.close()

        return stdout, stderr, exit_code


def __append_to_builder(builder, line):
    builder.write(line)
    builder.flush()
    return builder


class TestCli(unittest.TestCase):

    def test_call_lor_with_nothing_emits_help_to_stderr_and_nonzero_exit(self):
        args = []
        stdout, stderr, exit_code = run_cli(args)
        self.assertTrue("usage" in stderr)
        self.assertNotEqual(exit_code, 0)

    def test_call_lor_with_help_emits_help_to_stdout_and_zero_exit(self):
        args = ["--help"]
        stdout, stderr, exit_code = run_cli(args)
        self.assertTrue("usage" in stdout)
        self.assertEqual(exit_code, 0)

    def test_call_lor_explain_with_nothing_emits_help_to_stderr_and_nonzero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["explain"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertTrue(len(stderr) > 0)
                self.assertNotEqual(exit_code, 0)

    def test_call_lor_explain_with_help_emits_help_to_stdout_and_zero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["explain", "--help"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertTrue("usage" in stdout)
                self.assertEqual(exit_code, 0)

    def test_call_lor_explain_with_invalid_classname_emits_error_to_stderr_and_nonzero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["explain", "--module", "some.class.that.doesnt", "Exist"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertNotEqual(exit_code, 0)
                self.assertTrue(len(stderr) > 0)

    def test_call_lor_explain_with_valid_classname_emits_explanation_to_stdout_and_zero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["explain", "--module", "lor.tasks.general", "AlwaysRunsTask"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertEqual(exit_code, 0)
                self.assertTrue(len(stdout) > 0)

    def test_call_lor_ls_emits_list_of_classes_to_stdout_and_zero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["ls", "lor.tasks"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertEqual(exit_code, 0)
                # TODO: test output conforms

    def test_call_lor_run_with_invalid_task_classname_results_in_nonzero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["run", "--module", "some.invalid.module", "SomeInvalidClass"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertNotEqual(exit_code, 0)

    def test_call_lor_run_with_valid_task_classname_results_in_zero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["run", "--module", "lor.tasks.general", "AlwaysRunsTask", "--local-scheduler"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertEqual(exit_code, 0)

    def test_call_lor_properties_emits_varname_varval_space_separated_and_zero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["properties"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertEqual(exit_code, 0)
                # TODO: test output conforms

    def test_call_lor_dot_with_nothing_results_in_nonzero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["dot"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertNotEqual(exit_code, 0)
                self.assertTrue(len(stderr) > 0)

    def test_call_lor_dot_with_help_emits_usage_to_stdout_and_zero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["dot", "--help"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertEqual(exit_code, 0)
                self.assertTrue("usage" in stdout)

    def test_call_lor_dot_with_valid_task_class_emits_text_to_stdout_and_zero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["dot", "--module", "lor.tasks.general", "AlwaysRunsTask"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertEqual(exit_code, 0)
                # TODO: test output

    def test_call_lor_dot_with_invalid_task_class_returns_nonzero_exit(self):
        with TemporaryWorkspace() as ws:
            with TemporaryEnv():
                os.chdir(ws)
                args = ["dot", "--module", "some.class.that.doesnt", "Exist"]
                stdout, stderr, exit_code = run_cli(args)
                self.assertNotEqual(exit_code, 0)


