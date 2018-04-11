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
import tarfile

import os
from luigi import TaskParameter, Parameter, LocalTarget
from luigi.contrib.external_program import ExternalProgramTask


class TarballTask(ExternalProgramTask):
    """A task that puts another task's output (assuming it outputs a FileTarget) into a tarball)
    """

    describe = "Package a task's output into an uncompressed tarball."

    upstream_task = TaskParameter(description="Task that produces a local file")
    output_path = Parameter(description="Where the output archive should go")

    def requires(self):
        return self.upstream_task

    def program_args(self):
        input_path = self.input().path
        with tarfile.open(self.output().path, input_path) as tar:
            tar.add(input_path, arcname=os.path.basename(input_path))

    def output(self):
        return LocalTarget(self.output_path)
