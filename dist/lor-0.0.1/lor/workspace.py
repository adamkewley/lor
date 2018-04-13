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
"""
Workspace support.

A workspace is a structured, but standard, python project, which enables downstream projects to use a "convention
over configuration" design. Definitions in this module make it easier to work with that structure (e.g. creating it,
establishing whether a directory is a workspace, resolving paths in the workspace).

This module also provides global access to the current workspace, which can be established automatically (from the
current working dir or an env var) or set explicitly (e.g. by LoR's CLI commands). This enables downstream code to
perform working-directory-independent pathing.
"""
import os
import subprocess

import sys

import lor._paths
import lor._constants

from cookiecutter.main import cookiecutter

__current_workspace_path = None


def create(output_path):
    """
    Create a new workspace at `output path`, returns the workspace's path.

    :param output_path: Full path to the workspace to create
    :raises FileNotFoundError: if output_path does not exist
    :raises NotADirectoryError: if output_path is not a directory
    """

    output_dir, workspace_name = os.path.split(output_path)
    cookiecutter(
        lor._paths.lor_path("templates/workspace"),
        no_input=True,
        extra_context={
            "workspace_name": workspace_name
        },
        output_dir=output_dir)

    __print_create_message_for_dir(output_path)

    return output_path


def __print_create_message_for_dir(dir):
    for root, dirs, files in os.walk(dir):
        print("create", root)
        for file in files:
            print("create", os.path.join(root, file))


def get_path(cwd=None):
    """
    Returns the current workspace's path, or None if the workspace has not been set and cannot be located automatically.

    :return: The current workspace's path as a string, or None if the current workspace cannot be established.
    """
    global __current_workspace_path

    if cwd is None:
        cwd = os.getcwd()

    if __current_workspace_path is None:
        maybe_ws_path = try_locate(cwd)
        if maybe_ws_path is not None:
            __current_workspace_path = maybe_ws_path
        else:
            __current_workspace_path = None

    return __current_workspace_path


def _set_path(ws_path):
    """
    Set the current (application-wide) workspace's path. Can be set to "None" to reset manual workspace setting.

    :param ws_path: The path of the new workspace
    :raises FileNotFoundError if `ws_path` does not exist
    :raises NotADirectoryError if `ws_path` is not a directory
    :raises ValueError if `ws_path` is not a workspace
    """
    global __current_workspace_path

    if ws_path is None:
        __current_workspace_path = None
    else:
        __assert_is_ws_dir_path(ws_path)
        __current_workspace_path = ws_path


def __assert_is_ws_dir_path(ws_path):
    if not os.path.exists(ws_path):
        raise FileNotFoundError("{ws_path}: No such directory: should be a workspace directory".format(ws_path=ws_path))
    elif not os.path.isdir(ws_path):
        raise NotADirectoryError("{ws_path}: Not a directory: should be a workspace directory".format(ws_path=ws_path))
    elif not is_workspace(ws_path):
        raise ValueError("{ws_path}: Is not workspace: should be a workspace directory".format(ws_path=ws_path))


def run_install_script(ws_path):
    """
    Run a workspace's install script.

    :param ws_path: Path to the workspace
    :return: True if the install script ran successfully; otherwise, False
    :raises FileNotFoundError: if `workspace_path` does not exist
    :raises NotADirectoryError: if `workspace_path` is not a directory
    :raises FileNotFoundError: if the install script cannot be found
    """

    __assert_is_ws_dir_path(ws_path)

    installer_path = os.path.abspath(os.path.join(ws_path, lor._constants.WORKSPACE_INSTALL_BINSTUB))

    if not os.path.exists(installer_path):
        raise FileNotFoundError("{installer_path}: No such file: should be an installer script")

    print("run   ", lor._constants.WORKSPACE_INSTALL_BINSTUB)

    exit_code = subprocess.call([installer_path])

    if exit_code == 0:
        return True
    else:
        print("The install command failed. Please fix all errors and re-run {cmd} before using the workspace".format(cmd=installer_path), sys.stderr)
        return False


def try_locate(cwd=None):
    """
    Returns a path to the workspace, if it can be found: otherwise, returns `None`.

    This function looks for a workspace by:

    - Checking if LOR_HOME environment variable is set and trying that
    - Checking if `cwd` is a workspace
    """
    maybe_workspace_from_env = __try_get_workspace_path_from_env_var()

    if maybe_workspace_from_env is not None:
        return maybe_workspace_from_env
    else:
        maybe_workspace_path = __try_get_workspace_path_from_cwd(cwd)

        if maybe_workspace_path is not None:
            return maybe_workspace_path
        else:
            return None


def __try_get_workspace_path_from_env_var():
    if lor._constants.WORKSPACE_ENV_VARNAME in os.environ:
        lor_home = os.environ.get(lor._constants.WORKSPACE_ENV_VARNAME)

        if is_workspace(lor_home):
            return lor_home
        else:
            err_msg = "{env_k}: {env_v}: is not a workspace. {env_k} should be set to a workspace directory: ignoring".format(env_k=lor._constants.WORKSPACE_ENV_VARNAME, env_v=lor_home)
            print(err_msg, file=sys.stderr)
            return None
    else:
        return None


def __try_get_workspace_path_from_cwd(cwd=None):
    if cwd is None:
        cwd = os.getcwd()

    if is_workspace(cwd):
        return cwd
    else:
        return None


def is_workspace(path):
    """
    Return True if path is a workspace; otherwise, return False.

    Throws if the path does not exist or is a file.

    :param path: The path to check
    :return: True if path is a workspace. False if path is not a workspace.
    :raises FileNotFoundError: if path does not exist
    :raises NotADirectoryError: if path is not a directory
    """

    if not os.path.exists(path):
        raise FileNotFoundError("{path}: no such file or directory")

    if os.path.isfile(path):
        raise NotADirectoryError("{path}: is a file: workspaces should be directories")

    lor_binstub = os.path.join(path, lor._constants.WORKSPACE_EXEC_BINSTUB)

    return os.path.exists(lor_binstub)
