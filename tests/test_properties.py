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
import unittest

from lor import util, properties
from lor.properties import DictPropertyLoader, YAMLFilePropertyLoader
from tests import tst_helpers


class TestProperties(unittest.TestCase):

    def test_get_default_property_loaders_returns_list_of_property_loaders_for_workspace(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws_path)

        returned_property_loaders = workspace.get_default_property_loaders(ws_path)

        self.assertIsInstance(returned_property_loaders, list)

        for loader in returned_property_loaders:
            self.assertIsInstance(loader, PropertyLoader)

    def test_get_default_property_loaders_raises_FileNotFoundError_for_non_existent_path(self):
        non_existent_path = util.base36_str()

        with self.assertRaises(FileNotFoundError):
            workspace.get_default_property_loaders(non_existent_path)

    def test_get_default_property_loaders_raises_NotADirectoryError_if_path_is_file(self):
        _, path_to_file = tempfile.mkstemp()

        with self.assertRaises(NotADirectoryError):
            workspace.get_default_property_loaders(path_to_file)

    def test_get_default_property_loaders_raises_RuntimeError_if_dir_is_not_workspace(self):
        non_workspace_dir = tempfile.mkdtemp()

        with self.assertRaises(RuntimeError):
            workspace.get_default_property_loaders(non_workspace_dir)

    def test_DictPropertyLoader_init_works_with_standard_args(self):
        DictPropertyLoader(util.base36_str(), {})

    def test_DictPropertyLoader_get_name_returns_supplied_name(self):
        name = util.base36_str()
        loader = DictPropertyLoader(name, {})

        self.assertEqual(name, loader.get_name())

    def test_DictPropertyLoader_try_get_returns_property_from_dict(self):
        k = util.base36_str()
        v = util.base36_str()

        loader = DictPropertyLoader(util.base36_str(), {k: v})

        ret = loader.try_get(k)

        self.assertEqual(v, ret)

    def test_DictPropertyLoader_try_get_returns_None_if_property_does_not_exist(self):
        loader = DictPropertyLoader(util.base36_str(), {})

        self.assertIsNone(loader.try_get(util.base36_str()))

    def test_DictPropertyLoader_get_returns_property_from_dict(self):
        k = util.base36_str()
        v = util.base36_str()

        loader = DictPropertyLoader(util.base36_str(), {k: v})

        ret = loader.get(k)

        self.assertEqual(v, ret)

    def test_DictPropertyLoader_get_raises_KeyError_if_property_does_not_exist(self):
        loader = DictPropertyLoader(util.base36_str(), {})

        with self.assertRaises(KeyError):
            loader.get(util.base36_str())

    def test_DictPropertyLoader_get_all_returns_same_dict_as_supplied_in_ctor(self):
        d = {"k1": "v1", "k2": "v2"}
        loader = DictPropertyLoader(util.base36_str(), d)

        ret = loader.get_all()

        self.assertEqual(d, ret)

    def test_YAMLFilePropertyLoader_init_raises_FileNotFoundError_if_path_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            YAMLFilePropertyLoader(util.base36_str())

    def test_YAMLFilePropertyLoader_init_raises_RuntimeError_if_file_is_invalid(self):
        invalid_file = tst_helpers.fixture("properties/invalid-file")

        with self.assertRaises(RuntimeError):
            YAMLFilePropertyLoader(invalid_file)

    def test_YAMLFilePropertyLoader_get_name_contains_YAML_file_name(self):
        fixture_file = tst_helpers.fixture("properties/variables.yml")
        loader = YAMLFilePropertyLoader(fixture_file)

        ret = loader.get_name()
        filename = os.path.basename(fixture_file)

        self.assertTrue(filename in ret)

    def test_YAMLFilePropertyLoader_try_get_returns_variable_in_YAML_file(self):
        fixture_file = tst_helpers.fixture("properties/variables.yml")
        loader = YAMLFilePropertyLoader(fixture_file)

        ret = loader.try_get("foo")

        self.assertEqual("bar", ret)

    def test_YAMLFilePropertyLoader_try_get_returns_None_if_variable_not_in_YAML_file(self):
        fixture_file = tst_helpers.fixture("properties/variables.yml")
        loader = YAMLFilePropertyLoader(fixture_file)

        self.assertIsNone(loader.try_get(util.base36_str()))

    def test_YAMLFilePropertyLoader_get_returns_variable_in_YAML_file(self):
        fixture_file = tst_helpers.fixture("properties/variables.yml")
        loader = YAMLFilePropertyLoader(fixture_file)

        ret = loader.get("foo")

        self.assertEqual("bar", ret)

    def test_YAMLFilePropertyLoader_get_throws_KeyError_if_variable_not_in_YAML_file(self):
        fixture_file = tst_helpers.fixture("properties/variables.yml")
        loader = YAMLFilePropertyLoader(fixture_file)

        with self.assertRaises(KeyError):
            loader.get(util.base36_str())

    def test_YAMLFilePropertyLoader_get_all_returns_dict_of_values_loaded_from_YAML_file(self):
        fixture_file = tst_helpers.fixture("properties/variables.yml")
        loader = YAMLFilePropertyLoader(fixture_file)

        ret = loader.get_all()
        expected = {"foo": "bar"}

        self.assertEqual(expected, ret)

    def test_get_property_from_list_of_loaders_returns_prop_from_single_loader(self):
        k = util.base36_str()
        v = util.base36_str()
        loaders = [DictPropertyLoader(util.base36_str(), {k: v})]

        ret = properties.get_property_from_list_of_loaders(loaders, k)

        self.assertEqual(v, ret)

    def test_get_property_from_list_of_loaders_returns_prop_from_multiple_loaders(self):
        k1 = util.base36_str()
        v1 = util.base36_str()
        k2 = util.base36_str()
        v2 = util.base36_str()

        loaders = [
            DictPropertyLoader(util.base36_str(), {k1: v1}),
            DictPropertyLoader(util.base36_str(), {k2: v2}),
        ]

        ret = properties.get_property_from_list_of_loaders(loaders, k2)

        self.assertEqual(v2, ret)

    def test_get_property_from_list_of_loaders_raises_KeyError_if_property_is_not_in_loaders(self):
        with self.assertRaises(KeyError):
            properties.get_property_from_list_of_loaders([], util.base36_str())

    def test_get_property_from_list_of_loaders_overwrites_properties(self):
        k = util.base36_str()
        v1 = util.base36_str()
        v2 = util.base36_str()

        loaders = [
            DictPropertyLoader("first", {k: v1}),
            DictPropertyLoader("second", {k: v2}),
        ]

        ret = properties.get_property_from_list_of_loaders(loaders, k)

        self.assertEqual(ret, v1)

    def test_merge_list_of_property_loaders_takes_list_and_returns_dict(self):
        ret = properties.merge_list_of_property_loaders([])

        self.assertIsInstance(ret, dict)

    def test_merge_list_of_property_loaders_merges_properties_from_multiple_loaders_as_expected(self):
        k1 = util.base36_str()
        v1 = util.base36_str()
        k2 = util.base36_str()
        v2_a = util.base36_str()
        v2_b = util.base36_str()
        k3 = util.base36_str()
        v3 = util.base36_str()
        k4 = util.base36_str()
        v4 = util.base36_str()

        loaders = [
            DictPropertyLoader("first", {k1: v1, k2: v2_a}),
            DictPropertyLoader("second", {k2: v2_b, k3: v3}),
            DictPropertyLoader("third", {k4: v4}),
        ]

        ret = properties.merge_list_of_property_loaders(loaders)

        expected_ret = {
            k1: v1,
            k2: v2_a,
            k3: v3,
            k4: v4,
        }

        self.assertEqual(expected_ret, ret)
