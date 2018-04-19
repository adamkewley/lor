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
import os
import tempfile
import unittest

from lor import util


class TestHelpers(unittest.TestCase):

    def test_file_uri_returns_expected_results(self):
        cwd = os.getcwd()

        tests = [
            ("/", "file:///"),
            ("/dir1/dir2", "file:///dir1/dir2"),
            ("", "file://{cwd}/".format(cwd=cwd)),
            ("dir1/dir2", "file://{cwd}/dir1/dir2".format(cwd=cwd)),
        ]

        for input_path, expected_output in tests:
            actual_output = util.file_uri(input_path)
            self.assertEqual(expected_output, actual_output)

    def test_read_file_to_string_returns_file_contents_as_string(self):
        _, path = tempfile.mkstemp()
        content = util.base36_str()
        with open(path, "w") as f:
            f.write(content)

        returned_content = util.read_file_to_string(path)
        self.assertEqual(content, returned_content)

    def test_read_file_to_string_raises_FileNotFoundError_for_non_existent_path(self):
        with self.assertRaises(FileNotFoundError):
            util.read_file_to_string(util.base36_str(64))

    def test_read_file_to_string_raises_UnicodeDecodeError_for_binary_file(self):
        _, path = tempfile.mkstemp()
        with open(path, "wb") as f:
            f.write(os.urandom(32))

        with self.assertRaises(UnicodeDecodeError):
            util.read_file_to_string(path)

    def test_write_str_to_file(self):
        dir = tempfile.mkdtemp()
        dest = os.path.join(dir, "file")
        s = util.base36_str()

        util.write_str_to_file(dest, s)

        self.assertTrue(os.path.exists(dest))

        with open(dest, "r") as f:
            content = f.read()
            self.assertEqual(s, content)

    def test_write_str_to_file_raises_FileExistsError_if_file_exists(self):
        _, p = tempfile.mkstemp()
        with self.assertRaises(FileExistsError):
            util.write_str_to_file(p, util.base36_str())

    def test_uri_subfolder_returns_expected_result(self):
        tests = [
            {
                "base": "http://host/sub1",
                "part": "sub2",
                "result": "http://host/sub1/sub2"
            },
            {
                "base": "hdfs:///some/operations/folder/",
                "part": 'sub3',
                "result": "hdfs:///some/operations/folder/sub3"
            }
        ]

        for test in tests:
            result = util.uri_subfolder(test["base"], test["part"])
            self.assertEqual(result, test["result"])

    def test_or_join_returns_expected_results(self):
        self.assertEqual("", util.or_join([]))
        self.assertEqual("a", util.or_join(["a"]))
        self.assertEqual("a or b", util.or_join(["a", "b"]))
        self.assertEqual("a, b, or c", util.or_join(["a", "b", "c"]))

    def test_to_camel_case_returns_expected_results(self):
        cases = [
            ("some_str", "SomeStr"),
            ("some_other_str", "SomeOtherStr"),
            ("str", "Str"),
            ("", ""),
            ("Str", "Str"),
            ("SomeStr", "SomeStr"),
        ]

        for input_str, expected_output in cases:
            actual_output = util.to_camel_case(input_str)
            self.assertEqual(expected_output, actual_output)

    def test_to_snake_case_returns_expected_results(self):
        cases = [
            ("SomeStr", "some_str"),
            ("", ""),
            ("some_str", "some_str"),
            ("Some", "some"),
            ("SomeOtherStr", "some_other_str"),
            ("Some_ObviouslyMalformedStr", "some_obviously_malformed_str"),
        ]

        for input_str, expected_output in cases:
            actual_output = util.to_snake_case(input_str)
            self.assertEqual(expected_output, actual_output)



