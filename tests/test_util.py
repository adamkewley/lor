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
import unittest

from lor import util


class TestHelpers(unittest.TestCase):

    def test_resolve_template_str_returns_expected_results(self):
        tests = [
            {"input": "", "variables": {}, "expectedOutput": ""},
            {"input": "$VAR1", "variables": {}, "expectedOutput": "$VAR1"},
            {"input": "$VAR1", "variables": {"VAR1": "val"}, "expectedOutput": "val"},
            {"input": "$VAR1foo", "variables": {"VAR1": "val"}, "expectedOutput": "valfoo"},
            {"input": "$VAR1foo$VAR2", "variables": {"VAR1": "val"}, "expectedOutput": "valfoo$VAR2"},
            {"input": "$VAR1foo$VAR2", "variables": {"VAR1": "val", "VAR2": "val2"}, "expectedOutput": "valfooval2"},
        ]

        for test in tests:
            input_str = test["input"]
            variables = test["variables"]
            expected_output = test["expectedOutput"]
            actual_output = util.resolve_template_str(input_str, variables)
            self.assertEqual(actual_output, expected_output)

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

    def test_flatten_returns_expected_result(self):
        input = [1, [2, 3], 4, [5, 6, 7]]
        expected_output = [1, 2, 3, 4, 5, 6, 7]
        actual_output = util.flatten(input)
        self.assertEqual(actual_output, expected_output)

    def test_or_join_returns_expected_results(self):
        self.assertEqual("", util.or_join([]))
        self.assertEqual("a", util.or_join(["a"]))
        self.assertEqual("a or b", util.or_join(["a", "b"]))
        self.assertEqual("a, b, or c", util.or_join(["a", "b", "c"]))

    def test_to_camel_case_returns_expected_results(self):
        self.assertEqual("SomeStr", util.to_camel_case("some_str"))
        self.assertEqual("SomeOtherStr", util.to_camel_case("some_other_str"))
        self.assertEqual("Str", util.to_camel_case("str"))
        self.assertEqual("", util.to_camel_case(""))
        self.assertEqual("Str", util.to_camel_case("Str"))
        self.assertEqual("SomeStr", util.to_camel_case("SomeStr"))


