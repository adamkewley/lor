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

from lor import pathalias
from lor.properties import DictPropertyLoader
from tests import tst_helpers
import lor.util


class TestTest(TestCase):

    def test_resolve_raises_FileNotFoundError_if_alias_file_path_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            pathalias.resolve("doesnt-exist", "ignore")

    def test_resolve_raises_Exception_if_alias_file_path_is_a_directory(self):
        with self.assertRaises(Exception):
            pathalias.resolve(tempfile.mkdtemp(), "ignore")

    def test_resolve_raises_KeyError_if_alias_is_not_in_file(self):
        fixture = tst_helpers.fixture("paths/example.yml")
        with self.assertRaises(KeyError):
            pathalias.resolve(fixture, "doesnt-exist")

    def test_resolve_returns_path_if_given_a_valid_alias(self):
        fixture = tst_helpers.fixture("paths/example.yml")

        ret = pathalias.resolve(fixture, "foo")

        self.assertEqual("bar/", ret)

    def test_resolve_uses_property_loader_to_resolve_vars_in_file(self):
        fixture = tst_helpers.fixture("paths/example-with-var.yml")
        var_val = lor.util.base36_str()
        property_loader = DictPropertyLoader("doesnt-matter", {"bar": var_val})

        ret = pathalias.resolve(fixture, "foo", [property_loader])

        self.assertEqual(var_val, ret)
