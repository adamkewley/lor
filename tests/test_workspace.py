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
from lor import util
from lor import workspace
from lor.test import TemporaryEnv


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

    def test_create_returns_a_path_to_the_workspace(self):
        path = os.path.join(tempfile.mkdtemp(), "ws")
        ret = workspace.create(path)

        self.assertEqual(ret, path)

    def test__set_path_runs_ok_with_valid_workspace(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws_path)

        workspace._set_path(ws_path)

    def test__set_path_to_None_works_ok(self):
        workspace._set_path(None)

    def test__set_path_raises_FileNotFoundError_if_arg_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            workspace._set_path(util.base36_str())

    def test__set_path_raises_NotADirectoryError_if_arg_is_file(self):
        _, file_path = tempfile.mkstemp()
        with self.assertRaises(NotADirectoryError):
            workspace._set_path(file_path)

    def test__set_path_raises_ValueError_if_arg_is_no_a_workspace(self):
        some_dir = tempfile.mkdtemp()
        with self.assertRaises(ValueError):
            workspace._set_path(some_dir)

    def test_get_path_returns_None_if_manual_ws_set_is_None_and_cwd_is_not_a_workspace(self):
        some_dir = tempfile.mkdtemp()
        workspace._set_path(None)
        self.assertIsNone(workspace.get_path(some_dir))

    def test_get_path_returns_manually_set_path(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws_path)
        workspace._set_path(ws_path)

        returned_path = workspace.get_path()

        self.assertEqual(ws_path, returned_path)

    def test_get_path_returns_cwd_if_cwd_is_workspace_and_no_manual_override_set(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws_path)

        workspace._set_path(None)

        returned_path = workspace.get_path(ws_path)

        self.assertEqual(ws_path, returned_path)

    def test_get_path_returns_manually_set_path_even_if_supplied_cwd(self):
        ws1_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws1_path)

        ws2_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws2_path)

        workspace._set_path(ws1_path)

        returned_path = workspace.get_path(ws2_path)

        self.assertEqual(ws1_path, returned_path)

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

    def test_run_install_script_runs_bin_install(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws_path)
        installer_path = os.path.join(ws_path, lor._constants.WORKSPACE_INSTALL_BINSTUB)
        os.remove(installer_path)

        workspace_dir = ws_path

        install_path = os.path.join(workspace_dir, lor._constants.WORKSPACE_INSTALL_BINSTUB)
        str_written_by_script = util.base36_str(20)
        _, file_containing_str = tempfile.mkstemp()

        install_script = """#!/bin/bash
                echo {str} > {out}
                """.format(str=str_written_by_script, out=file_containing_str)

        with open(install_path, "w") as f:
            f.write(install_script)

        st = os.stat(str(install_path))
        os.chmod(install_path, st.st_mode | stat.S_IEXEC)

        workspace.run_install_script(workspace_dir)

        self.assertTrue(os.path.exists(file_containing_str))

        with open(file_containing_str, "r") as f:
            self.assertEqual(str_written_by_script, f.readlines()[0].strip())

    def test_run_install_script_raises_FileNotFoundError_if_workspace_path_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            workspace.run_install_script(util.base36_str())

    def test_run_install_script_raises_NotADirectoryError_if_workspace_path_is_not_a_dir(self):
        _, some_file = tempfile.mkstemp()
        with self.assertRaises(NotADirectoryError):
            workspace.run_install_script(some_file)

    def test_run_install_script_raises_FileNotFoundError_if_workspace_doesnt_contain_installer(self):
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(ws_path)
        installer_path = os.path.join(ws_path, lor._constants.WORKSPACE_INSTALL_BINSTUB)
        os.remove(installer_path)
        with self.assertRaises(FileNotFoundError):
            workspace.run_install_script(ws_path)

    def test_try_locate_returns_none_if_lor_home_is_not_set_and_cwd_is_not_a_workspace(self):
        cwd = tempfile.mkdtemp()
        self.assertIsNone(workspace.try_locate(cwd))

    def test_try_locate_returns_cwd_if_cwd_is_a_workspace(self):
        cwd = os.path.join(tempfile.mkdtemp(), "ws")
        workspace.create(cwd)

        ws_path = workspace.try_locate(cwd)

        self.assertEqual(os.path.realpath(cwd), os.path.realpath(ws_path))

    def test_try_locate_returns_env_cwd_if_env_cwd_is_a_workspace(self):
        cwd = os.path.join(tempfile.mkdtemp(), "wd")
        workspace.create(cwd)

        with TemporaryEnv():
            os.chdir(cwd)
            ws_path = workspace.try_locate()
            self.assertEqual(os.path.realpath(cwd), os.path.realpath(ws_path))

    def test_try_locate_returns_LOR_HOME_if_it_is_set_in_env(self):
        cwd = os.path.join(tempfile.mkdtemp(), "wd")
        workspace.create(cwd)

        with TemporaryEnv():
            os.environ[lor._constants.WORKSPACE_ENV_VARNAME] = cwd

            ws_path = workspace.try_locate()
            self.assertEqual(os.path.realpath(cwd), os.path.realpath(ws_path))

    def test_get_package_name_returns_a_string_for_new_workspace(self):
        cwd = os.path.join(tempfile.mkdtemp(), "wd")
        workspace.create(cwd)

        ret = workspace.get_package_name(cwd)

        self.assertIsInstance(ret, str)

    def test_get_package_name_uses_WORKSPACE_NAME_variable(self):
        cwd = os.path.join(tempfile.mkdtemp(), "wd")
        workspace.create(cwd)

        props_file = os.path.join(cwd, lor._constants.WORKSPACE_PROPS)

        ws_name = util.base36_str()
        content = "WORKSPACE_NAME: " + ws_name

        os.remove(props_file)
        util.write_str_to_file(props_file, content)

        ret = workspace.get_package_name(cwd)

        self.assertEqual(ret, ws_name)

    def test_get_package_name_raises_Exception_if_supplied_non_workspace(self):
        with self.assertRaises(Exception):
            workspace.get_package_name(tempfile.mkdtemp())

    def test_get_package_name_raises_Exception_if_properties_file_missing_from_workspace(self):
        cwd = os.path.join(tempfile.mkdtemp(), "wd")
        workspace.create(cwd)
        props_file = os.path.join(cwd, lor._constants.WORKSPACE_PROPS)
        os.remove(props_file)

        with self.assertRaises(Exception):
            workspace.get_package_name(cwd)

    def test_get_package_name_raises_Exception_if_properties_file_missing_WORKSPACE_NAME_key(self):
        cwd = os.path.join(tempfile.mkdtemp(), "wd")
        workspace.create(cwd)
        props_file = os.path.join(cwd, lor._constants.WORKSPACE_PROPS)
        os.remove(props_file)
        util.write_str_to_file(props_file, "")

        with self.assertRaises(Exception):
            workspace.get_package_name(cwd)
