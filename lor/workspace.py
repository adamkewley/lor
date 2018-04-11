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
"""Workspace support

A workspace is a structured, but standard, python project, which enables downstream projects to use a "convention
over configuration" design. Definitions in this module make it easier to work with that structure (e.g. when resolving
paths).
"""
import os
import subprocess
import sys

from cookiecutter.main import cookiecutter

import lor._paths
import lor._constants
import lor.pathalias
from lor import properties
from lor.properties import YAMLFilePropertyLoader


def create(output_path, property_loaders=None):
    """Create a new workspace at the output path.

    :param output_path: Full path to the workspace to create
    :param property_loaders: `PropertyLoader` the returned workspace should use
    """
    if property_loaders is None:
        property_loaders = []

    output_dir, workspace_name = os.path.split(output_path)
    cookiecutter(
        lor._paths.lor_path("templates/workspace"),
        no_input=True,
        extra_context={
            "workspace_name": workspace_name
        },
        output_dir=output_dir)

    __print_create_message_for_dir(output_path)

    return Workspace(output_path, property_loaders)


def __print_create_message_for_dir(dir):
    for root, dirs, files in os.walk(dir):
        print("create", root)
        for file in files:
            print("create", os.path.join(root, file))


def install(workspace_path):
    """
    Run a workspace's install script.

    :param workspace_path: Path to the workspace
    :return: True if the install script ran successfully; otherwise, False
    """

    installer_path_in_ws = "bin/install"
    print("run   ", os.path.join(workspace_path, installer_path_in_ws))

    installer_abspath = os.path.join(workspace_path, installer_path_in_ws)
    exit_code = subprocess.call([installer_abspath])

    if exit_code == 0:
        return True
    else:
        print("The install command failed. Please fix all errors and re-run {cmd} before using the workspace".format(
            cmd=installer_path_in_ws), sys.stderr)
        return False


def try_locate(cwd=None):
    """Returns a path to the workspace, if it can be found: otherwise, returns `None`.

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
    """Return True if path is a workspace; otherwise, return False.

    Throws if the path does not exist or is a file.

    :param path: The path to check
    :return: True if path is a workspace. False if path is not a workspace.
    """

    if not os.path.exists(path):
        raise FileNotFoundError("{path}: no such file or directory")

    if os.path.isfile(path):
        raise NotADirectoryError("{path}: is a file: workspaces should be directories")

    lor_binstub = os.path.join(path, lor._constants.WORKSPACE_EXEC_BINSTUB)

    return os.path.exists(lor_binstub)


def get_default_property_loaders(workspace_dir):
    """Returns a list of default property loaders for a workspace dir.

    Raises `FileNotFoundError` if `workspace_dir` does not exist.
    Raises `NotADirectoryError` if `workspace_dir` is not a directory.
    Raises `RuntimeError` if `workspace_dir` is not a workspace dir.

    :return: A list of `PropertyLoader`s, ordered by high- to low-priority
    """

    if not os.path.exists(workspace_dir):
        raise FileNotFoundError("{workspace_dir}: No such directory: expected workspace directory".format(workspace_dir=workspace_dir))
    elif not os.path.isdir(workspace_dir):
        raise NotADirectoryError("{workspace_dir}: Not a directory: expected a workspace directory".format(workspace_dir=workspace_dir))
    elif not is_workspace(workspace_dir):
        raise RuntimeError("{workspace_dir}: Not a workspace: it is a directory, but doesn't appear to be a workspace".format(workspace_dir=workspace_dir))
    else:
        workspace_properties_path = os.path.join(workspace_dir, lor._constants.WORKSPACE_PROPS)
        workspace_properties_loader = YAMLFilePropertyLoader(workspace_properties_path)

        return [workspace_properties_loader]


class Workspace:

    def __init__(self, workspace_path, property_loaders):
        workspace_path = os.path.abspath(workspace_path)
        if is_workspace(workspace_path):
            self.workspace_path = workspace_path
            self.property_loaders = property_loaders
        else:
            raise RuntimeError("{workspace_path}: is not a workspace".format(workspace_path=workspace_path))

    def resolve_path(self, path):
        """Resolve a path relative to the workspace.

        :param path: The path to resolve
        :return: A path resolved relative to the workspace
        """
        return os.path.join(self.workspace_path, path)

    def resolve_workspace_pathalias(self, alias):
        """Resolve a path from the workspace's workspace alias file.

        If the workspace aliases file does not exist, a FileNotFoundError is raised.
        If the `alias` does not exist, a KeyError is raised.

        :param alias: The alias to look up
        :return: A path resolved from the aliases file relative to the current workspace.
        """
        ws_alias_file = self.resolve_path(lor._constants.WORKSPACE_ALIASES)
        alias_val = self.resolve_alias_file(ws_alias_file, alias)
        return self.resolve_path(alias_val)

    def resolve_alias_file(self, alias_file_path, alias):
        """Resolve a path from an aliases file.

        If `alias_file_path` does not exist, FileNotFoundError is raised.
        If `alias` does not exist in the alias file, a KeyError is raised.

        :param alias_file_path: A filesystem path to an aliases (YAML) file. Relative paths are
        resolved relative to the current directory, NOT the current workspace.
        :param alias: The alias to resolve
        :return: The aliase's value
        """

        if os.path.exists(alias_file_path):
            return lor.pathalias.resolve(alias_file_path, alias, property_loaders=self.property_loaders)
        else:
            raise FileNotFoundError(
                "{alias}: cannot be resolved: the current workspace does not contain a workspace aliases file as {path}".format(
                    alias=alias, path=lor._constants.WORKSPACE_ALIASES))

    def get_property(self, prop_name):
        """Get the value of a property.

        If `prop_name` cannot be found, a KeyError is raised.

        :param prop_name: The property's string identifier.
        :return: The property's value.
        """
        return properties.get_property_from_list_of_loaders(self.property_loaders, prop_name)

    def get_properties(self):
        """Get a dict containing all available properties and their values.

        :return: A dict containing all properties and their values.
        """
        return properties.merge_list_of_property_loaders(self.property_loaders)

    def get_abspath(self):
        """Returns the absolute path of the workspace
        """
        return os.path.abspath(self.workspace_path)
