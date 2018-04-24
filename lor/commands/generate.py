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
import argparse
import importlib
import re
import sys

import lor.generators
from lor import util, workspace
from lor.generator import Generator
from lor.util import reflection
from lor.util.cli import CliCommand


class GenerateCommand(CliCommand):

    def name(self):
        return "generate"

    def description(self):
        return "generate code in workspace"

    def run(self, argv):
        parser = argparse.ArgumentParser(description=self.description())
        generators = self.__find_generators()

        self.__add_generators_as_subcommands(parser, generators)

        if len(argv) > 0:
            self.__launch_generator(parser, generators, argv)
        else:
            parser.print_help()
            exit(1)

    def __find_generators(self):
        generators_in_lor = self.__list_of_generators_to_dict_of_generator_commands(reflection.subclasses_in_pkg(lor.generators, Generator))

        ws_path = workspace.get_path()

        if ws_path is not None:
            ws_package = workspace.get_package_name(ws_path)
            sys.path.insert(0, ws_path)
            try:
                generator_pkg = importlib.import_module(ws_package + ".generators")
                generators_in_ws = self.__list_of_generators_to_dict_of_generator_commands(reflection.subclasses_in_pkg(generator_pkg, Generator))
            except ImportError as ex:
                generators_in_ws = {}
        else:
            generators_in_ws = {}

        return util.merge(generators_in_lor, generators_in_ws)

    def __list_of_generators_to_dict_of_generator_commands(self, generator_classes):
        return {
            self.__convert_generator_classname_to_cmd(generator_class.__name__): generator_class()
            for generator_class
            in generator_classes
        }

    def __convert_generator_classname_to_cmd(self, classname):
        classname_without_generator_suffix = re.sub(r"(?i)generator$", "", classname)
        return util.to_snake_case(classname_without_generator_suffix)

    def __add_generators_as_subcommands(self, parser, generators):
        subparser = parser.add_subparsers(
            help="generators",
            description="known generators")

        for generator_cmd, generator in generators.items():
            subparser.add_parser(
                name=generator_cmd,
                help=generator.description())

    def __launch_generator(self, parser, generators, argv):
        generator_name = argv[0]
        generator_args = argv[1:]

        if generator_name in generators:
            generator = generators[generator_name]
            generator.run(generator_args)
        else:
            choices = util.or_join(list(generators.keys()))
            err_msg = "invalid choice: {generator_name}: choose from {choices}".format(generator_name=generator_name, choices=choices)
            parser.error(err_msg)
            exit(1)
