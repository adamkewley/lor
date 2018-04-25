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
import logging
import os
import tarfile

from luigi import TaskParameter, Parameter, LocalTarget, Task

logger = logging.getLogger("luigi-interface")


class TarballTask(Task):
    """
    A task that puts another task's output (assuming it outputs a FileTarget) into a tarball)
    """

    describe = "Package a task's output into an uncompressed tarball."

    upstream_task = TaskParameter(description="Task that produces a local file")
    output_path = Parameter(description="Where the output archive should go")

    def requires(self):
        return self.upstream_task

    def run(self):
        input_path = self.input().path
        output_path = self.output().path

        if not os.path.exists(input_path):
            raise FileNotFoundError("{input_path}: no such file or directory: should be a *local* file/dir to be archived".format(input_path=input_path))

        logger.info("Putting {input_path} into a tar located at {output_path}".format(input_path=input_path, output_path=output_path))

        input_path = self.input().path
        with tarfile.open(self.output().path, "w") as tar:
            tar.add(input_path, arcname=os.path.basename(input_path))

        logger.info("{output_path}: tar created: size = {size} bytes".format(output_path=output_path, size= os.stat(output_path).st_size))

    def output(self):
        return LocalTarget(self.output_path)
