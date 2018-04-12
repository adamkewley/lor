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
import unittest

import luigi
from luigi import Target
from luigi.contrib.hdfs import HdfsClient

import lor._constants
from lor import util
from lor import workspace

tc = unittest.TestCase('__init__')


def assert_task_passes(luigi_task):
    """Assert that `luigi_task` can be executed on a local scheduler.

    An AssertionError is raised if the task cannot be executed

    :param luigi_task: A fully-instantiated Luigi task
    """
    ran_ok = luigi.build([luigi_task], local_scheduler=True)
    tc.assertTrue(ran_ok)
    __assert_output_exists(luigi_task.output())


def __assert_output_exists(output):
    if isinstance(output, Target):
        tc.assertTrue(output.exists)
    else:
        print("Incompatible output from task: " + str(output))


def assert_task_fails(luigi_task):
    """Assert that `luigi_task` cannot be executed on a local scheduler.

    An AssertionError is raised if the task executed successfully.

    :param luigi_task: A fully-instantiated Luigi task
    """
    ran_ok = luigi.build([luigi_task], local_scheduler=True)
    tc = unittest.TestCase('__init__')
    tc.assertTrue(not ran_ok)


class TemporaryHdfsDir(object):
    """Create a temporary directory on HDFS

    The directory's path on HDFS is returned. After the block exists, the dir is deleted. Useful for testing tasks
    on-cluster without filling the cluster's HDFS filesystem with test outputs.
    """

    def __init__(self):
        pass

    def __enter__(self):
        hdfs_client = HdfsClient()
        max_attempts = lor._constants.MAX_TMP_DIR_CREATION_ATTEMPTS
        for i in range(max_attempts):
            maybe_id = util.base36_str(10)
            if not hdfs_client.exists(maybe_id):
                hdfs_client.mkdir(maybe_id)
                self.path = maybe_id
                return maybe_id
            else:
                continue
        raise RuntimeError("Could not generate a temporary ID after {num} attempts".format(num=max_attempts))

    def __exit__(self, exc_type, exc_val, exc_tb):
        hdfs_client = HdfsClient()
        hdfs_client.remove(self.path)

        if exc_val is not None:
            raise exc_val
        else:
            return True


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
        ws = workspace.create(ws_path)
        workspace._set_path(ws)
        return ws

    def __exit__(self, exc_type, exc_val, exc_tb):
        workspace._set_path(self.existing)

        if exc_val is not None:
            raise exc_val
        else:
            return True
