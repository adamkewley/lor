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
"""General utility tasks
"""
from luigi import ExternalTask, Parameter


class DictPluckTask(ExternalTask):

    description = "Pluck a single output from a task that produces a dict of outputs"

    upstream_task = Parameter(description="A task that produces a dict output")
    key = Parameter(description="A key in the downstream task's output that should be plucked")

    def requires(self):
        return self.upstream_task

    def output(self):
        return self.input()[self.key]


class AlwaysRunsTask(ExternalTask):

    description = "A trivial task that always runs successfully"

    def complete(self):
        return True
