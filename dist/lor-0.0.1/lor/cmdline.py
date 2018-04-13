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
"""Top-level LoR CLI launcher
"""
import argparse
import sys

import lor._constants
import lor.commands
import lor.util.cli
from lor import workspace, util
from lor.commands.new import NewCommand
from lor.util import reflection
from lor.util.cli import CliCommand

CLI_DESCRIPTION = "Perform Luigi on Rails tasks"


def launch(out_of_workspace_subcommands=None, workspace_subcommands=None):
    """Launch LoR top-level CLI

    :param out_of_workspace_subcommands: A dict of <name: `CliCommand`>s to use when outside a workspace
    :param workspace_subcommands: A dict of <name: `CliCommand`>s to use when inside a workspace
    """
    if out_of_workspace_subcommands is None:
        out_of_workspace_subcommands = get_default_out_of_workspace_subcommands()

    if workspace_subcommands is None:
        workspace_subcommands = get_default_workspace_subcommands()

    if workspace.try_locate() is not None:
        commands = workspace_subcommands
    else:
        commands = out_of_workspace_subcommands

    __launch_cli(commands)


def get_default_workspace_subcommands():
    """Returns a dict of default in-workspace subcommands as <name: `CliCommand`>s

    :return A dict of <name: `CliCommand`>
    """
    subcommand_classes = reflection.subclasses_in_pkg(package=lor.commands, superclass=CliCommand)
    return {klass().name(): klass() for klass in subcommand_classes}


def get_default_out_of_workspace_subcommands():
    """Returns a dict of default out-of-workspace subcommands as <name: `CliCommand`>s

    :return: A dict of <name: `CliCommand`>
    """
    new_cmd = NewCommand()
    return {new_cmd.name(): new_cmd}


def __launch_cli(subcommands):
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    lor.util.cli.add_commands_as_subcommands(parser, subcommands.values())

    if len(sys.argv) > 1:
        __handle_top_level_args(subcommands, parser)
    else:
        parser.print_help(sys.stderr)
        exit(1)


def __handle_top_level_args(subcommands_by_name, parser):
    if sys.argv[1].startswith("-"):
        parser.parse_args()
    else:
        cmd_name = sys.argv[1]
        cmd_args = sys.argv[2:]
        __handle_command(subcommands_by_name, parser, cmd_name, cmd_args)


def __handle_command(subcommands_by_name, parser, cmd_name, cmd_args):
    if cmd_name in subcommands_by_name.keys():
        subcommand = subcommands_by_name[cmd_name]
        subcommand.run(cmd_args)
    else:
        choices = util.or_join(list(subcommands_by_name.keys()))
        err_msg = "invalid choice: {cmd_name}: choose from {choices}".format(cmd_name=cmd_name, choices=choices)
        parser.error(err_msg)
        exit(1)
