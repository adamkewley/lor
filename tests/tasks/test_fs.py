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

import luigi
from lor import util
from luigi import LocalTarget

from lor.tasks.fs import EnsureExistsOnLocalFilesystemTask


class TestFs(TestCase):

    def test_EnsureExistsOnLocalFilesystemTask_succeeds_if_file_exists(self):
        _, file_that_exists = tempfile.mkstemp()

        task = EnsureExistsOnLocalFilesystemTask(path=file_that_exists)

        ran_ok = luigi.build([task], local_scheduler=True)

        self.assertTrue(ran_ok)

    def test_EnsureExistsOnLocalFilesystemTask_fails_if_file_does_not_exist(self):
        file_that_does_not_exist = util.base36_str(20)

        task = EnsureExistsOnLocalFilesystemTask(path=file_that_does_not_exist)

        ran_ok = luigi.build([task], local_scheduler=True)

        self.assertFalse(ran_ok)

    def test_EnsureExistsOnLocalFilesystemTask_output_is_LocalTarget_to_the_path(self):
        _, file_that_exists = tempfile.mkstemp()

        task = EnsureExistsOnLocalFilesystemTask(path=file_that_exists)

        output = task.output()

        self.assertIsInstance(output, LocalTarget)
        self.assertEqual(file_that_exists, output.path)


