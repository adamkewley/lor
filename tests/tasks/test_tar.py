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
import filecmp
import os
import tarfile
import tempfile
from unittest import TestCase

import luigi

from lor import util
from lor.tasks.fs import EnsureExistsOnLocalFilesystemTask
from lor.tasks.tar import TarballTask


class TestTar(TestCase):

    def test_TarballTask_succeeds_if_given_a_dir(self):
        input_dir = tempfile.mkdtemp()
        output_path = os.path.join(tempfile.mkdtemp(), util.base36_str())

        tar_task = TarballTask(
            upstream_task=EnsureExistsOnLocalFilesystemTask(path=input_dir),
            output_path=output_path)

        ran_ok = luigi.build([tar_task], local_scheduler=True)

        self.assertTrue(ran_ok)
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(tarfile.is_tarfile(output_path))

    def test_TarballTask_output_tar_contains_input_file(self):
        _, input_file = tempfile.mkstemp()
        data_to_be_archived = os.urandom(1024)
        with open(input_file, "wb") as f:
            f.write(data_to_be_archived)
        output_path = os.path.join(tempfile.mkdtemp(), "output.tar")

        tar_task = TarballTask(
            upstream_task=EnsureExistsOnLocalFilesystemTask(path=input_file),
            output_path=output_path)

        ran_ok = luigi.build([tar_task], local_scheduler=True)

        self.assertTrue(ran_ok)
        self.assertTrue(os.path.exists(output_path))
        self.assertTrue(tarfile.is_tarfile(output_path))

        # Check actual content of the tar file
        with tarfile.open(output_path) as tar_obj:
            member = tar_obj.getmember(os.path.basename(input_file))
            tmp_dir = tempfile.mkdtemp()
            tar_obj.extract(member, path=tmp_dir)
            extracted_data_path = os.path.join(tmp_dir, member.name)

            self.assertTrue(os.path.exists(extracted_data_path))
            input_same_as_output = filecmp.cmp(input_file, extracted_data_path)
            self.assertTrue(input_same_as_output)
