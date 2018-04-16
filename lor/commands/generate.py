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

import lor.generators
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
        parser.add_argument("generator_name")
        parser.add_argument("generator_args", nargs='*')

        parsed_args = parser.parse_args(argv)

        generator_classes = self.__find_generators()

        for k in generator_classes:
            print(k.__name__)

        print(parsed_args)

    def __find_generators(self):
        return reflection.subclasses_in_pkg(lor.generators, Generator)
