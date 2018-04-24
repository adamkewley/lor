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
"""Testing support

This module contains helper functions that downstream workspaces might want to use for testing purposes.
"""
import os
import tempfile

from lor import workspace
from lor.generators.workspace import workspace_generator


class TemporaryEnv(object):
    """Enable the application's environment (env vars, pwd) to be temporarily mutated, resetting it afterwards.
    """

    def __enter__(self):
        self.env = os.environ.copy()
        self.cwd = os.getcwd()
        return os.environ

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.environ.clear()
        os.environ.update(self.env)
        os.chdir(self.cwd)

        if exc_val is not None:
            raise exc_val
        else:
            return True


class ChangeWorkspace(object):
    """Set the global workspace temporarily.
    """
    def __init__(self, ws_path):
        self.ws_path = ws_path

    def __enter__(self):
        self.existing = workspace.get_path()
        workspace._set_path(self.ws_path)
        return self.ws_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        workspace._set_path(self.existing)

        if exc_val is not None:
            raise exc_val
        else:
            return True


class TemporaryWorkspace(object):
    """Create a temporary workspace

    Creates a workspace and sets it as the global workspace temporarily.
    """

    def __enter__(self):
        self.existing = workspace.get_path()
        ws_path = os.path.join(tempfile.mkdtemp(), "ws")
        ws = workspace_generator.create(ws_path)
        workspace._set_path(ws)
        return ws

    def __exit__(self, exc_type, exc_val, exc_tb):
        workspace._set_path(self.existing)

        if exc_val is not None:
            raise exc_val
        else:
            return True
