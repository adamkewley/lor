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
"""Global workspace variable.

Workspaces are, themselves, immutable. A global is used by LoR because it simplifies downstream clients (mostly, Luigi
tasks) from having to use custom abstractions or write weird boilerplate + dependency injection stuff.
"""

from lor import workspace
from lor.workspace import Workspace

__current_workspace = None


def get(cwd=None):
    """Returns the current workspace as a `Workspace` object, or None if the workspace has not been set (or cannot
    be autoloaded).

    If a workspace has not been manually set with `set_current_workspace`, this function will attempt to load the
    workspace itself using `lor.workspace.try_autoload`.

    :return: A `Workspace` object representing the current workspace, or None if the current workspace cannot be
    established.
    """
    global __current_workspace

    if __current_workspace is None:
        maybe_ws_path = workspace.try_locate(cwd)
        if maybe_ws_path is not None:
            __current_workspace = Workspace(maybe_ws_path)
        else:
            __current_workspace = None

    return __current_workspace


def set(new_workspace):
    """Set the current (application-wide) workspace.
    """
    global __current_workspace

    if new_workspace is None or isinstance(new_workspace, Workspace):
        __current_workspace = new_workspace
    else:
        raise RuntimeError("`set_current_workspace` was called with a non-workspace object")


def bootstrap(prop_override_loaders=None):
    """Bootstrap the global workspace variable

    Explicitly initialize the global workspace variable with its default state + extra loaders (usually, from the CLI).
    This is usually called by CLI commands to prepare subsequent Luigi tasks with the correct workspace state.

    Raises a `RuntimeError` if the current workspace cannot be located.

    :param prop_override_loaders: A list of PropertyLoaders ordered by highest- to lowest-priority. All of these loaders are
    higher priority than the default property loaders.
    :return: The bootstrapped `Workspace` that will be returned by subsequent calls to `get_current_workspace`
    """

    if prop_override_loaders is None:
        prop_override_loaders = []

    workspace_dir = workspace.try_locate()

    if workspace_dir is None:
        raise RuntimeError("Cannot bootstrap workspace: cannot locate a workspace")

    default_loaders = workspace.get_default_property_loaders(workspace_dir)
    all_loaders = prop_override_loaders + default_loaders

    ws = Workspace(workspace_dir, all_loaders)

    set(ws)

    return ws
