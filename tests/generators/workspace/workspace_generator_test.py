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

import os

from lor.generators.workspace import workspace_generator


class TestWorkspaceGenerator(TestCase):

    def test_create_works_with_valid_arguments(self):
        path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace_generator.create(path)

    def test_create_creates_a_directory_at_path(self):
        path = os.path.join(tempfile.mkdtemp(), "ws")
        workspace_generator.create(path)
        self.assertTrue(os.path.exists(path))

    def test_create_raises_if_path_already_exists(self):
        path = tempfile.mkdtemp()
        with self.assertRaises(Exception):
            workspace_generator.create(path)

    def test_create_returns_a_path_to_the_workspace(self):
        path = os.path.join(tempfile.mkdtemp(), "ws")
        ret = workspace_generator.create(path)

        self.assertEqual(ret, path)
