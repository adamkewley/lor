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

from lor.generator import Generator


class WorkspaceGenerator(Generator):

    def __init__(self, destination_root=None):
        if destination_root is None:
            self.destination_root_path = os.getcwd()
        else:
            self.destination_root_path = destination_root

    def description(self):
        return "Generate a new LoR workspace"

    def run(self, argv):
        workspace_name = argv[0]

        template_env = {"workspace_name": workspace_name}

        self.mkdir(workspace_name)
        self.render_template("README.rst.jinja2", os.path.join(workspace_name, "README.md"), template_env)
        self.copy_file("requirements.txt", os.path.join(workspace_name, "requirements.txt"))
        self.render_template("setup.py.jinja2", os.path.join(workspace_name, "setup.py"), template_env)
        self.create_file("", os.path.join(workspace_name, "requirements_dev.txt"))

        python_src_dir = os.path.join(workspace_name, workspace_name)
        self.mkdir(python_src_dir)
        self.copy_file("pkg_init.py", os.path.join(python_src_dir, "__init__.py"))

        tasks_pkg_dir = os.path.join(python_src_dir, "tasks")
        self.mkdir(tasks_pkg_dir)
        self.copy_file("pkg_init.py", os.path.join(tasks_pkg_dir, "__init__.py"))

        generators_dir = os.path.join(python_src_dir, "generators")
        self.mkdir(generators_dir)
        self.copy_file("pkg_init.py", os.path.join(generators_dir, "__init__.py"))

        self.mkdir(os.path.join(workspace_name, "tests"))

        config_dir = os.path.join(workspace_name, "etc")
        self.mkdir(config_dir)
        self.create_file("WORKSPACE_NAME: {workspace_name}\n".format(workspace_name=workspace_name), os.path.join(config_dir, "properties.yml"))

        bin_dir = os.path.join(workspace_name, "bin")
        self.mkdir(bin_dir)
        self.copy_file("install", os.path.join(bin_dir, "install"))
        self.copy_file("lor", os.path.join(bin_dir, "lor"))

    def destination_root(self):
        return self.destination_root_path


def create(output_path):
    """
    Create a new workspace at `output path`, returns the workspace's path.

    :param output_path: Full path to the workspace to create
    :raises FileNotFoundError: if output_path does not exist
    :raises NotADirectoryError: if output_path is not a directory
    """

    output_dir, workspace_name = os.path.split(output_path)
    ws_generator = WorkspaceGenerator(output_dir)
    ws_generator.run([workspace_name])

    return output_path
