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
"""
File/directory generation support

Generators help with LoR's "convention over configuration" approach by generating the most common files that users are
likely to need (e.g. a Luigi task). Using generators, clients are more likely to write projects with a standard layout
rather than create their own, which should make LoR projects easier to work with.

This module contains helpers for writing Generators. Generators are classes that have a command-line interface and,
when ran, generate files in the output dir (usually, a workspace).
"""
import inspect
import os
import shutil

import jinja2
import multipath

from lor import workspace


class Generator:
    """
    Abstract base class for a generator.

    Concrete implementations of `Generator` should provide a run method that parses command-line arguments (supplied)
    and generates the necessary files in the source/destination. By default, the source is assumed to be the templates
    directory and the destination is assumed to be within the workspace.
    """

    def run(self, argv):
        """
        Run the generator.

        :param argv: Command-line arguments for the generator
        :raises Exception For a wide variety of reasons (CLI parsing, cannot copy file, cannot create file, invaild args, etc.)
        """
        raise NotImplementedError()

    def description(self):
        """
        Returns a human-readable description of the generator as a string.

        :return: A human-readable description of the generator as a string.
        """
        return self.__class__.__name__

    def source_roots(self):
        """
        Returns a list of source folders from which source files/templates should be read.

        By default, returns the "templates/" directory, if a `templates/` dir exists in the generator's package.
        Otherwise, returns the path of the generator's package.

        :return: A list of source folders as strings.
        """
        package_dir = os.path.dirname(inspect.getsourcefile(inspect.getmodule(self)))
        maybe_templates_dir = os.path.join(package_dir, "templates/")

        if os.path.exists(maybe_templates_dir):
            return [maybe_templates_dir]
        else:
            return [package_dir]

    def destination_root(self):
        """
        Returns the destination root directory.

        Relative destination paths are resolved relative to this root. By default, the destination root is the current
        workspace if a current workspace can be established; otherwise, an AssertionError is raised.

        :return: The destination root directory as a string
        """
        maybe_workspace_path = workspace.get_path()

        if maybe_workspace_path is None:
            raise AssertionError("Not currently in a workspace: by default, generators write to a workspace")
        else:
            return maybe_workspace_path

    def render_template(self, source, destination, env):
        """
        Render a Jinja2 template.

        :param source: Path to source Jinja2 templated file. Relative paths are resolved relative to `source_roots` until a path exists.
        :param destination: Destination path. Relative paths are resolved relative to `destination_root`
        :param jinja2_env: A dict containing variables that appear within the Jinja2 template
        :raises FileNotFoundError if source does not exist
        :raises FileExistsError if destination already exists
        """
        jinja2_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.source_roots()))

        try:
            template = jinja2_env.get_template(source)
        except jinja2.TemplateNotFound as ex:
            raise FileNotFoundError("{source}: Cannot find template: tried: {source_roots}".format(source=source, source_roots=self.source_roots()))

        rendered_template = template.render(env)

        self.create_file(rendered_template, destination)

    def create_file(self, content, destination):
        """
        Create a file at `destination` and populate it with `content`.

        :param content: String content of the file
        :param destination: Destination path. Relative paths are resolved relative to `destination_root`
        :raises FileExistsError if destination already exists
        """
        destination_path = os.path.join(self.destination_root(), destination)

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        if os.path.exists(destination_path):
            raise FileExistsError("{destination_path}: already exists".format(destination_path=destination_path))

        with open(destination_path, "w") as f:
            f.write(content)

        self.__print_creation(destination)

    def __print_creation(self, destination):
        print("create  {destination}".format(destination=destination))

    def copy_file(self, source, destination):
        """
        Copy a file from `source` to `destination`.

        :param source: Path to source file. Relative paths are resolved relative to `source_roots` until a path exists.
        :param destination: Destination path. Relative paths are resolved relative to `destination_root`
        :raises FileNotFoundError if `source` does not exist
        :raises FileExistsError if `destination` already exists
        """
        source_path = multipath.resolve(self.source_roots(), source)
        destination_path = os.path.join(self.destination_root(), destination)

        if os.path.exists(destination_path):
            raise FileExistsError("{destination_path}: already exists: cannot copy {source_path} to this location".format(destination_path=destination_path, source_path=source_path))

        shutil.copy(source_path, destination_path)

        self.__print_creation(destination)

    def mkdir(self, destination):
        """
        Create an empty directory at `destination`.

        :param destination: Destination path. Relative paths are resolved relative to `destination_root`
        :raises FileExistsError if `destination` already exists
        """
        destination_path = os.path.join(self.destination_root(), destination)

        if os.path.exists(destination_path):
            raise FileExistsError("{destination_path}: already exists: cannot create a directory at this path".format(destination_path=destination_path))

        os.mkdir(destination_path)

        self.__print_creation(destination)
