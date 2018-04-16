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
import os

from lor import util, workspace
from lor.generator import Generator


class TaskGenerator(Generator):

    def description(self):
        return "Generate a new task + tests"

    def run(self, argv):
        task_snake_case_name = argv[0]
        task_camel_case_name = util.to_camel_case(task_snake_case_name) + "Task"
        workspace_path = workspace.get_path()

        if workspace_path is None:
            raise RuntimeError("Not currently in a workspace: running a task generator requires being in a workspace")

        ws_package_name = workspace.get_package_name(workspace_path)

        self.render_template(
            source="task.py.jinja2",
            destination=os.path.join(ws_package_name, "tasks", task_snake_case_name + ".py"),
            env={
                "task_classname": task_camel_case_name
            })

        self.render_template(
            source="test_task.py.jinja2",
            destination=os.path.join("tests", "tasks", "test_" + task_snake_case_name + ".py"),
            env={
                "workspace_pkg": ws_package_name,
                "task_module": "lor.tasks." + task_snake_case_name,
                "task_classname": task_camel_case_name,
            })
