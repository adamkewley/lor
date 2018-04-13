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
"""Utility tasks for HDFS
"""
import os

import luigi
from luigi import Parameter, Task, TaskParameter, LocalTarget
from luigi.contrib.hdfs.hadoopcli_clients import HdfsClient
from luigi.contrib.hdfs.target import HdfsTarget


class MoveToHdfsTask(luigi.Task):
    """Move the output of a task (assuming it's a LocalTarget) onto HDFS
    """

    description = "Move the output of a task to HDFS"

    upstream_task = luigi.TaskParameter()
    cache_invalidator = Parameter(default=None, description="Can be used to invalidate Luigi's instance cacher (which doesn't work with task params)")

    def requires(self):
        return self.upstream_task

    def run(self):
        source = self.input().path
        target = self.output().path

        client = HdfsClient()
        client.put(source, target)

    def output(self):
        return HdfsTarget(os.path.basename(self.input().path))


class DownloadFromHdfsTask(Task):

    description = "Move a file/dir from HDFS to the local filesystem"

    upstream_task = TaskParameter(description="A task that produces a file/dir on HDFS")
    output_path = Parameter()

    def requires(self):
        return self.upstream_task

    def run(self):
        client = HdfsClient()
        client.get(self.input().path, self.output().path)

    def output(self):
        return LocalTarget(os.path.basename(self.input().path))


class EnsureExistsOnHdfsTask(luigi.ExternalTask):

    description = "Ensure a file/dir exists on HDFS"

    path = luigi.Parameter()

    def output(self):
        return HdfsTarget(self.path)

    def run(self):
        raise RuntimeError("{path} does not exist on HDFS (it should).".format(path=self.path))


class ClusterDeployTask(Task):

    description = "Deploy a local file/dir to the cluster"

    def source(self):
        raise RuntimeError()

    def destination(self):
        raise RuntimeError()

    def run(self):
        if not os.path.exists(self.source()):
            raise FileNotFoundError("{source}: No such file".format(source=self.source()))

        client = luigi.contrib.hdfs.HdfsClient()
        client.put(self.source(), self.destination())

    def output(self):
        return HdfsTarget(self.destination())
