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

Generators help with LoR's "convention over configuration" approach by providing generators for the most common files
that users are likely to need (e.g. a Luigi task). Using generators, clients are more likely to write projects with a
standard layout rather than create their own. This should hopefully make LoR projects standard enough for devs to work
together on them.

This module contains helpers for writing Generators. Generators are classes that have a command-line interface and, when
ran, generate files in the output dir (usually, a workspace). LoR generators have support for:

- Writing files with CLI feedback
- Rendering Jinda2 templates
- Running other generators
- Running executable files (e.g. install scripts)
"""
import inspect

from lor import workspace


class Generator:
    """
    Abstract base class for a generator.

    Concrete implementations of a Generator should provide a run method that parses command-line arguments (supplied)
    and generates the necessary files in the source/destination. By default, the source is assumed to be the templates
    directory and the destination is assumed to be within the workspace.
    """

    def run(self, argv):
        """
        Run the generator.

        :param argv: Command-line arguments for the generator
        """
        raise NotImplementedError()

    def description(self):
        """
        Returns a human-readable description of the generator as a string.

        :return: A human-readable description of the generator as a string.
        """
        return self.__name__

    def source_roots(self):
        """
        Returns a list of source folders from which files are copied/templates are rendered.

        By default, returns the "templates/" directory, if a `templates/` dir exists in the generator's package.
        Otherwise, returns the path of the generator's package.

        :return: A list of source folders as strings.
        """
        return [
            inspect.getsourcefile(inspect.getmodule(self))
        ]

    def destination_root(self):
        """
        Returns the destination root directory.

        Relative destination paths are resolved relative to this root. By default, the destination root is the current
        workspace if a current workspace can be established; otherwise, an AssertionError is raised.

        :return: The destination root directory as a string
        """
        return workspace.get_path()

    def render_template(self, source, destination, env):
        """
        Render a Jinja2 template.

        :param source: Path to source Jinja2 templated file. Relative paths are resolved relative to `source_roots` until a path exists.
        :param destination: Destination path. Relative paths are resolved relative to `destination_root`
        :param env: A dict containing variables that appear within the Jinja2 template
        :raises FileNotFoundError if source does not exist
        :raises FileExistsError if destination already exists
        """
        pass

    def create_file(self, content, destination):
        """
        Create a file populated with `content` at `destination`.

        :param content: String content of the file
        :param destination: Destination path. Relative paths are resolved relative to `destination_root`
        :raises FileExistsError if destination already exists
        """
        pass

    def copy_file(self, source, destination):
        """
        Copy a file from `source` to `destination`.

        :param source: Path to source file. Relative paths are resolved relative to `source_roots` until a path exists.
        :param destination: Destination path. Relative paths are resolved relative to `destination_root`
        :raises FileNotFoundError if `source` does not exist
        :raises FileExistsError if `destination` already exists
        """
        pass

    def mkdir(self, destination):
        """
        Create an empty directory at `destination`.

        :param destination: Destination path. Relative paths are resolved relative to `destination_root`
        :raises FileExistsError if `destination` already exists
        """
        pass
