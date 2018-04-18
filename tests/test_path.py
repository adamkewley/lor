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
from unittest import TestCase

from lor import path, workspace, util
from lor.generators.workspace import workspace_generator


class TestPaths(TestCase):

    def test_get_overlay_paths_returns_a_list(self):
        self.assertIsInstance(path.get_overlay_paths(), list)

    def test__set_overlay_paths_works_with_list_of_existient_dirs(self):
        paths = [
            tempfile.mkdtemp(),
            tempfile.mkdtemp(),
            tempfile.mkdtemp(),
        ]
        path._set_overlay_paths(paths)

    def test__set_overlay_paths_causes_get_overlay_paths_to_return_the_supplied_paths(self):
        paths = [
            tempfile.mkdtemp(),
            tempfile.mkdtemp(),
            tempfile.mkdtemp(),
        ]
        path._set_overlay_paths(paths)
        returned_paths = path.get_overlay_paths()
        self.assertEqual(paths, returned_paths)

    def test__set_overlay_paths_raises_ValueError_if_supplied_a_non_list(self):
        with self.assertRaises(ValueError):
            path._set_overlay_paths("not-a-list")

    def test__set_overlay_paths_raises_ValueError_if_supplied_a_list_of_non_strings(self):
        invalid_list = [
            "this-is-ok",
            [],  # this isn't
        ]
        with self.assertRaises(ValueError):
            path._set_overlay_paths(invalid_list)

    def test__set_overlay_paths_raises_FileNotFoundError_if_list_entry_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            path._set_overlay_paths(["doesnt-exist"])

    def test__set_overlay_paths_raises_NotADirectoryError_if_path_is_to_a_file(self):
        _, some_file = tempfile.mkstemp()
        with self.assertRaises(NotADirectoryError):
            path._set_overlay_paths([some_file])

    def test_join_returns_paths_joined_onto_workspace_if_no_overlay_paths_available(self):
        path._set_overlay_paths([])
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace_generator.create(ws_path)
        workspace._set_path(ws_path)

        fragment = util.base36_str()
        expected_result = os.path.join(ws_path, fragment)
        actual_result = path.join(fragment)

        self.assertEqual(expected_result, actual_result)

    def test_join_returns_paths_joined_onto_first_overlay_if_overlays_assigned(self):
        first_overlay = tempfile.mkdtemp()
        overlays = [
            first_overlay,
            tempfile.mkdtemp(),
        ]
        path._set_overlay_paths(overlays)

        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace_generator.create(ws_path)
        workspace._set_path(ws_path)

        fragment = util.base36_str()
        expected_result = os.path.join(first_overlay, fragment)
        actual_result = path.join(fragment)

        self.assertEqual(expected_result, actual_result)

    def test_join_raises_ValueError_if_no_overlays_and_not_in_workspace(self):
        path._set_overlay_paths([])
        workspace._set_path(None)

        with self.assertRaises(ValueError):
            path.join(util.base36_str())

    def test_join_works_with_multiple_fragments(self):
        first_overlay_path = tempfile.mkdtemp()
        path._set_overlay_paths([first_overlay_path])

        frag1 = util.base36_str()
        frag2 = util.base36_str()

        expected_result = os.path.join(first_overlay_path, frag1, frag2)
        actual_result = path.join(frag1, frag2)

        self.assertEqual(expected_result, actual_result)

    def test_join_all_returns_a_list(self):
        ret = path.join_all(util.base36_str())

        self.assertIsInstance(ret, list)

    def test_join_all_returns_list_of_overlays_then_workspace(self):
        overlay1 = tempfile.mkdtemp()
        overlay2 = tempfile.mkdtemp()
        overlay3 = tempfile.mkdtemp()

        overlays = [overlay1, overlay2, overlay3]
        path._set_overlay_paths(overlays)

        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace_generator.create(ws_path)
        workspace._set_path(ws_path)

        frag = util.base36_str()

        expected_ret = [
            os.path.join(p, frag)
            for p
            in [overlay1, overlay2, overlay3, ws_path]
        ]

        actual_ret = path.join_all(frag)

        self.assertEqual(expected_ret, actual_ret)

    def test_resolve_returns_result_from_overlay_if_exists_and_in_overlay(self):
        overlay1 = tempfile.mkdtemp()
        file_name = util.base36_str()
        self.__create_file(os.path.join(overlay1, file_name))

        path._set_overlay_paths([overlay1])

        returned_path = path.resolve(file_name)

        self.assertEqual(returned_path, os.path.join(overlay1, file_name))

    def test_resolve_returns_result_from_another_overlay_if_exists_in_different_overlay(self):
        empty_overlay = tempfile.mkdtemp()
        overlay_with_file = tempfile.mkdtemp()
        file_name = util.base36_str()
        self.__create_file(os.path.join(overlay_with_file, file_name))

        path._set_overlay_paths([empty_overlay, overlay_with_file])

        returned_path = path.resolve(file_name)

        self.assertEqual(os.path.join(overlay_with_file, file_name), returned_path)

    def test_resolve_returns_result_from_workspace_if_workspace_has_file(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace_generator.create(ws_path)
        workspace._set_path(ws_path)

        file_name = util.base36_str()
        self.__create_file(os.path.join(ws_path, file_name))

        some_overlay = tempfile.mkdtemp()
        path._set_overlay_paths([some_overlay])

        returned_path = path.resolve(file_name)

        self.assertEqual(os.path.join(ws_path, file_name), returned_path)

    def test_resolve_raises_ValueError_if_overlays_empty_and_not_in_workspace(self):
        path._set_overlay_paths([])
        workspace._set_path(None)

        with self.assertRaises(ValueError):
            path.resolve(util.base36_str())

    def test_resolve_raises_FileNotFoundError_if_file_doesnt_exist_in_any_location(self):
        overlays = [
            tempfile.mkdtemp(),
            tempfile.mkdtemp(),
            tempfile.mkdtemp()
        ]
        path._set_overlay_paths(overlays)
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace_generator.create(ws_path)
        workspace._set_path(ws_path)

        with self.assertRaises(FileNotFoundError):
            path.resolve(util.base36_str())

    def test_resolve_all_returns_a_list(self):
        self.assertIsInstance(path.resolve_all(), list)

    def test_resolve_all_list_is_empty_if_no_overlays_or_workspace(self):
        path._set_overlay_paths([])
        workspace._set_path(None)

        self.assertEqual([], path.resolve_all())

    def test_resolve_all_list_contains_elements_that_do_exist(self):
        file_name = util.base36_str()

        overlay_with_result = tempfile.mkdtemp()
        self.__create_file(os.path.join(overlay_with_result, file_name))

        empty_overlay = tempfile.mkdtemp()

        another_overlay_with_result = tempfile.mkdtemp()
        self.__create_file(os.path.join(another_overlay_with_result, file_name))

        path._set_overlay_paths([
            overlay_with_result,
            empty_overlay,
            another_overlay_with_result
        ])

        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace_generator.create(ws_path)
        self.__create_file(os.path.join(ws_path, file_name))
        workspace._set_path(ws_path)

        expected_result = [
            os.path.join(overlay_with_result, file_name),
            os.path.join(another_overlay_with_result, file_name),
            os.path.join(ws_path, file_name),
        ]

        actual_result = path.resolve_all(file_name)

        self.assertEqual(expected_result, actual_result)




    def __create_file(self, path):
        open(path, "a").close()
