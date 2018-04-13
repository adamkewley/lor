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
"""Utilities for command-line interfaces
"""


class CliCommand:
    """
    Abstract class that represents a CLI command (e.g. `run`, `import`)
    """

    def name(self):
        """
        Override to provide a method that returns a unique name for the command.
        :return:
        """
        raise NotImplementedError()

    def description(self):
        """
        Override to provide a method that returns a human-readable description of
        the command.
        :return:
        """
        raise NotImplementedError()

    def run(self, argv):
        """
        Override to provide a method that is called with the command's arguments
        :param argv:
        """
        raise NotImplementedError()


def add_commands_as_subcommands(arg_parser, subcommands):
    subparsers = arg_parser.add_subparsers(
        help="subcommands",
        description="valid subcommands")

    for command in subcommands:
        add_command_to_parser(subparsers, command)


def add_command_to_parser(arg_parser, command):
    subparser = arg_parser.add_parser(
        name=command.name(),
        help=command.description())
    subparser.set_defaults(func=lambda: command)


def add_properties_override_arg(subparser):
    subparser.add_argument(
        "--properties",
        type=str,
        help="Override a runtime variable by providing a 'KEY=VALUE' pair",
        nargs='*')


def extract_property_overrides(namespace):
    if namespace.properties is not None:
        return {e.split("=")[0]: e.split("=")[1] for e in namespace.properties}
    else:
        return {}
