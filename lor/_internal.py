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
Internal helper functions.
"""
import os
import sys
import lor._constants

from lor import workspace, path, props


def bootstrap_globals(prop_overrides):
    """
    Bootstrap global variables.

    Used by LoR CLI to bootstrap CLI overrides (variable vals etc.)

    :param prop_overrides:
    :return:
    :raises RuntimeError: If not in a workspace
    :raises FileNotFoundError: If workspace properties.yml file is missing
    """
    workspace_path = workspace.try_locate()

    if workspace_path is None:
        raise RuntimeError("Not currently in a workspace (or cannot locate one)")

    workspace._set_path(workspace_path)

    path._set_overlay_paths([])  # Not using overlay paths yet

    prop_file_path = os.path.join(workspace.get_path(), lor._constants.WORKSPACE_PROPS)

    if not os.path.exists(prop_file_path):
        raise FileNotFoundError("{prop_file_path}: No such file: a properties file is *required* in the workspace when running LoR")

    loaders = [
        props.DictPropertyLoader("cli-overrides", prop_overrides),
        props.YAMLFilePropertyLoader(prop_file_path),
    ]

    # This allows workspaces to be loaded dynamically at runtime by LoR and Luigi
    # (the Luigi docs get clients to set PYTHONPATH explicitly)
    sys.path.insert(0, workspace.get_path())

    props._set_loaders(loaders)
