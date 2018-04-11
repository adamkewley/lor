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
import stat
import tempfile
from unittest import TestCase

import lor._constants
from lor import workspace
from lor.properties import DictPropertyLoader, PropertyLoader
from lor.test import TemporaryEnv
from lor.workspace import Workspace
from lor import util
from tests import tst_helpers


class TestWorkspaces(TestCase):

    def test_create_works_with_valid_arguments(self):
        path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(path)

    def test_create_creates_a_directory_at_path(self):
        path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(path)
        self.assertTrue(os.path.exists(path))

    def test_create_raises_if_path_already_exists(self):
        path = tempfile.mkdtemp()
        with self.assertRaises(Exception):
            workspace.create(path)

    def test_create_returns_a_Workspace_instance(self):
        path = os.path.join(tempfile.mkdtemp(), "ws")
        ret = workspace.create(path)

        self.assertIsInstance(ret, Workspace)

    def test_create_accepts_a_list_arg(self):
        path = os.path.join(tempfile.mkdtemp(), "ws")

        workspace.create(path, [])

    def test_is_workspace_raises_FileNotFoundError_if_path_does_not_exist(self):
        path = "doesnt-exist"
        with self.assertRaises(FileNotFoundError):
            workspace.is_workspace(path)

    def test_is_workspace_raises_NotADirectoryError_if_path_is_a_file(self):
        _, path = tempfile.mkstemp()
        with self.assertRaises(NotADirectoryError):
            workspace.is_workspace(path)

    def test_is_workspace_returns_false_if_dir_doesnt_contain_binstub(self):
        path = tempfile.mkdtemp()
        self.assertFalse(workspace.is_workspace(path))

    def test_is_workspace_returns_true_if_path_contains_binstub(self):
        path = tempfile.mkdtemp()
        bin_subfolder = os.path.join(path, lor._constants.WORKSPACE_EXEC_BINSTUB.split("/")[0])
        os.mkdir(bin_subfolder)
        lor_binstub = os.path.join(bin_subfolder, lor._constants.WORKSPACE_EXEC_BINSTUB.split("/")[1])
        with open(lor_binstub, "w"):
            pass

        self.assertTrue(workspace.is_workspace(path))

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

    def test_Workspace_init_raises_if_called_with_non_existent_dir(self):
        with self.assertRaises(FileNotFoundError):
            Workspace("some-non-existent-workspace", [])

    def test_Workspace_init_raises_if_called_with_a_file(self):
        _, path = tempfile.mkstemp()
        
        with self.assertRaises(NotADirectoryError):            
            Workspace(path, [])

    def test_Workspace_init_raises_if_called_with_a_non_workspace_directory(self):
        path = tempfile.mkdtemp()
        
        with self.assertRaises(Exception):
            Workspace(path, [])

    def test_Workspace_init_works_fine_when_called_with_a_workspace(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws_path)

        Workspace(ws_path, [])

    def test_Workspace_init_accepts_a_property_loader_as_2nd_arg(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws_path)

        property_loader = DictPropertyLoader(util.base36_str(), {})

        Workspace(ws_path, property_loader)

    def test_Workspace_resolve_resolves_path_relative_to_workspace(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)

        subpath = util.base36_str()
        ret = ws.resolve_path(subpath)

        self.assertEqual(
            os.path.relpath(os.path.join(ws_path, subpath)),
            os.path.relpath(ret))

    def test_Workspace_resolve_does_nothing_to_an_absolute_path(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)

        subpath = "/" + util.base36_str()
        ret = ws.resolve_path(subpath)

        self.assertEqual(subpath, ret)

    def test_Workspace_resolve_workspace_alias_raises_FileNotFoundError_if_workspace_aliases_file_does_not_exist(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)

        aliases_path = os.path.join(ws_path, lor._constants.WORKSPACE_ALIASES)
        os.remove(aliases_path)

        with self.assertRaises(FileNotFoundError):
            ws.resolve_workspace_pathalias(util.base36_str())

    def test_Workspace_resolve_workspace_alias_raises_KeyError_if_alias_does_not_exist(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)

        with self.assertRaises(KeyError):
            ws.resolve_workspace_pathalias(util.base36_str())

    def test_Workspace_resolve_workspace_alias_returns_value_when_called_with_actual_alias(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)

        ret = ws.resolve_workspace_pathalias("TEST_FIXTURES")

        self.assertEqual(
            os.path.realpath(ret),
            os.path.realpath(os.path.join(ws_path, "tests/fixtures")))

    def test_Workspace_resolve_alias_raises_FileNotFoundError_if_supplied_non_existient_path(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)

        non_existient_path = util.base36_str()

        with self.assertRaises(FileNotFoundError):
            ws.resolve_alias_file(non_existient_path, util.base36_str())

    def test_Workspace_resolve_alias_works_with_absolute_path_to_aliases_file(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)
        fixture_path = os.path.abspath(tst_helpers.fixture("paths/example.yml"))

        ret = ws.resolve_alias_file(fixture_path, "foo")

        self.assertEqual("bar/", ret)

    def test_Workspace_resolve_alias_raises_KeyError_if_alias_not_in_aliases_file(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)
        fixture_path = os.path.abspath(tst_helpers.fixture("paths/example.yml"))

        non_existient_key = util.base36_str()

        with self.assertRaises(KeyError):
            ws.resolve_alias_file(fixture_path, non_existient_key)

    def test_Workspace_resolve_alias_resolves_relative_paths_relative_to_cwd(self):
        # The resolve_alias function shouldn't assume clients want relpaths relative to
        # the workspace because aliases might be used in other ways (e.g. from scripts).
        # Clients *should* use `resolve` if they want a path relative to the workspace.

        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)

        fixture_path = tst_helpers.fixture("paths/example.yml")
        cwd = os.getcwd()
        fixture_relpath = os.path.relpath(fixture_path, cwd)

        ret = ws.resolve_alias_file(fixture_relpath, "foo")

        self.assertEqual("bar/", ret)

    def test_Workspace_get_property_raises_KeyError_if_property_cannot_be_loaded_from_property_loader(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        property_loader = []

        ws = workspace.create(ws_path, property_loader)

        with self.assertRaises(KeyError):
            ws.get_property(util.base36_str())

    def test_Workspace_get_property_returns_value_if_value_can_be_loaded_from_property_loader(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        prop_key = util.base36_str()
        prop_val = util.base36_str()
        property_loader = DictPropertyLoader(
            name=util.base36_str(),
            property_dict={prop_key: prop_val})

        ws = workspace.create(ws_path, [property_loader])

        self.assertEqual(prop_val, ws.get_property(prop_key))

    def test_Workspace_get_properties_returns_dict(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path)

        ret = ws.get_properties()

        self.assertIsInstance(ret, dict)

    def test_Workspce_get_properties_returns_dict_returned_by_property_loader(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        prop_dict = {"some": "var"}
        property_loader = DictPropertyLoader(
            name=util.base36_str(),
            property_dict=prop_dict)

        ws = workspace.create(ws_path, [property_loader])

        self.assertEqual(property_loader.get_all(), ws.get_properties())

    def test_Workspace_get_path_returns_absolute_workspace_path(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace.create(ws_path, [])

        self.assertTrue(ws.get_abspath().startswith("/"))
        self.assertEqual(os.path.realpath(ws_path), os.path.realpath(ws.get_abspath()))

    def test_calling_install_on_a_workspace_runs_bin_install(self):
        workspace_dir = tempfile.mkdtemp()

        bin_dir = os.path.join(workspace_dir, "bin")
        os.mkdir(bin_dir)

        install_path = os.path.join(bin_dir, "install")
        str_written_by_script = util.base36_str(20)
        _, file_containing_str = tempfile.mkstemp()

        install_script = """#!/bin/bash
                echo {str} > {out}
                """.format(str=str_written_by_script, out=file_containing_str)

        with open(install_path, "w") as f:
            f.write(install_script)

        st = os.stat(str(install_path))
        os.chmod(install_path, st.st_mode | stat.S_IEXEC)

        workspace.install(workspace_dir)

        self.assertTrue(os.path.exists(file_containing_str))

        with open(file_containing_str, "r") as f:
            self.assertEqual(str_written_by_script, f.readlines()[0].strip())

    def test_try_locate_workspace_returns_none_if_lor_home_is_not_set_and_cwd_is_not_a_workspace(self):
        cwd = tempfile.mkdtemp()
        self.assertIsNone(workspace.try_locate(cwd))

    def test_try_locate_workspace_returns_cwd_if_cwd_is_a_workspace(self):
        cwd = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(cwd)

        ws_path = workspace.try_locate(cwd)

        self.assertEqual(os.path.realpath(cwd), os.path.realpath(ws_path))

    def test_try_locate_workspace_returns_env_cwd_if_env_cwd_is_a_workspace(self):
        cwd = os.path.join(tempfile.mkdtemp(), "wd")
        workspace.create(cwd)

        with TemporaryEnv():
            os.chdir(cwd)
            ws_path = workspace.try_locate()
            self.assertEqual(os.path.realpath(cwd), os.path.realpath(ws_path))

    def test_try_locate_workspace_returns_LOR_HOME_if_it_is_set_in_env(self):
        cwd = os.path.join(tempfile.mkdtemp(), "wd")
        workspace.create(cwd)

        with TemporaryEnv():
            os.environ[lor._constants.WORKSPACE_ENV_VARNAME] = cwd

            ws_path = workspace.try_locate()
            self.assertEqual(os.path.realpath(cwd), os.path.realpath(ws_path))
