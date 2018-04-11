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
import tempfile
from unittest import TestCase

from lor import util
from lor.util import subprocess
from tests import tst_helpers


class TestSubprocess(TestCase):

    def test_call_returns_0_if_subprocess_returns_0(self):
        exit_code = subprocess.call(["python3", tst_helpers.fixture("print_hello_world.py")])
        self.assertEqual(0, exit_code)

    def test_call_returns_1_if_subprocess_returns_1(self):
        exit_code = subprocess.call(["python3", tst_helpers.fixture("fail.py")])
        self.assertEqual(1, exit_code)

    def test_call_with_stdout_reducer_returns_exit_code_and_final_state(self):
        args = ["python3", tst_helpers.fixture("print_hello_world.py")]
        initial_stdout_state = ""

        exit_code, final_stdout_state = subprocess.call_with_stdout_reducer(args, initial_stdout_state, self.__uppercase_reducer)

        self.assertEqual("HELLO, WORLD!", final_stdout_state)
        self.assertEqual(0, exit_code)

    def __uppercase_reducer(self, s, line):
        return s + line.upper()

    def test_call_with_stdout_reducer_returns_nonzero_exit_code_for_failing_application(self):
        args = ["python3", tst_helpers.fixture("fail.py")]
        initial_stdout_state = ""

        exit_code, final_stdout_state = subprocess.call_with_stdout_reducer(args, initial_stdout_state, self.__uppercase_reducer)

        self.assertEqual("", final_stdout_state)
        self.assertEqual(1, exit_code)

    def test_call_with_output_reducers_with_stdout_reducer_works_as_expected(self):
        args = ["python3", tst_helpers.fixture("print_hello_world.py")]
        initial_stdout_state = ""

        exit_code, final_stdout_state, final_stderr_state = subprocess.call_with_output_reducers(
            args,
            stdout_initial_state=initial_stdout_state,
            stdout_reducer=self.__uppercase_reducer)

        self.assertEqual("HELLO, WORLD!", final_stdout_state)
        self.assertEqual(0, exit_code)

    def test_call_with_output_reducers_with_stderr_reducer_works_as_expected(self):
        args = ["python3", tst_helpers.fixture("print_stderr.py")]
        initial_stderr_state = ""

        exit_code, final_stdout_state, final_stderr_state = subprocess.call_with_output_reducers(
            args,
            stderr_initial_state=initial_stderr_state,
            stderr_reducer=self.__uppercase_reducer)

        self.assertEqual("I'M IN STDERR!", final_stderr_state)
        self.assertEqual(0, exit_code)

    def test_call_with_output_reducers_returns_nonzero_exit_code_for_failing_application(self):
        args = ["python3", tst_helpers.fixture("fail.py")]

        exit_code, final_stdout_state, final_stderr_state = subprocess.call_with_output_reducers(args)

        self.assertEqual(1, exit_code)

    def test_call_and_write_stdout_to_file_returns_exit_code(self):
        args = ["python3", tst_helpers.fixture("print_stderr.py")]
        _, tmp_output = tempfile.mkstemp()

        exit_code = subprocess.call_and_write_stdout_to_file(args, tmp_output)

        self.assertEqual(0, exit_code)

    def test_call_and_write_stdout_to_file_returns_error_exit_code(self):
        args = ["python3", tst_helpers.fixture("fail.py")]
        _, tmp_output = tempfile.mkstemp()

        exit_code = subprocess.call_and_write_stdout_to_file(args, tmp_output)

        self.assertEqual(1, exit_code)

    def test_call_and_write_stdout_to_file_writes_stdout_to_file(self):
        args = ["python3", tst_helpers.fixture("print_hello_world.py")]
        _, tmp_output = tempfile.mkstemp()

        subprocess.call_and_write_stdout_to_file(args, tmp_output)

        file_content = util.read_file_to_string(tmp_output)

        self.assertEqual("Hello, world!\n", file_content)
